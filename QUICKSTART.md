# 🚀 RecruitIQ Quick Start Guide

Get up and running with RecruitIQ's interactive interface in minutes!

## ⚡ 30-Second Setup

```bash
# One-line installation
python3 install.py

# Launch RecruitIQ
recruitiq
```

That's it! The beautiful interactive interface will guide you through everything.

## 🎯 First Steps

### 1. Welcome Screen
When you launch `recruitiq`, you'll see the main menu:

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
```

### 2. Initialize Database
- Press `5` for Settings
- Select `Initialize Database`
- Confirm to set up your local job database

### 3. Start Scraping
- Press `1` for Scrape Jobs
- Enter job query (e.g., "software engineer")
- Set location and limits
- Watch the progress bars!

### 4. Explore Your Data
- Press `2` to search your collected jobs
- Press `3` to see analytics and trends
- Press `4` for salary insights

## 🎨 Interface Tips

### Navigation
- Use **number keys** to select menu options
- **Enter** to confirm choices
- **Ctrl+C** for emergency exit
- **0** to go back or exit

### Smart Defaults
RecruitIQ provides intelligent defaults for:
- Job queries ("software engineer")
- Locations ("United States")
- Scraping limits (50-100 jobs)
- Search parameters

### Progress Tracking
Watch real-time progress with:
- 🕷️ **Scraping Progress** - Platform-by-platform updates
- 📊 **Job Counts** - Live statistics in status bar
- ⚡ **Speed Indicators** - Time estimates and completion

## 🔧 Troubleshooting

### Common Issues

**"recruitiq command not found"**
```bash
# Use direct Python execution
python3 cli.py
```

**Database errors**
- Try Settings → Initialize Database
- Check Python version (3.8+ required)

**Scraping issues**
- Some sites may block automated requests
- RecruitIQ provides fallback mock data
- Try different job queries or locations

### Getting Help
- Press `7` in the main menu for help
- Check the full README.md for detailed docs
- Run `python3 demo.py` for a guided tour

## 🎯 Quick Workflows

### Job Seeker Workflow
1. **Scrape** → Enter your target role
2. **Search** → Filter by company/location  
3. **Analytics** → Check salary trends
4. **Repeat** → Weekly market updates

### Recruiter Workflow
1. **Scrape** → Multiple role types
2. **Analytics** → Market intelligence
3. **Salary** → Competitive analysis
4. **Search** → Candidate sourcing insights

### Researcher Workflow
1. **Scrape** → Comprehensive data collection
2. **Analytics** → Skills and trends analysis
3. **Export** → Data for further research
4. **Monitor** → Regular market tracking

## 🎬 See It In Action

```bash
# Run the interactive demo
python3 demo.py
```

The demo showcases all features with example data and workflows.

## 🆘 Need Help?

- **In-app help**: Press `7` in main menu
- **Demo**: Run `python3 demo.py`
- **Issues**: Check GitHub issues page
- **Docs**: Read the full README.md

---

**Happy job hunting with RecruitIQ! 🎯** 