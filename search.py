from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from db.session import get_session
from db.models import JobPosting
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

class JobSearcher:
    """Search and filter jobs from the local database"""
    
    def __init__(self):
        self.session = get_session()
    
    def search_jobs(
        self,
        title: Optional[str] = None,
        location: Optional[str] = None,
        company: Optional[str] = None,
        platform: Optional[str] = None,
        employment_type: Optional[str] = None,
        min_salary: Optional[float] = None,
        max_salary: Optional[float] = None,
        keywords: Optional[str] = None,
        days_ago: Optional[int] = None,
        limit: int = 50
    ) -> List[JobPosting]:
        """
        Search jobs with various filters
        
        Args:
            title: Job title keywords
            location: Location filter
            company: Company name filter
            platform: Source platform filter
            employment_type: Employment type filter
            min_salary: Minimum salary filter
            max_salary: Maximum salary filter
            keywords: Keywords to search in description
            days_ago: Only show jobs posted within N days
            limit: Maximum number of results
            
        Returns:
            List of JobPosting objects
        """
        try:
            query = self.session.query(JobPosting).filter(JobPosting.is_active == True)
            
            # Apply filters
            if title:
                query = query.filter(JobPosting.title.ilike(f'%{title}%'))
            
            if location:
                query = query.filter(JobPosting.location.ilike(f'%{location}%'))
            
            if company:
                query = query.filter(JobPosting.company_name.ilike(f'%{company}%'))
            
            if platform:
                query = query.filter(JobPosting.source_platform.ilike(f'%{platform}%'))
            
            if employment_type:
                query = query.filter(JobPosting.employment_type.ilike(f'%{employment_type}%'))
            
            if min_salary:
                query = query.filter(
                    or_(
                        JobPosting.salary_min >= min_salary,
                        JobPosting.salary_max >= min_salary
                    )
                )
            
            if max_salary:
                query = query.filter(
                    and_(
                        JobPosting.salary_min <= max_salary,
                        JobPosting.salary_min.isnot(None)
                    )
                )
            
            if keywords:
                keyword_filter = or_(
                    JobPosting.job_description.ilike(f'%{keywords}%'),
                    JobPosting.title.ilike(f'%{keywords}%')
                )
                query = query.filter(keyword_filter)
            
            if days_ago:
                cutoff_date = datetime.now() - timedelta(days=days_ago)
                query = query.filter(JobPosting.posted_date >= cutoff_date)
            
            # Order by posted date (newest first)
            query = query.order_by(desc(JobPosting.posted_date))
            
            # Apply limit
            results = query.limit(limit).all()
            
            return results
            
        except Exception as e:
            console.print(f"[red]Error searching jobs: {e}[/red]")
            return []
        finally:
            self.session.close()
    
    def search_and_display(
        self,
        title: Optional[str] = None,
        location: Optional[str] = None,
        company: Optional[str] = None,
        platform: Optional[str] = None,
        employment_type: Optional[str] = None,
        min_salary: Optional[float] = None,
        max_salary: Optional[float] = None,
        keywords: Optional[str] = None,
        days_ago: Optional[int] = None,
        limit: int = 50,
        detailed: bool = False
    ):
        """Search jobs and display results in a formatted table"""
        
        # Build search criteria string for display
        criteria = []
        if title:
            criteria.append(f"Title: {title}")
        if location:
            criteria.append(f"Location: {location}")
        if company:
            criteria.append(f"Company: {company}")
        if platform:
            criteria.append(f"Platform: {platform}")
        if employment_type:
            criteria.append(f"Type: {employment_type}")
        if min_salary:
            criteria.append(f"Min Salary: ${min_salary:,.0f}")
        if max_salary:
            criteria.append(f"Max Salary: ${max_salary:,.0f}")
        if keywords:
            criteria.append(f"Keywords: {keywords}")
        if days_ago:
            criteria.append(f"Within {days_ago} days")
        
        criteria_text = " | ".join(criteria) if criteria else "No filters applied"
        
        console.print(Panel.fit(
            f"[bold blue]Job Search Results[/bold blue]\n"
            f"Search Criteria: [yellow]{criteria_text}[/yellow]\n"
            f"Limit: [cyan]{limit}[/cyan]",
            title="🔍 Search"
        ))
        
        # Perform search
        jobs = self.search_jobs(
            title=title,
            location=location,
            company=company,
            platform=platform,
            employment_type=employment_type,
            min_salary=min_salary,
            max_salary=max_salary,
            keywords=keywords,
            days_ago=days_ago,
            limit=limit
        )
        
        if not jobs:
            console.print("[yellow]No jobs found matching your criteria.[/yellow]")
            return
        
        console.print(f"\n[green]Found {len(jobs)} jobs:[/green]\n")
        
        if detailed:
            self._display_detailed_results(jobs)
        else:
            self._display_summary_table(jobs)
    
    def _display_summary_table(self, jobs: List[JobPosting]):
        """Display jobs in a summary table format"""
        table = Table(title=f"Job Search Results ({len(jobs)} jobs)")
        table.add_column("Title", style="magenta", max_width=30)
        table.add_column("Company", style="cyan", max_width=20)
        table.add_column("Location", style="green", max_width=20)
        table.add_column("Salary", style="yellow", max_width=15)
        table.add_column("Type", style="blue", max_width=12)
        table.add_column("Platform", style="red", max_width=12)
        table.add_column("Posted", style="dim", max_width=10)
        
        for job in jobs:
            # Format salary
            salary_str = "Not specified"
            if job.salary_min and job.salary_max:
                if job.salary_min == job.salary_max:
                    salary_str = f"${job.salary_min:,.0f}"
                else:
                    salary_str = f"${job.salary_min:,.0f}-${job.salary_max:,.0f}"
            elif job.salary_min:
                salary_str = f"${job.salary_min:,.0f}+"
            
            # Format posted date
            posted_str = "Unknown"
            if job.posted_date:
                days_ago = (datetime.now() - job.posted_date).days
                if days_ago == 0:
                    posted_str = "Today"
                elif days_ago == 1:
                    posted_str = "Yesterday"
                elif days_ago < 7:
                    posted_str = f"{days_ago}d ago"
                elif days_ago < 30:
                    posted_str = f"{days_ago//7}w ago"
                else:
                    posted_str = f"{days_ago//30}m ago"
            
            table.add_row(
                job.title[:30] + "..." if len(job.title) > 30 else job.title,
                job.company_name[:20] + "..." if len(job.company_name) > 20 else job.company_name,
                (job.location or "Remote")[:20],
                salary_str,
                job.employment_type or "Unknown",
                job.source_platform,
                posted_str
            )
        
        console.print(table)
        
        # Show instructions for detailed view
        console.print("\n[dim]💡 Tip: Use --detailed flag for full job descriptions and URLs[/dim]")
    
    def _display_detailed_results(self, jobs: List[JobPosting]):
        """Display jobs with full details"""
        for i, job in enumerate(jobs, 1):
            # Format salary
            salary_info = "Salary not specified"
            if job.salary_min and job.salary_max:
                if job.salary_min == job.salary_max:
                    salary_info = f"Salary: ${job.salary_min:,.0f} {job.salary_currency}"
                else:
                    salary_info = f"Salary: ${job.salary_min:,.0f} - ${job.salary_max:,.0f} {job.salary_currency}"
            elif job.salary_min:
                salary_info = f"Salary: ${job.salary_min:,.0f}+ {job.salary_currency}"
            
            # Format posted date
            posted_info = "Posted date unknown"
            if job.posted_date:
                posted_info = f"Posted: {job.posted_date.strftime('%Y-%m-%d %H:%M')}"
            
            # Create job panel
            job_content = (
                f"[bold magenta]{job.title}[/bold magenta]\n"
                f"[cyan]{job.company_name}[/cyan] | [green]{job.location or 'Remote'}[/green]\n"
                f"[yellow]{salary_info}[/yellow] | [blue]{job.employment_type or 'Type not specified'}[/blue]\n"
                f"[red]Platform: {job.source_platform}[/red] | [dim]{posted_info}[/dim]\n\n"
                f"[bold]Description:[/bold]\n"
                f"{job.job_description[:300]}{'...' if len(job.job_description) > 300 else ''}\n\n"
                f"[bold]URL:[/bold] [link]{job.url}[/link]"
            )
            
            console.print(Panel(
                job_content,
                title=f"Job {i}/{len(jobs)}",
                border_style="blue"
            ))
            console.print()  # Add spacing between jobs
    
    def get_search_suggestions(self) -> Dict[str, List[str]]:
        """Get suggestions for search filters based on existing data"""
        try:
            suggestions = {}
            
            # Top companies
            top_companies = self.session.query(JobPosting.company_name, func.count(JobPosting.id)).filter(
                JobPosting.is_active == True
            ).group_by(JobPosting.company_name).order_by(desc(func.count(JobPosting.id))).limit(10).all()
            suggestions['companies'] = [company for company, _ in top_companies]
            
            # Top locations
            top_locations = self.session.query(JobPosting.location, func.count(JobPosting.id)).filter(
                JobPosting.is_active == True,
                JobPosting.location.isnot(None)
            ).group_by(JobPosting.location).order_by(desc(func.count(JobPosting.id))).limit(10).all()
            suggestions['locations'] = [location for location, _ in top_locations]
            
            # Available platforms
            platforms = self.session.query(JobPosting.source_platform).filter(
                JobPosting.is_active == True
            ).distinct().all()
            suggestions['platforms'] = [platform[0] for platform in platforms]
            
            # Employment types
            emp_types = self.session.query(JobPosting.employment_type).filter(
                JobPosting.is_active == True,
                JobPosting.employment_type.isnot(None)
            ).distinct().all()
            suggestions['employment_types'] = [emp_type[0] for emp_type in emp_types]
            
            return suggestions
            
        except Exception as e:
            console.print(f"[red]Error getting suggestions: {e}[/red]")
            return {}
        finally:
            self.session.close()
    
    def display_search_help(self):
        """Display search help and suggestions"""
        suggestions = self.get_search_suggestions()
        
        console.print(Panel.fit(
            "[bold blue]RecruitIQ Search Help[/bold blue]\n\n"
            "[bold]Available search options:[/bold]\n"
            "• --title: Search job titles (e.g. 'software engineer', 'python developer')\n"
            "• --location: Filter by location (e.g. 'New York', 'Remote')\n"
            "• --company: Filter by company name\n"
            "• --platform: Filter by job platform (Indeed, Google Careers, etc.)\n"
            "• --employment-type: Filter by employment type (Full-time, Part-time, etc.)\n"
            "• --min-salary: Minimum salary filter (e.g. 50000)\n"
            "• --max-salary: Maximum salary filter (e.g. 100000)\n"
            "• --keywords: Search in job descriptions\n"
            "• --days-ago: Only show jobs posted within N days\n"
            "• --limit: Maximum number of results (default: 50)\n"
            "• --detailed: Show full job descriptions and URLs",
            title="🔍 Search Help"
        ))
        
        if suggestions:
            console.print("\n[bold green]Popular search options:[/bold green]")
            
            if suggestions.get('companies'):
                console.print(f"[cyan]Companies:[/cyan] {', '.join(suggestions['companies'][:5])}")
            
            if suggestions.get('locations'):
                console.print(f"[green]Locations:[/green] {', '.join(suggestions['locations'][:5])}")
            
            if suggestions.get('platforms'):
                console.print(f"[red]Platforms:[/red] {', '.join(suggestions['platforms'])}")
            
            if suggestions.get('employment_types'):
                console.print(f"[blue]Employment Types:[/blue] {', '.join(suggestions['employment_types'])}")
        
        console.print("\n[bold yellow]Example searches:[/bold yellow]")
        console.print("• recruitiq search --title 'python developer' --location 'New York'")
        console.print("• recruitiq search --company 'Google' --min-salary 100000")
        console.print("• recruitiq search --keywords 'machine learning' --days-ago 7 --detailed")
        console.print("• recruitiq search --platform 'RemoteOK' --employment-type 'Full-time'")
    
    def __del__(self):
        """Cleanup database session"""
        if hasattr(self, 'session') and self.session:
            self.session.close() 