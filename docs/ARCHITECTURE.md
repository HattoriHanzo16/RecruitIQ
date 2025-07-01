# 🏗️ RecruitIQ Technical Architecture

## Table of Contents
- [System Overview](#system-overview)
- [Architecture Patterns](#architecture-patterns)
- [Core Components](#core-components)
- [Database Design](#database-design)
- [AI Integration](#ai-integration)
- [Web Scraping Engine](#web-scraping-engine)
- [Analytics Engine](#analytics-engine)
- [CLI Framework](#cli-framework)
- [Testing Architecture](#testing-architecture)
- [Security Design](#security-design)
- [Performance Optimization](#performance-optimization)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)

## System Overview

RecruitIQ is a sophisticated job market intelligence platform built using a modular, layered architecture following Domain-Driven Design (DDD) principles and Clean Architecture patterns.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                      │
├─────────────────────┬───────────────────┬───────────────────┤
│   CLI Interface     │  Interactive UI   │   Report Engine   │
│  (Typer + Rich)    │   (Rich + Async)  │  (Plotly + HTML)  │
└─────────────────────┴───────────────────┴───────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                       │
├─────────────────────┬───────────────────┬───────────────────┤
│   Job Analyzer      │   CV Analyzer     │   Market Intel    │
│                     │   (OpenAI GPT-4)  │                   │
└─────────────────────┴───────────────────┴───────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                            │
├─────────────────────┬───────────────────┬───────────────────┤
│   Job Entities      │  Analytics Models │   AI Models       │
│   Business Logic    │  Market Rules     │   CV Processing   │
└─────────────────────┴───────────────────┴───────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                      │
├─────────────────────┬───────────────────┬───────────────────┤
│   Database (ORM)    │   Web Scrapers    │   External APIs   │
│ PostgreSQL/SQLite   │  Multi-Platform   │   OpenAI API      │
└─────────────────────┴───────────────────┴───────────────────┘
```

## Architecture Patterns

### 1. Layered Architecture
- **Presentation Layer**: CLI interfaces, interactive dashboards, report generation
- **Application Layer**: Business use cases, orchestration, AI processing
- **Domain Layer**: Core business entities, rules, and domain logic
- **Infrastructure Layer**: Data persistence, external services, I/O operations

### 2. Dependency Inversion
```python
# Domain defines interfaces
class JobRepository(ABC):
    @abstractmethod
    def save(self, job: JobPosting) -> None: ...
    
    @abstractmethod
    def find_by_criteria(self, criteria: SearchCriteria) -> List[JobPosting]: ...

# Infrastructure implements interfaces
class SQLJobRepository(JobRepository):
    def __init__(self, session: Session):
        self._session = session
    
    def save(self, job: JobPosting) -> None:
        self._session.add(job)
        self._session.commit()
```

### 3. Factory Pattern
```python
class ScraperFactory:
    _scrapers = {
        'indeed': IndeedScraper,
        'linkedin': LinkedInScraper,
        'remoteok': RemoteOKScraper,
        'glassdoor': GlassdoorScraper,
        'company': CompanyScraper
    }
    
    @classmethod
    def create_scraper(cls, platform: str) -> BaseScraper:
        if platform not in cls._scrapers:
            raise ValueError(f"Unknown platform: {platform}")
        return cls._scrapers[platform]()
```

### 4. Strategy Pattern
```python
class AnalysisStrategy(ABC):
    @abstractmethod
    def analyze(self, data: DataFrame) -> AnalysisResult: ...

class SalaryAnalysisStrategy(AnalysisStrategy):
    def analyze(self, data: DataFrame) -> SalaryAnalysisResult:
        # Implement salary-specific analysis
        pass

class SkillsAnalysisStrategy(AnalysisStrategy):
    def analyze(self, data: DataFrame) -> SkillsAnalysisResult:
        # Implement skills-specific analysis
        pass
```

## Core Components

### 1. CLI Framework (`recruitiq/cli/`)

#### Main CLI Application
```python
# main.py - Typer-based CLI with rich formatting
import typer
from rich.console import Console
from rich.progress import Progress

app = typer.Typer(
    name="recruitiq",
    help="AI-Powered Job Market Intelligence Platform",
    rich_markup_mode="rich"
)

@app.command()
def scrape(
    platform: List[str] = typer.Option(["all"], help="Platforms to scrape"),
    query: str = typer.Option(..., help="Job search query"),
    location: str = typer.Option("Remote", help="Job location"),
    limit: int = typer.Option(100, help="Maximum jobs to scrape")
) -> None:
    """Scrape jobs from specified platforms with intelligent rate limiting."""
    with Progress() as progress:
        # Implement scraping with progress tracking
        pass
```

#### Interactive Interface
```python
# interactive.py - Rich-based TUI with real-time updates
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table

class InteractiveInterface:
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        
    def run(self) -> None:
        """Launch interactive dashboard with live updates."""
        self._setup_layout()
        self._start_event_loop()
        
    def _setup_layout(self) -> None:
        self.layout.split_column(
            Layout(self._create_header(), name="header", size=3),
            Layout(name="main"),
            Layout(self._create_footer(), name="footer", size=3)
        )
```

### 2. Core Business Logic (`recruitiq/core/`)

#### Job Market Analyzer
```python
# analyzer.py - Advanced market intelligence engine
class JobMarketAnalyzer:
    def __init__(self, repository: JobRepository, ai_service: AIService):
        self._repository = repository
        self._ai_service = ai_service
        
    async def analyze_market_trends(
        self, 
        timeframe: DateRange,
        criteria: AnalysisCriteria
    ) -> MarketAnalysisResult:
        """Perform comprehensive market analysis using ML algorithms."""
        
        # Fetch and preprocess data
        jobs = await self._repository.fetch_jobs_by_timeframe(timeframe)
        processed_data = self._preprocess_data(jobs)
        
        # Apply multiple analysis strategies
        strategies = [
            SalaryTrendAnalysis(),
            SkillsDemandAnalysis(),
            GeographicAnalysis(),
            CompanyHiringPatterns()
        ]
        
        results = []
        for strategy in strategies:
            result = await strategy.analyze(processed_data)
            results.append(result)
            
        return MarketAnalysisResult.aggregate(results)
```

#### AI-Powered CV Analyzer
```python
# cv_analyzer.py - OpenAI GPT-4 integration for CV analysis
class CVAnalyzer:
    def __init__(self, openai_client: OpenAI, fallback_analyzer: FallbackAnalyzer):
        self._openai_client = openai_client
        self._fallback_analyzer = fallback_analyzer
        
    async def analyze_cv(self, cv_content: str) -> CVAnalysisResult:
        """Analyze CV using GPT-4 with structured output parsing."""
        
        try:
            # Construct structured prompt for consistent JSON output
            prompt = self._build_analysis_prompt(cv_content)
            
            response = await self._openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse and validate JSON response
            analysis_data = json.loads(response.choices[0].message.content)
            return CVAnalysisResult.from_dict(analysis_data)
            
        except (OpenAIError, JSONDecodeError) as e:
            logger.warning(f"AI analysis failed: {e}, using fallback")
            return await self._fallback_analyzer.analyze(cv_content)
    
    def _build_analysis_prompt(self, cv_content: str) -> str:
        """Construct structured prompt for consistent AI responses."""
        return f"""
        Analyze the following CV and return a JSON response with this exact structure:
        {{
            "personal_info": {{"name": "", "email": "", "phone": "", "linkedin": ""}},
            "skills": {{"programming_languages": [], "frameworks": [], "databases": []}},
            "experience_years": 0,
            "professional_summary": "",
            "cv_score": 0,
            "strengths": [],
            "improvements": [],
            "recommended_roles": []
        }}
        
        CV Content:
        {cv_content}
        """
```

### 3. Web Scraping Engine (`recruitiq/scrapers/`)

#### Base Scraper Architecture
```python
# Base scraper with ethical rate limiting and error handling
class BaseScraper(ABC):
    def __init__(self):
        self.session = requests.Session()
        self.rate_limiter = AsyncLimiter(1, 2)  # 1 request per 2 seconds
        self.retry_strategy = ExponentialBackoff(max_retries=3)
        
    async def scrape_jobs(
        self, 
        query: str, 
        location: str, 
        limit: int = 100
    ) -> List[JobPosting]:
        """Scrape jobs with intelligent rate limiting and error recovery."""
        
        jobs = []
        page = 1
        
        while len(jobs) < limit:
            try:
                async with self.rate_limiter:
                    page_jobs = await self._scrape_page(query, location, page)
                    
                if not page_jobs:
                    break
                    
                # Deduplicate using content hashing
                unique_jobs = self._deduplicate_jobs(page_jobs, jobs)
                jobs.extend(unique_jobs)
                
                page += 1
                
            except ScrapingError as e:
                if await self.retry_strategy.should_retry(e):
                    await self.retry_strategy.wait()
                    continue
                else:
                    logger.error(f"Max retries exceeded: {e}")
                    break
                    
        return jobs[:limit]
    
    @abstractmethod
    async def _scrape_page(
        self, 
        query: str, 
        location: str, 
        page: int
    ) -> List[JobPosting]:
        """Platform-specific page scraping implementation."""
        pass
```

#### Platform-Specific Implementations
```python
# indeed.py - Indeed scraper with anti-detection measures
class IndeedScraper(BaseScraper):
    BASE_URL = "https://indeed.com/jobs"
    
    def __init__(self):
        super().__init__()
        self.session.headers.update({
            'User-Agent': self._get_random_user_agent(),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    async def _scrape_page(
        self, 
        query: str, 
        location: str, 
        page: int
    ) -> List[JobPosting]:
        """Scrape Indeed job listings with advanced parsing."""
        
        params = {
            'q': query,
            'l': location,
            'start': page * 10,
            'sort': 'date'
        }
        
        async with self.session.get(self.BASE_URL, params=params) as response:
            response.raise_for_status()
            soup = BeautifulSoup(await response.text(), 'html.parser')
            
        jobs = []
        job_cards = soup.find_all('div', class_='job_seen_beacon')
        
        for card in job_cards:
            job = self._parse_job_card(card)
            if job and self._validate_job(job):
                jobs.append(job)
                
        return jobs
    
    def _parse_job_card(self, card: BeautifulSoup) -> Optional[JobPosting]:
        """Extract job details from Indeed job card."""
        try:
            title_elem = card.find('h2', class_='jobTitle')
            title = title_elem.get_text(strip=True) if title_elem else None
            
            company_elem = card.find('span', class_='companyName')
            company = company_elem.get_text(strip=True) if company_elem else None
            
            location_elem = card.find('div', class_='companyLocation')
            location = location_elem.get_text(strip=True) if location_elem else None
            
            salary_elem = card.find('span', class_='salary-snippet')
            salary_text = salary_elem.get_text(strip=True) if salary_elem else None
            
            # Parse salary using regex patterns
            salary_range = self._parse_salary(salary_text) if salary_text else None
            
            # Extract additional metadata
            job_url = self._extract_job_url(title_elem)
            posted_date = self._extract_posted_date(card)
            
            return JobPosting(
                title=title,
                company=company,
                location=location,
                salary_min=salary_range.min if salary_range else None,
                salary_max=salary_range.max if salary_range else None,
                url=job_url,
                platform='indeed',
                posted_date=posted_date,
                scraped_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse job card: {e}")
            return None
```

## Database Design

### Entity-Relationship Model

```sql
-- Job postings with full-text search capabilities
CREATE TABLE job_postings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    salary_min INTEGER,
    salary_max INTEGER,
    currency VARCHAR(3) DEFAULT 'USD',
    description TEXT,
    requirements TEXT,
    benefits TEXT,
    employment_type job_type_enum DEFAULT 'full_time',
    experience_level experience_level_enum,
    url TEXT UNIQUE,
    platform platform_enum NOT NULL,
    posted_date TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_remote BOOLEAN DEFAULT FALSE,
    skills TEXT[], -- PostgreSQL array for skills
    
    -- Full-text search vectors
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', 
            coalesce(title, '') || ' ' || 
            coalesce(company, '') || ' ' || 
            coalesce(description, '')
        )
    ) STORED,
    
    -- Indexes for performance
    CONSTRAINT unique_job_per_platform UNIQUE (url, platform)
);

-- Optimized indexes for common queries
CREATE INDEX CONCURRENTLY idx_job_postings_search 
    ON job_postings USING GIN (search_vector);
    
CREATE INDEX CONCURRENTLY idx_job_postings_location_salary 
    ON job_postings (location, salary_min, salary_max);
    
CREATE INDEX CONCURRENTLY idx_job_postings_company_date 
    ON job_postings (company, posted_date DESC);
    
CREATE INDEX CONCURRENTLY idx_job_postings_skills 
    ON job_postings USING GIN (skills);

-- CV analysis results with JSON storage
CREATE TABLE cv_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_path VARCHAR(500) NOT NULL,
    file_hash VARCHAR(64) UNIQUE, -- SHA-256 for deduplication
    analysis_result JSONB NOT NULL,
    ai_provider VARCHAR(50), -- 'openai' or 'fallback'
    analysis_version VARCHAR(10) DEFAULT '1.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- JSONB indexes for fast queries
    INDEX idx_cv_analyses_name (((analysis_result->>'name'))),
    INDEX idx_cv_analyses_skills USING GIN ((analysis_result->'skills')),
    INDEX idx_cv_analyses_score (((analysis_result->>'cv_score')::numeric))
);
```

### SQLAlchemy Models

```python
# models.py - Advanced ORM models with relationships and validation
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
import uuid

class JobPosting(Base):
    __tablename__ = 'job_postings'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    location = Column(String(255), index=True)
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    currency = Column(String(3), default='USD')
    description = Column(Text)
    requirements = Column(Text)
    benefits = Column(Text)
    employment_type = Column(ENUM(EmploymentType), default=EmploymentType.FULL_TIME)
    experience_level = Column(ENUM(ExperienceLevel))
    url = Column(Text, unique=True)
    platform = Column(ENUM(Platform), nullable=False)
    posted_date = Column(DateTime(timezone=True))
    scraped_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    is_remote = Column(Boolean, default=False)
    skills = Column(ARRAY(String))
    
    # Hybrid properties for computed fields
    @hybrid_property
    def salary_midpoint(self):
        if self.salary_min and self.salary_max:
            return (self.salary_min + self.salary_max) / 2
        return self.salary_min or self.salary_max
    
    @hybrid_property
    def days_since_posted(self):
        if self.posted_date:
            return (datetime.utcnow() - self.posted_date).days
        return None
    
    # Validation methods
    @validates('salary_min', 'salary_max')
    def validate_salary(self, key, value):
        if value is not None and value < 0:
            raise ValueError(f"{key} cannot be negative")
        return value
    
    @validates('url')
    def validate_url(self, key, url):
        if url and not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return url
    
    # Class methods for complex queries
    @classmethod
    def search_by_criteria(cls, session, criteria: SearchCriteria):
        """Advanced search with multiple filters and full-text search."""
        query = session.query(cls)
        
        # Full-text search
        if criteria.query:
            query = query.filter(
                cls.search_vector.match(criteria.query)
            )
        
        # Location filtering with fuzzy matching
        if criteria.location:
            query = query.filter(
                cls.location.ilike(f'%{criteria.location}%')
            )
        
        # Salary range filtering
        if criteria.salary_min:
            query = query.filter(
                or_(
                    cls.salary_min >= criteria.salary_min,
                    cls.salary_max >= criteria.salary_min
                )
            )
        
        # Skills filtering using array operations
        if criteria.required_skills:
            for skill in criteria.required_skills:
                query = query.filter(
                    cls.skills.any(skill.lower())
                )
        
        return query.order_by(cls.posted_date.desc())
```

## AI Integration

### OpenAI GPT-4 Integration

```python
# AI service with advanced prompt engineering and response validation
class AIService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.token_counter = TokenCounter()
        self.response_cache = TTLCache(maxsize=1000, ttl=3600)  # 1-hour cache
        
    async def analyze_cv_content(self, cv_text: str) -> CVAnalysisResult:
        """Analyze CV using GPT-4 with structured prompts and validation."""
        
        # Check cache first
        cache_key = hashlib.sha256(cv_text.encode()).hexdigest()
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]
        
        # Estimate tokens and truncate if necessary
        estimated_tokens = self.token_counter.count(cv_text)
        if estimated_tokens > 3000:  # Leave room for response
            cv_text = self.token_counter.truncate(cv_text, 3000)
        
        # Construct structured prompt with examples
        prompt = self._build_cv_analysis_prompt(cv_text)
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert HR analyst and career advisor."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for consistency
                max_tokens=2000,
                response_format={"type": "json_object"}  # Ensure JSON response
            )
            
            # Parse and validate response
            result_data = json.loads(response.choices[0].message.content)
            result = CVAnalysisResult.from_dict(result_data)
            
            # Validate result structure
            if not self._validate_cv_analysis_result(result):
                raise ValueError("Invalid AI response structure")
            
            # Cache successful result
            self.response_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            raise AIAnalysisError(f"Failed to analyze CV: {str(e)}")
    
    def _build_cv_analysis_prompt(self, cv_text: str) -> str:
        """Build structured prompt with examples for consistent responses."""
        return f"""
        Analyze the following CV and extract structured information. 
        Return ONLY a valid JSON object with this exact structure:
        
        {{
            "personal_info": {{
                "name": "Full Name",
                "email": "email@example.com",
                "phone": "+1234567890",
                "linkedin": "linkedin.com/in/profile",
                "github": "github.com/username",
                "location": "City, Country"
            }},
            "professional_summary": "Brief 2-3 sentence summary of experience",
            "experience_years": 5,
            "skills": {{
                "programming_languages": ["Python", "Java"],
                "frameworks": ["Django", "React"],
                "databases": ["PostgreSQL", "MongoDB"],
                "cloud_platforms": ["AWS", "Azure"],
                "devops_tools": ["Docker", "Kubernetes"],
                "other_technical": ["Machine Learning", "API Design"],
                "soft_skills": ["Leadership", "Communication"]
            }},
            "cv_score": 8.5,
            "strengths": [
                "Strong technical expertise in modern technologies",
                "Proven leadership experience"
            ],
            "areas_for_improvement": [
                "Could benefit from cloud certifications",
                "Consider adding more quantified achievements"
            ],
            "recommended_job_titles": [
                "Senior Software Engineer",
                "Tech Lead"
            ],
            "market_insights": {{
                "salary_expectation": "Based on experience, $120k-150k USD",
                "demand_level": "High demand for these skills",
                "trending_skills": ["Kubernetes", "Machine Learning"]
            }}
        }}
        
        CV Content:
        {cv_text}
        """
```

## Analytics Engine

### Advanced Market Analysis

```python
# Advanced analytics with statistical analysis and ML predictions
class MarketIntelligenceEngine:
    def __init__(self, data_repository: JobRepository):
        self.repository = data_repository
        self.ml_models = MLModelRegistry()
        
    async def generate_market_report(
        self, 
        criteria: MarketAnalysisCriteria
    ) -> MarketIntelligenceReport:
        """Generate comprehensive market intelligence report."""
        
        # Parallel data collection
        tasks = [
            self._analyze_salary_trends(criteria),
            self._analyze_skills_demand(criteria),
            self._analyze_geographic_distribution(criteria),
            self._analyze_company_hiring_patterns(criteria),
            self._predict_market_trends(criteria)
        ]
        
        results = await asyncio.gather(*tasks)
        
        return MarketIntelligenceReport(
            salary_analysis=results[0],
            skills_analysis=results[1],
            geographic_analysis=results[2],
            company_analysis=results[3],
            predictions=results[4],
            generated_at=datetime.utcnow()
        )
    
    async def _analyze_salary_trends(
        self, 
        criteria: MarketAnalysisCriteria
    ) -> SalaryTrendAnalysis:
        """Perform advanced salary trend analysis with statistical significance."""
        
        # Fetch salary data with temporal grouping
        query = """
        SELECT 
            DATE_TRUNC('month', posted_date) as month,
            PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY salary_midpoint) as q1,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary_midpoint) as median,
            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY salary_midpoint) as q3,
            AVG(salary_midpoint) as mean,
            COUNT(*) as job_count,
            STDDEV(salary_midpoint) as std_dev
        FROM job_postings 
        WHERE salary_midpoint IS NOT NULL 
            AND posted_date >= %s
            AND (%s IS NULL OR search_vector @@ plainto_tsquery(%s))
        GROUP BY DATE_TRUNC('month', posted_date)
        ORDER BY month
        """
        
        params = [
            criteria.start_date,
            criteria.query,
            criteria.query
        ]
        
        salary_data = await self.repository.execute_query(query, params)
        
        # Statistical analysis
        trend_analysis = self._calculate_salary_trends(salary_data)
        outlier_analysis = self._detect_salary_outliers(salary_data)
        seasonality = self._analyze_seasonal_patterns(salary_data)
        
        return SalaryTrendAnalysis(
            monthly_trends=trend_analysis,
            outliers=outlier_analysis,
            seasonality=seasonality,
            growth_rate=self._calculate_growth_rate(salary_data),
            confidence_interval=self._calculate_confidence_interval(salary_data)
        )
    
    def _calculate_salary_trends(self, data: List[Dict]) -> TrendAnalysis:
        """Calculate salary trends using linear regression and seasonal decomposition."""
        
        df = pd.DataFrame(data)
        df['month'] = pd.to_datetime(df['month'])
        df.set_index('month', inplace=True)
        
        # Linear trend analysis
        X = np.arange(len(df)).reshape(-1, 1)
        y = df['median'].values
        
        model = LinearRegression().fit(X, y)
        trend_slope = model.coef_[0]
        r_squared = model.score(X, y)
        
        # Seasonal decomposition
        decomposition = seasonal_decompose(
            df['median'], 
            model='additive', 
            period=12
        )
        
        return TrendAnalysis(
            slope=trend_slope,
            r_squared=r_squared,
            seasonal_component=decomposition.seasonal.to_dict(),
            trend_component=decomposition.trend.to_dict(),
            is_significant=abs(trend_slope) > 100  # $100/month threshold
        )
```

## Testing Architecture

### Comprehensive Testing Strategy

```python
# conftest.py - Advanced pytest configuration with fixtures
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def postgres_container():
    """PostgreSQL test container for integration tests."""
    with PostgresContainer("postgres:15") as postgres:
        yield postgres

@pytest.fixture(scope="session")
def test_database_url(postgres_container):
    """Database URL for test database."""
    return postgres_container.get_connection_url()

@pytest.fixture
def db_session(test_database_url):
    """Database session with automatic rollback."""
    engine = create_engine(test_database_url)
    TestingSessionLocal = sessionmaker(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for AI testing."""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = json.dumps({
        "personal_info": {"name": "Test User", "email": "test@example.com"},
        "skills": {"programming_languages": ["Python"]},
        "cv_score": 8.5,
        "strengths": ["Strong technical skills"],
        "areas_for_improvement": ["Could add more projects"]
    })
    
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client

@pytest.fixture
def sample_job_data():
    """Sample job posting data for tests."""
    return [
        JobPosting(
            title="Senior Python Developer",
            company="Tech Corp",
            location="San Francisco, CA",
            salary_min=120000,
            salary_max=150000,
            platform=Platform.INDEED,
            posted_date=datetime.utcnow() - timedelta(days=1)
        ),
        JobPosting(
            title="Data Scientist",
            company="Data Inc",
            location="New York, NY",
            salary_min=100000,
            salary_max=130000,
            platform=Platform.LINKEDIN,
            posted_date=datetime.utcnow() - timedelta(days=2)
        )
    ]
```

### Performance Testing

```python
# Performance tests with benchmarking
import pytest
import time
from concurrent.futures import ThreadPoolExecutor

class TestPerformance:
    """Performance and load testing suite."""
    
    @pytest.mark.performance
    def test_database_query_performance(self, db_session, sample_job_data):
        """Test database query performance under load."""
        
        # Insert test data
        for job in sample_job_data * 1000:  # 2000 jobs
            db_session.add(job)
        db_session.commit()
        
        # Test search performance
        start_time = time.time()
        
        results = db_session.query(JobPosting).filter(
            JobPosting.search_vector.match('python developer')
        ).limit(100).all()
        
        query_time = time.time() - start_time
        
        assert query_time < 0.1  # Should complete in under 100ms
        assert len(results) > 0
    
    @pytest.mark.performance
    async def test_concurrent_scraping_performance(self):
        """Test scraping performance under concurrent load."""
        
        scraper = IndeedScraper()
        
        # Test concurrent scraping
        async def scrape_task():
            return await scraper.scrape_jobs("python", "remote", limit=10)
        
        start_time = time.time()
        
        # Run 10 concurrent scraping tasks
        tasks = [scrape_task() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        assert total_time < 30  # Should complete in under 30 seconds
        assert all(len(result) > 0 for result in results)
    
    @pytest.mark.benchmark
    def test_cv_analysis_performance(self, benchmark, mock_openai_client):
        """Benchmark CV analysis performance."""
        
        cv_analyzer = CVAnalyzer(mock_openai_client, Mock())
        sample_cv = "Sample CV content with technical skills..."
        
        # Benchmark the analysis
        result = benchmark(
            asyncio.run,
            cv_analyzer.analyze_cv(sample_cv)
        )
        
        assert result is not None
```

## Security Design

### Security Architecture

```python
# Security middleware and validation
class SecurityManager:
    """Comprehensive security management for RecruitIQ."""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.input_validator = InputValidator()
        self.audit_logger = AuditLogger()
    
    async def validate_scraping_request(self, request: ScrapingRequest) -> bool:
        """Validate scraping request for security compliance."""
        
        # Rate limiting
        if not await self.rate_limiter.check_limit(request.source_ip):
            raise RateLimitExceeded("Too many requests")
        
        # Input validation
        if not self.input_validator.validate_query(request.query):
            raise InvalidInput("Invalid search query")
        
        # Audit logging
        await self.audit_logger.log_request(request)
        
        return True
    
    def sanitize_input(self, user_input: str) -> str:
        """Sanitize user input to prevent injection attacks."""
        
        # Remove potential SQL injection patterns
        sanitized = re.sub(r'[;\'\"\\]', '', user_input)
        
        # Limit length
        sanitized = sanitized[:500]
        
        # Remove potential XSS patterns
        sanitized = html.escape(sanitized)
        
        return sanitized.strip()

class InputValidator:
    """Advanced input validation with configurable rules."""
    
    ALLOWED_QUERY_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-\+\(\)\.]+$')
    ALLOWED_LOCATION_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-\,\.]+$')
    
    def validate_query(self, query: str) -> bool:
        """Validate search query format."""
        if not query or len(query) > 200:
            return False
        return bool(self.ALLOWED_QUERY_PATTERN.match(query))
    
    def validate_location(self, location: str) -> bool:
        """Validate location format."""
        if not location or len(location) > 100:
            return False
        return bool(self.ALLOWED_LOCATION_PATTERN.match(location))
```

## Performance Optimization

### Caching Strategy

```python
# Multi-level caching for optimal performance
class CacheManager:
    """Advanced caching with multiple levels and invalidation strategies."""
    
    def __init__(self):
        # L1: In-memory cache for hot data
        self.memory_cache = TTLCache(maxsize=1000, ttl=300)  # 5 minutes
        
        # L2: Redis cache for shared data
        self.redis_cache = Redis(host='localhost', port=6379, db=0)
        
        # L3: Database query result cache
        self.query_cache = SQLQueryCache()
    
    async def get_market_analysis(
        self, 
        criteria: MarketAnalysisCriteria
    ) -> Optional[MarketAnalysisResult]:
        """Get market analysis with multi-level caching."""
        
        cache_key = self._generate_cache_key(criteria)
        
        # L1: Check memory cache
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]
        
        # L2: Check Redis cache
        cached_data = await self.redis_cache.get(cache_key)
        if cached_data:
            result = MarketAnalysisResult.from_json(cached_data)
            self.memory_cache[cache_key] = result  # Promote to L1
            return result
        
        return None
    
    async def set_market_analysis(
        self, 
        criteria: MarketAnalysisCriteria,
        result: MarketAnalysisResult
    ) -> None:
        """Store market analysis in all cache levels."""
        
        cache_key = self._generate_cache_key(criteria)
        
        # Store in all levels
        self.memory_cache[cache_key] = result
        await self.redis_cache.setex(
            cache_key, 
            3600,  # 1 hour TTL
            result.to_json()
        )
```

### Database Optimization

```python
# Database optimization with connection pooling and query optimization
class OptimizedJobRepository:
    """High-performance repository with advanced querying."""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(
            database_url,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    async def search_jobs_optimized(
        self, 
        criteria: SearchCriteria
    ) -> List[JobPosting]:
        """Optimized job search with advanced indexing."""
        
        # Use raw SQL for complex queries with proper indexing
        query = """
        SELECT * FROM job_postings 
        WHERE (
            ($1 IS NULL OR search_vector @@ plainto_tsquery($1))
            AND ($2 IS NULL OR location ILIKE $2)
            AND ($3 IS NULL OR salary_min >= $3)
            AND ($4 IS NULL OR skills && $4)
        )
        ORDER BY 
            ts_rank(search_vector, plainto_tsquery($1)) DESC,
            posted_date DESC
        LIMIT $5
        """
        
        params = [
            criteria.query,
            f'%{criteria.location}%' if criteria.location else None,
            criteria.salary_min,
            criteria.required_skills,
            criteria.limit
        ]
        
        async with self.engine.begin() as conn:
            result = await conn.execute(text(query), params)
            return [JobPosting.from_row(row) for row in result.fetchall()]
```

## Technology Stack

### Core Technologies

- **Language**: Python 3.8+
- **CLI Framework**: Typer + Rich for beautiful terminal interfaces
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI Integration**: OpenAI GPT-4 API
- **Web Scraping**: aiohttp + BeautifulSoup + Selenium
- **Analytics**: Pandas + NumPy + Scikit-learn
- **Visualization**: Plotly for interactive charts
- **Testing**: pytest + pytest-asyncio + pytest-cov
- **Caching**: Redis for distributed caching
- **Async**: asyncio for concurrent processing

### Development Tools

- **Code Quality**: black, isort, flake8, mypy
- **Security**: bandit, safety
- **Documentation**: Sphinx + MyST
- **CI/CD**: GitHub Actions
- **Containerization**: Docker + Docker Compose
- **Monitoring**: Prometheus + Grafana

### Performance Specifications

- **Database Performance**: < 100ms for most queries with proper indexing
- **Scraping Rate**: 1-2 requests/second per platform with rate limiting
- **AI Analysis**: < 5 seconds per CV analysis
- **Memory Usage**: < 500MB typical usage
- **Concurrent Users**: Designed for 100+ concurrent CLI sessions
- **Test Coverage**: 80%+ code coverage maintained

---

This architecture enables RecruitIQ to handle large-scale job market analysis while maintaining high performance, security, and reliability standards. 