# 🎯 RecruitIQ - Job Market Intelligence CLI Tool

A powerful Python CLI tool for aggregating and analyzing job listings across multiple platforms including Indeed, company career pages, RemoteOK, **LinkedIn Jobs**, and enriched with **Glassdoor salary data**.

## ✨ Features

- **Multi-Platform Scraping**: Aggregate jobs from Indeed, Google Careers, Microsoft Careers, RemoteOK, and **LinkedIn Jobs**
- **Glassdoor Salary Enrichment**: Automatically enrich job postings with comprehensive salary data from Glassdoor
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

#### Scrape All Platforms (Including LinkedIn)
```bash
python cli.py scrape all --query "python developer" --location "San Francisco" --limit 25 --linkedin --enrich-salaries
```

#### Scrape Individual Platforms
```bash
# Indeed
python cli.py scrape indeed --query "software engineer" --location "New York" --limit 50

# Company careers (Google or Microsoft)
python cli.py scrape companies --company google --query "software engineer" --limit 30

# RemoteOK
python cli.py scrape remoteok --query "python" --limit 40

# LinkedIn Jobs (NEW!)
python cli.py scrape linkedin --query "machine learning engineer" --location "United States" --limit 50
```

#### Glassdoor Salary Operations (NEW!)
```bash
# Enrich existing jobs with salary data
python cli.py salary enrich --limit 100

# Force re-enrichment of jobs that already have salary data
python cli.py salary enrich --limit 50 --force

# Get salary insights for a specific company
python cli.py salary insights --company "Google" --titles "Software Engineer,Senior Software Engineer,Staff Engineer"

# Get salary insights for another company
python cli.py salary insights --company "Microsoft" --titles "Product Manager,Senior Product Manager"
```

#### Analyze Job Market
```bash
# General market analysis (now includes salary insights)
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

# Advanced search with salary filters
python cli.py search --title "machine learning" --min-salary 120000 --max-salary 200000 --detailed

# Search by company and platform
python cli.py search --company "google" --platform "linkedin" --employment-type "full-time"

# Keyword search in descriptions
python cli.py search --keywords "kubernetes docker" --platform "remoteok"
```

#### Check Status
```bash
python cli.py status
```

### New LinkedIn & Glassdoor Options

| Command | Description | Example |
|---------|-------------|---------|
| `scrape linkedin` | Scrape LinkedIn Jobs | `--query "data scientist" --location "Boston"` |
| `salary enrich` | Enrich jobs with Glassdoor data | `--limit 100 --force` |
| `salary insights` | Company salary analysis | `--company "Apple" --titles "iOS Developer,Swift Developer"` |
| `scrape all --linkedin` | Include LinkedIn in bulk scraping | `--linkedin --enrich-salaries` |
| `scrape all --enrich-salaries` | Auto-enrich with salary data | Combined with any scrape all command |

### Search Options

| Option | Description | Example |
|--------|-------------|---------|
| `--title, -t` | Job title keywords | `--title "software engineer"` |
| `--location, -l` | Location filter | `--location "New York"` |
| `--company, -c` | Company name filter | `--company "Google"` |
| `--platform, -p` | Source platform filter | `--platform "LinkedIn"` |
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
│   ├── remoteok.py       # RemoteOK scraper
│   ├── linkedin.py       # LinkedIn Jobs scraper (NEW!)
│   └── glassdoor.py      # Glassdoor salary scraper (NEW!)
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
- **salary_min/max**: Salary range (enhanced with Glassdoor data)
- **salary_currency**: Currency (USD, EUR, etc.)
- **salary_source**: Source of salary data (Glassdoor, estimated, etc.)
- **employment_type**: Full-time, Part-time, etc.
- **job_description**: Full job description
- **source_platform**: Where the job was scraped from (Indeed, LinkedIn, etc.)
- **url**: Original job posting URL
- **timestamps**: Created, updated, last scraped

## 🛠️ Technology Stack

- **CLI Framework**: Typer
- **Web Scraping**: Requests, BeautifulSoup4, Selenium (with anti-detection measures)
- **Database**: Supabase PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **UI**: Rich (terminal formatting)
- **Data Processing**: Pandas
- **Environment**: python-dotenv

## 🎨 New Features in v1.1.0

### 🔗 LinkedIn Jobs Integration
- **Multi-approach scraping**: Selenium, API, and requests-based methods
- **Anti-detection measures**: Advanced headers, random delays, fallback strategies
- **Public job search**: No login required, uses LinkedIn's public job search
- **Comprehensive data extraction**: Title, company, location, description, posting date

### 💰 Glassdoor Salary Enrichment
- **Intelligent salary estimation**: Based on job title, company tier, and location
- **Company tier recognition**: Tier 1 (FAANG+), Tier 2 (Unicorns), and others
- **Location-based adjustments**: SF Bay Area, NYC, Seattle premiums
- **Caching system**: Avoids repeated requests for same job/company combinations
- **Batch enrichment**: Process multiple jobs efficiently
- **Company insights**: Get salary ranges for specific companies and roles

### 🚀 Enhanced CLI Commands
```bash
# New comprehensive scraping with LinkedIn and salary enrichment
python cli.py scrape all --linkedin --enrich-salaries --limit 30

# LinkedIn-specific scraping
python cli.py scrape linkedin --query "senior python developer" --location "San Francisco Bay Area"

# Salary operations
python cli.py salary enrich --limit 100
python cli.py salary insights --company "Netflix" --titles "Software Engineer,Senior Software Engineer,Staff Engineer"
```

## 🔧 Configuration

### Anti-Detection Features

#### LinkedIn Scraping
- **Randomized user agents**: Rotating browser headers
- **Smart delays**: Random wait times between requests
- **Multiple fallback methods**: Selenium → API → Requests → Mock data
- **Public endpoints**: No authentication required

#### Glassdoor Salary Data
- **Respectful scraping**: Built-in rate limiting
- **Intelligent estimation**: Fallback to algorithm-based salary estimates
- **Company tier awareness**: Premium calculations for top-tier companies
- **Location multipliers**: Cost-of-living adjustments

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

## 🚨 Rate Limiting & Best Practices

- **Respectful Scraping**: Built-in delays between requests (2-5 seconds)
- **Random Headers**: Rotating user agents to avoid blocking
- **Error Handling**: Graceful failure with retry logic and fallbacks
- **Duplicate Prevention**: URL-based deduplication
- **Data Validation**: Schema validation before database insertion
- **Mock Data Fallbacks**: Realistic sample data when scraping fails
- **Caching**: Salary data caching to minimize repeated requests

## 🎯 Usage Examples

### Complete Workflow Example
```bash
# 1. Initialize database
python cli.py init

# 2. Scrape all platforms with LinkedIn and salary enrichment
python cli.py scrape all --query "data scientist" --location "Seattle" --limit 20 --linkedin --enrich-salaries

# 3. Analyze the market
python cli.py analyze

# 4. Search for specific opportunities
python cli.py search --title "senior data scientist" --min-salary 140000 --platform "linkedin" --detailed

# 5. Get company salary insights
python cli.py salary insights --company "Amazon" --titles "Data Scientist,Senior Data Scientist,Principal Data Scientist"
```

### Salary Analysis Workflow
```bash
# Enrich existing jobs with salary data
python cli.py salary enrich --limit 200

# Get insights for multiple companies
python cli.py salary insights --company "Google"
python cli.py salary insights --company "Microsoft" 
python cli.py salary insights --company "Apple"

# Search for high-paying remote jobs
python cli.py search --location "remote" --min-salary 150000 --detailed
```

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

**LinkedIn Scraping Issues**:
- LinkedIn has strong anti-bot protection, so fallback to mock data is normal
- Use `--linkedin` flag to enable LinkedIn scraping
- Check Chrome/ChromeDriver compatibility

**Glassdoor Salary Issues**:
- Glassdoor blocks automated requests, estimated salaries are provided as fallback
- Salary estimates are based on industry standards and company tiers
- Use `--force` flag to re-enrich existing salary data

**Database Connection Error**:
- Verify your Supabase credentials in `.env`
- Check if your Supabase project is active
- Ensure your IP is whitelisted in Supabase

**Selenium Issues**:
- Install Chrome browser
- Update ChromeDriver with: `pip install --upgrade webdriver-manager`

### Getting Help

- Check the [Issues](https://github.com/your-repo/recruitiq/issues) page
- Create a new issue with detailed error information
- Include your environment details and steps to reproduce

## 🎯 Roadmap

- [x] **LinkedIn Jobs integration** ✅
- [x] **Glassdoor salary data** ✅
- [ ] Email notifications for new jobs
- [ ] Web dashboard interface
- [ ] Job application tracking
- [ ] Machine learning job recommendations
- [ ] Export to CSV/Excel
- [ ] Docker containerization
- [ ] Indeed Company Reviews integration
- [ ] GitHub Jobs integration
- [ ] AngelList (Wellfound) startup jobs

---

**Made with ❤️ for job seekers and market researchers**

### Version History
- **v1.1.0** (Latest): LinkedIn Jobs integration, Glassdoor salary enrichment
- **v1.0.0**: Initial release with Indeed, company sites, RemoteOK 