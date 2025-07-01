from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="recruitiq",
    version="2.0.0",
    author="RecruitIQ Team",
    author_email="contact@recruitiq.dev",
    description="Interactive Job Market Intelligence CLI Tool - Beautiful terminal interface for job scraping and analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/recruitiq",
    packages=find_packages(),
    py_modules=['cli', 'interactive_cli', 'install', 'analyze', 'search', 'utils'],
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
            "recruitiq=cli:app",
            "recruitiq-interactive=interactive_cli:main",
            "recruitiq-install=install:main",
        ],
    },
    keywords="jobs, scraping, analysis, cli, career, recruitment, interactive, terminal, tui",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/recruitiq/issues",
        "Source": "https://github.com/yourusername/recruitiq",
        "Documentation": "https://github.com/yourusername/recruitiq#readme",
    },
) 