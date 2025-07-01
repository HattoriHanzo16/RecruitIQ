# 🎯 RecruitIQ

**Interactive Job Market Intelligence CLI Tool**

A beautiful, powerful terminal interface for aggregating and analyzing job listings across multiple platforms. Transform your job search with real-time data, comprehensive analytics, and an intuitive interactive experience.

![RecruitIQ Banner](https://img.shields.io/badge/RecruitIQ-v2.0.0-blue?style=for-the-badge&logo=terminal)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

## ✨ Features

- 🖥️ **Beautiful Interactive Interface** - Modern terminal UI with intuitive navigation
- 🕷️ **Multi-Platform Scraping** - Indeed, LinkedIn, RemoteOK, Company Sites & more
- 📊 **Advanced Analytics Suite** - Executive dashboards, salary intelligence, skills analysis
- 📈 **Interactive HTML Reports** - Beautiful, exportable reports with charts and insights
- 🔍 **Advanced Search & Filtering** - Multiple criteria with real-time results
- 💰 **Comprehensive Salary Intelligence** - Location-based, company-specific compensation data
- 🏢 **Company Intelligence** - Hiring patterns, activity trends, and competitive analysis
- 📍 **Geographic Market Analysis** - Location-based insights and remote work trends
- 🛠️ **Skills Demand Forecasting** - Technology trends and in-demand skills tracking
- 🗄️ **Local Database** - Fast searches and offline analysis
- ⚡ **Progress Tracking** - Real-time feedback during scraping operations
- 🎨 **Rich Terminal UI** - Beautiful colors, panels, tables, and progress bars

## 🚀 Quick Start

### One-Line Installation

```bash
# Download and run the installer
python3 -c "$(curl -fsSL https://raw.githubusercontent.com/yourusername/recruitiq/main/install.py)"
```

### Manual Installation

```bash
git clone https://github.com/yourusername/recruitiq.git
cd recruitiq
python3 install.py
```

### Launch RecruitIQ

```bash
recruitiq
```

That's it! The beautiful interactive interface will guide you through everything.

## 🎨 Interactive Interface

```
╭─────────────────────────────────────────────────────────────╮
│                🎯 RecruitIQ - Job Market Intelligence        │
╰─────────────────────────────────────────────────────────────╯

┌─ 🎯 Main Menu ─────────────────────────────────────────────┐
│ 1   🕷️  Scrape Jobs        Scrape jobs from all platforms  │
│ 2   🔍 Search Jobs        Search and filter local database │
│ 3   📊 Analytics          View job market analysis         │
│ 4   💰 Salary Insights    Glassdoor salary data           │
│ 5   ⚙️  Settings          Configure preferences            │
│ 6   📋 Status             View system statistics           │
│ 7   ❓ Help               Get help and documentation       │
│ 0   🚪 Exit               Exit RecruitIQ                   │
└────────────────────────────────────────────────────────────┘

💾 Jobs: 1,247 | 🕒 14:32:15 | 📊 Ready
```

### Key Features of the Interactive Interface

- **🎯 Menu-Driven Navigation** - Simple number-based menu system
- **⚡ Real-Time Progress** - Watch scraping progress with beautiful progress bars
- **📊 Live Statistics** - See job counts and status updates in real-time
- **🎨 Rich Formatting** - Color-coded output, tables, and panels
- **🔄 Interactive Prompts** - Smart defaults and validation for all inputs
- **💫 Smooth Workflows** - Guided processes from scraping to analysis

## 🕷️ Scraping Capabilities

### Supported Platforms

| Platform | Description | Data Quality |
|----------|-------------|--------------|
| **Indeed** | Global job search engine | ⭐⭐⭐⭐⭐ |
| **LinkedIn** | Professional network jobs | ⭐⭐⭐⭐ |
| **RemoteOK** | Remote work opportunities | ⭐⭐⭐⭐⭐ |
| **Company Sites** | Direct company careers | ⭐⭐⭐⭐ |
| **Glassdoor** | Salary data enrichment | ⭐⭐⭐⭐ |

### Interactive Scraping Process

1. **Choose Platform** - Select from all platforms or individual sources
2. **Set Parameters** - Job query, location, and limits with smart defaults
3. **Watch Progress** - Real-time progress bars and status updates
4. **Review Results** - Summary statistics and save confirmation
5. **Optional Enrichment** - Add salary data from Glassdoor

## 📊 Analytics Dashboard

The interactive analytics provide instant insights:

- **📈 Summary Dashboard** - Total jobs, recent activity, top platforms
- **🛠️ Skills Analysis** - Most in-demand technologies and frameworks
- **💰 Salary Statistics** - Average, median, and range analysis
- **🏢 Company Insights** - Top hiring companies and their activity
- **📍 Location Trends** - Geographic distribution of opportunities

## 🔍 Advanced Search Interface

Interactive search with:

- **🎯 Smart Filters** - Title, company, location, salary range
- **💡 Auto-Suggestions** - Based on your existing job database
- **📋 Result Modes** - Summary tables or detailed job descriptions
- **⚡ Real-Time Search** - Instant results as you type criteria

## 📊 Advanced Analytics Suite

### Executive Dashboard
- **📈 Market Overview** - Total jobs, growth rates, platform distribution
- **💰 Salary Statistics** - Average, median, range analysis across all data
- **🏆 Top Performers** - Leading companies, locations, and hiring trends
- **📅 Time Series Analysis** - Job posting trends and growth patterns

### Salary Intelligence
- **🌍 Geographic Analysis** - Location-based salary comparisons
- **🏢 Company Benchmarking** - Compensation by organization
- **📊 Salary Distribution** - Percentile analysis and market positioning
- **💼 Role-Specific Insights** - Job title compensation breakdowns

### Skills Demand Analysis
- **🛠️ Technology Trends** - Most in-demand programming languages and frameworks
- **📈 Skill Growth** - Emerging technologies and declining skills
- **🎯 Market Gaps** - Underserved skills and opportunities
- **🔗 Skill Correlation** - Related technologies and skill combinations

### Company Intelligence
- **📊 Hiring Activity** - Company recruitment patterns and volumes
- **💰 Compensation Benchmarks** - Company-specific salary data
- **📍 Geographic Presence** - Where companies are hiring
- **📈 Growth Trends** - Expanding vs. contracting organizations

### Geographic Market Analysis
- **🗺️ Market Distribution** - Job concentration by location
- **💰 Cost of Living Adjusted Salaries** - Location-based compensation analysis
- **🌐 Remote Work Trends** - Remote vs. on-site opportunities
- **🏙️ Emerging Markets** - Growing job markets and opportunities

## 📈 Interactive HTML Reports

Generate beautiful, shareable reports with:

### Executive Summary Report
```bash
recruitiq report --type executive --days 30
```
- **📊 Key Metrics Dashboard** - Total jobs, growth rates, platform breakdown
- **📈 Interactive Charts** - Platform distribution, top companies
- **💰 Salary Overview** - Market compensation summary
- **📱 Mobile-Responsive** - Beautiful design that works anywhere

### Market Intelligence Report
```bash
recruitiq report --type market --role "data scientist"
```
- **🎯 Role-Specific Analysis** - Focus on particular job types
- **📍 Geographic Distribution** - Location-based market insights
- **📊 Time Series Charts** - Posting trends and patterns
- **🏢 Company Activity** - Who's hiring and where

### Salary Analysis Report
```bash
recruitiq report --type salary --titles "software engineer,senior engineer"
```
- **💰 Comprehensive Salary Data** - Multiple role comparisons
- **📊 Percentile Analysis** - Market positioning insights
- **🏢 Company Benchmarks** - Organization-specific compensation
- **📈 Interactive Visualizations** - Sortable, filterable charts

### Skills Demand Report
```bash
recruitiq report --type skills
```
- **🛠️ Technology Landscape** - Programming languages, frameworks, tools
- **📈 Demand Trends** - Growing and declining technologies
- **🎯 Market Opportunities** - Underserved skills and niches
- **📊 Category Breakdown** - Languages, frameworks, databases, cloud

### Company Insights Report
```bash
recruitiq report --type company --companies "Google,Microsoft,Apple"
```
- **🏢 Hiring Patterns** - Company recruitment strategies
- **💰 Compensation Analysis** - Organization salary benchmarks
- **📍 Geographic Presence** - Where companies are expanding
- **📊 Competitive Analysis** - Side-by-side company comparisons

## 💰 Salary Intelligence

Glassdoor-powered salary insights:

- **🏢 Company Analysis** - Salary ranges by company and role
- **📊 Market Intelligence** - Industry benchmarks and trends
- **🎯 Role-Specific Data** - Detailed breakdowns by job title
- **📈 Interactive Reports** - Beautiful terminal-based salary reports

## ⚙️ Settings & Configuration

Easy configuration through the interactive interface:

- **🗄️ Database Management** - Initialize, backup, and maintain your job database
- **🔧 Scraper Settings** - Configure scraping preferences and limits
- **📊 Cache Management** - Clear analytics cache and update statistics
- **🛠️ System Diagnostics** - Test scraper functionality and connectivity

## 🎯 Getting Started Guide

### 1. Install RecruitIQ
```bash
python3 -c "$(curl -fsSL https://raw.githubusercontent.com/yourusername/recruitiq/main/install.py)"
```

### 2. Launch the Interactive Interface
```bash
recruitiq
```

### 3. Initialize Your Database
- Choose option `5` (Settings)
- Select `Initialize Database`
- Confirm the setup

### 4. Start Scraping Jobs
- Choose option `1` (Scrape Jobs)
- Enter your preferred job query (e.g., "software engineer")
- Set your location and limits
- Watch the magic happen!

### 5. Analyze the Market
- Choose option `3` (Analytics)
- Explore the summary dashboard
- Check skills analysis for trending technologies

### 6. Search Your Data
- Choose option `2` (Search Jobs)
- Filter by your criteria
- View detailed results

## 🛠️ Command Line Usage (Advanced)

For power users, all functionality is available via command line:

### Analytics Commands
```bash
# Interactive analytics menu
recruitiq analyze --interactive

# Executive summary
recruitiq analyze

# Skills analysis
recruitiq analyze --skills

# Salary intelligence
recruitiq analyze --salary

# Company insights
recruitiq analyze --company

# Geographic analysis
recruitiq analyze --geographic
```

### HTML Report Generation
```bash
# Executive summary report
recruitiq report --type executive --days 30

# Market intelligence for specific role
recruitiq report --type market --role "data scientist"

# Salary analysis for multiple titles
recruitiq report --type salary --titles "software engineer,senior engineer,staff engineer"

# Skills demand report
recruitiq report --type skills

# Company insights report
recruitiq report --type company --companies "Google,Microsoft,Apple"

# Custom output directory
recruitiq report --type executive --output custom_reports
```

### Advanced Scraping
```bash
# Comprehensive scraping with all options
recruitiq --no-interactive scrape all --query "python developer" --linkedin --enrich-salaries

# Platform-specific scraping
recruitiq scrape linkedin --query "machine learning engineer" --location "San Francisco"
recruitiq scrape indeed --query "data scientist" --location "New York"

# Company-specific scraping
recruitiq scrape companies --company google --query "software engineer"
```

### Advanced Search
```bash
# Multi-criteria search
recruitiq search --title "senior engineer" --location "remote" --min-salary 120000 --detailed

# Company and platform filtering
recruitiq search --company "google" --platform "linkedin" --employment-type "full-time"

# Keyword-based search
recruitiq search --keywords "kubernetes docker" --platform "remoteok" --days-ago 7
```

## 🏗️ Architecture

RecruitIQ 2.0 features a modern, modular architecture:

```
recruitiq/
├── interactive_cli.py    # 🎨 Beautiful interactive interface
├── cli.py               # 📱 Traditional CLI commands
├── install.py           # 🚀 One-click installer
├── scrapers/            # 🕷️ Platform-specific scrapers
├── db/                  # 🗄️ Database models and management
├── analyze.py           # 📊 Analytics and insights
├── search.py            # 🔍 Advanced search functionality
└── utils.py             # 🛠️ Shared utilities
```

## 💻 System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Chrome Browser**: For web scraping (auto-installed)
- **Terminal**: Modern terminal with color support
- **Memory**: 512MB+ RAM for database operations

## 🚨 Best Practices

- **⏱️ Rate Limiting** - Built-in delays respect website policies
- **🔄 Error Handling** - Graceful failures with helpful error messages
- **💾 Data Quality** - Automatic validation and deduplication
- **🎯 Focused Scraping** - Use specific queries for better results
- **📊 Regular Analysis** - Check market trends weekly

## 🎯 Use Cases

### For Job Seekers
- **Market Research** - Understand salary ranges and in-demand skills
- **Company Analysis** - Research potential employers and their hiring patterns
- **Skill Gap Analysis** - Identify technologies to learn for career growth
- **Location Insights** - Find the best cities for your profession

### For Recruiters
- **Market Intelligence** - Understand compensation trends and competition
- **Sourcing Strategy** - Identify where top talent is being hired
- **Competitive Analysis** - Monitor competitor hiring activities
- **Skills Mapping** - Track technology adoption in the industry

### For Researchers
- **Labor Market Analysis** - Study employment trends and patterns
- **Economic Research** - Analyze job market health and growth
- **Technology Trends** - Track adoption of new frameworks and tools
- **Geographic Studies** - Research regional employment patterns

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create** a feature branch
4. **Make** your changes
5. **Test** thoroughly
6. **Submit** a pull request

### Development Setup
```bash
git clone https://github.com/yourusername/recruitiq.git
cd recruitiq
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- 📚 **Documentation**: [GitHub Wiki](https://github.com/yourusername/recruitiq/wiki)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/recruitiq/issues)
- 💬 **Community**: [Discussions](https://github.com/yourusername/recruitiq/discussions)
- 📧 **Contact**: contact@recruitiq.dev

## 🎯 Roadmap

### v2.1 (Coming Soon)
- [ ] **Export Functionality** - CSV, Excel, and PDF reports
- [ ] **Job Alerts** - Email notifications for new matching jobs
- [ ] **Application Tracking** - Track your job applications
- [ ] **Resume Analysis** - Match your skills to job requirements

### v3.0 (Future)
- [ ] **Web Dashboard** - Browser-based interface
- [ ] **Mobile App** - iOS and Android applications
- [ ] **AI Recommendations** - Machine learning job matching
- [ ] **Team Collaboration** - Share insights with your team

---

**Made with ❤️ for job seekers, recruiters, and market researchers**

*Transform your job search today with RecruitIQ's beautiful interactive interface!* 