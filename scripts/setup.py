from setuptools import setup, find_packages
import os

# Get the parent directory (project root)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Read README from docs directory
readme_path = os.path.join(parent_dir, "docs", "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "RecruitIQ - Job Market Intelligence CLI Tool"

# Read requirements from project root
requirements_path = os.path.join(parent_dir, "requirements.txt")
if os.path.exists(requirements_path):
    with open(requirements_path, "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
else:
    requirements = [
        "typer>=0.9.0",
        "rich>=13.0.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "alembic>=1.12.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "selenium>=4.15.0",
        "webdriver-manager>=4.0.0",
        "pandas>=2.0.0",
        "plotly>=5.17.0",
        "jinja2>=3.1.0"
    ]

setup(
    name="recruitiq",
    version="2.0.0",
    author="RecruitIQ Team",
    author_email="contact@recruitiq.dev",
    description="Job Market Intelligence Platform - Beautiful CLI with analytics, reporting, and comprehensive job market insights",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HattoriHanzo16/RecruitIQ",
    package_dir={"": parent_dir},
    packages=find_packages(where=parent_dir),
    include_package_data=True,
    package_data={
        "recruitiq": ["alembic.ini"],
        "recruitiq.db": ["*.py"],
        "recruitiq.scrapers": ["*.py"],
        "recruitiq.core": ["*.py"],
        "recruitiq.cli": ["*.py"],
        "recruitiq.utils": ["*.py"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop", 
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Terminals",
        "Topic :: System :: Shells",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "recruitiq=recruitiq.cli.main:app",
            "recruitiq-interactive=recruitiq.cli.interactive:main",
            "recruitiq-install=scripts.install:main",
        ],
    },
    keywords="jobs, scraping, analysis, cli, career, recruitment, interactive, terminal, tui, analytics, intelligence",
    project_urls={
                "Bug Reports": "https://github.com/HattoriHanzo16/RecruitIQ/issues",
        "Source": "https://github.com/HattoriHanzo16/RecruitIQ",
        "Documentation": "https://github.com/HattoriHanzo16/RecruitIQ#readme",
    },
) 