from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from .base import Base

class JobPosting(Base):
    """SQLAlchemy model for job postings"""
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=True, index=True)
    posted_date = Column(DateTime(timezone=True), nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String(10), nullable=True, default="USD")
    employment_type = Column(String(50), nullable=True)  # Full-time, Part-time, Contract, etc.
    job_description = Column(Text, nullable=True)
    source_platform = Column(String(100), nullable=False, index=True)
    url = Column(Text, nullable=False)
    last_scraped = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    # Ensure uniqueness of URL per platform
    __table_args__ = (UniqueConstraint('url', 'source_platform', name='unique_job_url_platform'),)

    def __repr__(self):
        return f"<JobPosting(id={self.id}, title='{self.title}', company='{self.company_name}', platform='{self.source_platform}')>" 