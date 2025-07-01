#!/usr/bin/env python3
"""
RecruitIQ Advanced Analytics Dashboards
Interactive dashboards with filtering and real-time insights
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
import re

from db.session import get_session
from db.models import JobPosting
from sqlalchemy import func, desc, and_, or_
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.columns import Columns

console = Console()

class AdvancedAnalyticsDashboard:
    """Advanced analytics dashboard with interactive filtering"""
    
    def __init__(self):
        self.session = get_session()
        self.filters = {}
        
    def interactive_filter_setup(self) -> Dict[str, Any]:
        """Interactive filter setup for analytics"""
        console.print(Panel("🔧 Analytics Filter Setup", style="blue"))
        
        filters = {}
        
        # Date range filter
        if Confirm.ask("📅 Filter by date range?", default=False):
            days = int(Prompt.ask("Number of days to analyze", default="30"))
            filters['date_range'] = days
        
        # Job title filter
        if Confirm.ask("🎯 Filter by job titles?", default=False):
            titles = Prompt.ask("Job titles (comma-separated)", default="software engineer,data scientist")
            filters['job_titles'] = [title.strip() for title in titles.split(',')]
        
        # Location filter
        if Confirm.ask("📍 Filter by locations?", default=False):
            locations = Prompt.ask("Locations (comma-separated)", default="New York,San Francisco")
            filters['locations'] = [loc.strip() for loc in locations.split(',')]
        
        # Company filter
        if Confirm.ask("🏢 Filter by companies?", default=False):
            companies = Prompt.ask("Companies (comma-separated)", default="Google,Microsoft")
            filters['companies'] = [comp.strip() for comp in companies.split(',')]
        
        # Salary range filter
        if Confirm.ask("💰 Filter by salary range?", default=False):
            min_salary = float(Prompt.ask("Minimum salary", default="0"))
            max_salary = float(Prompt.ask("Maximum salary", default="500000"))
            filters['salary_range'] = (min_salary, max_salary)
        
        # Platform filter
        if Confirm.ask("🌐 Filter by platforms?", default=False):
            platforms = Prompt.ask("Platforms (comma-separated)", default="Indeed,LinkedIn")
            filters['platforms'] = [plat.strip() for plat in platforms.split(',')]
        
        self.filters = filters
        return filters
    
    def comprehensive_market_analysis(self) -> Dict[str, Any]:
        """Comprehensive market analysis with current filters"""
        console.print(Panel("📊 Comprehensive Market Analysis", style="green"))
        
        # Build filtered query
        query = self._build_filtered_query()
        jobs = query.all()
        
        if not jobs:
            return {"error": "No jobs found with current filters"}
        
        analysis = {
            'total_jobs': len(jobs),
            'job_growth_analysis': self._analyze_job_growth(jobs),
            'salary_analysis': self._analyze_salaries(jobs),
            'skills_demand': self._analyze_skills_demand(jobs),
            'geographic_distribution': self._analyze_geographic_distribution(jobs),
            'company_insights': self._analyze_companies(jobs),
            'employment_trends': self._analyze_employment_trends(jobs),
            'platform_performance': self._analyze_platform_performance(jobs)
        }
        
        return analysis
    
    def display_comprehensive_dashboard(self):
        """Display comprehensive analytics dashboard"""
        analysis = self.comprehensive_market_analysis()
        
        if "error" in analysis:
            console.print(f"[red]{analysis['error']}[/red]")
            return
        
        # Summary metrics
        self._display_summary_metrics(analysis)
        
        # Job growth trends
        if analysis['job_growth_analysis']:
            self._display_job_growth_chart(analysis['job_growth_analysis'])
        
        # Salary insights
        if analysis['salary_analysis']:
            self._display_salary_insights(analysis['salary_analysis'])
        
        # Skills demand
        if analysis['skills_demand']:
            self._display_skills_demand_chart(analysis['skills_demand'])
        
        # Geographic distribution
        if analysis['geographic_distribution']:
            self._display_geographic_chart(analysis['geographic_distribution'])
        
        # Company insights
        if analysis['company_insights']:
            self._display_company_insights(analysis['company_insights'])
    
    def salary_benchmarking_dashboard(self, job_title: str = None):
        """Salary benchmarking dashboard"""
        console.print(Panel("💰 Salary Benchmarking Dashboard", style="yellow"))
        
        if not job_title:
            job_title = Prompt.ask("🎯 Job title to benchmark", default="software engineer")
        
        # Get salary data for the title
        query = self.session.query(JobPosting).filter(
            JobPosting.is_active == True,
            JobPosting.salary_min.isnot(None),
            JobPosting.title.ilike(f'%{job_title}%')
        )
        
        jobs = query.all()
        
        if not jobs:
            console.print(f"[red]No salary data found for '{job_title}'[/red]")
            return
        
        salary_data = self._comprehensive_salary_analysis(jobs, job_title)
        self._display_salary_benchmarking(salary_data)
    
    def skills_intelligence_dashboard(self):
        """Skills intelligence and demand forecasting dashboard"""
        console.print(Panel("🛠️ Skills Intelligence Dashboard", style="magenta"))
        
        # Get all job descriptions
        jobs = self.session.query(JobPosting).filter(
            JobPosting.is_active == True,
            JobPosting.job_description.isnot(None)
        ).all()
        
        if not jobs:
            console.print("[red]No job descriptions found for analysis[/red]")
            return
        
        skills_data = self._advanced_skills_analysis(jobs)
        self._display_skills_intelligence(skills_data)
    
    def company_intelligence_dashboard(self):
        """Company hiring intelligence dashboard"""
        console.print(Panel("🏢 Company Intelligence Dashboard", style="cyan"))
        
        # Get company hiring data
        company_data = self._analyze_company_hiring_patterns()
        self._display_company_intelligence(company_data)
    
    def market_trends_dashboard(self):
        """Market trends and forecasting dashboard"""
        console.print(Panel("📈 Market Trends Dashboard", style="red"))
        
        trends_data = self._analyze_market_trends()
        self._display_market_trends(trends_data)
    
    def _build_filtered_query(self):
        """Build SQLAlchemy query with current filters"""
        query = self.session.query(JobPosting).filter(JobPosting.is_active == True)
        
        # Date range filter
        if 'date_range' in self.filters:
            cutoff_date = datetime.now() - timedelta(days=self.filters['date_range'])
            query = query.filter(JobPosting.created_at >= cutoff_date)
        
        # Job titles filter
        if 'job_titles' in self.filters:
            title_filters = [JobPosting.title.ilike(f'%{title}%') for title in self.filters['job_titles']]
            query = query.filter(or_(*title_filters))
        
        # Locations filter
        if 'locations' in self.filters:
            location_filters = [JobPosting.location.ilike(f'%{loc}%') for loc in self.filters['locations']]
            query = query.filter(or_(*location_filters))
        
        # Companies filter
        if 'companies' in self.filters:
            company_filters = [JobPosting.company_name.ilike(f'%{comp}%') for comp in self.filters['companies']]
            query = query.filter(or_(*company_filters))
        
        # Salary range filter
        if 'salary_range' in self.filters:
            min_sal, max_sal = self.filters['salary_range']
            query = query.filter(
                and_(
                    JobPosting.salary_min >= min_sal,
                    JobPosting.salary_min <= max_sal
                )
            )
        
        # Platforms filter
        if 'platforms' in self.filters:
            platform_filters = [JobPosting.source_platform.ilike(f'%{plat}%') for plat in self.filters['platforms']]
            query = query.filter(or_(*platform_filters))
        
        return query
    
    def _analyze_job_growth(self, jobs: List[JobPosting]) -> Dict[str, Any]:
        """Analyze job growth trends"""
        if not jobs:
            return {}
        
        # Group jobs by date
        date_counts = {}
        for job in jobs:
            if job.created_at:
                date_key = job.created_at.strftime('%Y-%m-%d')
                date_counts[date_key] = date_counts.get(date_key, 0) + 1
        
        # Calculate growth rate
        sorted_dates = sorted(date_counts.keys())
        if len(sorted_dates) >= 2:
            recent_period = sorted_dates[-7:]  # Last 7 days
            earlier_period = sorted_dates[-14:-7]  # 7 days before that
            
            recent_avg = sum(date_counts.get(date, 0) for date in recent_period) / len(recent_period)
            earlier_avg = sum(date_counts.get(date, 0) for date in earlier_period) / len(earlier_period)
            
            growth_rate = ((recent_avg - earlier_avg) / max(earlier_avg, 1)) * 100
        else:
            growth_rate = 0
        
        return {
            'daily_counts': date_counts,
            'growth_rate': growth_rate,
            'total_jobs': len(jobs),
            'avg_daily_postings': sum(date_counts.values()) / len(date_counts) if date_counts else 0
        }
    
    def _analyze_salaries(self, jobs: List[JobPosting]) -> Dict[str, Any]:
        """Analyze salary trends and distributions"""
        salary_jobs = [job for job in jobs if job.salary_min]
        
        if not salary_jobs:
            return {}
        
        salaries = [job.salary_min for job in salary_jobs]
        
        # Salary by location
        location_salaries = {}
        for job in salary_jobs:
            if job.location:
                location = job.location.split(',')[0].strip()
                if location not in location_salaries:
                    location_salaries[location] = []
                location_salaries[location].append(job.salary_min)
        
        # Calculate location averages
        location_avg_salaries = {
            loc: {
                'average': sum(sals) / len(sals),
                'count': len(sals),
                'min': min(sals),
                'max': max(sals)
            }
            for loc, sals in location_salaries.items() if len(sals) >= 3
        }
        
        return {
            'total_with_salary': len(salary_jobs),
            'average_salary': sum(salaries) / len(salaries),
            'median_salary': sorted(salaries)[len(salaries) // 2],
            'min_salary': min(salaries),
            'max_salary': max(salaries),
            'salary_distribution': self._create_salary_buckets(salaries),
            'location_salaries': location_avg_salaries
        }
    
    def _create_salary_buckets(self, salaries: List[float]) -> Dict[str, int]:
        """Create salary distribution buckets"""
        buckets = {
            '<50k': 0,
            '50k-75k': 0,
            '75k-100k': 0,
            '100k-150k': 0,
            '150k-200k': 0,
            '200k+': 0
        }
        
        for salary in salaries:
            if salary < 50000:
                buckets['<50k'] += 1
            elif salary < 75000:
                buckets['50k-75k'] += 1
            elif salary < 100000:
                buckets['75k-100k'] += 1
            elif salary < 150000:
                buckets['100k-150k'] += 1
            elif salary < 200000:
                buckets['150k-200k'] += 1
            else:
                buckets['200k+'] += 1
        
        return buckets
    
    def _analyze_skills_demand(self, jobs: List[JobPosting]) -> Dict[str, Any]:
        """Analyze skills demand from job descriptions"""
        # Enhanced skills database
        skills_db = {
            'Programming Languages': {
                'python': ['python'],
                'javascript': ['javascript', 'js'],
                'java': ['java'],
                'typescript': ['typescript', 'ts'],
                'go': ['golang', 'go'],
                'rust': ['rust'],
                'c++': ['c++', 'cpp'],
                'c#': ['c#', 'csharp'],
                'ruby': ['ruby'],
                'php': ['php'],
                'swift': ['swift'],
                'kotlin': ['kotlin'],
                'scala': ['scala'],
                'r': [' r '],
                'sql': ['sql']
            },
            'Web Frameworks': {
                'react': ['react', 'reactjs'],
                'angular': ['angular'],
                'vue': ['vue.js', 'vuejs'],
                'django': ['django'],
                'flask': ['flask'],
                'spring': ['spring'],
                'express': ['express.js', 'expressjs'],
                'fastapi': ['fastapi'],
                'laravel': ['laravel'],
                'rails': ['rails', 'ruby on rails']
            },
            'Databases': {
                'postgresql': ['postgresql', 'postgres'],
                'mysql': ['mysql'],
                'mongodb': ['mongodb', 'mongo'],
                'redis': ['redis'],
                'elasticsearch': ['elasticsearch'],
                'cassandra': ['cassandra'],
                'dynamodb': ['dynamodb']
            },
            'Cloud & DevOps': {
                'aws': ['aws', 'amazon web services'],
                'azure': ['azure', 'microsoft azure'],
                'gcp': ['gcp', 'google cloud'],
                'docker': ['docker'],
                'kubernetes': ['kubernetes', 'k8s'],
                'terraform': ['terraform'],
                'jenkins': ['jenkins'],
                'git': ['git'],
                'ci/cd': ['ci/cd', 'continuous integration']
            }
        }
        
        skill_counts = {}
        total_descriptions = 0
        
        for job in jobs:
            if job.job_description:
                description = job.job_description.lower()
                total_descriptions += 1
                
                for category, skills in skills_db.items():
                    if category not in skill_counts:
                        skill_counts[category] = {}
                    
                    for skill_name, keywords in skills.items():
                        for keyword in keywords:
                            if keyword in description:
                                skill_counts[category][skill_name] = skill_counts[category].get(skill_name, 0) + 1
                                break  # Count each skill only once per job
        
        # Calculate percentages and trends
        for category in skill_counts:
            for skill in skill_counts[category]:
                count = skill_counts[category][skill]
                skill_counts[category][skill] = {
                    'count': count,
                    'percentage': (count / total_descriptions) * 100 if total_descriptions > 0 else 0
                }
        
        return {
            'skill_counts': skill_counts,
            'total_descriptions': total_descriptions,
            'top_skills': self._get_top_skills_from_analysis(skill_counts)
        }
    
    def _get_top_skills_from_analysis(self, skill_counts: Dict) -> List[Dict]:
        """Get top skills across all categories"""
        all_skills = []
        for category, skills in skill_counts.items():
            for skill, data in skills.items():
                all_skills.append({
                    'skill': skill,
                    'category': category,
                    'count': data['count'],
                    'percentage': data['percentage']
                })
        
        return sorted(all_skills, key=lambda x: x['count'], reverse=True)[:20]
    
    def _display_summary_metrics(self, analysis: Dict[str, Any]):
        """Display summary metrics in a beautiful panel"""
        metrics = []
        
        metrics.append(Panel(
            f"[bold green]{analysis['total_jobs']:,}[/bold green]\nTotal Jobs",
            title="📊 Jobs Analyzed",
            width=20
        ))
        
        if analysis['job_growth_analysis']:
            growth = analysis['job_growth_analysis']['growth_rate']
            color = "green" if growth >= 0 else "red"
            symbol = "📈" if growth >= 0 else "📉"
            metrics.append(Panel(
                f"[bold {color}]{growth:+.1f}%[/bold {color}]\nGrowth Rate",
                title=f"{symbol} Weekly Growth",
                width=20
            ))
        
        if analysis['salary_analysis']:
            avg_salary = analysis['salary_analysis']['average_salary']
            metrics.append(Panel(
                f"[bold cyan]${avg_salary:,.0f}[/bold cyan]\nAverage",
                title="💰 Salary",
                width=20
            ))
        
        console.print(Columns(metrics, expand=False))
        console.print()
    
    def _display_job_growth_chart(self, growth_data: Dict[str, Any]):
        """Display job growth visualization"""
        console.print(Panel("📈 Job Growth Trends", style="blue"))
        
        if growth_data['daily_counts']:
            # Create a simple text-based chart for terminal
            dates = sorted(growth_data['daily_counts'].keys())[-14:]  # Last 14 days
            counts = [growth_data['daily_counts'].get(date, 0) for date in dates]
            
            # Simple bar chart in terminal
            max_count = max(counts) if counts else 1
            
            table = Table(title="Daily Job Postings (Last 14 Days)")
            table.add_column("Date", style="cyan")
            table.add_column("Jobs", style="green")
            table.add_column("Chart", style="blue")
            
            for date, count in zip(dates, counts):
                bar_length = int((count / max_count) * 20) if max_count > 0 else 0
                bar = "█" * bar_length
                table.add_row(date, str(count), bar)
            
            console.print(table)
        
        console.print(f"Growth Rate: [{'green' if growth_data['growth_rate'] >= 0 else 'red'}]{growth_data['growth_rate']:+.1f}%[/]")
        console.print()
    
    def _display_salary_insights(self, salary_data: Dict[str, Any]):
        """Display salary insights"""
        console.print(Panel("💰 Salary Analysis", style="yellow"))
        
        # Salary statistics
        stats_table = Table(title="Salary Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Average", f"${salary_data['average_salary']:,.0f}")
        stats_table.add_row("Median", f"${salary_data['median_salary']:,.0f}")
        stats_table.add_row("Range", f"${salary_data['min_salary']:,.0f} - ${salary_data['max_salary']:,.0f}")
        stats_table.add_row("Jobs with Salary", str(salary_data['total_with_salary']))
        
        console.print(stats_table)
        
        # Salary distribution
        if salary_data['salary_distribution']:
            console.print("\n💰 Salary Distribution:")
            for bucket, count in salary_data['salary_distribution'].items():
                if count > 0:
                    percentage = (count / salary_data['total_with_salary']) * 100
                    console.print(f"  {bucket}: {count} jobs ({percentage:.1f}%)")
        
        console.print()
    
    def _display_skills_demand_chart(self, skills_data: Dict[str, Any]):
        """Display skills demand visualization"""
        console.print(Panel("🛠️ Skills Demand Analysis", style="magenta"))
        
        if skills_data['top_skills']:
            table = Table(title="Top 15 Most Demanded Skills")
            table.add_column("Rank", style="cyan", width=6)
            table.add_column("Skill", style="magenta", width=15)
            table.add_column("Category", style="blue", width=18)
            table.add_column("Jobs", style="green", width=8)
            table.add_column("% of Jobs", style="yellow", width=10)
            
            for i, skill in enumerate(skills_data['top_skills'][:15], 1):
                table.add_row(
                    str(i),
                    skill['skill'],
                    skill['category'],
                    str(skill['count']),
                    f"{skill['percentage']:.1f}%"
                )
            
            console.print(table)
        
        console.print()
    
    def _comprehensive_salary_analysis(self, jobs: List[JobPosting], job_title: str) -> Dict[str, Any]:
        """Comprehensive salary analysis for benchmarking"""
        salaries = [job.salary_min for job in jobs if job.salary_min]
        
        if not salaries:
            return {}
        
        # Percentile analysis
        sorted_salaries = sorted(salaries)
        n = len(sorted_salaries)
        
        percentiles = {
            'p10': sorted_salaries[int(n * 0.1)],
            'p25': sorted_salaries[int(n * 0.25)],
            'p50': sorted_salaries[int(n * 0.5)],
            'p75': sorted_salaries[int(n * 0.75)],
            'p90': sorted_salaries[int(n * 0.9)]
        }
        
        # Company salary comparison
        company_salaries = {}
        for job in jobs:
            if job.salary_min and job.company_name:
                if job.company_name not in company_salaries:
                    company_salaries[job.company_name] = []
                company_salaries[job.company_name].append(job.salary_min)
        
        company_avg = {
            company: sum(sals) / len(sals)
            for company, sals in company_salaries.items()
            if len(sals) >= 2
        }
        
        return {
            'job_title': job_title,
            'total_samples': len(salaries),
            'percentiles': percentiles,
            'average': sum(salaries) / len(salaries),
            'company_averages': dict(sorted(company_avg.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    
    def _display_salary_benchmarking(self, salary_data: Dict[str, Any]):
        """Display salary benchmarking results"""
        if not salary_data:
            return
        
        console.print(Panel(f"💰 Salary Benchmarking: {salary_data['job_title']}", style="yellow"))
        
        # Percentile table
        percentile_table = Table(title="Salary Percentiles")
        percentile_table.add_column("Percentile", style="cyan")
        percentile_table.add_column("Salary", style="green")
        
        for p, salary in salary_data['percentiles'].items():
            percentile_table.add_row(p.upper(), f"${salary:,.0f}")
        
        console.print(percentile_table)
        
        # Company comparison
        if salary_data['company_averages']:
            console.print("\n🏢 Top Paying Companies:")
            company_table = Table()
            company_table.add_column("Company", style="magenta")
            company_table.add_column("Average Salary", style="green")
            
            for company, avg_salary in list(salary_data['company_averages'].items())[:8]:
                company_table.add_row(company, f"${avg_salary:,.0f}")
            
            console.print(company_table)
        
        console.print(f"\nSample Size: {salary_data['total_samples']} jobs")
        console.print()
    
    def __del__(self):
        """Cleanup database session"""
        if hasattr(self, 'session') and self.session:
            self.session.close()

# Convenience functions for CLI integration
def launch_interactive_dashboard():
    """Launch interactive analytics dashboard"""
    dashboard = AdvancedAnalyticsDashboard()
    
    console.print(Panel("🚀 Advanced Analytics Dashboard", style="blue"))
    
    # Setup filters
    if Confirm.ask("Set up filters for analysis?", default=True):
        dashboard.interactive_filter_setup()
    
    # Display dashboard
    dashboard.display_comprehensive_dashboard()

def launch_salary_benchmarking():
    """Launch salary benchmarking dashboard"""
    dashboard = AdvancedAnalyticsDashboard()
    dashboard.salary_benchmarking_dashboard()

def launch_skills_intelligence():
    """Launch skills intelligence dashboard"""
    dashboard = AdvancedAnalyticsDashboard()
    dashboard.skills_intelligence_dashboard()

def launch_company_intelligence():
    """Launch company intelligence dashboard"""
    dashboard = AdvancedAnalyticsDashboard()
    dashboard.company_intelligence_dashboard() 