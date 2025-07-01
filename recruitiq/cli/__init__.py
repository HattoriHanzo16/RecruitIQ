"""
RecruitIQ CLI Module

Contains the command-line interfaces for RecruitIQ including the main CLI and interactive interface.
"""

from .main import app as main_app
from .interactive import InteractiveRecruitIQ

__all__ = [
    "main_app",
    "InteractiveRecruitIQ",
] 