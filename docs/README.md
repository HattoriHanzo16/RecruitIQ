<div align="center">

<img src="images/logo.png" alt="RecruitIQ Logo" width="300" />

# 🎯 RecruitIQ - Job Market Intelligence Platform

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey)](https://github.com/HattoriHanzo16/RecruitIQ)

**The most advanced job market intelligence platform with beautiful CLI interfaces, comprehensive analytics, and professional reporting.**

[✨ Features](#features) • [🚀 Quick Start](#quick-start) • [📊 Analytics](#analytics) • [🛠️ Development](#development)

</div>

## 🌟 Overview

RecruitIQ transforms job market research from tedious manual work into intelligent, automated insights. Built for developers, recruiters, and job seekers who need deep market understanding.

### ✨ What Makes RecruitIQ Special

- **🎨 Beautiful Interactive Interface**: Rich terminal UI with real-time progress and intuitive navigation
- **🕷️ Multi-Platform Scraping**: Indeed, LinkedIn, RemoteOK, Company Career Pages, and Glassdoor integration
- **📊 Advanced Analytics**: Executive dashboards, salary intelligence, skills demand analysis
- **📱 Professional Reporting**: Export beautiful HTML reports with interactive charts
- **🧠 Market Intelligence**: Geographic analysis, company insights, trend forecasting
- **⚡ High Performance**: Efficient scraping with smart rate limiting and error recovery

## 🚀 Quick Start

### One-Line Installation

```bash
git clone https://github.com/HattoriHanzo16/RecruitIQ.git
cd recruitiq
python scripts/install.py
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/HattoriHanzo16/RecruitIQ.git
cd recruitiq

# Install dependencies
pip install -r requirements.txt

# Initialize database
python main.py init

# Launch interactive interface
recruitiq
```

## 📋 Features

### 🕷️ Intelligent Job Scraping

- **Multi-Platform Support**: Indeed, LinkedIn, RemoteOK, Company Sites, Glassdoor
- **Smart Deduplication**: Advanced algorithms prevent duplicate job listings
- **Rate Limiting**: Respectful scraping that won't get blocked
- **Error Recovery**: Robust handling of network issues and site changes

### 🎨 Beautiful CLI Interfaces

#### Interactive Main Interface
```bash
recruitiq  # Launch full interactive experience
```

#### Command Line Interface
```bash
# Scrape jobs from all platforms
recruitiq scrape all --query "python developer" --location "San Francisco"

# Search local database
recruitiq search --title "data scientist" --min-salary 100000 --detailed

# Generate analytics
recruitiq analyze --interactive

# Export HTML reports
recruitiq report --type executive --days 30
```

### 📊 Advanced Analytics

#### Executive Dashboard
- Market overview with key metrics
- Job growth trends and forecasting
- Platform performance analysis
- Geographic distribution insights

#### Salary Intelligence
- Comprehensive salary analysis by location, company, and role
- Market benchmarking for specific positions
- Compensation trend tracking
- Salary range distributions

#### Skills Demand Analysis
- Technology trend identification
- In-demand skills tracking
- Programming language popularity
- Framework and tool insights

#### Company Intelligence
- Hiring pattern analysis
- Company-specific salary insights
- Recruitment activity tracking
- Competitive analysis

### 📱 Professional HTML Reporting

Generate beautiful, interactive reports:

```bash
# Executive summary report
recruitiq report --type executive --days 30

# Salary analysis for specific roles  
recruitiq report --type salary --titles "software engineer,data scientist"

# Skills demand report
recruitiq report --type skills

# Company insights report
recruitiq report --type company --companies "Google,Microsoft,Amazon"

# Market intelligence report
recruitiq report --type market --role "python developer"
```

Reports include:
- Interactive Plotly charts
- Professional CSS styling
- Mobile-responsive design
- Export capabilities
- Comprehensive data tables

## 🏗️ Project Structure

```
recruitiq/
├── recruitiq/                 # Main package
│   ├── core/                 # Business logic
│   │   ├── analyzer.py       # Job market analysis
│   │   ├── searcher.py       # Database search
│   │   ├── reporter.py       # HTML report generation
│   │   └── dashboard.py      # Interactive dashboards
│   ├── cli/                  # Command line interfaces
│   │   ├── main.py          # Main CLI application
│   │   └── interactive.py    # Interactive terminal UI
│   ├── scrapers/            # Web scraping modules
│   │   ├── indeed.py        # Indeed scraper
│   │   ├── linkedin.py      # LinkedIn scraper
│   │   ├── remoteok.py      # RemoteOK scraper
│   │   ├── company_sites.py # Company career pages
│   │   └── glassdoor.py     # Glassdoor salary data
│   ├── db/                  # Database layer
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── session.py       # Database session management
│   │   └── base.py          # Database configuration
│   └── utils/               # Utility functions
│       ├── helpers.py       # General utilities
│       └── validators.py    # Data validation
├── scripts/                 # Installation and setup
│   ├── install.py          # One-click installer
│   └── setup.py            # Package setup
├── tests/                   # Unit tests
├── docs/                    # Documentation
├── alembic/                 # Database migrations
└── main.py                  # Application entry point
```

## 🔧 Configuration

### Database Setup

RecruitIQ uses PostgreSQL by default. Configure your database:

```bash
# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/recruitiq"

# Or use SQLite for development
export DATABASE_URL="sqlite:///recruitiq.db"

# Initialize database
recruitiq init
```

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/recruitiq

# Web Scraping
SCRAPING_DELAY=1  # Delay between requests (seconds)
USER_AGENT="RecruitIQ Bot 1.0"

# Reporting
REPORTS_DIR=./reports
```

## 📊 Analytics Deep Dive

### Executive Summary
Get a comprehensive overview of the job market:
- Total jobs tracked across all platforms
- Weekly growth rates and trends
- Platform performance comparison
- Geographic distribution analysis

### Salary Intelligence
Advanced compensation analysis:
- Location-based salary variations
- Company-specific compensation data
- Role progression salary mapping
- Market benchmarking tools

### Skills Demand Forecasting
Understand technology trends:
- Programming language popularity
- Framework adoption rates
- Emerging technology tracking
- Skills gap analysis

### Market Trends
Predictive market insights:
- Hiring velocity by company size
- Remote work adoption rates
- Industry-specific trends
- Seasonal hiring patterns

## 🛠️ Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/HattoriHanzo16/RecruitIQ.git
cd recruitiq

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
python -m pytest tests/

# Run interactive interface
python main.py
```

### Project Architecture

RecruitIQ follows a modular architecture:

1. **CLI Layer** (`recruitiq/cli/`): User interfaces and command handling
2. **Core Layer** (`recruitiq/core/`): Business logic and analytics
3. **Data Layer** (`recruitiq/db/`): Database models and session management
4. **Scraping Layer** (`recruitiq/scrapers/`): Web scraping implementations
5. **Utils Layer** (`recruitiq/utils/`): Shared utilities and helpers

### Adding New Scrapers

```python
# Create new scraper in recruitiq/scrapers/
from .base import BaseScraper

class NewSiteScraper(BaseScraper):
    def search_jobs(self, query, location, limit):
        # Implement scraping logic
        return jobs_list
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 🔒 Legal & Ethics

RecruitIQ follows ethical scraping practices:
- Respects robots.txt files
- Implements rate limiting
- Uses appropriate delays between requests
- Doesn't overload target servers
- Complies with terms of service

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Documentation**: [GitHub Wiki](https://github.com/HattoriHanzo16/RecruitIQ/wiki)
- **Issues**: [GitHub Issues](https://github.com/HattoriHanzo16/RecruitIQ/issues)
- **Discussions**: [GitHub Discussions](https://github.com/HattoriHanzo16/RecruitIQ/discussions)

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for beautiful CLIs
- Styled with [Rich](https://rich.readthedocs.io/) for terminal interfaces
- Powered by [SQLAlchemy](https://www.sqlalchemy.org/) for database operations
- Charts by [Plotly](https://plotly.com/python/) for interactive visualizations

---

<div align="center">

**⭐ Star this repo if RecruitIQ helps you land your dream job! ⭐**

[🏠 Home](https://github.com/HattoriHanzo16/RecruitIQ) • [📚 Docs](https://github.com/HattoriHanzo16/RecruitIQ/wiki) • [🐛 Issues](https://github.com/HattoriHanzo16/RecruitIQ/issues) • [💬 Discussions](https://github.com/HattoriHanzo16/RecruitIQ/discussions)

</div> 