"""
Tests for database models and relationships
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from recruitiq.db.models import JobPosting


class TestJobPosting:
    """Test JobPosting model"""
    
    def test_create_job_posting(self, db_session, sample_job_posting):
        """Test creating a job posting"""
        job = JobPosting(**sample_job_posting)
        db_session.add(job)
        db_session.commit()
        
        assert job.id is not None
        assert job.title == 'Senior Python Developer'
        assert job.company_name == 'TechCorp Inc.'
        assert job.is_active is True
    
    def test_job_posting_str_representation(self, sample_job_posting):
        """Test string representation of JobPosting"""
        job = JobPosting(**sample_job_posting)
        expected = "Senior Python Developer at TechCorp Inc."
        assert str(job) == expected
    
    def test_job_posting_required_fields(self, db_session):
        """Test that required fields are enforced"""
        # Test missing title
        with pytest.raises(IntegrityError):
            job = JobPosting(
                company_name='Test Company',
                source_platform='Indeed'
            )
            db_session.add(job)
            db_session.commit()
    
    def test_job_posting_timestamps(self, db_session, sample_job_posting):
        """Test that timestamps are set correctly"""
        job = JobPosting(**sample_job_posting)
        db_session.add(job)
        db_session.commit()
        
        assert job.created_at is not None
        assert job.updated_at is not None
        assert isinstance(job.created_at, datetime)
        assert isinstance(job.updated_at, datetime)
    
    def test_job_posting_update_timestamp(self, db_session, sample_job_posting):
        """Test that updated_at changes when job is modified"""
        job = JobPosting(**sample_job_posting)
        db_session.add(job)
        db_session.commit()
        
        original_updated_at = job.updated_at
        
        # Wait a moment and update
        import time
        time.sleep(0.1)
        job.title = 'Updated Title'
        db_session.commit()
        
        assert job.updated_at > original_updated_at
    
    def test_job_posting_salary_validation(self, db_session, sample_job_posting):
        """Test salary field constraints"""
        # Test negative salary
        sample_job_posting['salary_min'] = -1000
        job = JobPosting(**sample_job_posting)
        db_session.add(job)
        
        # Should still allow negative (might be data quality issue to handle elsewhere)
        db_session.commit()
        assert job.salary_min == -1000
    
    def test_job_posting_url_uniqueness(self, db_session, sample_job_posting):
        """Test URL uniqueness constraint"""
        # Create first job
        job1 = JobPosting(**sample_job_posting)
        db_session.add(job1)
        db_session.commit()
        
        # Try to create second job with same URL
        job2 = JobPosting(**sample_job_posting)
        job2.title = 'Different Title'
        db_session.add(job2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_job_posting_default_values(self, db_session):
        """Test default values for optional fields"""
        job = JobPosting(
            title='Test Job',
            company_name='Test Company',
            source_platform='Indeed',
            url='https://test.com/unique-job'
        )
        db_session.add(job)
        db_session.commit()
        
        assert job.is_active is True
        assert job.employment_type is None
        assert job.salary_currency is None
    
    def test_job_posting_search_by_attributes(self, populated_db):
        """Test querying jobs by various attributes"""
        # Search by title
        python_jobs = populated_db.query(JobPosting).filter(
            JobPosting.title.ilike('%python%')
        ).all()
        assert len(python_jobs) == 1
        assert python_jobs[0].title == 'Senior Python Developer'
        
        # Search by location
        remote_jobs = populated_db.query(JobPosting).filter(
            JobPosting.location.ilike('%remote%')
        ).all()
        assert len(remote_jobs) == 1
        assert remote_jobs[0].location == 'Remote'
        
        # Search by salary range
        high_salary_jobs = populated_db.query(JobPosting).filter(
            JobPosting.salary_min >= 140000
        ).all()
        assert len(high_salary_jobs) == 1
        assert high_salary_jobs[0].title == 'Data Scientist'
    
    def test_job_posting_date_range_queries(self, populated_db):
        """Test querying jobs by date ranges"""
        # Get jobs from last 2 days
        cutoff_date = datetime.now() - timedelta(days=2)
        recent_jobs = populated_db.query(JobPosting).filter(
            JobPosting.posted_date >= cutoff_date
        ).all()
        
        assert len(recent_jobs) >= 2  # Should include recent jobs
    
    def test_job_posting_platform_grouping(self, populated_db):
        """Test grouping jobs by platform"""
        from sqlalchemy import func
        
        platform_counts = populated_db.query(
            JobPosting.source_platform,
            func.count(JobPosting.id).label('count')
        ).group_by(JobPosting.source_platform).all()
        
        platform_dict = {platform: count for platform, count in platform_counts}
        
        assert 'Indeed' in platform_dict
        assert 'LinkedIn' in platform_dict
        assert 'RemoteOK' in platform_dict
        assert 'Company Sites' in platform_dict
    
    def test_job_posting_active_filter(self, populated_db):
        """Test filtering active vs inactive jobs"""
        # All jobs should be active by default
        active_jobs = populated_db.query(JobPosting).filter(
            JobPosting.is_active == True
        ).all()
        
        assert len(active_jobs) == 4
        
        # Deactivate one job
        job = active_jobs[0]
        job.is_active = False
        populated_db.commit()
        
        # Check active count decreased
        active_jobs = populated_db.query(JobPosting).filter(
            JobPosting.is_active == True
        ).all()
        
        assert len(active_jobs) == 3
    
    def test_job_posting_salary_statistics(self, populated_db):
        """Test salary-related queries and statistics"""
        from sqlalchemy import func
        
        # Get average salary
        avg_salary = populated_db.query(
            func.avg(JobPosting.salary_min)
        ).scalar()
        
        assert avg_salary is not None
        assert avg_salary > 0
        
        # Get salary range
        min_salary = populated_db.query(
            func.min(JobPosting.salary_min)
        ).scalar()
        max_salary = populated_db.query(
            func.max(JobPosting.salary_min)
        ).scalar()
        
        assert min_salary <= max_salary
        assert min_salary == 90000  # From sample data
        assert max_salary == 140000  # From sample data 