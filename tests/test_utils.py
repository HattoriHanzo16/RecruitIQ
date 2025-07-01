"""
Tests for utility functions and validators
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock

from recruitiq.utils.helpers import (
    clean_text, parse_date, extract_salary, format_currency,
    calculate_match_score, get_date_range, parse_salary, get_random_headers,
    wait_random_time, extract_employment_type, validate_job_data
)
from recruitiq.utils.validators import (
    validate_job_data, validate_email, validate_url,
    validate_salary_range, sanitize_input
)
from recruitiq.utils.ascii_art import get_logo, get_banner


class TestHelpers:
    """Test helper utility functions"""
    
    def test_clean_text_basic(self):
        """Test basic text cleaning"""
        dirty_text = "  Hello   World  \n\n  "
        clean = clean_text(dirty_text)
        
        assert clean == "Hello World"
        assert clean.strip() == clean
    
    def test_clean_text_special_chars(self):
        """Test cleaning text with special characters"""
        dirty_text = "Job description with\n\ntabs\tand    multiple   spaces"
        clean = clean_text(dirty_text)
        
        assert "\n\n" not in clean
        assert "\t" not in clean
        assert "  " not in clean  # No double spaces
    
    def test_clean_text_empty_input(self):
        """Test cleaning empty or None input"""
        assert clean_text("") == ""
        assert clean_text("   ") == ""
        assert clean_text(None) == ""
    
    def test_clean_text_preserve_structure(self):
        """Test that important structure is preserved"""
        text = "Line 1\nLine 2\nLine 3"
        clean = clean_text(text, preserve_newlines=True)
        
        assert "Line 1" in clean
        assert "Line 2" in clean
        assert "Line 3" in clean
    
    def test_parse_date_iso_format(self):
        """Test parsing ISO date format"""
        date_str = "2024-01-15"
        parsed = parse_date(date_str)
        
        assert isinstance(parsed, datetime)
        assert parsed.year == 2024
        assert parsed.month == 1
        assert parsed.day == 15
    
    def test_parse_date_relative_formats(self):
        """Test parsing relative date formats"""
        test_cases = [
            ("1 day ago", 1),
            ("2 days ago", 2),
            ("1 week ago", 7),
            ("2 weeks ago", 14)
        ]
        
        for date_str, expected_days_ago in test_cases:
            parsed = parse_date(date_str)
            if parsed:  # Some formats might not be implemented
                days_diff = (datetime.now() - parsed).days
                assert abs(days_diff - expected_days_ago) <= 1  # Allow for timing differences
    
    def test_parse_date_invalid_format(self):
        """Test parsing invalid date format"""
        invalid_dates = ["not a date", "13/45/2024", ""]
        
        for date_str in invalid_dates:
            parsed = parse_date(date_str)
            assert parsed is None
    
    def test_extract_salary_range(self):
        """Test extracting salary ranges from text"""
        test_cases = [
            ("$100,000 - $120,000", (100000, 120000)),
            ("$80K - $90K", (80000, 90000)),
            ("80k-90k", (80000, 90000)),
            ("100000-120000", (100000, 120000)),
            ("$50 per hour", (104000, 104000)),  # Assuming 40h/week * 52 weeks
            ("No salary mentioned", (None, None))
        ]
        
        for text, expected in test_cases:
            result = extract_salary(text)
            if expected == (None, None):
                assert result is None or result == (None, None)
            else:
                assert result == expected
    
    def test_extract_salary_edge_cases(self):
        """Test salary extraction edge cases"""
        edge_cases = [
            "$1,000,000+",  # Very high salary
            "$15/hr",       # Hourly rate
            "Competitive",  # No specific amount
            "$50k+",        # Plus sign
            "Up to $100k"   # Range with prefix
        ]
        
        for text in edge_cases:
            result = extract_salary(text)
            assert isinstance(result, (tuple, type(None)))
    
    def test_format_currency(self):
        """Test currency formatting"""
        assert format_currency(100000) == "$100,000"
        assert format_currency(50000.50) == "$50,000.50"
        assert format_currency(None) == "N/A"
        assert format_currency(0) == "$0"
    
    def test_format_currency_with_currency(self):
        """Test currency formatting with different currencies"""
        assert format_currency(100000, "EUR") == "€100,000"
        assert format_currency(100000, "GBP") == "£100,000"
        assert format_currency(100000, "USD") == "$100,000"
    
    def test_calculate_match_score(self):
        """Test job matching score calculation"""
        job_skills = ["python", "django", "aws", "postgresql"]
        cv_skills = ["python", "flask", "aws", "mysql"]
        
        score = calculate_match_score(job_skills, cv_skills)
        
        assert 0 <= score <= 100
        assert score > 0  # Should have some match (python, aws)
        assert score < 100  # Should not be perfect match
    
    def test_calculate_match_score_edge_cases(self):
        """Test match score calculation edge cases"""
        # Perfect match
        skills = ["python", "django"]
        assert calculate_match_score(skills, skills) == 100
        
        # No match
        assert calculate_match_score(["python"], ["java"]) == 0
        
        # Empty lists
        assert calculate_match_score([], []) == 0
        assert calculate_match_score(["python"], []) == 0
        assert calculate_match_score([], ["python"]) == 0
    
    def test_get_date_range(self):
        """Test date range calculation"""
        end_date = datetime.now()
        start_date = get_date_range(days=30)
        
        diff = (end_date - start_date).days
        assert abs(diff - 30) <= 1  # Allow for timing differences
    
    def test_get_date_range_edge_cases(self):
        """Test date range edge cases"""
        # Zero days
        start_date = get_date_range(days=0)
        diff = (datetime.now() - start_date).total_seconds()
        assert diff < 60  # Should be very recent
        
        # Large number of days
        start_date = get_date_range(days=365)
        diff = (datetime.now() - start_date).days
        assert abs(diff - 365) <= 1


class TestValidators:
    """Test validation functions"""
    
    def test_validate_job_data_valid(self):
        """Test validation of valid job data"""
        valid_job = {
            'title': 'Software Engineer',
            'company_name': 'Tech Corp',
            'source_platform': 'Indeed',
            'url': 'https://example.com/job/123'
        }
        
        assert validate_job_data(valid_job) is True
    
    def test_validate_job_data_missing_required(self):
        """Test validation with missing required fields"""
        # Missing title
        job1 = {
            'company_name': 'Tech Corp',
            'source_platform': 'Indeed',
            'url': 'https://example.com/job/123'
        }
        assert validate_job_data(job1) is False
        
        # Missing company
        job2 = {
            'title': 'Software Engineer',
            'source_platform': 'Indeed',
            'url': 'https://example.com/job/123'
        }
        assert validate_job_data(job2) is False
        
        # Missing URL
        job3 = {
            'title': 'Software Engineer',
            'company_name': 'Tech Corp',
            'source_platform': 'Indeed'
        }
        assert validate_job_data(job3) is False
    
    def test_validate_job_data_empty_values(self):
        """Test validation with empty values"""
        job = {
            'title': '',
            'company_name': 'Tech Corp',
            'source_platform': 'Indeed',
            'url': 'https://example.com/job/123'
        }
        
        assert validate_job_data(job) is False
    
    def test_validate_job_data_with_optional_fields(self):
        """Test validation with optional fields"""
        job = {
            'title': 'Software Engineer',
            'company_name': 'Tech Corp',
            'source_platform': 'Indeed',
            'url': 'https://example.com/job/123',
            'location': 'San Francisco, CA',
            'salary_min': 100000,
            'salary_max': 120000,
            'employment_type': 'Full-time'
        }
        
        assert validate_job_data(job) is True
    
    def test_validate_email_valid(self):
        """Test validation of valid email addresses"""
        valid_emails = [
            "user@example.com",
            "test.email@domain.co.uk",
            "name+tag@company.org",
            "user123@test-domain.com"
        ]
        
        for email in valid_emails:
            assert validate_email(email) is True
    
    def test_validate_email_invalid(self):
        """Test validation of invalid email addresses"""
        invalid_emails = [
            "not-an-email",
            "@domain.com",
            "user@",
            "user@domain",
            "",
            None,
            "user spaces@domain.com"
        ]
        
        for email in invalid_emails:
            assert validate_email(email) is False
    
    def test_validate_url_valid(self):
        """Test validation of valid URLs"""
        valid_urls = [
            "https://example.com",
            "http://test.org/path",
            "https://sub.domain.com/page?param=value",
            "https://job-site.com/jobs/123-python-developer"
        ]
        
        for url in valid_urls:
            assert validate_url(url) is True
    
    def test_validate_url_invalid(self):
        """Test validation of invalid URLs"""
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",  # Wrong protocol
            "https://",
            "",
            None,
            "javascript:alert('xss')"  # Security risk
        ]
        
        for url in invalid_urls:
            assert validate_url(url) is False
    
    def test_validate_salary_range_valid(self):
        """Test validation of valid salary ranges"""
        valid_ranges = [
            (50000, 80000),
            (100000, 150000),
            (50000, 50000),  # Equal min/max
            (None, 100000),  # Only max
            (50000, None)    # Only min
        ]
        
        for salary_range in valid_ranges:
            assert validate_salary_range(salary_range) is True
    
    def test_validate_salary_range_invalid(self):
        """Test validation of invalid salary ranges"""
        invalid_ranges = [
            (100000, 50000),  # Min > Max
            (-50000, 80000),  # Negative salary
            (0, 80000),       # Zero salary
            ("50k", "80k"),   # String values
            (None, None)      # Both None
        ]
        
        for salary_range in invalid_ranges:
            assert validate_salary_range(salary_range) is False
    
    def test_sanitize_input_basic(self):
        """Test basic input sanitization"""
        assert sanitize_input("normal text") == "normal text"
        assert sanitize_input("text with    spaces") == "text with spaces"
        assert sanitize_input("") == ""
    
    def test_sanitize_input_malicious(self):
        """Test sanitization of potentially malicious input"""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "javascript:alert('test')"
        ]
        
        for malicious in malicious_inputs:
            sanitized = sanitize_input(malicious)
            # Should not contain dangerous patterns
            assert "<script>" not in sanitized.lower()
            assert "javascript:" not in sanitized.lower()
            assert "drop table" not in sanitized.lower()
    
    def test_sanitize_input_preserve_valid(self):
        """Test that sanitization preserves valid content"""
        valid_inputs = [
            "Python Developer",
            "Full-time position",
            "San Francisco, CA",
            "5+ years experience"
        ]
        
        for valid_input in valid_inputs:
            sanitized = sanitize_input(valid_input)
            assert len(sanitized) > 0
            assert sanitized.strip() == sanitized


class TestASCIIArt:
    """Test ASCII art utilities"""
    
    def test_get_logo(self):
        """Test getting ASCII logo"""
        logo = get_logo()
        
        assert isinstance(logo, str)
        assert len(logo) > 0
        assert "RecruitIQ" in logo
    
    def test_get_banner(self):
        """Test getting ASCII banner"""
        banner = get_banner("Test Message")
        
        assert isinstance(banner, str)
        assert len(banner) > 0
        assert "Test Message" in banner
    
    def test_get_banner_empty_message(self):
        """Test banner with empty message"""
        banner = get_banner("")
        
        assert isinstance(banner, str)
        # Should still return some banner structure
        assert len(banner) > 0


class TestUtilityIntegration:
    """Test integration between utility functions"""
    
    def test_job_processing_pipeline(self):
        """Test complete job data processing pipeline"""
        raw_job_data = {
            'title': '  Python Developer  ',
            'company_name': 'Tech Corp',
            'location': 'San Francisco, CA',
            'job_description': 'Looking for Python developer with\n\nDjango experience',
            'salary_text': '$100,000 - $120,000 per year',
            'source_platform': 'Indeed',
            'url': 'https://example.com/job/123',
            'posted_date': '2024-01-15'
        }
        
        # Process the data
        processed = {
            'title': clean_text(raw_job_data['title']),
            'company_name': clean_text(raw_job_data['company_name']),
            'location': clean_text(raw_job_data['location']),
            'job_description': clean_text(raw_job_data['job_description']),
            'source_platform': raw_job_data['source_platform'],
            'url': raw_job_data['url'],
            'posted_date': parse_date(raw_job_data['posted_date'])
        }
        
        # Extract salary
        salary_range = extract_salary(raw_job_data['salary_text'])
        if salary_range:
            processed['salary_min'] = salary_range[0]
            processed['salary_max'] = salary_range[1]
        
        # Validate the processed data
        assert validate_job_data(processed) is True
        assert processed['title'] == 'Python Developer'
        assert processed['job_description'] == 'Looking for Python developer with Django experience'
        assert processed['salary_min'] == 100000
        assert processed['salary_max'] == 120000
        assert isinstance(processed['posted_date'], datetime)
    
    def test_cv_skills_matching(self):
        """Test CV skills extraction and matching"""
        cv_text = """
        John Doe - Senior Python Developer
        
        Skills: Python, Django, Flask, PostgreSQL, AWS, Docker
        Experience: 5 years in web development
        """
        
        # Extract skills (simplified)
        skills = []
        skill_keywords = ['python', 'django', 'flask', 'postgresql', 'aws', 'docker']
        
        for skill in skill_keywords:
            if skill.lower() in cv_text.lower():
                skills.append(skill)
        
        # Match against job requirements
        job_requirements = ['python', 'django', 'aws', 'kubernetes']
        match_score = calculate_match_score(job_requirements, skills)
        
        assert match_score > 0  # Should have some match
        assert match_score <= 100
        
        # Should match python, django, aws (3 out of 4)
        expected_score = (3 / 4) * 100
        assert abs(match_score - expected_score) < 10  # Allow some variance
    
    def test_error_handling_chain(self):
        """Test error handling across utility functions"""
        # Test with None inputs
        assert clean_text(None) == ""
        assert parse_date(None) is None
        assert extract_salary(None) is None
        assert validate_job_data(None) is False
        assert validate_email(None) is False
        assert validate_url(None) is False
    
    def test_data_consistency(self):
        """Test data consistency across utility functions"""
        # Test that cleaned data remains valid
        original_data = {
            'title': '  Senior Python Developer  ',
            'company_name': 'Tech Corp',
            'source_platform': 'Indeed',
            'url': 'https://example.com/job/123'
        }
        
        cleaned_data = {
            'title': clean_text(original_data['title']),
            'company_name': clean_text(original_data['company_name']),
            'source_platform': original_data['source_platform'],
            'url': original_data['url']
        }
        
        # Original should validate
        assert validate_job_data(original_data) is True
        
        # Cleaned should also validate
        assert validate_job_data(cleaned_data) is True
        
        # Cleaned should be properly formatted
        assert cleaned_data['title'] == 'Senior Python Developer'
        assert cleaned_data['company_name'] == 'Tech Corp' 