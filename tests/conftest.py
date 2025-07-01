"""
Pytest configuration and fixtures for RecruitIQ tests
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from recruitiq.db.base import Base
from recruitiq.db.models import JobPosting
from recruitiq.db.session import get_session


@pytest.fixture(scope="session")
def test_database():
    """Create a temporary test database"""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    return Session


@pytest.fixture
def db_session(test_database):
    """Create a database session for testing"""
    session = test_database()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_job_posting():
    """Create a sample job posting for testing"""
    return {
        'title': 'Senior Python Developer',
        'company_name': 'TechCorp Inc.',
        'location': 'San Francisco, CA',
        'posted_date': datetime.now() - timedelta(days=1),
        'salary_min': 120000,
        'salary_max': 160000,
        'salary_currency': 'USD',
        'employment_type': 'Full-time',
        'job_description': 'We are looking for a senior Python developer with 5+ years of experience in Django, Flask, and AWS.',
        'source_platform': 'Indeed',
        'url': 'https://example.com/job/123',
        'last_scraped': datetime.now(),
        'is_active': True
    }


@pytest.fixture
def sample_job_postings():
    """Create multiple sample job postings for testing"""
    base_date = datetime.now()
    return [
        {
            'title': 'Senior Python Developer',
            'company_name': 'TechCorp Inc.',
            'location': 'San Francisco, CA',
            'posted_date': base_date - timedelta(days=1),
            'salary_min': 120000,
            'salary_max': 160000,
            'salary_currency': 'USD',
            'employment_type': 'Full-time',
            'job_description': 'Python developer with Django experience',
            'source_platform': 'Indeed',
            'url': 'https://example.com/job/1',
            'is_active': True
        },
        {
            'title': 'Data Scientist',
            'company_name': 'DataCorp LLC',
            'location': 'New York, NY',
            'posted_date': base_date - timedelta(days=2),
            'salary_min': 140000,
            'salary_max': 180000,
            'salary_currency': 'USD',
            'employment_type': 'Full-time',
            'job_description': 'Data scientist with machine learning and Python experience',
            'source_platform': 'LinkedIn',
            'url': 'https://example.com/job/2',
            'is_active': True
        },
        {
            'title': 'Remote JavaScript Developer',
            'company_name': 'RemoteTech',
            'location': 'Remote',
            'posted_date': base_date - timedelta(days=3),
            'salary_min': 90000,
            'salary_max': 130000,
            'salary_currency': 'USD',
            'employment_type': 'Full-time',
            'job_description': 'Remote JavaScript developer with React and Node.js experience',
            'source_platform': 'RemoteOK',
            'url': 'https://example.com/job/3',
            'is_active': True
        },
        {
            'title': 'DevOps Engineer',
            'company_name': 'CloudCorp',
            'location': 'Seattle, WA',
            'posted_date': base_date - timedelta(days=4),
            'salary_min': 110000,
            'salary_max': 150000,
            'salary_currency': 'USD',
            'employment_type': 'Full-time',
            'job_description': 'DevOps engineer with AWS, Docker, and Kubernetes experience',
            'source_platform': 'Company Sites',
            'url': 'https://example.com/job/4',
            'is_active': True
        }
    ]


@pytest.fixture
def populated_db(db_session, sample_job_postings):
    """Database session with sample job postings"""
    for job_data in sample_job_postings:
        job = JobPosting(**job_data)
        db_session.add(job)
    db_session.commit()
    return db_session


@pytest.fixture
def mock_cv_text():
    """Sample CV text for testing CV analysis"""
    return """
    John Doe
    Senior Software Engineer
    
    Email: john.doe@email.com
    Phone: (555) 123-4567
    LinkedIn: https://linkedin.com/in/johndoe
    GitHub: https://github.com/johndoe
    
    PROFESSIONAL SUMMARY
    Senior software engineer with 8 years of experience in Python, Django, and AWS.
    
    TECHNICAL SKILLS
    Programming Languages: Python, JavaScript, Java, SQL
    Frameworks: Django, Flask, React, Node.js
    Databases: PostgreSQL, MongoDB, Redis
    Cloud: AWS, Docker, Kubernetes
    Tools: Git, Jenkins, JIRA
    
    EXPERIENCE
    Senior Software Engineer - TechCorp (2020-Present)
    - Developed microservices using Python and Django
    - Deployed applications on AWS using Docker and Kubernetes
    - Led a team of 5 developers
    
    Software Engineer - StartupCorp (2018-2020)
    - Built REST APIs using Flask and PostgreSQL
    - Implemented CI/CD pipelines with Jenkins
    
    EDUCATION
    Bachelor of Science in Computer Science - University of Technology (2015)
    
    CERTIFICATIONS
    AWS Certified Solutions Architect
    """


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response for CV analysis"""
    return {
        "personal_information": {
            "name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "(555) 123-4567",
            "linkedin": "https://linkedin.com/in/johndoe",
            "github": "https://github.com/johndoe",
            "location": "Not specified"
        },
        "professional_summary": {
            "years_of_experience": 8,
            "job_title": "Senior Software Engineer",
            "industry": "Technology"
        },
        "skills": {
            "programming_languages": ["python", "javascript", "java", "sql"],
            "frameworks_libraries": ["django", "flask", "react", "node.js"],
            "databases": ["postgresql", "mongodb", "redis"],
            "cloud_devops": ["aws", "docker", "kubernetes"],
            "tools_software": ["git", "jenkins", "jira"],
            "methodologies": ["microservices", "rest api", "ci/cd"],
            "soft_skills": ["leadership", "teamwork"],
            "certifications": ["aws certified solutions architect"],
            "domain_expertise": ["web development", "api development"]
        },
        "experience_analysis": {
            "total_years": 8,
            "most_recent_job": "Senior Software Engineer",
            "key_achievements": [
                "Led a team of 5 developers",
                "Developed microservices architecture",
                "Implemented CI/CD pipelines"
            ],
            "career_progression": "Progressed from Software Engineer to Senior Software Engineer"
        },
        "education": {
            "degrees": ["Bachelor of Science in Computer Science"],
            "institutions": ["University of Technology"],
            "certifications": ["AWS Certified Solutions Architect"]
        },
        "cv_feedback": {
            "strengths": [
                "Strong technical skills in modern technologies",
                "Good progression from engineer to senior engineer",
                "Leadership experience mentioned",
                "Relevant certifications included"
            ],
            "improvements": [
                "Add more quantifiable achievements",
                "Include soft skills section",
                "Add project details and impact"
            ],
            "missing_elements": [
                "Portfolio or project links",
                "Specific metrics and achievements",
                "Industry awards or recognition"
            ],
            "overall_score": 7,
            "suggestions": [
                "Add metrics to achievements (e.g., 'improved performance by 30%')",
                "Include links to notable projects",
                "Add soft skills and languages section"
            ]
        },
        "job_market_insights": {
            "suitable_job_titles": [
                "senior software engineer",
                "python developer", 
                "backend engineer",
                "devops engineer"
            ],
            "recommended_skills": [
                "kubernetes",
                "terraform",
                "microservices",
                "system design"
            ],
            "industry_trends": "Strong alignment with current market trends in cloud and microservices"
        }
    }


@pytest.fixture
def mock_scraped_jobs():
    """Mock scraped job data for scraper testing"""
    return [
        {
            'title': 'Python Developer',
            'company_name': 'Test Company',
            'location': 'Test City',
            'posted_date': datetime.now(),
            'job_description': 'Python developer position with Django',
            'source_platform': 'Indeed',
            'url': 'https://test.com/job/1'
        },
        {
            'title': 'Data Scientist',
            'company_name': 'Data Corp',
            'location': 'Data City',
            'posted_date': datetime.now(),
            'job_description': 'Data scientist with machine learning experience',
            'source_platform': 'Indeed',
            'url': 'https://test.com/job/2'
        }
    ]


@pytest.fixture
def mock_requests_response():
    """Mock requests response for web scraping tests"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = """
    <html>
        <body>
            <div class="job">
                <h2>Python Developer</h2>
                <span class="company">Test Company</span>
                <span class="location">Test City</span>
                <div class="description">Python developer position</div>
            </div>
        </body>
    </html>
    """
    return mock_response


@pytest.fixture
def temp_cv_file():
    """Create a temporary CV file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""
        John Doe
        Software Engineer
        
        Email: john@example.com
        Skills: Python, Django, AWS
        
        Experience:
        - 5 years in software development
        - Python and Django expert
        """)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    os.unlink(temp_path)


@pytest.fixture
def mock_database_url():
    """Mock database URL for testing"""
    return "sqlite:///test.db"


# Mock patches for external dependencies
@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    with patch('recruitiq.core.cv_analyzer.openai.OpenAI') as mock:
        yield mock


@pytest.fixture
def mock_selenium_driver():
    """Mock Selenium WebDriver for testing"""
    with patch('recruitiq.scrapers.base.webdriver.Chrome') as mock:
        driver_instance = Mock()
        driver_instance.get.return_value = None
        driver_instance.find_elements.return_value = []
        driver_instance.quit.return_value = None
        mock.return_value = driver_instance
        yield driver_instance


@pytest.fixture
def mock_requests():
    """Mock requests for testing"""
    with patch('requests.get') as mock:
        yield mock 