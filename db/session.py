from sqlalchemy.orm import Session
from db.base import SessionLocal, engine, Base
from db.models import JobPosting

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_session() -> Session:
    """Get a database session"""
    return SessionLocal()

def init_db():
    """Initialize the database with tables"""
    create_tables()

def save_job_posting(session: Session, job_data: dict) -> JobPosting:
    """
    Save a job posting to the database
    
    Args:
        session: Database session
        job_data: Dictionary containing job posting data
        
    Returns:
        JobPosting: The saved job posting object
    """
    job_posting = JobPosting(**job_data)
    
    try:
        session.add(job_posting)
        session.commit()
        session.refresh(job_posting)
        return job_posting
    except Exception as e:
        session.rollback()
        raise e

def update_or_create_job_posting(session: Session, job_data: dict) -> JobPosting:
    """
    Update existing job posting or create new one based on URL and platform
    
    Args:
        session: Database session
        job_data: Dictionary containing job posting data
        
    Returns:
        JobPosting: The updated or created job posting object
    """
    existing_job = session.query(JobPosting).filter(
        JobPosting.url == job_data['url'],
        JobPosting.source_platform == job_data['source_platform']
    ).first()
    
    if existing_job:
        # Update existing job
        for key, value in job_data.items():
            setattr(existing_job, key, value)
        session.commit()
        session.refresh(existing_job)
        return existing_job
    else:
        # Create new job
        return save_job_posting(session, job_data) 