#!/usr/bin/env python3
"""
RecruitIQ CV Analyzer
AI-powered CV analysis using OpenAI for intelligent feedback and job matching
"""

import re
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.status import Status

from ..db.session import get_session
from ..db.models import JobPosting
from sqlalchemy import func, or_, and_

console = Console()

class CVAnalyzer:
    """Comprehensive CV analysis and job matching system"""
    
    def __init__(self):
        self.session = get_session()
        self.openai_client = self._setup_openai_client()
        
    def _setup_openai_client(self):
        """Setup OpenAI client for CV analysis"""
        try:
            import openai
            
            # Try to get API key from environment variable
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                console.print("[yellow]⚠️ OPENAI_API_KEY not found in environment variables[/yellow]")
                api_key = Prompt.ask("Enter your OpenAI API key", password=True)
                if not api_key:
                    raise ValueError("OpenAI API key is required for CV analysis")
            
            client = openai.OpenAI(api_key=api_key)
            
            # Test the connection
            try:
                client.models.list()
                console.print("[green]✅ OpenAI connection established[/green]")
                return client
            except Exception as e:
                console.print(f"[red]❌ OpenAI connection failed: {e}[/red]")
                return None
                
        except ImportError:
            console.print("[yellow]⚠️ OpenAI package not installed. Install with: pip install openai[/yellow]")
            return None
        except Exception as e:
            console.print(f"[red]❌ Error setting up OpenAI: {e}[/red]")
            return None
    
    def parse_cv_file(self, file_path: str) -> str:
        """Parse CV file and extract text content"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"CV file not found: {file_path}")
        
        file_extension = file_path.suffix.lower()
        console.print(f"[dim]Parsing {file_extension} file: {file_path.name}[/dim]")
        
        try:
            if file_extension == '.txt':
                text = self._parse_txt(file_path)
            elif file_extension == '.pdf':
                text = self._parse_pdf(file_path)
            elif file_extension in ['.docx', '.doc']:
                text = self._parse_docx(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}. Supported: .txt, .pdf, .docx, .doc")
            
            # Debug: Show text length and preview
            text = text.strip()
            console.print(f"[dim]Extracted {len(text)} characters from CV[/dim]")
            
            if len(text) > 100:
                preview = text[:200] + "..." if len(text) > 200 else text
                console.print(f"[dim]Preview: {preview}[/dim]")
            
            if len(text) < 50:
                console.print(f"[yellow]⚠️ Warning: CV text is very short ({len(text)} characters). Check if file was parsed correctly.[/yellow]")
            
            return text
            
        except Exception as e:
            console.print(f"[red]Error parsing CV: {e}[/red]")
            # Provide specific help based on error type
            if "PyPDF2" in str(e):
                console.print("[yellow]💡 Install PDF support: pip install PyPDF2[/yellow]")
            elif "docx" in str(e):
                console.print("[yellow]💡 Install DOCX support: pip install python-docx[/yellow]")
            raise
    
    def _parse_txt(self, file_path: Path) -> str:
        """Parse text file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    def _parse_pdf(self, file_path: Path) -> str:
        """Parse PDF file using multiple methods for better compatibility"""
        try:
            import PyPDF2
            text = ""
            
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                console.print(f"[dim]PDF has {len(pdf_reader.pages)} pages[/dim]")
                
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += page_text + "\n"
                    console.print(f"[dim]Page {i+1}: {len(page_text)} characters[/dim]")
            
            # If PyPDF2 fails to extract much text, try alternative methods
            if len(text.strip()) < 100:
                console.print("[yellow]⚠️ PyPDF2 extracted limited text. Trying alternative method...[/yellow]")
                try:
                    # Try pdfplumber as fallback
                    import pdfplumber
                    alternative_text = ""
                    with pdfplumber.open(file_path) as pdf:
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                alternative_text += page_text + "\n"
                    
                    if len(alternative_text.strip()) > len(text.strip()):
                        console.print("[green]✅ Alternative method extracted more text[/green]")
                        text = alternative_text
                        
                except ImportError:
                    console.print("[dim]pdfplumber not available. Install with: pip install pdfplumber[/dim]")
                except Exception as e:
                    console.print(f"[dim]Alternative PDF parsing failed: {e}[/dim]")
            
            return text
            
        except ImportError:
            console.print("[yellow]⚠️ PyPDF2 not installed. Install with: pip install PyPDF2[/yellow]")
            console.print("[dim]For better PDF parsing, also try: pip install pdfplumber[/dim]")
            raise ImportError("PyPDF2 required for PDF parsing")
    
    def _parse_docx(self, file_path: Path) -> str:
        """Parse DOCX file"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            console.print("[yellow]⚠️ python-docx not installed. Install with: pip install python-docx[/yellow]")
            raise ImportError("python-docx required for DOCX parsing")
    
    def ai_analyze_cv(self, cv_text: str) -> Dict[str, Any]:
        """Use OpenAI to analyze CV and extract comprehensive information"""
        if not self.openai_client:
            console.print("[red]❌ OpenAI client not available. Using fallback analysis.[/red]")
            return self._fallback_analysis(cv_text)
        
        if len(cv_text.strip()) < 50:
            console.print("[red]❌ CV text is too short for meaningful analysis.[/red]")
            return self._fallback_analysis(cv_text)
        
        try:
            console.print("[dim]Sending CV to OpenAI for analysis...[/dim]")
            
            prompt = f"""
            Analyze this CV/Resume and return ONLY a valid JSON object with the following structure. Do not include any text before or after the JSON:

            {{
                "personal_information": {{
                    "name": "extracted name or null",
                    "email": "extracted email or null", 
                    "phone": "extracted phone or null",
                    "linkedin": "extracted linkedin URL or null",
                    "github": "extracted github URL or null",
                    "location": "extracted location or null"
                }},
                "professional_summary": {{
                    "years_of_experience": 0,
                    "job_title": "most recent or primary job title",
                    "industry": "industry/domain"
                }},
                "skills": {{
                    "programming_languages": ["list of programming languages"],
                    "frameworks_libraries": ["list of frameworks and libraries"],
                    "databases": ["list of databases"],
                    "cloud_devops": ["list of cloud and devops tools"],
                    "tools_software": ["list of tools and software"],
                    "methodologies": ["list of methodologies"],
                    "soft_skills": ["list of soft skills"],
                    "certifications": ["list of certifications"],
                    "domain_expertise": ["list of domain areas"]
                }},
                "experience_analysis": {{
                    "total_years": 0,
                    "most_recent_job": "title",
                    "key_achievements": ["list of achievements"],
                    "career_progression": "brief description"
                }},
                "education": {{
                    "degrees": ["list of degrees"],
                    "institutions": ["list of institutions"],
                    "certifications": ["list of certifications"]
                }},
                "cv_feedback": {{
                    "strengths": ["3-5 strength points"],
                    "improvements": ["3-5 improvement points"],
                    "missing_elements": ["missing elements"],
                    "overall_score": 7,
                    "suggestions": ["specific suggestions"]
                }},
                "job_market_insights": {{
                    "suitable_job_titles": ["recommended job titles"],
                    "recommended_skills": ["skills to develop"],
                    "industry_trends": "trends alignment"
                }}
            }}

            CV Text:
            {cv_text[:4000]}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert HR consultant. Return only valid JSON, no additional text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.2
            )
            
            analysis_text = response.choices[0].message.content.strip()
            console.print(f"[dim]Received {len(analysis_text)} characters from OpenAI[/dim]")
            
            # Find JSON in response
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                console.print("[red]❌ No JSON found in AI response[/red]")
                console.print(f"[dim]Raw response: {analysis_text[:200]}...[/dim]")
                raise ValueError("No JSON found in AI response")
            
            json_text = analysis_text[json_start:json_end]
            console.print(f"[dim]Parsing JSON ({len(json_text)} characters)...[/dim]")
            
            try:
                analysis = json.loads(json_text)
                analysis['analysis_date'] = datetime.now().isoformat()
                analysis['ai_powered'] = True
                analysis['word_count'] = len(cv_text.split())
                
                console.print("[green]✅ AI analysis completed successfully[/green]")
                return analysis
                
            except json.JSONDecodeError as je:
                console.print(f"[red]❌ JSON parsing failed: {je}[/red]")
                console.print(f"[dim]Problematic JSON: {json_text[:300]}...[/dim]")
                raise ValueError(f"JSON parsing failed: {je}")
                
        except Exception as e:
            console.print(f"[red]❌ AI analysis failed: {e}[/red]")
            if "rate_limit" in str(e).lower():
                console.print("[yellow]💡 OpenAI rate limit hit. Try again in a moment.[/yellow]")
            elif "api_key" in str(e).lower():
                console.print("[yellow]💡 Check your OpenAI API key configuration.[/yellow]")
            console.print("[yellow]Falling back to basic analysis...[/yellow]")
            return self._fallback_analysis(cv_text)
    
    def _fallback_analysis(self, cv_text: str) -> Dict[str, Any]:
        """Fallback analysis when OpenAI is not available"""
        console.print("[yellow]🔄 Using basic pattern-based analysis...[/yellow]")
        
        # Basic contact info extraction
        contact_info = self._extract_basic_contact_info(cv_text)
        
        # Basic skills extraction using keywords
        skills = self._extract_basic_skills(cv_text)
        
        # Basic experience estimation
        experience_years = self._extract_basic_experience(cv_text)
        
        return {
            'personal_information': contact_info,
            'professional_summary': {
                'years_of_experience': experience_years,
                'job_title': 'Not determined',
                'industry': 'Not determined'
            },
            'skills': skills,
            'experience_analysis': {
                'total_years': experience_years,
                'most_recent_job': 'Not determined',
                'key_achievements': [],
                'career_progression': 'Not analyzed'
            },
            'education': {
                'degrees': [],
                'institutions': [],
                'certifications': []
            },
            'cv_feedback': {
                'strengths': ['CV provided for analysis'],
                'improvements': ['Use AI analysis for detailed feedback'],
                'missing_elements': ['Requires AI analysis for detailed review'],
                'overall_score': 5,
                'suggestions': ['Set up OpenAI API key for comprehensive analysis']
            },
            'job_market_insights': {
                'suitable_job_titles': ['software engineer', 'developer'],
                'recommended_skills': ['Modern programming languages', 'Cloud technologies'],
                'industry_trends': 'Requires AI analysis'
            },
            'analysis_date': datetime.now().isoformat(),
            'ai_powered': False,
            'word_count': len(cv_text.split())
        }
    
    def _extract_basic_contact_info(self, cv_text: str) -> Dict[str, str]:
        """Basic contact information extraction"""
        contact_info = {}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, cv_text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Phone patterns
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',
            r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, cv_text)
            if phones:
                contact_info['phone'] = phones[0]
                break
        
        # LinkedIn and GitHub
        linkedin_pattern = r'linkedin\.com/in/[A-Za-z0-9-]+'
        linkedin = re.findall(linkedin_pattern, cv_text.lower())
        if linkedin:
            contact_info['linkedin'] = f"https://{linkedin[0]}"
        
        github_pattern = r'github\.com/[A-Za-z0-9-]+'
        github = re.findall(github_pattern, cv_text.lower())
        if github:
            contact_info['github'] = f"https://{github[0]}"
        
        return contact_info
    
    def _extract_basic_skills(self, cv_text: str) -> Dict[str, List[str]]:
        """Basic skills extraction using keyword matching"""
        cv_text_lower = cv_text.lower()
        
        basic_skills = {
            'programming_languages': ['python', 'javascript', 'java', 'c++', 'c#', 'go', 'rust', 'ruby', 'php'],
            'frameworks_libraries': ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'node.js'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle'],
            'cloud_devops': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins'],
            'tools_software': ['git', 'github', 'jira', 'slack', 'figma']
        }
        
        extracted = {}
        for category, skills_list in basic_skills.items():
            found = []
            for skill in skills_list:
                if skill in cv_text_lower:
                    found.append(skill)
            if found:
                extracted[category] = found
        
        return extracted
    
    def _extract_basic_experience(self, cv_text: str) -> Optional[int]:
        """Basic experience years extraction"""
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'(\d+)\+?\s*years?\s+in\s+',
            r'experience[:\s]+(\d+)\+?\s*years?'
        ]
        
        years = []
        for pattern in patterns:
            matches = re.findall(pattern, cv_text.lower())
            years.extend([int(match) for match in matches])
        
        return max(years) if years else None
    
    def match_jobs(self, analysis: Dict[str, Any], max_results: int = 20) -> List[Dict[str, Any]]:
        """Match jobs based on AI analysis results"""
        
        # Extract skills from analysis
        skills_data = analysis.get('skills', {})
        all_skills = []
        
        # Flatten all skills into a single list
        for skill_list in skills_data.values():
            if isinstance(skill_list, list):
                all_skills.extend([skill.lower() for skill in skill_list])
        
        if not all_skills:
            console.print("[yellow]No skills extracted for job matching[/yellow]")
            return []
        
        # Get experience years
        experience_years = None
        if 'professional_summary' in analysis:
            experience_years = analysis['professional_summary'].get('years_of_experience')
        elif 'experience_analysis' in analysis:
            experience_years = analysis['experience_analysis'].get('total_years')
        
        # Query jobs from database
        jobs = self.session.query(JobPosting).filter(
            JobPosting.is_active == True,
            JobPosting.job_description.isnot(None)
        ).all()
        
        if not jobs:
            console.print("[yellow]No jobs in database for matching[/yellow]")
            return []
        
        matched_jobs = []
        
        for job in jobs:
            job_desc_lower = job.job_description.lower()
            
            # Calculate skill match score
            skill_matches = []
            for skill in all_skills:
                if skill in job_desc_lower:
                    skill_matches.append(skill)
            
            match_score = len(skill_matches) / len(all_skills) * 100 if all_skills else 0
            
            # Experience matching (if available)
            experience_match = True
            if experience_years and job.job_description:
                # Look for experience requirements in job description
                exp_patterns = [
                    r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
                    r'(\d+)-(\d+)\s*years?',
                    r'minimum\s+(\d+)\s*years?'
                ]
                
                required_experience = []
                for pattern in exp_patterns:
                    matches = re.findall(pattern, job_desc_lower)
                    for match in matches:
                        if isinstance(match, tuple):
                            required_experience.extend([int(x) for x in match if x.isdigit()])
                        else:
                            required_experience.append(int(match))
                
                if required_experience:
                    min_required = min(required_experience)
                    if experience_years < min_required:
                        experience_match = False
                        match_score *= 0.7  # Reduce score for experience mismatch
            
            if match_score > 5:  # Lower threshold for AI analysis
                matched_jobs.append({
                    'job': job,
                    'match_score': round(match_score, 1),
                    'matched_skills': skill_matches,
                    'experience_match': experience_match
                })
        
        # Sort by match score
        matched_jobs.sort(key=lambda x: x['match_score'], reverse=True)
        
        return matched_jobs[:max_results]
    
    def suggest_scraping_query(self, analysis: Dict[str, Any]) -> str:
        """Suggest a scraping query based on AI analysis"""
        
        # Try to get job titles from AI insights first
        if 'job_market_insights' in analysis:
            job_titles = analysis['job_market_insights'].get('suitable_job_titles', [])
            if job_titles and isinstance(job_titles, list):
                return job_titles[0]
        
        # Fallback to skills-based query
        skills_data = analysis.get('skills', {})
        query_parts = []
        
        # Add programming languages (limit to top 2)
        prog_langs = skills_data.get('programming_languages', [])
        if prog_langs:
            query_parts.extend(prog_langs[:2])
        
        # Add frameworks (limit to top 1)
        frameworks = skills_data.get('frameworks_libraries', [])
        if frameworks:
            query_parts.append(frameworks[0])
        
        # Add relevant technologies
        cloud_skills = skills_data.get('cloud_devops', [])
        if cloud_skills:
            if 'aws' in [skill.lower() for skill in cloud_skills]:
                query_parts.append('aws')
            elif 'azure' in [skill.lower() for skill in cloud_skills]:
                query_parts.append('azure')
        
        # Default to software engineer if no specific skills
        if not query_parts:
            return "software engineer"
        
        return " ".join(query_parts[:3])  # Limit to 3 main terms
    
    def display_cv_analysis(self, analysis: Dict[str, Any]):
        """Display AI-powered CV analysis results in a beautiful format"""
        
        ai_powered = analysis.get('ai_powered', False)
        title = "🤖 AI-Powered CV Analysis" if ai_powered else "📄 Basic CV Analysis"
        console.print(Panel(title, style="blue"))
        
        # Personal Information
        personal_info = analysis.get('personal_information', {})
        if personal_info:
            contact_table = Table(title="📞 Contact Information")
            contact_table.add_column("Type", style="cyan")
            contact_table.add_column("Value", style="white")
            
            for key, value in personal_info.items():
                if value:
                    contact_table.add_row(key.title(), str(value))
            
            console.print(contact_table)
        
        # Professional Summary
        prof_summary = analysis.get('professional_summary', {})
        if prof_summary:
            summary_text = ""
            if prof_summary.get('years_of_experience'):
                summary_text += f"Experience: {prof_summary['years_of_experience']} years\n"
            if prof_summary.get('job_title'):
                summary_text += f"Role: {prof_summary['job_title']}\n"
            if prof_summary.get('industry'):
                summary_text += f"Industry: {prof_summary['industry']}"
            
            if summary_text:
                console.print(Panel(summary_text, title="💼 Professional Summary", style="green"))
        
        # Skills by Category
        skills = analysis.get('skills', {})
        if skills:
            for category, skill_list in skills.items():
                if skill_list and isinstance(skill_list, list):
                    category_name = category.replace('_', ' ').title()
                    skills_text = ", ".join(skill_list)
                    console.print(Panel(
                        f"[yellow]{skills_text}[/yellow]",
                        title=f"🛠️ {category_name} ({len(skill_list)} skills)"
                    ))
        
        # CV Feedback (AI-powered)
        cv_feedback = analysis.get('cv_feedback', {})
        if cv_feedback and ai_powered:
            # Strengths
            if cv_feedback.get('strengths'):
                strengths_text = "\n".join([f"✅ {strength}" for strength in cv_feedback['strengths']])
                console.print(Panel(strengths_text, title="💪 Strengths", style="green"))
            
            # Areas for improvement
            if cv_feedback.get('improvements'):
                improvements_text = "\n".join([f"⚠️ {improvement}" for improvement in cv_feedback['improvements']])
                console.print(Panel(improvements_text, title="📈 Areas for Improvement", style="yellow"))
            
            # Overall score
            if cv_feedback.get('overall_score'):
                score = cv_feedback['overall_score']
                score_color = "green" if score >= 7 else "yellow" if score >= 5 else "red"
                console.print(Panel(
                    f"[{score_color}]CV Score: {score}/10[/{score_color}]",
                    title="🎯 Overall Assessment"
                ))
        
        # Job Market Insights (AI-powered)
        job_insights = analysis.get('job_market_insights', {})
        if job_insights and ai_powered:
            if job_insights.get('suitable_job_titles'):
                titles = ", ".join(job_insights['suitable_job_titles'][:5])
                console.print(Panel(
                    f"[cyan]{titles}[/cyan]",
                    title="🎯 Recommended Job Titles"
                ))
            
            if job_insights.get('recommended_skills'):
                skills_to_learn = ", ".join(job_insights['recommended_skills'][:5])
                console.print(Panel(
                    f"[magenta]{skills_to_learn}[/magenta]",
                    title="📚 Skills to Develop"
                ))
        
        # Statistics
        word_count = analysis.get('word_count', 0)
        total_skills = 0
        if skills:
            for skill_list in skills.values():
                if isinstance(skill_list, list):
                    total_skills += len(skill_list)
        
        stats_text = f"Word Count: {word_count}\nTotal Skills: {total_skills}"
        if ai_powered:
            stats_text += f"\nAnalysis Type: AI-Powered"
        else:
            stats_text += f"\nAnalysis Type: Basic Pattern Matching"
            
        console.print(Panel(stats_text, title="📊 Statistics", style="dim"))
    
    def display_job_matches(self, matched_jobs: List[Dict[str, Any]]):
        """Display job matching results"""
        
        if not matched_jobs:
            console.print("[yellow]No matching jobs found in database[/yellow]")
            return
        
        console.print(Panel(f"🎯 Found {len(matched_jobs)} Matching Jobs", style="green"))
        
        # Summary table
        table = Table(title="Job Matches")
        table.add_column("Rank", style="cyan", width=5)
        table.add_column("Job Title", style="magenta", width=25)
        table.add_column("Company", style="blue", width=20)
        table.add_column("Match %", style="green", width=8)
        table.add_column("Skills", style="yellow", width=30)
        table.add_column("Experience", style="white", width=10)
        
        for i, match in enumerate(matched_jobs[:10], 1):  # Show top 10
            job = match['job']
            skills_preview = ", ".join(match['matched_skills'][:3])
            if len(match['matched_skills']) > 3:
                skills_preview += f" (+{len(match['matched_skills'])-3} more)"
            
            exp_status = "✅" if match['experience_match'] else "⚠️"
            
            table.add_row(
                str(i),
                job.title[:25] + "..." if len(job.title) > 25 else job.title,
                job.company_name[:20] + "..." if len(job.company_name) > 20 else job.company_name,
                f"{match['match_score']}%",
                skills_preview,
                exp_status
            )
        
        console.print(table)
        
        # Show details for top match
        if matched_jobs and Confirm.ask("Show details for top match?", default=True):
            top_match = matched_jobs[0]
            job = top_match['job']
            
            details = f"""
[bold]Title:[/bold] {job.title}
[bold]Company:[/bold] {job.company_name}
[bold]Location:[/bold] {job.location or 'Not specified'}
[bold]Platform:[/bold] {job.source_platform}
[bold]Match Score:[/bold] {top_match['match_score']}%
[bold]Matched Skills:[/bold] {', '.join(top_match['matched_skills'])}
[bold]Posted:[/bold] {job.posted_date.strftime('%Y-%m-%d') if job.posted_date else 'Unknown'}
"""
            if job.salary_min:
                details += f"\n[bold]Salary:[/bold] ${job.salary_min:,}"
                if job.salary_max and job.salary_max != job.salary_min:
                    details += f" - ${job.salary_max:,}"
            
            if job.url:
                details += f"\n[bold]URL:[/bold] {job.url}"
            
            console.print(Panel(details, title="🎯 Top Job Match", style="green"))
    
    def interactive_cv_analysis(self):
        """Interactive AI-powered CV analysis workflow"""
        title = "🤖 AI-Powered CV Analysis & Job Matching" if self.openai_client else "📄 Basic CV Analysis & Job Matching"
        console.print(Panel(title, style="blue"))
        
        # Get CV file path
        cv_path = Prompt.ask("📁 Enter CV file path (PDF, DOCX, or TXT)")
        
        if not Path(cv_path).exists():
            console.print(f"[red]❌ File not found: {cv_path}[/red]")
            return
        
        try:
            # Parse CV
            with Status("📖 Parsing CV file...", console=console):
                cv_text = self.parse_cv_file(cv_path)
            
            if len(cv_text.strip()) < 50:
                console.print("[red]❌ CV text is too short or couldn't be parsed properly[/red]")
                return
            
            # AI Analysis
            with Status("🤖 Analyzing CV with AI...", console=console) if self.openai_client else Status("🔍 Analyzing CV...", console=console):
                analysis = self.ai_analyze_cv(cv_text)
            
            # Display analysis
            self.display_cv_analysis(analysis)
            
            if not Confirm.ask("\nContinue to job matching?", default=True):
                return
            
            # Match jobs
            with Status("🎯 Matching jobs from database...", console=console):
                matched_jobs = self.match_jobs(analysis)
            
            self.display_job_matches(matched_jobs)
            
            # Suggest scraping
            if len(matched_jobs) < 5:
                console.print("\n[yellow]⚠️ Limited matches found in current database[/yellow]")
                suggested_query = self.suggest_scraping_query(analysis)
                
                if Confirm.ask(f"Run scraping for '{suggested_query}' to find more opportunities?"):
                    console.print(f"[cyan]💡 Suggested command:[/cyan]")
                    console.print(f"[dim]recruitiq scrape all --query \"{suggested_query}\"[/dim]")
                    
                    # Option to run scraping directly
                    if Confirm.ask("Run scraping now?", default=False):
                        return self._run_targeted_scraping(suggested_query, analysis)
            
        except Exception as e:
            console.print(f"[red]❌ Error during CV analysis: {e}[/red]")
            if "openai" in str(e).lower():
                console.print("[yellow]💡 Try setting up your OpenAI API key for better analysis[/yellow]")
    
    def _run_targeted_scraping(self, query: str, analysis: Dict[str, Any]):
        """Run targeted scraping based on CV analysis"""
        console.print(f"[blue]🕷️ Running targeted scraping for: {query}[/blue]")
        
        try:
            from ..scrapers import IndeedScraper, RemoteOKScraper
            from ..db.session import update_or_create_job_posting
            from ..utils.validators import validate_job_data
            
            total_saved = 0
            
            # Scrape Indeed
            with Status("🔍 Scraping Indeed...", console=console):
                indeed_scraper = IndeedScraper()
                indeed_jobs = indeed_scraper.search_jobs(query, "United States", 100)
                
                for job_data in indeed_jobs:
                    if validate_job_data(job_data):
                        try:
                            update_or_create_job_posting(self.session, job_data)
                            total_saved += 1
                        except:
                            continue
            
            # Scrape RemoteOK
            with Status("🌍 Scraping RemoteOK...", console=console):
                remote_scraper = RemoteOKScraper()
                remote_jobs = remote_scraper.search_jobs(query, 100)
                
                for job_data in remote_jobs:
                    if validate_job_data(job_data):
                        try:
                            update_or_create_job_posting(self.session, job_data)
                            total_saved += 1
                        except:
                            continue
            
            console.print(f"[green]✅ Scraped {total_saved} new jobs![/green]")
            
            # Re-run matching with new jobs
            if total_saved > 0:
                with Status("🎯 Re-matching with new jobs...", console=console):
                    matched_jobs = self.match_jobs(analysis)
                self.display_job_matches(matched_jobs)
            
        except Exception as e:
            console.print(f"[red]❌ Scraping failed: {e}[/red]")
    
    def __del__(self):
        """Clean up database session"""
        if hasattr(self, 'session'):
            self.session.close() 