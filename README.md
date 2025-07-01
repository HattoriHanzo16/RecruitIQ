# 🎯 RecruitIQ

**Interactive Job Market Intelligence CLI Tool**

A beautiful, powerful terminal interface for aggregating and analyzing job listings across multiple platforms. Transform your job search with real-time data, comprehensive analytics, and an intuitive interactive experience.

![RecruitIQ Banner](https://img.shields.io/badge/RecruitIQ-v2.0.0-blue?style=for-the-badge&logo=terminal)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

## ✨ Features

- 🖥️ **Beautiful Interactive Interface** - Modern terminal UI with intuitive navigation
- 🕷️ **Multi-Platform Scraping** - Indeed, LinkedIn, RemoteOK, Company Sites & more
- 📊 **Real-Time Analytics** - Job market trends, salary insights, and skills analysis
- 🔍 **Advanced Search** - Filter jobs by title, location, company, salary, and more
- 💰 **Salary Intelligence** - Glassdoor integration for compensation data
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

```bash
# Traditional CLI commands (bypass interactive interface)
recruitiq --no-interactive scrape all --query "python developer"
recruitiq --no-interactive search --title "senior engineer" --detailed
recruitiq --no-interactive analyze --skills
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