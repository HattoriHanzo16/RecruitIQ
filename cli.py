#!/usr/bin/env python3
"""
RecruitIQ - Job Market Intelligence CLI Tool

A powerful CLI tool for aggregating and analyzing job listings across multiple platforms.
"""

import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import time
import os

# Import RecruitIQ modules
from scrapers import IndeedScraper, CompanyScraper, RemoteOKScraper
from analyze import JobAnalyzer
from search import JobSearcher
from db.session import init_db, get_session, update_or_create_job_posting
from utils import validate_job_data

# Initialize Typer app and Rich console
app = typer.Typer(
    name="recruitiq",
    help="🎯 RecruitIQ - Job Market Intelligence CLI Tool",
    rich_markup_mode="rich"
)
console = Console()

# Sub-applications for better organization
scrape_app = typer.Typer(name="scrape", help="🕷️ Scrape job listings from various platforms")
app.add_typer(scrape_app, name="scrape")

@app.callback()
def main():
    """
    🎯 RecruitIQ - Job Market Intelligence CLI Tool
    
    Aggregate and analyze job listings across different job platforms.
    """
    pass

@app.command()
def init():
    """🚀 Initialize the database and create tables"""
    try:
        console.print("[yellow]Initializing RecruitIQ database...[/yellow]")
        init_db()
        console.print("[green]✅ Database initialized successfully![/green]")
    except Exception as e:
        console.print(f"[red]❌ Error initializing database: {e}[/red]")
        raise typer.Exit(1)

@scrape_app.command("all")
def scrape_all(
    query: str = typer.Option("software engineer", "--query", "-q", help="Job search query"),
    location: str = typer.Option("New York, NY", "--location", "-l", help="Location for Indeed search"),
    limit_per_platform: int = typer.Option(25, "--limit", help="Jobs to scrape per platform")
):
    """🌐 Scrape jobs from all supported platforms"""
    
    console.print(Panel.fit(
        f"[bold blue]Starting comprehensive job scraping[/bold blue]\n"
        f"Query: [yellow]{query}[/yellow]\n"
        f"Location (Indeed): [green]{location}[/green]\n"
        f"Limit per platform: [cyan]{limit_per_platform}[/cyan]",
        title="🕷️ RecruitIQ Scraper"
    ))
    
    total_jobs_saved = 0
    
    # Initialize database
    try:
        init_db()
    except Exception as e:
        console.print(f"[red]Error initializing database: {e}[/red]")
        raise typer.Exit(1)
    
    # Scrape Indeed
    console.print("\n[bold blue]🔍 Scraping Indeed...[/bold blue]")
    try:
        indeed_scraper = IndeedScraper()
        indeed_jobs = indeed_scraper.search_jobs(query, location, limit_per_platform)
        saved_count = _save_jobs_to_db(indeed_jobs, "Indeed")
        total_jobs_saved += saved_count
        console.print(f"[green]✅ Indeed: {saved_count} jobs saved[/green]")
    except Exception as e:
        console.print(f"[red]❌ Indeed scraping failed: {e}[/red]")
    
    # Scrape company sites
    console.print("\n[bold blue]🏢 Scraping company career pages...[/bold blue]")
    try:
        company_scraper = CompanyScraper()
        company_jobs = company_scraper.scrape_all_companies(query, limit_per_platform)
        saved_count = _save_jobs_to_db(company_jobs, "Company Sites")
        total_jobs_saved += saved_count
        console.print(f"[green]✅ Company Sites: {saved_count} jobs saved[/green]")
    except Exception as e:
        console.print(f"[red]❌ Company sites scraping failed: {e}[/red]")
    
    # Scrape RemoteOK
    console.print("\n[bold blue]🌍 Scraping RemoteOK...[/bold blue]")
    try:
        remote_scraper = RemoteOKScraper()
        remote_jobs = remote_scraper.search_jobs(query, limit_per_platform)
        saved_count = _save_jobs_to_db(remote_jobs, "RemoteOK")
        total_jobs_saved += saved_count
        console.print(f"[green]✅ RemoteOK: {saved_count} jobs saved[/green]")
    except Exception as e:
        console.print(f"[red]❌ RemoteOK scraping failed: {e}[/red]")
    
    # Summary
    console.print(Panel.fit(
        f"[bold green]Scraping completed![/bold green]\n"
        f"Total jobs saved: [yellow]{total_jobs_saved}[/yellow]\n"
        f"Run [cyan]recruitiq analyze[/cyan] to see insights!",
        title="📊 Summary"
    ))

@scrape_app.command("indeed")
def scrape_indeed(
    query: str = typer.Option("software engineer", "--query", "-q", help="Job search query"),
    location: str = typer.Option("New York, NY", "--location", "-l", help="Location to search"),
    limit: int = typer.Option(50, "--limit", help="Maximum jobs to scrape")
):
    """🔍 Scrape jobs from Indeed"""
    
    console.print(f"[blue]Scraping Indeed for '{query}' in '{location}'...[/blue]")
    
    try:
        init_db()
        scraper = IndeedScraper()
        jobs = scraper.search_jobs(query, location, limit)
        saved_count = _save_jobs_to_db(jobs, "Indeed")
        console.print(f"[green]✅ Successfully scraped and saved {saved_count} Indeed jobs![/green]")
    except Exception as e:
        console.print(f"[red]❌ Error scraping Indeed: {e}[/red]")
        raise typer.Exit(1)

@scrape_app.command("companies")
def scrape_companies(
    company: str = typer.Option("google", "--company", "-c", help="Company to scrape (google, microsoft)"),
    query: str = typer.Option("software engineer", "--query", "-q", help="Job search query"),
    limit: int = typer.Option(50, "--limit", help="Maximum jobs to scrape")
):
    """🏢 Scrape jobs from company career pages"""
    
    console.print(f"[blue]Scraping {company} careers for '{query}'...[/blue]")
    
    try:
        init_db()
        scraper = CompanyScraper()
        jobs = scraper.scrape_jobs(company, query, limit)
        saved_count = _save_jobs_to_db(jobs, f"{company.title()} Careers")
        console.print(f"[green]✅ Successfully scraped and saved {saved_count} {company} jobs![/green]")
    except Exception as e:
        console.print(f"[red]❌ Error scraping {company}: {e}[/red]")
        raise typer.Exit(1)

@scrape_app.command("remoteok")
def scrape_remoteok(
    query: str = typer.Option("software", "--query", "-q", help="Job search query"),
    limit: int = typer.Option(50, "--limit", help="Maximum jobs to scrape")
):
    """🌍 Scrape jobs from RemoteOK"""
    
    console.print(f"[blue]Scraping RemoteOK for '{query}'...[/blue]")
    
    try:
        init_db()
        scraper = RemoteOKScraper()
        jobs = scraper.search_jobs(query, limit)
        saved_count = _save_jobs_to_db(jobs, "RemoteOK")
        console.print(f"[green]✅ Successfully scraped and saved {saved_count} RemoteOK jobs![/green]")
    except Exception as e:
        console.print(f"[red]❌ Error scraping RemoteOK: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def analyze(
    skills: bool = typer.Option(False, "--skills", help="Show skills analysis"),
    trends: bool = typer.Option(False, "--trends", help="Show job posting trends")
):
    """📊 Generate and display job market analysis"""
    
    analyzer = JobAnalyzer()
    
    if skills:
        console.print("\n")
        analyzer.display_skills_analysis()
    elif trends:
        console.print("\n[bold blue]📈 Job Market Trends (30 days)[/bold blue]")
        trends_data = analyzer.analyze_job_trends(30)
        if "error" not in trends_data:
            console.print(f"Total jobs in period: [green]{trends_data['total_jobs_period']}[/green]")
            # Add more trend visualization here
        else:
            console.print(f"[red]Error: {trends_data['error']}[/red]")
    else:
        analyzer.display_summary()

@app.command()
def search(
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Job title keywords"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Location filter"),
    company: Optional[str] = typer.Option(None, "--company", "-c", help="Company name filter"),
    platform: Optional[str] = typer.Option(None, "--platform", "-p", help="Platform filter"),
    employment_type: Optional[str] = typer.Option(None, "--employment-type", "-e", help="Employment type filter"),
    min_salary: Optional[float] = typer.Option(None, "--min-salary", help="Minimum salary filter"),
    max_salary: Optional[float] = typer.Option(None, "--max-salary", help="Maximum salary filter"),
    keywords: Optional[str] = typer.Option(None, "--keywords", "-k", help="Keywords in description"),
    days_ago: Optional[int] = typer.Option(None, "--days-ago", "-d", help="Jobs posted within N days"),
    limit: int = typer.Option(50, "--limit", help="Maximum results"),
    detailed: bool = typer.Option(False, "--detailed", help="Show detailed job information"),
    help_flag: bool = typer.Option(False, "--help-search", help="Show search help and examples")
):
    """🔍 Search through local job database"""
    
    if help_flag:
        searcher = JobSearcher()
        searcher.display_search_help()
        return
    
    searcher = JobSearcher()
    searcher.search_and_display(
        title=title,
        location=location,
        company=company,
        platform=platform,
        employment_type=employment_type,
        min_salary=min_salary,
        max_salary=max_salary,
        keywords=keywords,
        days_ago=days_ago,
        limit=limit,
        detailed=detailed
    )

@app.command()
def status():
    """📋 Show RecruitIQ database status and statistics"""
    
    try:
        session = get_session()
        from db.models import JobPosting
        from sqlalchemy import func
        
        total_jobs = session.query(JobPosting).filter(JobPosting.is_active == True).count()
        
        if total_jobs == 0:
            console.print("[yellow]No jobs in database. Run 'recruitiq scrape all' to get started![/yellow]")
            return
        
        # Platform counts
        platform_counts = session.query(
            JobPosting.source_platform,
            func.count(JobPosting.id)
        ).filter(
            JobPosting.is_active == True
        ).group_by(JobPosting.source_platform).all()
        
        # Recent jobs
        from datetime import datetime, timedelta
        recent_jobs = session.query(JobPosting).filter(
            JobPosting.is_active == True,
            JobPosting.posted_date >= datetime.now() - timedelta(days=7)
        ).count()
        
        console.print(Panel.fit(
            f"[bold blue]RecruitIQ Database Status[/bold blue]\n\n"
            f"Total Jobs: [green]{total_jobs:,}[/green]\n"
            f"Recent Jobs (7 days): [yellow]{recent_jobs:,}[/yellow]\n\n"
            f"[bold]Jobs by Platform:[/bold]\n" +
            "\n".join([f"• {platform}: [cyan]{count}[/cyan]" for platform, count in platform_counts]),
            title="📊 Status"
        ))
        
        session.close()
        
    except Exception as e:
        console.print(f"[red]❌ Error getting status: {e}[/red]")
        console.print("[yellow]💡 Try running 'recruitiq init' to initialize the database[/yellow]")

@app.command()
def version():
    """🏷️ Show RecruitIQ version information"""
    console.print(Panel.fit(
        "[bold blue]RecruitIQ v1.0.0[/bold blue]\n"
        "Job Market Intelligence CLI Tool\n\n"
        "[dim]Built with Python, SQLAlchemy, Typer, and Rich[/dim]",
        title="🎯 RecruitIQ"
    ))

def _save_jobs_to_db(jobs: list, source_name: str) -> int:
    """Save jobs to database and return count of saved jobs"""
    if not jobs:
        return 0
    
    session = get_session()
    saved_count = 0
    
    try:
        for job_data in jobs:
            if validate_job_data(job_data):
                try:
                    update_or_create_job_posting(session, job_data)
                    saved_count += 1
                except Exception as e:
                    console.print(f"[dim red]Warning: Failed to save job: {e}[/dim red]")
                    continue
        
        return saved_count
        
    except Exception as e:
        console.print(f"[red]Error saving jobs from {source_name}: {e}[/red]")
        return saved_count
    finally:
        session.close()

if __name__ == "__main__":
    app() 