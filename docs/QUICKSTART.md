# 🚀 RecruitIQ Quick Start Guide

Get up and running with RecruitIQ in under 5 minutes!

## 📋 Prerequisites

- Python 3.8 or higher
- Chrome browser (for web scraping)
- Terminal with color support

## ⚡ 1-Minute Installation

### Option 1: One-Line Installer (Recommended)

```bash
git clone https://github.com/HattoriHanzo16/RecruitIQ.git
cd recruitiq
python scripts/install.py
```

### Option 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/HattoriHanzo16/RecruitIQ.git
cd recruitiq

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .

# Initialize database
python main.py init
```

## 🎯 Quick Start Commands

### Launch Interactive Interface
```bash
recruitiq
```
This opens the beautiful terminal interface where you can navigate with simple number choices.

### Command Line Usage
```bash
# Scrape jobs from all platforms
recruitiq scrape all --query "python developer" --location "San Francisco"

# Search your local database
recruitiq search --title "data scientist" --min-salary 100000

# Generate analytics
recruitiq analyze

# Create HTML reports
recruitiq report --type executive
```

## 🎮 5-Minute Tutorial

### Step 1: Launch RecruitIQ
```bash
recruitiq
```

### Step 2: Scrape Your First Jobs
1. Select option `1` (🕷️ Scrape Jobs)
2. Enter job query: `software engineer`
3. Enter location: `United States`
4. Set jobs per platform: `50`
5. Include LinkedIn: `y`
6. Watch the progress bars!

### Step 3: Explore Your Data
1. Select option `3` (📊 Analytics)
2. Choose option `1` (📈 Executive Summary)
3. Explore the market overview

### Step 4: Search Jobs
1. Go back to main menu
2. Select option `2` (🔍 Search Jobs)
3. Try searching for: `python`
4. View the results

### Step 5: Generate a Report
1. Press `Ctrl+C` to exit interactive mode
2. Run: `recruitiq report --type executive`
3. Open the generated HTML file in your browser

## 📊 Common Use Cases

### For Job Seekers
```bash
# Research your target role
recruitiq scrape all --query "your target role" --location "your city"

# Analyze salary ranges
recruitiq analyze --salary

# Find remote opportunities
recruitiq search --keywords "remote" --employment-type "full-time"

# Generate skills report
recruitiq report --type skills
```

### For Recruiters
```bash
# Monitor competitor hiring
recruitiq scrape all --query "software engineer" --location "San Francisco"

# Analyze market rates
recruitiq analyze --salary

# Generate company insights
recruitiq report --type company --companies "Google,Microsoft,Meta"
```

### For Market Research
```bash
# Comprehensive market scan
recruitiq scrape all --query "data scientist" --linkedin --enrich-salaries

# Generate executive report
recruitiq report --type executive --days 30

# Track skills trends
recruitiq report --type skills
```

## 🎨 Interface Navigation

### Interactive Menu System
- Use **number keys** to select options
- Press **Enter** to confirm
- Use **Ctrl+C** to exit or go back
- Look for **[brackets]** for default values

### Progress Indicators
- **🕷️ Scraping Progress**: Real-time job collection
- **💾 Database Status**: Job count in status bar
- **🕒 Current Time**: Always visible
- **📊 System Status**: Ready/Processing indicators

## 🔧 Configuration

### Database Setup
RecruitIQ works out of the box with SQLite, but for production use:

```bash
# Set environment variable for PostgreSQL
export DATABASE_URL="postgresql://user:password@localhost:5432/recruitiq"

# Initialize with new database
recruitiq init
```

### Scraping Settings
```bash
# Adjust scraping delay (default: 1 second)
export SCRAPING_DELAY=2

# Set custom user agent
export USER_AGENT="Your Custom Bot 1.0"
```

## 🎯 Pro Tips

### Efficient Scraping
- Start with **broad queries** to build a large dataset
- Use **specific locations** for targeted analysis
- Enable **salary enrichment** for compensation insights
- Run scraping during **off-peak hours** for better success rates

### Powerful Analytics
- Use the **interactive analytics menu** for guided exploration
- Generate **HTML reports** for presentations
- Export data for **custom analysis**
- Set up **regular scraping** to track trends over time

### Advanced Search
- Combine **multiple filters** for precise results
- Use **keywords** to search job descriptions
- Try **salary ranges** to find opportunities in your bracket
- Use **--detailed** flag for full job information

## 🆘 Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
pip install -e .
```

**Database connection issues:**
```bash
recruitiq init
```

**Chrome driver problems:**
```bash
pip install --upgrade webdriver-manager
```

**Permission errors:**
```bash
# On macOS/Linux
sudo python scripts/install.py

# On Windows (run as administrator)
python scripts/install.py
```

### Getting Help
```bash
# Show help for any command
recruitiq --help
recruitiq search --help
recruitiq scrape --help

# Interactive help
recruitiq
# Then select option 7 (❓ Help)
```

## 🎉 You're Ready!

You now have RecruitIQ set up and know the basics. Here's what to do next:

1. **🕷️ Start scraping** jobs in your field
2. **📊 Explore analytics** to understand the market
3. **🔍 Search and filter** to find specific opportunities
4. **📱 Generate reports** to share insights
5. **⭐ Star the repo** if you find it useful!

## 📚 Next Steps

- Read the [full documentation](README.md) for advanced features
- Join our [community discussions](https://github.com/HattoriHanzo16/RecruitIQ/discussions)
- Report [issues or request features](https://github.com/HattoriHanzo16/RecruitIQ/issues)
- Contribute to the project on [GitHub](https://github.com/HattoriHanzo16/RecruitIQ)

---

**Happy job hunting! 🎯** 