# 🎯 RecruitIQ - Job Market Intelligence CLI Tool

A powerful Python CLI tool for aggregating and analyzing job listings across multiple platforms including Indeed, company career pages, and RemoteOK.

## ✨ Features

- **Multi-Platform Scraping**: Aggregate jobs from Indeed, Google Careers, Microsoft Careers, and RemoteOK
- **Supabase Storage**: Store all job data in a PostgreSQL database via Supabase
- **Advanced Search**: Filter jobs by title, location, company, salary, and more
- **Market Analysis**: Generate insights including top companies, locations, skills, and salary statistics
- **Beautiful CLI**: Rich terminal interface with tables, panels, and colored output
- **Database Management**: Built-in Alembic migrations for schema management

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Supabase account and database
- Chrome browser (for Selenium-based scrapers)

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd recruitiq
```

2. **Set up virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
Create a `.env` file in the project root:
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
DATABASE_URL=postgresql://username:password@db.supabase.co:5432/postgres
```

5. **Initialize the database**:
```bash
python cli.py init
```

## 📖 Usage

### Basic Commands

#### Initialize Database
```bash
python cli.py init
```

#### Scrape All Platforms
```bash
python cli.py scrape all --query "python developer" --location "San Francisco" --limit 25
```

#### Scrape Individual Platforms
```bash
# Indeed
python cli.py scrape indeed --query "software engineer" --location "New York" --limit 50

# Company careers (Google or Microsoft)
python cli.py scrape companies --company google --query "software engineer" --limit 30

# RemoteOK
python cli.py scrape remoteok --query "python" --limit 40
```

#### Analyze Job Market
```bash
# General market analysis
python cli.py analyze

# Skills analysis
python cli.py analyze --skills

# Job posting trends
python cli.py analyze --trends
```

#### Search Jobs
```bash
# Basic search
python cli.py search --title "python developer" --location "remote"

# Advanced search with filters
python cli.py search --title "machine learning" --min-salary 100000 --days-ago 7 --detailed

# Search by company
python cli.py search --company "google" --employment-type "full-time"

# Keyword search in descriptions
python cli.py search --keywords "kubernetes docker" --platform "remoteok"
```

#### Check Status
```bash
python cli.py status
```

### Search Options

| Option | Description | Example |
|--------|-------------|---------|
| `--title, -t` | Job title keywords | `--title "software engineer"` |
| `--location, -l` | Location filter | `--location "New York"` |
| `--company, -c` | Company name filter | `--company "Google"` |
| `--platform, -p` | Source platform filter | `--platform "Indeed"` |
| `--employment-type, -e` | Employment type | `--employment-type "Full-time"` |
| `--min-salary` | Minimum salary | `--min-salary 80000` |
| `--max-salary` | Maximum salary | `--max-salary 150000` |
| `--keywords, -k` | Description keywords | `--keywords "python react"` |
| `--days-ago, -d` | Jobs within N days | `--days-ago 7` |
| `--limit` | Max results | `--limit 100` |
| `--detailed` | Full job details | `--detailed` |

## 🏗️ Architecture

### Project Structure
```
recruitiq/
├── cli.py                 # Main CLI interface
├── db/
│   ├── __init__.py
│   ├── base.py           # SQLAlchemy base configuration
│   ├── models.py         # Database models
│   └── session.py        # Database session management
├── alembic/              # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── scrapers/
│   ├── __init__.py
│   ├── indeed.py         # Indeed scraper
│   ├── company_sites.py  # Company career pages scraper
│   └── remoteok.py       # RemoteOK scraper
├── analyze.py            # Job market analysis
├── search.py             # Job search functionality
├── utils.py              # Utility functions
├── requirements.txt      # Python dependencies
└── README.md
```

### Database Schema

The `job_postings` table includes:
- **id**: Primary key
- **title**: Job title
- **company_name**: Company name
- **location**: Job location
- **posted_date**: When the job was posted
- **salary_min/max**: Salary range
- **employment_type**: Full-time, Part-time, etc.
- **job_description**: Full job description
- **source_platform**: Where the job was scraped from
- **url**: Original job posting URL
- **timestamps**: Created, updated, last scraped

## 🛠️ Technology Stack

- **CLI Framework**: Typer
- **Web Scraping**: Requests, BeautifulSoup4, Selenium
- **Database**: Supabase PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **UI**: Rich (terminal formatting)
- **Data Processing**: Pandas
- **Environment**: python-dotenv

## 🎨 Screenshots

### Market Analysis
![Analysis](https://via.placeholder.com/800x400?text=Job+Market+Analysis+Screenshot)

### Job Search Results
![Search](https://via.placeholder.com/800x400?text=Job+Search+Results+Screenshot)

## 🔧 Configuration

### Supabase Setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Get your project URL and anon key from Settings > API
3. Update your `.env` file with the credentials

### Adding New Scrapers

To add a new job platform:

1. Create a new scraper in `scrapers/` following the existing pattern
2. Implement the required methods: `search_jobs()`, `_extract_job_data()`
3. Add the scraper to `scrapers/__init__.py`
4. Update the CLI commands in `cli.py`

### Custom Analysis

Extend the `JobAnalyzer` class in `analyze.py` to add custom analytics:

```python
def custom_analysis(self):
    # Your custom analysis logic here
    pass
```

## 🚨 Rate Limiting & Best Practices

- **Respectful Scraping**: Built-in delays between requests
- **Random Headers**: Rotating user agents to avoid blocking
- **Error Handling**: Graceful failure with retry logic
- **Duplicate Prevention**: URL-based deduplication
- **Data Validation**: Schema validation before database insertion

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**Database Connection Error**:
- Verify your Supabase credentials in `.env`
- Check if your Supabase project is active
- Ensure your IP is whitelisted in Supabase

**Selenium Issues**:
- Install Chrome browser
- Update ChromeDriver with: `pip install --upgrade webdriver-manager`

**No Jobs Found**:
- Try broader search terms
- Check if the platforms are accessible
- Verify your internet connection

**Import Errors**:
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

### Getting Help

- Check the [Issues](https://github.com/your-repo/recruitiq/issues) page
- Create a new issue with detailed error information
- Include your environment details and steps to reproduce

## 🎯 Roadmap

- [ ] LinkedIn Jobs integration
- [ ] Glassdoor salary data
- [ ] Email notifications for new jobs
- [ ] Web dashboard interface
- [ ] Job application tracking
- [ ] Machine learning job recommendations
- [ ] Export to CSV/Excel
- [ ] Docker containerization

---

**Made with ❤️ for job seekers and market researchers** 