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
        self.filters = {}
    
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
    
    def generate_html_report(self, report_type: str = "executive", **kwargs) -> str:
        """Generate beautiful HTML reports"""
        try:
            # Try multiple import approaches for better compatibility
            try:
                from reports import RecruitIQReporter
            except ImportError:
                import importlib.util
                import os
                
                # Get the absolute path to reports.py
                reports_path = os.path.join(os.path.dirname(__file__), 'reports.py')
                spec = importlib.util.spec_from_file_location("reports", reports_path)
                reports_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(reports_module)
                RecruitIQReporter = reports_module.RecruitIQReporter
            
            reporter = RecruitIQReporter()
            
            if report_type == "executive":
                days = kwargs.get('days', 30)
                return reporter.generate_executive_summary(days)
            elif report_type == "market":
                focus_role = kwargs.get('focus_role', None)
                return reporter.generate_market_intelligence_report(focus_role)
            elif report_type == "salary":
                job_titles = kwargs.get('job_titles', None)
                return reporter.generate_salary_analysis_report(job_titles)
            elif report_type == "skills":
                return reporter.generate_skills_demand_report()
            elif report_type == "company":
                companies = kwargs.get('companies', None)
                return reporter.generate_company_insights_report(companies)
            else:
                return reporter.generate_executive_summary()
                
        except ImportError as e:
            console.print(f"[red]HTML reporting requires additional packages: {e}[/red]")
            console.print("[yellow]Run: pip install plotly jinja2[/yellow]")
            return ""
        except Exception as e:
            console.print(f"[red]Error generating HTML report: {e}[/red]")
            return ""
    
    def interactive_analytics_menu(self):
        """Interactive analytics menu with multiple options"""
        from rich.prompt import Prompt, Confirm
        
        console.print(Panel("📊 Advanced Analytics Menu", style="blue"))
        
        options = [
            ("1", "📈 Executive Summary", "Complete overview with key metrics"),
            ("2", "🛠️ Skills Analysis", "Most in-demand skills and technologies"),
            ("3", "💰 Salary Intelligence", "Comprehensive salary analysis"),
            ("4", "🏢 Company Insights", "Company hiring patterns and trends"),
            ("5", "📍 Geographic Analysis", "Location-based job market insights"),
            ("6", "📊 Generate HTML Report", "Export beautiful HTML reports"),
            ("7", "🔧 Advanced Filtering", "Set custom filters for analysis"),
            ("0", "⬅️ Back", "Return to main menu")
        ]
        
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="bold cyan")
        table.add_column("Option", style="bold")
        table.add_column("Description", style="dim")
        
        for key, option, desc in options:
            table.add_row(key, option, desc)
        
        console.print(table)
        
        choice = Prompt.ask("Select analytics option", choices=[opt[0] for opt in options])
        
        if choice == "1":
            self.display_summary()
        elif choice == "2":
            self.display_skills_analysis()
        elif choice == "3":
            self.display_salary_intelligence()
        elif choice == "4":
            self.display_company_insights()
        elif choice == "5":
            self.display_geographic_analysis()
        elif choice == "6":
            self.interactive_report_generation()
        elif choice == "7":
            self.setup_advanced_filters()
        
        return choice != "0"
    
    def display_salary_intelligence(self):
        """Enhanced salary intelligence dashboard"""
        console.print(Panel("💰 Salary Intelligence Dashboard", style="yellow"))
        
        try:
            session = get_session()
            
            # Get jobs with salary data
            salary_jobs = session.query(JobPosting).filter(
                JobPosting.is_active == True,
                JobPosting.salary_min.isnot(None)
            ).all()
            
            if not salary_jobs:
                console.print("[yellow]No salary data available[/yellow]")
                return
            
            # Overall salary statistics
            salaries = [job.salary_min for job in salary_jobs]
            avg_salary = sum(salaries) / len(salaries)
            median_salary = sorted(salaries)[len(salaries) // 2]
            
            # Salary by location
            location_salaries = {}
            for job in salary_jobs:
                if job.location:
                    location = job.location.split(',')[0].strip()
                    if location not in location_salaries:
                        location_salaries[location] = []
                    location_salaries[location].append(job.salary_min)
            
            # Calculate location averages (minimum 3 jobs)
            location_avg = {
                loc: sum(sals) / len(sals)
                for loc, sals in location_salaries.items()
                if len(sals) >= 3
            }
            
            # Salary by company
            company_salaries = {}
            for job in salary_jobs:
                if job.company_name not in company_salaries:
                    company_salaries[job.company_name] = []
                company_salaries[job.company_name].append(job.salary_min)
            
            company_avg = {
                comp: sum(sals) / len(sals)
                for comp, sals in company_salaries.items()
                if len(sals) >= 2
            }
            
            # Display results
            console.print(Panel.fit(
                f"Average Salary: [green]${avg_salary:,.0f}[/green]\n"
                f"Median Salary: [yellow]${median_salary:,.0f}[/yellow]\n"
                f"Jobs with Salary: [cyan]{len(salary_jobs):,}[/cyan]\n"
                f"Salary Range: [blue]${min(salaries):,.0f} - ${max(salaries):,.0f}[/blue]",
                title="📊 Overall Statistics"
            ))
            
            # Top paying locations
            if location_avg:
                console.print("\n🌍 Top Paying Locations:")
                location_table = Table()
                location_table.add_column("Location", style="magenta")
                location_table.add_column("Average Salary", style="green")
                location_table.add_column("Job Count", style="cyan")
                
                sorted_locations = sorted(location_avg.items(), key=lambda x: x[1], reverse=True)[:10]
                for location, avg in sorted_locations:
                    job_count = len(location_salaries[location])
                    location_table.add_row(location, f"${avg:,.0f}", str(job_count))
                
                console.print(location_table)
            
            # Top paying companies
            if company_avg:
                console.print("\n🏢 Top Paying Companies:")
                company_table = Table()
                company_table.add_column("Company", style="magenta")
                company_table.add_column("Average Salary", style="green")
                company_table.add_column("Job Count", style="cyan")
                
                sorted_companies = sorted(company_avg.items(), key=lambda x: x[1], reverse=True)[:10]
                for company, avg in sorted_companies:
                    job_count = len(company_salaries[company])
                    company_table.add_row(company, f"${avg:,.0f}", str(job_count))
                
                console.print(company_table)
            
            session.close()
            
        except Exception as e:
            console.print(f"[red]Error in salary analysis: {e}[/red]")
    
    def display_company_insights(self):
        """Display company hiring insights"""
        console.print(Panel("🏢 Company Hiring Insights", style="cyan"))
        
        try:
            session = get_session()
            
            # Company hiring activity
            company_activity = session.query(
                JobPosting.company_name,
                func.count(JobPosting.id).label('job_count'),
                func.avg(JobPosting.salary_min).label('avg_salary')
            ).filter(
                JobPosting.is_active == True
            ).group_by(
                JobPosting.company_name
            ).having(
                func.count(JobPosting.id) >= 3
            ).order_by(
                desc('job_count')
            ).limit(15).all()
            
            if company_activity:
                table = Table(title="Top Hiring Companies")
                table.add_column("Rank", style="cyan", width=6)
                table.add_column("Company", style="magenta", width=25)
                table.add_column("Active Jobs", style="green", width=12)
                table.add_column("Avg Salary", style="yellow", width=15)
                
                for i, (company, job_count, avg_salary) in enumerate(company_activity, 1):
                    salary_str = f"${avg_salary:,.0f}" if avg_salary else "N/A"
                    table.add_row(str(i), company, str(job_count), salary_str)
                
                console.print(table)
            
            # Recent hiring trends (last 30 days)
            from datetime import datetime, timedelta
            recent_date = datetime.now() - timedelta(days=30)
            
            recent_hiring = session.query(
                JobPosting.company_name,
                func.count(JobPosting.id).label('recent_jobs')
            ).filter(
                JobPosting.is_active == True,
                JobPosting.created_at >= recent_date
            ).group_by(
                JobPosting.company_name
            ).having(
                func.count(JobPosting.id) >= 5
            ).order_by(
                desc('recent_jobs')
            ).limit(10).all()
            
            if recent_hiring:
                console.print("\n📈 Most Active Hirers (Last 30 Days):")
                recent_table = Table()
                recent_table.add_column("Company", style="magenta")
                recent_table.add_column("Recent Jobs", style="green")
                
                for company, recent_jobs in recent_hiring:
                    recent_table.add_row(company, str(recent_jobs))
                
                console.print(recent_table)
            
            session.close()
            
        except Exception as e:
            console.print(f"[red]Error in company analysis: {e}[/red]")
    
    def display_geographic_analysis(self):
        """Display geographic job market analysis"""
        console.print(Panel("📍 Geographic Job Market Analysis", style="green"))
        
        try:
            session = get_session()
            
            # Location distribution
            location_data = session.query(
                JobPosting.location,
                func.count(JobPosting.id).label('job_count'),
                func.avg(JobPosting.salary_min).label('avg_salary')
            ).filter(
                JobPosting.is_active == True,
                JobPosting.location.isnot(None)
            ).group_by(
                JobPosting.location
            ).having(
                func.count(JobPosting.id) >= 3
            ).order_by(
                desc('job_count')
            ).limit(20).all()
            
            if location_data:
                table = Table(title="Job Market by Location")
                table.add_column("Rank", style="cyan", width=6)
                table.add_column("Location", style="magenta", width=30)
                table.add_column("Jobs", style="green", width=10)
                table.add_column("Avg Salary", style="yellow", width=15)
                table.add_column("% of Total", style="blue", width=12)
                
                total_jobs = session.query(JobPosting).filter(JobPosting.is_active == True).count()
                
                for i, (location, job_count, avg_salary) in enumerate(location_data, 1):
                    salary_str = f"${avg_salary:,.0f}" if avg_salary else "N/A"
                    percentage = (job_count / total_jobs) * 100
                    table.add_row(
                        str(i),
                        location,
                        str(job_count),
                        salary_str,
                        f"{percentage:.1f}%"
                    )
                
                console.print(table)
            
            # Remote vs on-site analysis
            remote_keywords = ['remote', 'work from home', 'distributed', 'telecommute']
            remote_jobs = session.query(JobPosting).filter(
                JobPosting.is_active == True,
                func.or_(*[JobPosting.location.ilike(f'%{keyword}%') for keyword in remote_keywords])
            ).count()
            
            console.print(f"\n🌐 Remote Work Statistics:")
            console.print(f"Remote Jobs: [green]{remote_jobs:,}[/green]")
            console.print(f"On-site Jobs: [yellow]{total_jobs - remote_jobs:,}[/yellow]")
            console.print(f"Remote Percentage: [cyan]{(remote_jobs / total_jobs * 100):.1f}%[/cyan]")
            
            session.close()
            
        except Exception as e:
            console.print(f"[red]Error in geographic analysis: {e}[/red]")
    
    def interactive_report_generation(self):
        """Interactive HTML report generation"""
        from rich.prompt import Prompt, Confirm
        
        console.print(Panel("📊 HTML Report Generation", style="blue"))
        
        report_types = [
            ("executive", "📈 Executive Summary"),
            ("market", "🎯 Market Intelligence"),
            ("salary", "💰 Salary Analysis"),
            ("skills", "🛠️ Skills Demand"),
            ("company", "🏢 Company Insights")
        ]
        
        console.print("Available report types:")
        for i, (key, name) in enumerate(report_types, 1):
            console.print(f"{i}. {name}")
        
        choice = int(Prompt.ask("Select report type", default="1"))
        report_type = report_types[choice - 1][0]
        
        # Get additional parameters based on report type
        kwargs = {}
        if report_type == "executive":
            kwargs['days'] = int(Prompt.ask("Analysis period (days)", default="30"))
        elif report_type == "market":
            focus_role = Prompt.ask("Focus on specific role (optional)", default="")
            if focus_role:
                kwargs['focus_role'] = focus_role
        elif report_type == "salary":
            job_titles = Prompt.ask("Job titles to analyze (comma-separated)", default="")
            if job_titles:
                kwargs['job_titles'] = [title.strip() for title in job_titles.split(',')]
        elif report_type == "company":
            companies = Prompt.ask("Companies to analyze (comma-separated)", default="")
            if companies:
                kwargs['companies'] = [comp.strip() for comp in companies.split(',')]
        
        # Generate report
        console.print("[yellow]Generating HTML report...[/yellow]")
        
        try:
            file_path = self.generate_html_report(report_type, **kwargs)
            if file_path:
                console.print(f"[green]✅ Report generated: {file_path}[/green]")
                
                if Confirm.ask("Open report in browser?", default=True):
                    import webbrowser
                    import os
                    webbrowser.open(f"file://{os.path.abspath(file_path)}")
            else:
                console.print("[red]❌ Report generation failed[/red]")
                
        except Exception as e:
            console.print(f"[red]Error generating report: {e}[/red]")
    
    def setup_advanced_filters(self):
        """Setup advanced filters for analytics"""
        from rich.prompt import Prompt, Confirm
        
        console.print(Panel("🔧 Advanced Analytics Filters", style="magenta"))
        
        self.filters = {}
        
        if Confirm.ask("Filter by date range?", default=False):
            days = int(Prompt.ask("Number of days to analyze", default="30"))
            self.filters['days'] = days
        
        if Confirm.ask("Filter by job titles?", default=False):
            titles = Prompt.ask("Job titles (comma-separated)")
            self.filters['job_titles'] = [title.strip() for title in titles.split(',')]
        
        if Confirm.ask("Filter by companies?", default=False):
            companies = Prompt.ask("Companies (comma-separated)")
            self.filters['companies'] = [comp.strip() for comp in companies.split(',')]
        
        if Confirm.ask("Filter by locations?", default=False):
            locations = Prompt.ask("Locations (comma-separated)")
            self.filters['locations'] = [loc.strip() for loc in locations.split(',')]
        
        if Confirm.ask("Filter by salary range?", default=False):
            min_salary = float(Prompt.ask("Minimum salary", default="0"))
            max_salary = float(Prompt.ask("Maximum salary", default="500000"))
            self.filters['salary_range'] = (min_salary, max_salary)
        
        console.print(f"[green]✅ Filters applied: {len(self.filters)} active filters[/green]")