#!/usr/bin/env python3
"""
RecruitIQ Advanced Reporting System
Generate beautiful HTML reports with interactive visualizations
"""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from jinja2 import Template
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from db.session import get_session
from db.models import JobPosting
from sqlalchemy import func, desc
from rich.console import Console

console = Console()

class RecruitIQReporter:
    """Advanced HTML report generator for job market analytics"""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.session = get_session()
        
    def generate_executive_summary(self, days: int = 30) -> str:
        """Generate executive summary report"""
        data = self._collect_summary_data(days)
        charts = self._create_summary_charts(data)
        
        template = self._get_executive_template()
        
        html_content = template.render(
            title="RecruitIQ Executive Summary",
            generated_date=datetime.now().strftime("%B %d, %Y at %H:%M"),
            period_days=days,
            data=data,
            charts=charts,
            css=self._get_base_css()
        )
        
        filename = f"executive_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def generate_market_intelligence_report(self, focus_role: str = None) -> str:
        """Generate comprehensive market intelligence report"""
        data = self._collect_market_data(focus_role)
        charts = self._create_market_charts(data)
        
        template = self._get_market_template()
        
        html_content = template.render(
            title=f"Market Intelligence Report" + (f" - {focus_role}" if focus_role else ""),
            generated_date=datetime.now().strftime("%B %d, %Y at %H:%M"),
            focus_role=focus_role,
            data=data,
            charts=charts,
            css=self._get_market_css()
        )
        
        filename = f"market_intelligence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def generate_salary_analysis_report(self, job_titles: List[str] = None) -> str:
        """Generate detailed salary analysis report"""
        data = self._collect_salary_data(job_titles)
        charts = self._create_salary_charts(data)
        
        template = self._get_salary_template()
        
        html_content = template.render(
            title="Salary Analysis Report",
            generated_date=datetime.now().strftime("%B %d, %Y at %H:%M"),
            job_titles=job_titles,
            data=data,
            charts=charts,
            css=self._get_salary_css()
        )
        
        filename = f"salary_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def generate_skills_demand_report(self) -> str:
        """Generate skills demand and technology trends report"""
        data = self._collect_skills_data()
        charts = self._create_skills_charts(data)
        
        template = self._get_skills_template()
        
        html_content = template.render(
            title="Skills Demand & Technology Trends",
            generated_date=datetime.now().strftime("%B %d, %Y at %H:%M"),
            data=data,
            charts=charts,
            css=self._get_skills_css()
        )
        
        filename = f"skills_demand_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def generate_company_insights_report(self, companies: List[str] = None) -> str:
        """Generate company hiring insights report"""
        data = self._collect_company_data(companies)
        charts = self._create_company_charts(data)
        
        template = self._get_company_template()
        
        html_content = template.render(
            title="Company Hiring Insights",
            generated_date=datetime.now().strftime("%B %d, %Y at %H:%M"),
            companies=companies,
            data=data,
            charts=charts,
            css=self._get_company_css()
        )
        
        filename = f"company_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def _collect_summary_data(self, days: int) -> Dict[str, Any]:
        """Collect data for executive summary"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        total_jobs = self.session.query(JobPosting).filter(JobPosting.is_active == True).count()
        recent_jobs = self.session.query(JobPosting).filter(
            JobPosting.is_active == True,
            JobPosting.created_at >= cutoff_date
        ).count()
        
        platform_data = self.session.query(
            JobPosting.source_platform,
            func.count(JobPosting.id).label('count')
        ).filter(
            JobPosting.is_active == True
        ).group_by(JobPosting.source_platform).all()
        
        return {
            'total_jobs': total_jobs,
            'recent_jobs': recent_jobs,
            'platform_data': platform_data,
            'growth_rate': (recent_jobs / max(total_jobs - recent_jobs, 1)) * 100 if total_jobs > recent_jobs else 0
        }
    
    def _collect_market_data(self, focus_role: str = None) -> Dict[str, Any]:
        """Collect comprehensive market data"""
        query = self.session.query(JobPosting).filter(JobPosting.is_active == True)
        
        if focus_role:
            query = query.filter(JobPosting.title.ilike(f'%{focus_role}%'))
        
        jobs = query.all()
        
        if not jobs:
            return {'error': 'No jobs found for analysis'}
        
        # Location analysis
        location_data = {}
        for job in jobs:
            if job.location:
                location = job.location.split(',')[0].strip()  # Get city
                location_data[location] = location_data.get(location, 0) + 1
        
        # Time series data
        time_data = {}
        for job in jobs:
            if job.created_at:
                date_key = job.created_at.strftime('%Y-%m-%d')
                time_data[date_key] = time_data.get(date_key, 0) + 1
        
        # Employment type analysis
        employment_data = {}
        for job in jobs:
            emp_type = job.employment_type or 'Unknown'
            employment_data[emp_type] = employment_data.get(emp_type, 0) + 1
        
        return {
            'total_jobs': len(jobs),
            'location_data': dict(sorted(location_data.items(), key=lambda x: x[1], reverse=True)[:15]),
            'time_data': time_data,
            'employment_data': employment_data,
            'focus_role': focus_role
        }
    
    def _collect_salary_data(self, job_titles: List[str] = None) -> Dict[str, Any]:
        """Collect salary analysis data"""
        query = self.session.query(JobPosting).filter(
            JobPosting.is_active == True,
            JobPosting.salary_min.isnot(None)
        )
        
        if job_titles:
            title_filters = [JobPosting.title.ilike(f'%{title}%') for title in job_titles]
            query = query.filter(func.or_(*title_filters))
        
        jobs = query.all()
        
        if not jobs:
            return {'error': 'No salary data found'}
        
        # Salary by title analysis
        title_salaries = {}
        for job in jobs:
            title = job.title
            if title not in title_salaries:
                title_salaries[title] = []
            title_salaries[title].append(job.salary_min)
        
        # Salary by company analysis
        company_salaries = {}
        for job in jobs:
            company = job.company_name
            if company not in company_salaries:
                company_salaries[company] = []
            company_salaries[company].append(job.salary_min)
        
        # Salary by location analysis
        location_salaries = {}
        for job in jobs:
            if job.location:
                location = job.location.split(',')[0].strip()
                if location not in location_salaries:
                    location_salaries[location] = []
                location_salaries[location].append(job.salary_min)
        
        return {
            'total_jobs_with_salary': len(jobs),
            'title_salaries': {k: {
                'average': sum(v) / len(v),
                'min': min(v),
                'max': max(v),
                'count': len(v)
            } for k, v in title_salaries.items() if len(v) >= 3},
            'company_salaries': {k: {
                'average': sum(v) / len(v),
                'min': min(v),
                'max': max(v),
                'count': len(v)
            } for k, v in company_salaries.items() if len(v) >= 3},
            'location_salaries': {k: {
                'average': sum(v) / len(v),
                'min': min(v),
                'max': max(v),
                'count': len(v)
            } for k, v in location_salaries.items() if len(v) >= 3}
        }
    
    def _collect_skills_data(self) -> Dict[str, Any]:
        """Collect skills and technology demand data"""
        jobs = self.session.query(JobPosting.job_description).filter(
            JobPosting.is_active == True,
            JobPosting.job_description.isnot(None)
        ).all()
        
        if not jobs:
            return {'error': 'No job descriptions found'}
        
        # Technology skills to track
        tech_skills = {
            'Languages': ['python', 'javascript', 'java', 'typescript', 'go', 'rust', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin'],
            'Frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'fastapi', 'laravel', 'rails'],
            'Databases': ['postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'dynamodb'],
            'Cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins'],
            'Data': ['pandas', 'numpy', 'tensorflow', 'pytorch', 'spark', 'hadoop', 'tableau', 'power bi'],
            'Tools': ['git', 'jira', 'slack', 'figma', 'sketch', 'postman', 'webpack', 'babel']
        }
        
        skill_counts = {category: {} for category in tech_skills.keys()}
        total_descriptions = len(jobs)
        
        for job in jobs:
            description = job.job_description.lower()
            for category, skills in tech_skills.items():
                for skill in skills:
                    if skill.lower() in description:
                        skill_counts[category][skill] = skill_counts[category].get(skill, 0) + 1
        
        # Calculate percentages and sort
        for category in skill_counts:
            skill_counts[category] = {
                skill: {
                    'count': count,
                    'percentage': (count / total_descriptions) * 100
                }
                for skill, count in sorted(skill_counts[category].items(), key=lambda x: x[1], reverse=True)
            }
        
        return {
            'total_descriptions_analyzed': total_descriptions,
            'skill_counts': skill_counts,
            'top_skills_overall': self._get_top_skills_overall(skill_counts)
        }
    
    def _get_top_skills_overall(self, skill_counts: Dict) -> List[Dict]:
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
    
    def _collect_company_data(self, companies: List[str] = None) -> Dict[str, Any]:
        """Collect company hiring insights data"""
        query = self.session.query(JobPosting).filter(JobPosting.is_active == True)
        
        if companies:
            company_filters = [JobPosting.company_name.ilike(f'%{company}%') for company in companies]
            query = query.filter(func.or_(*company_filters))
        
        jobs = query.all()
        
        if not jobs:
            return {'error': 'No company data found'}
        
        # Company hiring activity
        company_activity = {}
        for job in jobs:
            company = job.company_name
            if company not in company_activity:
                company_activity[company] = {
                    'total_jobs': 0,
                    'avg_salary': 0,
                    'salary_count': 0,
                    'locations': set(),
                    'platforms': set()
                }
            
            company_activity[company]['total_jobs'] += 1
            company_activity[company]['platforms'].add(job.source_platform)
            
            if job.location:
                company_activity[company]['locations'].add(job.location)
            
            if job.salary_min:
                company_activity[company]['avg_salary'] += job.salary_min
                company_activity[company]['salary_count'] += 1
        
        # Calculate averages
        for company, data in company_activity.items():
            if data['salary_count'] > 0:
                data['avg_salary'] = data['avg_salary'] / data['salary_count']
            else:
                data['avg_salary'] = None
            data['locations'] = list(data['locations'])
            data['platforms'] = list(data['platforms'])
        
        return {
            'total_companies': len(company_activity),
            'company_activity': dict(sorted(company_activity.items(), key=lambda x: x[1]['total_jobs'], reverse=True)),
            'companies_analyzed': companies
        }
    
    def _create_summary_charts(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Create charts for executive summary"""
        charts = {}
        
        if data['platform_data']:
            platforms = [item[0] for item in data['platform_data']]
            counts = [item[1] for item in data['platform_data']]
            
            fig = go.Figure(data=[go.Pie(
                labels=platforms,
                values=counts,
                hole=0.3,
                textinfo='label+percent'
            )])
            
            fig.update_layout(
                title="Job Distribution by Platform",
                height=400
            )
            
            charts['platform_distribution'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        return charts
    
    def _create_market_charts(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Create charts for market intelligence report"""
        charts = {}
        
        # Location distribution
        if data['location_data']:
            locations = list(data['location_data'].keys())
            counts = list(data['location_data'].values())
            
            fig = go.Figure(data=[go.Bar(
                x=locations,
                y=counts,
                marker_color='lightcoral'
            )])
            
            fig.update_layout(
                title="Job Distribution by Location",
                xaxis_title="Location",
                yaxis_title="Number of Jobs",
                height=400,
                xaxis_tickangle=-45
            )
            
            charts['location_distribution'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        # Time series chart
        if data['time_data']:
            dates = sorted(data['time_data'].keys())
            counts = [data['time_data'][date] for date in dates]
            
            fig = go.Figure(data=[go.Scatter(
                x=dates,
                y=counts,
                mode='lines+markers',
                line=dict(color='blue', width=2),
                marker=dict(size=6)
            )])
            
            fig.update_layout(
                title="Job Posting Trends Over Time",
                xaxis_title="Date",
                yaxis_title="Number of Jobs",
                height=400
            )
            
            charts['time_series'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        return charts
    
    def _create_salary_charts(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Create charts for salary analysis report"""
        charts = {}
        
        # Salary by title
        if data['title_salaries']:
            titles = list(data['title_salaries'].keys())[:10]  # Top 10
            averages = [data['title_salaries'][title]['average'] for title in titles]
            
            fig = go.Figure(data=[go.Bar(
                x=[title[:30] + '...' if len(title) > 30 else title for title in titles],
                y=averages,
                marker_color='green'
            )])
            
            fig.update_layout(
                title="Average Salary by Job Title",
                xaxis_title="Job Title",
                yaxis_title="Average Salary ($)",
                height=400,
                xaxis_tickangle=-45
            )
            
            charts['salary_by_title'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        return charts
    
    def _create_skills_charts(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Create charts for skills demand report"""
        charts = {}
        
        # Top skills overall
        if data['top_skills_overall']:
            top_skills = data['top_skills_overall'][:15]
            skills = [skill['skill'] for skill in top_skills]
            percentages = [skill['percentage'] for skill in top_skills]
            
            fig = go.Figure(data=[go.Bar(
                x=percentages,
                y=skills,
                orientation='h',
                marker_color='purple'
            )])
            
            fig.update_layout(
                title="Most In-Demand Skills",
                xaxis_title="Percentage of Job Postings (%)",
                yaxis_title="Skill",
                height=500,
                margin=dict(l=100)
            )
            
            charts['top_skills'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        return charts
    
    def _create_company_charts(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Create charts for company insights report"""
        charts = {}
        
        # Company hiring activity
        if data['company_activity']:
            companies = list(data['company_activity'].keys())[:15]
            job_counts = [data['company_activity'][company]['total_jobs'] for company in companies]
            
            fig = go.Figure(data=[go.Bar(
                x=[company[:20] + '...' if len(company) > 20 else company for company in companies],
                y=job_counts,
                marker_color='orange'
            )])
            
            fig.update_layout(
                title="Company Hiring Activity",
                xaxis_title="Company",
                yaxis_title="Total Job Postings",
                height=400,
                xaxis_tickangle=-45
            )
            
            charts['company_activity'] = fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        return charts
    
    def _get_executive_template(self) -> Template:
        """Get executive summary HTML template"""
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>{{ css }}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{{ title }}</h1>
            <p class="subtitle">Generated on {{ generated_date }}</p>
        </header>
        
        <section class="summary-cards">
            <div class="card">
                <h3>Total Jobs</h3>
                <div class="metric">{{ "{:,}".format(data.total_jobs) }}</div>
            </div>
            <div class="card">
                <h3>Recent Jobs ({{ period_days }} days)</h3>
                <div class="metric">{{ "{:,}".format(data.recent_jobs) }}</div>
            </div>
            <div class="card">
                <h3>Growth Rate</h3>
                <div class="metric">{{ "%.1f%%"|format(data.growth_rate) }}</div>
            </div>
        </section>
        
        <section class="charts">
            {% if charts.platform_distribution %}
            <div class="chart-container">
                {{ charts.platform_distribution|safe }}
            </div>
            {% endif %}
        </section>
        
        <footer>
            <p>Generated by RecruitIQ - Job Market Intelligence Platform</p>
        </footer>
    </div>
</body>
</html>
        """
        return Template(template_str)
    
    def _get_market_template(self) -> Template:
        """Get market intelligence HTML template"""
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>{{ css }}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{{ title }}</h1>
            <p class="subtitle">Generated on {{ generated_date }}</p>
            {% if focus_role %}
            <p class="focus">Focus Role: {{ focus_role }}</p>
            {% endif %}
        </header>
        
        <section class="summary-cards">
            <div class="card">
                <h3>Total Jobs Analyzed</h3>
                <div class="metric">{{ "{:,}".format(data.total_jobs) }}</div>
            </div>
            <div class="card">
                <h3>Unique Locations</h3>
                <div class="metric">{{ data.location_data|length }}</div>
            </div>
            <div class="card">
                <h3>Employment Types</h3>
                <div class="metric">{{ data.employment_data|length }}</div>
            </div>
        </section>
        
        <section class="charts">
            {% if charts.location_distribution %}
            <div class="chart-container">
                {{ charts.location_distribution|safe }}
            </div>
            {% endif %}
            
            {% if charts.time_series %}
            <div class="chart-container">
                {{ charts.time_series|safe }}
            </div>
            {% endif %}
        </section>
        
        <footer>
            <p>Generated by RecruitIQ - Job Market Intelligence Platform</p>
        </footer>
    </div>
</body>
</html>
        """
        return Template(template_str)
    
    def _get_salary_template(self) -> Template:
        """Get salary analysis HTML template"""
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>{{ css }}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{{ title }}</h1>
            <p class="subtitle">Generated on {{ generated_date }}</p>
        </header>
        
        <section class="summary-cards">
            <div class="card">
                <h3>Jobs with Salary Data</h3>
                <div class="metric">{{ "{:,}".format(data.total_jobs_with_salary) }}</div>
            </div>
            <div class="card">
                <h3>Job Titles Analyzed</h3>
                <div class="metric">{{ data.title_salaries|length }}</div>
            </div>
            <div class="card">
                <h3>Companies Analyzed</h3>
                <div class="metric">{{ data.company_salaries|length }}</div>
            </div>
        </section>
        
        <section class="charts">
            {% if charts.salary_by_title %}
            <div class="chart-container">
                {{ charts.salary_by_title|safe }}
            </div>
            {% endif %}
        </section>
        
        <footer>
            <p>Generated by RecruitIQ - Job Market Intelligence Platform</p>
        </footer>
    </div>
</body>
</html>
        """
        return Template(template_str)
    
    def _get_skills_template(self) -> Template:
        """Get skills demand HTML template"""
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>{{ css }}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{{ title }}</h1>
            <p class="subtitle">Generated on {{ generated_date }}</p>
        </header>
        
        <section class="summary-cards">
            <div class="card">
                <h3>Job Descriptions Analyzed</h3>
                <div class="metric">{{ "{:,}".format(data.total_descriptions_analyzed) }}</div>
            </div>
            <div class="card">
                <h3>Skills Categories</h3>
                <div class="metric">{{ data.skill_counts|length }}</div>
            </div>
            <div class="card">
                <h3>Top Skill</h3>
                <div class="metric">{{ data.top_skills_overall[0].skill if data.top_skills_overall else "N/A" }}</div>
            </div>
        </section>
        
        <section class="charts">
            {% if charts.top_skills %}
            <div class="chart-container">
                {{ charts.top_skills|safe }}
            </div>
            {% endif %}
        </section>
        
        <footer>
            <p>Generated by RecruitIQ - Job Market Intelligence Platform</p>
        </footer>
    </div>
</body>
</html>
        """
        return Template(template_str)
    
    def _get_company_template(self) -> Template:
        """Get company insights HTML template"""
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>{{ css }}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{{ title }}</h1>
            <p class="subtitle">Generated on {{ generated_date }}</p>
        </header>
        
        <section class="summary-cards">
            <div class="card">
                <h3>Total Companies</h3>
                <div class="metric">{{ "{:,}".format(data.total_companies) }}</div>
            </div>
        </section>
        
        <section class="charts">
            {% if charts.company_activity %}
            <div class="chart-container">
                {{ charts.company_activity|safe }}
            </div>
            {% endif %}
        </section>
        
        <footer>
            <p>Generated by RecruitIQ - Job Market Intelligence Platform</p>
        </footer>
    </div>
</body>
</html>
        """
        return Template(template_str)
    
    def _get_market_css(self) -> str:
        """Get CSS for market intelligence"""
        return self._get_base_css()
    
    def _get_salary_css(self) -> str:
        """Get CSS for salary analysis"""
        return self._get_base_css()
    
    def _get_skills_css(self) -> str:
        """Get CSS for skills demand"""
        return self._get_base_css()
    
    def _get_company_css(self) -> str:
        """Get CSS for company insights"""
        return self._get_base_css()
    
    def _get_base_css(self) -> str:
        """Get base CSS styles for all reports"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        header h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .subtitle {
            color: #7f8c8d;
            font-size: 1.1em;
        }
        
        .focus {
            color: #3498db;
            font-weight: 600;
            margin-top: 10px;
        }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h3 {
            color: #2c3e50;
            font-size: 1.1em;
            margin-bottom: 15px;
            font-weight: 600;
        }
        
        .metric {
            font-size: 2.5em;
            font-weight: 700;
            color: #3498db;
        }
        
        .charts {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        footer {
            text-align: center;
            background: rgba(255,255,255,0.9);
            padding: 20px;
            border-radius: 15px;
            color: #7f8c8d;
        }
        
        @media (max-width: 768px) {
            .charts {
                grid-template-columns: 1fr;
            }
            
            .chart-container {
                min-width: 0;
            }
            
            header h1 {
                font-size: 2em;
            }
            
            .metric {
                font-size: 2em;
            }
        }
        """
    
    def __del__(self):
        """Cleanup database session"""
        if hasattr(self, 'session') and self.session:
            self.session.close()

# Convenience functions
def generate_executive_report(days: int = 30, output_dir: str = "reports") -> str:
    """Generate executive summary report"""
    reporter = RecruitIQReporter(output_dir)
    return reporter.generate_executive_summary(days)

def generate_market_report(focus_role: str = None, output_dir: str = "reports") -> str:
    """Generate market intelligence report"""
    reporter = RecruitIQReporter(output_dir)
    return reporter.generate_market_intelligence_report(focus_role)

def generate_salary_report(job_titles: List[str] = None, output_dir: str = "reports") -> str:
    """Generate salary analysis report"""
    reporter = RecruitIQReporter(output_dir)
    return reporter.generate_salary_analysis_report(job_titles)

def generate_skills_report(output_dir: str = "reports") -> str:
    """Generate skills demand report"""
    reporter = RecruitIQReporter(output_dir)
    return reporter.generate_skills_demand_report()

def generate_company_report(companies: List[str] = None, output_dir: str = "reports") -> str:
    """Generate company insights report"""
    reporter = RecruitIQReporter(output_dir)
    return reporter.generate_company_insights_report(companies) 