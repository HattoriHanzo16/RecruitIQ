import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict, List, Any, Optional
from collections import Counter
from datetime import datetime, timedelta
from db.session import get_session
from db.models import JobPosting
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

class JobAnalyzer:
    """Analyzer for job market data and trends"""
    
    def __init__(self):
        self.session = get_session()
    
    def generate_summary_stats(self) -> Dict[str, Any]:
        """Generate comprehensive summary statistics"""
        try:
            # Basic counts
            total_jobs = self.session.query(JobPosting).filter(JobPosting.is_active == True).count()
            
            if total_jobs == 0:
                return {"error": "No job data available. Run 'recruitiq scrape all' first."}
            
            # Top job titles
            top_titles = self.session.query(
                JobPosting.title,
                func.count(JobPosting.id).label('count')
            ).filter(
                JobPosting.is_active == True
            ).group_by(
                JobPosting.title
            ).order_by(
                desc('count')
            ).limit(10).all()
            
            # Top locations
            top_locations = self.session.query(
                JobPosting.location,
                func.count(JobPosting.id).label('count')
            ).filter(
                JobPosting.is_active == True,
                JobPosting.location.isnot(None)
            ).group_by(
                JobPosting.location
            ).order_by(
                desc('count')
            ).limit(10).all()
            
            # Top companies
            top_companies = self.session.query(
                JobPosting.company_name,
                func.count(JobPosting.id).label('count')
            ).filter(
                JobPosting.is_active == True
            ).group_by(
                JobPosting.company_name
            ).order_by(
                desc('count')
            ).limit(10).all()
            
            # Platform distribution
            platform_stats = self.session.query(
                JobPosting.source_platform,
                func.count(JobPosting.id).label('count')
            ).filter(
                JobPosting.is_active == True
            ).group_by(
                JobPosting.source_platform
            ).order_by(
                desc('count')
            ).all()
            
            # Employment type distribution
            employment_stats = self.session.query(
                JobPosting.employment_type,
                func.count(JobPosting.id).label('count')
            ).filter(
                JobPosting.is_active == True,
                JobPosting.employment_type.isnot(None)
            ).group_by(
                JobPosting.employment_type
            ).order_by(
                desc('count')
            ).all()
            
            # Salary statistics
            salary_stats = self._calculate_salary_stats()
            
            # Recent posting trends
            recent_jobs = self.session.query(JobPosting).filter(
                JobPosting.is_active == True,
                JobPosting.posted_date >= datetime.now() - timedelta(days=7)
            ).count()
            
            return {
                "total_jobs": total_jobs,
                "top_titles": [(title, count) for title, count in top_titles],
                "top_locations": [(location or "Remote/Unspecified", count) for location, count in top_locations],
                "top_companies": [(company, count) for company, count in top_companies],
                "platform_distribution": [(platform, count) for platform, count in platform_stats],
                "employment_types": [(emp_type or "Unspecified", count) for emp_type, count in employment_stats],
                "salary_stats": salary_stats,
                "recent_jobs_7_days": recent_jobs,
                "last_updated": datetime.now()
            }
            
        except Exception as e:
            return {"error": f"Error generating statistics: {e}"}
        finally:
            self.session.close()
    
    def _calculate_salary_stats(self) -> Dict[str, Any]:
        """Calculate salary statistics"""
        try:
            # Get jobs with salary information
            jobs_with_salary = self.session.query(JobPosting).filter(
                JobPosting.is_active == True,
                JobPosting.salary_min.isnot(None)
            ).all()
            
            if not jobs_with_salary:
                return {"error": "No salary data available"}
            
            # Calculate average salary (using minimum salary for jobs with ranges)
            salaries = []
            salary_ranges = []
            
            for job in jobs_with_salary:
                if job.salary_min:
                    salaries.append(job.salary_min)
                    if job.salary_max and job.salary_max != job.salary_min:
                        salary_ranges.append((job.salary_min, job.salary_max))
            
            if salaries:
                avg_salary = sum(salaries) / len(salaries)
                min_salary = min(salaries)
                max_salary = max(salaries)
                median_salary = sorted(salaries)[len(salaries) // 2]
                
                return {
                    "average_salary": round(avg_salary, 2),
                    "median_salary": round(median_salary, 2),
                    "min_salary": round(min_salary, 2),
                    "max_salary": round(max_salary, 2),
                    "jobs_with_salary": len(jobs_with_salary),
                    "salary_ranges": len(salary_ranges)
                }
            
            return {"error": "No valid salary data found"}
            
        except Exception as e:
            return {"error": f"Error calculating salary stats: {e}"}
    
    def analyze_job_trends(self, days: int = 30) -> Dict[str, Any]:
        """Analyze job posting trends over time"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Daily job postings
            daily_posts = self.session.query(
                func.date(JobPosting.posted_date).label('date'),
                func.count(JobPosting.id).label('count')
            ).filter(
                JobPosting.is_active == True,
                JobPosting.posted_date >= cutoff_date
            ).group_by(
                func.date(JobPosting.posted_date)
            ).order_by('date').all()
            
            # Platform trends
            platform_trends = self.session.query(
                JobPosting.source_platform,
                func.count(JobPosting.id).label('count')
            ).filter(
                JobPosting.is_active == True,
                JobPosting.posted_date >= cutoff_date
            ).group_by(
                JobPosting.source_platform
            ).order_by(desc('count')).all()
            
            return {
                "period_days": days,
                "daily_postings": [(str(date), count) for date, count in daily_posts],
                "platform_trends": [(platform, count) for platform, count in platform_trends],
                "total_jobs_period": sum(count for _, count in daily_posts)
            }
            
        except Exception as e:
            return {"error": f"Error analyzing trends: {e}"}
        finally:
            self.session.close()
    
    def get_skills_analysis(self) -> Dict[str, Any]:
        """Analyze most mentioned skills and technologies"""
        try:
            # Get all job descriptions
            jobs = self.session.query(JobPosting.job_description).filter(
                JobPosting.is_active == True,
                JobPosting.job_description.isnot(None)
            ).all()
            
            if not jobs:
                return {"error": "No job description data available"}
            
            # Common tech skills to look for
            tech_skills = [
                'python', 'javascript', 'java', 'react', 'node.js', 'sql',
                'aws', 'docker', 'kubernetes', 'git', 'linux', 'typescript',
                'postgresql', 'mongodb', 'redis', 'elasticsearch', 'kafka',
                'microservices', 'rest api', 'graphql', 'machine learning',
                'data science', 'devops', 'ci/cd', 'agile', 'scrum'
            ]
            
            skill_counts = Counter()
            
            for job in jobs:
                description = job.job_description.lower()
                for skill in tech_skills:
                    if skill.lower() in description:
                        skill_counts[skill] += 1
            
            # Get top 15 skills
            top_skills = skill_counts.most_common(15)
            
            return {
                "top_skills": top_skills,
                "total_jobs_analyzed": len(jobs),
                "skills_searched": len(tech_skills)
            }
            
        except Exception as e:
            return {"error": f"Error analyzing skills: {e}"}
        finally:
            self.session.close()
    
    def display_summary(self):
        """Display formatted summary statistics"""
        stats = self.generate_summary_stats()
        
        if "error" in stats:
            console.print(f"[red]Error: {stats['error']}[/red]")
            return
        
        # Main statistics panel
        console.print(Panel.fit(
            f"[bold blue]RecruitIQ Job Market Analysis[/bold blue]\n"
            f"Total Jobs: [green]{stats['total_jobs']:,}[/green]\n"
            f"Recent Jobs (7 days): [yellow]{stats['recent_jobs_7_days']:,}[/yellow]\n"
            f"Last Updated: [dim]{stats['last_updated'].strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
            title="📊 Overview"
        ))
        
        # Top job titles table
        if stats['top_titles']:
            title_table = Table(title="🎯 Top 10 Job Titles")
            title_table.add_column("Rank", style="cyan", no_wrap=True)
            title_table.add_column("Job Title", style="magenta")
            title_table.add_column("Count", style="green")
            
            for i, (title, count) in enumerate(stats['top_titles'], 1):
                title_table.add_row(str(i), title, str(count))
            
            console.print(title_table)
        
        # Top locations table
        if stats['top_locations']:
            location_table = Table(title="📍 Top 10 Locations")
            location_table.add_column("Rank", style="cyan", no_wrap=True)
            location_table.add_column("Location", style="magenta")
            location_table.add_column("Count", style="green")
            
            for i, (location, count) in enumerate(stats['top_locations'], 1):
                location_table.add_row(str(i), location, str(count))
            
            console.print(location_table)
        
        # Top companies table
        if stats['top_companies']:
            company_table = Table(title="🏢 Top 10 Companies")
            company_table.add_column("Rank", style="cyan", no_wrap=True)
            company_table.add_column("Company", style="magenta")
            company_table.add_column("Count", style="green")
            
            for i, (company, count) in enumerate(stats['top_companies'], 1):
                company_table.add_row(str(i), company, str(count))
            
            console.print(company_table)
        
        # Salary statistics
        if 'salary_stats' in stats and 'error' not in stats['salary_stats']:
            salary_stats = stats['salary_stats']
            console.print(Panel.fit(
                f"Average Salary: [green]${salary_stats['average_salary']:,.2f}[/green]\n"
                f"Median Salary: [yellow]${salary_stats['median_salary']:,.2f}[/yellow]\n"
                f"Salary Range: [cyan]${salary_stats['min_salary']:,.2f} - ${salary_stats['max_salary']:,.2f}[/cyan]\n"
                f"Jobs with Salary Info: [blue]{salary_stats['jobs_with_salary']}[/blue]",
                title="💰 Salary Statistics"
            ))
        
        # Platform distribution
        if stats['platform_distribution']:
            platform_table = Table(title="🌐 Jobs by Platform")
            platform_table.add_column("Platform", style="magenta")
            platform_table.add_column("Count", style="green")
            platform_table.add_column("Percentage", style="cyan")
            
            total = stats['total_jobs']
            for platform, count in stats['platform_distribution']:
                percentage = (count / total) * 100
                platform_table.add_row(platform, str(count), f"{percentage:.1f}%")
            
            console.print(platform_table)
    
    def display_skills_analysis(self):
        """Display skills analysis"""
        skills_data = self.get_skills_analysis()
        
        if "error" in skills_data:
            console.print(f"[red]Error: {skills_data['error']}[/red]")
            return
        
        skills_table = Table(title="🛠️ Most In-Demand Skills")
        skills_table.add_column("Rank", style="cyan", no_wrap=True)
        skills_table.add_column("Skill", style="magenta")
        skills_table.add_column("Mentions", style="green")
        skills_table.add_column("% of Jobs", style="yellow")
        
        total_jobs = skills_data['total_jobs_analyzed']
        
        for i, (skill, count) in enumerate(skills_data['top_skills'], 1):
            percentage = (count / total_jobs) * 100
            skills_table.add_row(str(i), skill.title(), str(count), f"{percentage:.1f}%")
        
        console.print(skills_table)
        
        console.print(Panel.fit(
            f"Jobs Analyzed: [green]{total_jobs:,}[/green]\n"
            f"Skills Searched: [blue]{skills_data['skills_searched']}[/blue]",
            title="📈 Analysis Details"
        )) 