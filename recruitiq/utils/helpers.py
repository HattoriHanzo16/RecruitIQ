import re
import time
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\-.,()$]', '', text)
    return text

def parse_salary(salary_text: str) -> Dict[str, Optional[float]]:
    """
    Parse salary information from text
    
    Returns:
        Dict with 'min', 'max', and 'currency' keys
    """
    if not salary_text:
        return {'min': None, 'max': None, 'currency': 'USD'}
    
    # Clean the text
    salary_text = clean_text(salary_text.upper())
    
    # Extract currency
    currency = 'USD'
    if '$' in salary_text:
        currency = 'USD'
    elif '€' in salary_text or 'EUR' in salary_text:
        currency = 'EUR'
    elif '£' in salary_text or 'GBP' in salary_text:
        currency = 'GBP'
    
    # Remove currency symbols and text
    salary_text = re.sub(r'[$€£,]', '', salary_text)
    salary_text = re.sub(r'\b(USD|EUR|GBP|PER|YEAR|ANNUALLY|HOUR|HOURLY|K)\b', '', salary_text)
    
    # Find numeric ranges
    range_match = re.search(r'(\d+(?:\.\d+)?)\s*[-TO]\s*(\d+(?:\.\d+)?)', salary_text)
    if range_match:
        min_sal = float(range_match.group(1))
        max_sal = float(range_match.group(2))
        
        # Convert K notation
        if 'K' in salary_text.upper():
            min_sal *= 1000
            max_sal *= 1000
            
        return {'min': min_sal, 'max': max_sal, 'currency': currency}
    
    # Single number
    single_match = re.search(r'(\d+(?:\.\d+)?)', salary_text)
    if single_match:
        salary = float(single_match.group(1))
        if 'K' in salary_text.upper():
            salary *= 1000
        return {'min': salary, 'max': salary, 'currency': currency}
    
    return {'min': None, 'max': None, 'currency': currency}

def parse_date(date_text: str) -> Optional[datetime]:
    """Parse posted date from various formats"""
    if not date_text:
        return None
    
    date_text = clean_text(date_text.lower())
    now = datetime.now()
    
    # Handle relative dates
    if 'today' in date_text or 'just posted' in date_text:
        return now
    elif 'yesterday' in date_text:
        return now - timedelta(days=1)
    elif 'days ago' in date_text:
        days_match = re.search(r'(\d+)\s*days?\s*ago', date_text)
        if days_match:
            days = int(days_match.group(1))
            return now - timedelta(days=days)
    elif 'week' in date_text and 'ago' in date_text:
        weeks_match = re.search(r'(\d+)\s*weeks?\s*ago', date_text)
        if weeks_match:
            weeks = int(weeks_match.group(1))
            return now - timedelta(weeks=weeks)
        else:
            return now - timedelta(weeks=1)
    elif 'month' in date_text and 'ago' in date_text:
        months_match = re.search(r'(\d+)\s*months?\s*ago', date_text)
        if months_match:
            months = int(months_match.group(1))
            return now - timedelta(days=months*30)
        else:
            return now - timedelta(days=30)
    
    # Try to parse absolute dates
    date_patterns = [
        r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
        r'(\d{1,2})-(\d{1,2})-(\d{4})',  # MM-DD-YYYY
        r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, date_text)
        if match:
            try:
                if pattern.startswith(r'(\d{4})'):  # YYYY-MM-DD
                    year, month, day = map(int, match.groups())
                else:  # MM/DD/YYYY or MM-DD-YYYY
                    month, day, year = map(int, match.groups())
                return datetime(year, month, day)
            except ValueError:
                continue
    
    return None

def get_random_headers() -> Dict[str, str]:
    """Get random user agent headers to avoid blocking"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
    ]
    
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

def setup_selenium_driver(headless: bool = True) -> webdriver.Chrome:
    """Setup and configure Selenium Chrome driver"""
    options = Options()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def wait_random_time(min_seconds: float = 1.0, max_seconds: float = 3.0):
    """Wait for a random amount of time to avoid detection"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def extract_employment_type(text: str) -> Optional[str]:
    """Extract employment type from job description text"""
    if not text:
        return None
    
    text = text.lower()
    
    if any(term in text for term in ['full-time', 'full time', 'fulltime']):
        return 'Full-time'
    elif any(term in text for term in ['part-time', 'part time', 'parttime']):
        return 'Part-time'
    elif any(term in text for term in ['contract', 'contractor', 'freelance']):
        return 'Contract'
    elif any(term in text for term in ['intern', 'internship']):
        return 'Internship'
    elif any(term in text for term in ['temporary', 'temp']):
        return 'Temporary'
    
    return None

def validate_job_data(job_data: Dict[str, Any]) -> bool:
    """Validate that job data contains required fields"""
    required_fields = ['title', 'company_name', 'source_platform', 'url']
    return all(field in job_data and job_data[field] for field in required_fields)

def extract_salary(text: str) -> Optional[tuple]:
    """Extract salary range from text, returns (min, max) tuple or None"""
    if not text:
        return None
    
    salary_data = parse_salary(text)
    if salary_data and salary_data.get('min') is not None:
        return (salary_data['min'], salary_data['max'])
    return None

def format_currency(amount: Optional[float], currency: str = "USD") -> str:
    """Format currency amount for display"""
    if amount is None:
        return "N/A"
    
    symbols = {
        "USD": "$",
        "EUR": "€", 
        "GBP": "£"
    }
    
    symbol = symbols.get(currency, "$")
    return f"{symbol}{amount:,.2f}".rstrip('0').rstrip('.')

def calculate_match_score(job_skills: List[str], cv_skills: List[str]) -> float:
    """Calculate job matching score between job requirements and CV skills"""
    if not job_skills or not cv_skills:
        return 0.0
    
    # Convert to lowercase for comparison
    job_skills_lower = [skill.lower() for skill in job_skills]
    cv_skills_lower = [skill.lower() for skill in cv_skills]
    
    # Find matches
    matches = set(job_skills_lower) & set(cv_skills_lower)
    
    # Calculate percentage match
    score = (len(matches) / len(job_skills_lower)) * 100
    return round(score, 2)

def get_date_range(days: int) -> datetime:
    """Get date that is 'days' number of days ago"""
    return datetime.now() - timedelta(days=days) 