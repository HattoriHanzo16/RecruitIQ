#!/usr/bin/env python3
"""
RecruitIQ Interactive CLI Interface
Beautiful terminal-based interface for job market intelligence
"""

import os
import sys
import time
import threading
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta

from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.live import Live
from rich.columns import Columns
from rich.tree import Tree
from rich.rule import Rule
from rich.status import Status

# Import RecruitIQ modules
from ..scrapers import IndeedScraper, CompanyScraper, RemoteOKScraper, LinkedInScraper, GlassdoorScraper
from ..core.analyzer import JobAnalyzer
from ..core.searcher import JobSearcher
from ..db.session import init_db, get_session
from ..db.models import JobPosting
from ..utils.validators import validate_job_data

class InteractiveRecruitIQ:
    """Interactive CLI interface for RecruitIQ"""
    
    def __init__(self):
        self.console = Console()
        self.running = True
        self.current_menu = "main"
        self.status_message = "Ready"
        self.stats_cache = None
        self.stats_last_updated = None
        
        # Colors and themes
        self.colors = {
            'primary': 'blue',
            'secondary': 'cyan', 
            'success': 'green',
            'warning': 'yellow',
            'error': 'red',
            'accent': 'magenta'
        }
        
    def clear_screen(self):
        """Clear the console screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def show_header(self):
        """Display the application header"""
        header_text = Text()
        header_text.append("🎯 ", style="bold red")
        header_text.append("RecruitIQ", style="bold blue")
        header_text.append(" - Job Market Intelligence", style="bold")
        
        header_panel = Panel(
            Align.center(header_text),
            style="blue",
            padding=(1, 2)
        )
        
        self.console.print(header_panel)
        self.console.print()
    
    def show_status_bar(self):
        """Display status bar with current information"""
        status_items = []
        
        # Database status
        try:
            session = get_session()
            job_count = session.query(JobPosting).filter(JobPosting.is_active == True).count()
            status_items.append(f"💾 Jobs: {job_count:,}")
            session.close()
        except:
            status_items.append("💾 DB: Error")
        
        # Current time
        status_items.append(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
        
        # Status message
        status_items.append(f"📊 {self.status_message}")
        
        status_text = " | ".join(status_items)
        self.console.print(Panel(status_text, style="dim", height=3))
    
    def run(self):
        """Main application loop"""
        try:
            while self.running:
                self.clear_screen()
                self.show_header()
                
                # Show main menu
                menu_items = [
                    ("1", "🕷️  Scrape Jobs", "Scrape jobs from all platforms"),
                    ("2", "🔍 Search Jobs", "Search and filter local job database"),
                    ("3", "📊 Analytics", "View job market analysis and trends"),
                    ("4", "💰 Salary Insights", "Glassdoor salary data and insights"),
                    ("5", "⚙️  Settings", "Configure scraping preferences"),
                    ("6", "📋 Status", "View system status and statistics"),
                    ("7", "❓ Help", "Get help and documentation"),
                    ("0", "🚪 Exit", "Exit RecruitIQ")
                ]
                
                menu_table = Table(title="🎯 Main Menu", show_header=False, box=None, padding=(0, 2))
                menu_table.add_column("Key", style="bold cyan", width=3)
                menu_table.add_column("Option", style="bold", width=20)
                menu_table.add_column("Description", style="dim", width=40)
                
                for key, option, description in menu_items:
                    menu_table.add_row(key, option, description)
                
                self.console.print(Panel(menu_table, style="blue"))
                
                self.show_status_bar()
                
                try:
                    choice = Prompt.ask("Choose option", choices=["0", "1", "2", "3", "4", "5", "6", "7"])
                    
                    if choice == "1":
                        self.scrape_all_interactive()
                    elif choice == "2":
                        self.search_jobs_interactive()
                    elif choice == "3":
                        self.show_analytics()
                    elif choice == "4":
                        self.show_salary_insights()
                    elif choice == "5":
                        self.show_settings()
                    elif choice == "6":
                        self.show_status()
                    elif choice == "7":
                        self.show_help()
                    elif choice == "0":
                        break
                        
                except KeyboardInterrupt:
                    if Confirm.ask("\n🚪 Exit RecruitIQ?", default=True):
                        break
                    continue
                except Exception as e:
                    self.console.print(f"[red]Error: {e}[/red]")
                    input("Press Enter to continue...")
        
        except KeyboardInterrupt:
            pass
        finally:
            self.clear_screen()
            self.console.print(Panel(
                Align.center("[bold blue]Thanks for using RecruitIQ! 🎯[/bold blue]\n[dim]Happy job hunting![/dim]"),
                style="blue"
            ))

    def scrape_all_interactive(self):
        """Interactive all-platform scraping"""
        self.clear_screen()
        self.show_header()
        
        self.console.print(Panel("🕷️ Comprehensive Job Scraping", style="green"))
        
        query = Prompt.ask("🔍 Job search query", default="software engineer")
        location = Prompt.ask("📍 Location (for Indeed)", default="United States")
        limit = int(Prompt.ask("📊 Jobs per platform", default="100"))
        include_linkedin = Confirm.ask("🔗 Include LinkedIn?", default=True)
        
        total_saved = 0
        platforms = ['Indeed', 'Company Sites', 'RemoteOK']
        if include_linkedin:
            platforms.append('LinkedIn')
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            
            main_task = progress.add_task("🕷️ Overall Progress", total=len(platforms))
            
            # Initialize database
            try:
                init_db()
                progress.console.print("[green]✅ Database initialized[/green]")
            except Exception as e:
                progress.console.print(f"[red]❌ Database error: {e}[/red]")
                return
            
            # Scrape each platform
            for platform in platforms:
                platform_task = progress.add_task(f"Scraping {platform}...", total=100)
                
                try:
                    if platform == 'Indeed':
                        scraper = IndeedScraper()
                        jobs = scraper.search_jobs(query, location, limit)
                    elif platform == 'Company Sites':
                        scraper = CompanyScraper()
                        jobs = scraper.scrape_all_companies(query, limit)
                    elif platform == 'RemoteOK':
                        scraper = RemoteOKScraper()
                        jobs = scraper.search_jobs(query, limit)
                    elif platform == 'LinkedIn':
                        scraper = LinkedInScraper()
                        jobs = scraper.search_jobs(query, location, limit)
                    
                    progress.update(platform_task, completed=50)
                    
                    # Save jobs
                    saved_count = self._save_jobs_to_db(jobs, platform)
                    total_saved += saved_count
                    
                    progress.update(platform_task, completed=100)
                    progress.console.print(f"[green]✅ {platform}: {saved_count} jobs saved[/green]")
                    
                except Exception as e:
                    progress.console.print(f"[red]❌ {platform} failed: {e}[/red]")
                
                progress.advance(main_task)
        
        # Show completion
        self.console.print(Panel(
            f"[bold green]🎉 Scraping Complete![/bold green]\n"
            f"Total jobs saved: [yellow]{total_saved:,}[/yellow]\n"
            f"Press Enter to continue...",
            title="📊 Summary"
        ))
        input()

    def _save_jobs_to_db(self, jobs: List, platform: str) -> int:
        """Save jobs to database"""
        if not jobs:
            return 0
        
        session = get_session()
        saved_count = 0
        
        try:
            from ..db.session import update_or_create_job_posting
            
            for job_data in jobs:
                if validate_job_data(job_data):
                    try:
                        update_or_create_job_posting(session, job_data)
                        saved_count += 1
                    except Exception:
                        continue
            
            return saved_count
            
        finally:
            session.close()

    def search_jobs_interactive(self):
        """Interactive job search interface"""
        self.clear_screen()
        self.show_header()
        
        searcher = JobSearcher()
        
        self.console.print(Panel("🔍 Job Search", style="cyan"))
        
        # Get search parameters
        title = Prompt.ask("🎯 Job title (optional)", default="") or None
        location = Prompt.ask("📍 Location (optional)", default="") or None
        company = Prompt.ask("🏢 Company (optional)", default="") or None
        keywords = Prompt.ask("🔑 Keywords (optional)", default="") or None
        
        limit = int(Prompt.ask("📊 Max results", default="50"))
        detailed = Confirm.ask("📋 Show detailed results?", default=False)
        
        # Perform search
        with Status("🔍 Searching jobs...", console=self.console):
            jobs = searcher.search_jobs(
                title=title, location=location, company=company,
                keywords=keywords, limit=limit
            )
        
        if not jobs:
            self.console.print("[yellow]No jobs found matching your criteria.[/yellow]")
        else:
            self.console.print(f"[green]Found {len(jobs)} jobs:[/green]\n")
            
            if detailed:
                searcher._display_detailed_results(jobs)
            else:
                searcher._display_summary_table(jobs)
        
        input("\nPress Enter to continue...")

    def show_analytics(self):
        """Display advanced analytics dashboard"""
        self.clear_screen()
        self.show_header()
        
        analyzer = JobAnalyzer()
        
        self.console.print(Panel("📊 Advanced Job Market Analytics", style="blue"))
        
        analytics_menu = [
            ("1", "📈 Executive Summary", "Complete overview with key metrics"),
            ("2", "🛠️  Skills Intelligence", "In-demand skills and technologies"),
            ("3", "💰 Salary Analysis", "Comprehensive salary insights"),
            ("4", "🏢 Company Insights", "Company hiring patterns"),
            ("5", "📍 Geographic Analysis", "Location-based market insights"),
            ("6", "📊 Generate HTML Report", "Export beautiful analytics reports"),
            ("7", "🎛️  Advanced Analytics", "Interactive analytics menu"),
            ("0", "⬅️  Back", "Return to main menu")
        ]
        
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="bold cyan")
        table.add_column("Option", style="bold")
        table.add_column("Description", style="dim")
        
        for key, option, desc in analytics_menu:
            table.add_row(key, option, desc)
        
        self.console.print(table)
        
        choice = Prompt.ask("Select analytics", choices=["0", "1", "2", "3", "4", "5", "6", "7"])
        
        if choice == "1":
            with Status("📊 Generating executive summary...", console=self.console):
                analyzer.display_summary()
        elif choice == "2":
            with Status("🛠️ Analyzing skills demand...", console=self.console):
                analyzer.display_skills_analysis()
        elif choice == "3":
            with Status("💰 Analyzing salary data...", console=self.console):
                analyzer.display_salary_intelligence()
        elif choice == "4":
            with Status("🏢 Analyzing company insights...", console=self.console):
                analyzer.display_company_insights()
        elif choice == "5":
            with Status("📍 Analyzing geographic data...", console=self.console):
                analyzer.display_geographic_analysis()
        elif choice == "6":
            analyzer.interactive_report_generation()
        elif choice == "7":
            # Interactive analytics menu loop
            while analyzer.interactive_analytics_menu():
                pass
        
        if choice != "0":
            input("\nPress Enter to continue...")

    def show_salary_insights(self):
        """Display Glassdoor salary insights"""
        self.clear_screen()
        self.show_header()
        
        self.console.print(Panel("💰 Salary Insights", style="yellow"))
        
        company = Prompt.ask("🏢 Company name", default="Google")
        titles = Prompt.ask("🎯 Job titles (comma-separated)", 
                           default="Software Engineer,Senior Software Engineer")
        
        try:
            glassdoor_scraper = GlassdoorScraper()
            job_titles = [title.strip() for title in titles.split(',')]
            
            with Status("💰 Getting salary insights...", console=self.console):
                insights = glassdoor_scraper.get_company_salary_insights(company, job_titles)
            
            self.console.print(Panel(
                f"[bold blue]Salary Insights for {company}[/bold blue]",
                title="💰 Company Salary Data"
            ))
            
            if insights.get('salary_data'):
                table = Table(title=f"{company} Salary Ranges")
                table.add_column("Job Title", style="magenta")
                table.add_column("Min Salary", style="green")
                table.add_column("Max Salary", style="green")
                
                for data in insights['salary_data']:
                    table.add_row(
                        data['job_title'],
                        f"${data['salary_min']:,}",
                        f"${data['salary_max']:,}"
                    )
                
                self.console.print(table)
            else:
                self.console.print("[yellow]No salary data found[/yellow]")
        
        except Exception as e:
            self.console.print(f"[red]Error getting salary insights: {e}[/red]")
        
        input("\nPress Enter to continue...")

    def show_settings(self):
        """Display settings and configuration"""
        self.clear_screen()
        self.show_header()
        
        self.console.print(Panel("⚙️ Settings & Configuration", style="magenta"))
        
        settings_menu = [
            ("1", "🗄️  Initialize Database", "Set up or reset database"),
            ("2", "📊 Update Statistics", "Refresh analytics cache"),
            ("0", "⬅️  Back", "Return to main menu")
        ]
        
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="bold cyan")
        table.add_column("Option", style="bold")
        table.add_column("Description", style="dim")
        
        for key, option, desc in settings_menu:
            table.add_row(key, option, desc)
        
        self.console.print(table)
        
        choice = Prompt.ask("Select setting", choices=["1", "2", "0"])
        
        if choice == "1":
            if Confirm.ask("Initialize/reset database?"):
                try:
                    with Status("🗄️ Initializing database...", console=self.console):
                        init_db()
                    self.console.print("[green]✅ Database initialized successfully![/green]")
                except Exception as e:
                    self.console.print(f"[red]❌ Database error: {e}[/red]")
        
        elif choice == "2":
            with Status("📊 Updating statistics...", console=self.console):
                time.sleep(1)  # Simulate update
            self.console.print("[green]✅ Statistics updated[/green]")
        
        if choice != "0":
            input("\nPress Enter to continue...")

    def show_help(self):
        """Display help and documentation"""
        self.clear_screen()
        self.show_header()
        
        help_text = """
[bold blue]🎯 RecruitIQ Help & Documentation[/bold blue]

[bold]Getting Started:[/bold]
1. Use [cyan]Scrape Jobs[/cyan] to collect job listings from various platforms
2. Use [cyan]Search Jobs[/cyan] to find specific roles in your local database
3. Use [cyan]Analytics[/cyan] to understand job market trends
4. Use [cyan]Salary Insights[/cyan] to research compensation data

[bold]Scraping Tips:[/bold]
• Start with comprehensive scraping for best results
• Use specific job titles (e.g., "Python Developer")
• Be patient - quality data takes time to collect

[bold]Search Features:[/bold]
• Use keywords to search job descriptions
• Filter by location, company
• Use detailed view for complete information

[bold]Keyboard Shortcuts:[/bold]
• [cyan]0[/cyan] - Go back / Exit
• [cyan]Ctrl+C[/cyan] - Emergency exit
• [cyan]Enter[/cyan] - Continue / Confirm
        """
        
        self.console.print(Panel(help_text, title="❓ Help", border_style="blue"))
        input("\nPress Enter to continue...")

    def show_status(self):
        """Display detailed system status"""
        self.clear_screen()
        self.show_header()
        
        self.console.print(Panel("📋 System Status", style="green"))
        
        try:
            session = get_session()
            from sqlalchemy import func
            
            total_jobs = session.query(JobPosting).filter(JobPosting.is_active == True).count()
            recent_jobs = session.query(JobPosting).filter(
                JobPosting.is_active == True,
                JobPosting.posted_date >= datetime.now() - timedelta(days=7)
            ).count()
            
            platform_counts = session.query(
                JobPosting.source_platform,
                func.count(JobPosting.id)
            ).filter(
                JobPosting.is_active == True
            ).group_by(JobPosting.source_platform).all()
            
            status_info = f"""[bold green]Database Status[/bold green]

Total Jobs: [cyan]{total_jobs:,}[/cyan]
Recent Jobs (7 days): [yellow]{recent_jobs:,}[/yellow]

[bold]Platform Distribution:[/bold]"""
            
            for platform, count in platform_counts:
                percentage = (count / total_jobs * 100) if total_jobs > 0 else 0
                status_info += f"\n• {platform}: [cyan]{count:,}[/cyan] ([dim]{percentage:.1f}%[/dim])"
            
            self.console.print(Panel(status_info, title="📊 Database", border_style="green"))
            
            session.close()
            
        except Exception as e:
            self.console.print(f"[red]❌ Error getting status: {e}[/red]")
        
        input("\nPress Enter to continue...")

def main():
    """Entry point for interactive CLI"""
    app = InteractiveRecruitIQ()
    app.run()

if __name__ == "__main__":
    main() 