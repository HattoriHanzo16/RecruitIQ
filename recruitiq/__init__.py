"""
RecruitIQ - Job Market Intelligence Platform

A comprehensive job market analysis and scraping platform with beautiful CLI interfaces,
advanced analytics, and HTML reporting capabilities.
"""

__version__ = "2.0.0"
__author__ = "RecruitIQ Team"
__description__ = "Job Market Intelligence Platform"

# Core imports for easy access
from .core.analyzer import JobAnalyzer
from .core.searcher import JobSearcher
from .core.reporter import RecruitIQReporter
from .core.dashboard import AdvancedAnalyticsDashboard

# Scraper imports
from .scrapers import (
    IndeedScraper,
    LinkedInScraper, 
    CompanyScraper,
    RemoteOKScraper,
    GlassdoorScraper
)

# Database imports
from .db.session import init_db, get_session
from .db.models import JobPosting

__all__ = [
    "JobAnalyzer",
    "JobSearcher", 
    "RecruitIQReporter",
    "AdvancedAnalyticsDashboard",
    "IndeedScraper",
    "LinkedInScraper",
    "CompanyScraper", 
    "RemoteOKScraper",
    "GlassdoorScraper",
    "init_db",
    "get_session",
    "JobPosting",
] 