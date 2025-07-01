"""
Data validation utilities for RecruitIQ
"""

from typing import Dict, Any
import re
from datetime import datetime


def validate_job_data(job_data: Dict[str, Any]) -> bool:
    """
    Validate job data before saving to database
    
    Args:
        job_data: Dictionary containing job information
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(job_data, dict):
        return False
    
    # Required fields
    required_fields = ['title', 'company_name']
    for field in required_fields:
        if not job_data.get(field) or not job_data[field].strip():
            return False
    
    # Title validation
    title = job_data['title'].strip()
    if len(title) < 2 or len(title) > 200:
        return False
    
    # Company name validation
    company = job_data['company_name'].strip()
    if len(company) < 1 or len(company) > 200:
        return False
    
    # Optional field validation
    if job_data.get('location'):
        location = job_data['location'].strip()
        if len(location) > 200:
            return False
    
    if job_data.get('description'):
        description = job_data['description'].strip()
        if len(description) > 10000:  # Max description length
            return False
    
    # Salary validation
    if job_data.get('salary_min') is not None:
        try:
            salary_min = float(job_data['salary_min'])
            if salary_min < 0 or salary_min > 1000000:
                return False
        except (ValueError, TypeError):
            return False
    
    if job_data.get('salary_max') is not None:
        try:
            salary_max = float(job_data['salary_max'])
            if salary_max < 0 or salary_max > 1000000:
                return False
        except (ValueError, TypeError):
            return False
    
    # URL validation
    if job_data.get('job_url'):
        url = job_data['job_url'].strip()
        if url and not _is_valid_url(url):
            return False
    
    return True


def _is_valid_url(url: str) -> bool:
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def validate_search_params(**kwargs) -> Dict[str, Any]:
    """
    Validate and clean search parameters
    
    Returns:
        Dict containing cleaned parameters
    """
    cleaned = {}
    
    # String fields
    string_fields = ['title', 'location', 'company', 'platform', 'employment_type', 'keywords']
    for field in string_fields:
        value = kwargs.get(field)
        if value and isinstance(value, str):
            cleaned_value = value.strip()
            if cleaned_value:
                cleaned[field] = cleaned_value
    
    # Numeric fields
    if kwargs.get('min_salary'):
        try:
            min_salary = float(kwargs['min_salary'])
            if min_salary >= 0:
                cleaned['min_salary'] = min_salary
        except (ValueError, TypeError):
            pass
    
    if kwargs.get('max_salary'):
        try:
            max_salary = float(kwargs['max_salary'])
            if max_salary >= 0:
                cleaned['max_salary'] = max_salary
        except (ValueError, TypeError):
            pass
    
    if kwargs.get('days_ago'):
        try:
            days_ago = int(kwargs['days_ago'])
            if days_ago >= 0:
                cleaned['days_ago'] = days_ago
        except (ValueError, TypeError):
            pass
    
    if kwargs.get('limit'):
        try:
            limit = int(kwargs['limit'])
            if limit > 0:
                cleaned['limit'] = min(limit, 1000)  # Cap at 1000
        except (ValueError, TypeError):
            cleaned['limit'] = 50  # Default
    
    return cleaned


def validate_email(email: str) -> bool:
    """Validate email address format"""
    if not email or not isinstance(email, str):
        return False
    
    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    return email_pattern.match(email.strip()) is not None


def validate_url(url: str) -> bool:
    """Validate URL format"""
    if not url or not isinstance(url, str):
        return False
    
    # Only allow http/https protocols for security
    if not url.strip().startswith(('http://', 'https://')):
        return False
    
    return _is_valid_url(url.strip())


def validate_salary_range(salary_range: tuple) -> bool:
    """Validate salary range tuple (min, max)"""
    if not isinstance(salary_range, tuple) or len(salary_range) != 2:
        return False
    
    min_sal, max_sal = salary_range
    
    # Allow None values for partial ranges
    if min_sal is None and max_sal is None:
        return False
    
    # Check individual values
    if min_sal is not None:
        if not isinstance(min_sal, (int, float)) or min_sal <= 0:
            return False
    
    if max_sal is not None:
        if not isinstance(max_sal, (int, float)) or max_sal <= 0:
            return False
    
    # Check range validity
    if min_sal is not None and max_sal is not None:
        if min_sal > max_sal:
            return False
    
    return True


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove potentially dangerous patterns
    text = text.strip()
    
    # Remove script tags
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove javascript: protocol
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    
    # Remove SQL injection patterns
    text = re.sub(r'(drop\s+table|delete\s+from|insert\s+into|update\s+set)', '', text, flags=re.IGNORECASE)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip() 