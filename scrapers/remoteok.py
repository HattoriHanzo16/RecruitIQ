import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import time
import json
from utils import (
    clean_text, parse_salary, parse_date, get_random_headers, 
    wait_random_time, extract_employment_type, validate_job_data
)

class RemoteOKScraper:
    """Scraper for RemoteOK job listings"""
    
    def __init__(self):
        self.base_url = "https://remoteok.io"
        self.api_url = "https://remoteok.io/api"
        self.session = requests.Session()
        self.session.headers.update(get_random_headers())
    
    def search_jobs(self, query: str = "software", limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search for remote jobs on RemoteOK
        
        Args:
            query: Job keywords (software, python, react, etc.)
            limit: Maximum number of jobs to scrape
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        try:
            # RemoteOK has a public API
            response = self.session.get(self.api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Filter jobs based on query and limit
            for job in data[:limit]:
                if self._matches_query(job, query):
                    job_data = self._extract_job_data(job)
                    if job_data and validate_job_data(job_data):
                        jobs.append(job_data)
                        
                        if len(jobs) >= limit:
                            break
            
            wait_random_time(2, 4)
            
        except Exception as e:
            print(f"Error scraping RemoteOK API: {e}")
            # Fallback to web scraping if API fails
            jobs = self._scrape_web(query, limit)
        
        return jobs
    
    def _matches_query(self, job: Dict, query: str) -> bool:
        """Check if job matches the search query"""
        if not query:
            return True
        
        query_lower = query.lower()
        
        # Check in title, company, tags, and description
        searchable_fields = [
            job.get('position', ''),
            job.get('company', ''),
            job.get('description', ''),
            ' '.join(job.get('tags', []))
        ]
        
        searchable_text = ' '.join(searchable_fields).lower()
        
        # Simple keyword matching
        query_words = query_lower.split()
        return any(word in searchable_text for word in query_words)
    
    def _extract_job_data(self, job: Dict) -> Optional[Dict[str, Any]]:
        """Extract job data from RemoteOK API response"""
        try:
            # Skip the first item which is usually metadata
            if not isinstance(job, dict) or 'position' not in job:
                return None
            
            title = job.get('position', '')
            company_name = job.get('company', '')
            location = job.get('location', 'Remote')
            description = job.get('description', '')
            job_id = job.get('id', '')
            
            if not title or not company_name or not job_id:
                return None
            
            # Build job URL
            job_url = f"{self.base_url}/job/{job_id}"
            
            # Parse salary if available
            salary_info = {'min': None, 'max': None, 'currency': 'USD'}
            salary_min = job.get('salary_min')
            salary_max = job.get('salary_max')
            
            if salary_min:
                salary_info['min'] = float(salary_min)
            if salary_max:
                salary_info['max'] = float(salary_max)
            
            # Parse posted date
            posted_date = None
            if 'date' in job:
                # RemoteOK provides epoch timestamp
                try:
                    from datetime import datetime
                    posted_date = datetime.fromtimestamp(int(job['date']))
                except (ValueError, TypeError):
                    posted_date = parse_date(str(job['date']))
            
            # Extract tags for additional info
            tags = job.get('tags', [])
            tags_text = ' '.join(tags) if tags else ''
            
            # Combine description with tags for full job description
            full_description = f"{description}\n\nSkills: {tags_text}" if tags_text else description
            
            job_data = {
                'title': clean_text(title),
                'company_name': clean_text(company_name),
                'location': clean_text(location),
                'posted_date': posted_date,
                'salary_min': salary_info['min'],
                'salary_max': salary_info['max'],
                'salary_currency': salary_info['currency'],
                'employment_type': 'Full-time',  # RemoteOK is mostly full-time remote
                'job_description': clean_text(full_description),
                'source_platform': 'RemoteOK',
                'url': job_url
            }
            
            return job_data
            
        except Exception as e:
            print(f"Error extracting RemoteOK job data: {e}")
            return None
    
    def _scrape_web(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback web scraping method if API fails"""
        jobs = []
        
        try:
            # Search URL with query
            search_url = f"{self.base_url}"
            if query:
                search_url += f"/{query.replace(' ', '-')}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job rows
            job_rows = soup.find_all('tr', class_='job')
            
            for row in job_rows[:limit]:
                job_data = self._extract_web_job_data(row)
                if job_data and validate_job_data(job_data):
                    jobs.append(job_data)
                    
                if len(jobs) >= limit:
                    break
            
        except Exception as e:
            print(f"Error web scraping RemoteOK: {e}")
        
        return jobs
    
    def _extract_web_job_data(self, job_row) -> Optional[Dict[str, Any]]:
        """Extract job data from web scraped row"""
        try:
            # Title and URL
            title_elem = job_row.find('h2', itemprop='title')
            if not title_elem:
                return None
            
            title = clean_text(title_elem.get_text())
            
            # URL
            link_elem = job_row.find('a', itemprop='url')
            job_url = link_elem.get('href') if link_elem else None
            if job_url and not job_url.startswith('http'):
                job_url = self.base_url + job_url
            
            # Company
            company_elem = job_row.find('h3', itemprop='name')
            company_name = clean_text(company_elem.get_text()) if company_elem else 'Unknown'
            
            # Location (usually "Remote" for RemoteOK)
            location_elem = job_row.find('[itemprop="jobLocation"]')
            location = clean_text(location_elem.get_text()) if location_elem else 'Remote'
            
            # Salary
            salary_elem = job_row.find('.salary')
            salary_info = {'min': None, 'max': None, 'currency': 'USD'}
            if salary_elem:
                salary_info = parse_salary(salary_elem.get_text())
            
            # Tags/Skills
            tag_elems = job_row.find_all('.tag')
            tags = [clean_text(tag.get_text()) for tag in tag_elems]
            description = f"Skills: {', '.join(tags)}" if tags else ""
            
            if not title or not job_url:
                return None
            
            job_data = {
                'title': title,
                'company_name': company_name,
                'location': location,
                'posted_date': None,
                'salary_min': salary_info['min'],
                'salary_max': salary_info['max'],
                'salary_currency': salary_info['currency'],
                'employment_type': 'Full-time',
                'job_description': description,
                'source_platform': 'RemoteOK',
                'url': job_url
            }
            
            return job_data
            
        except Exception as e:
            print(f"Error extracting web job data: {e}")
            return None
    
    def get_job_details(self, job_url: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed job information from job URL
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            Dictionary with detailed job information
        """
        try:
            response = self.session.get(job_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get full job description
            description_elem = soup.find('.markdown')
            if not description_elem:
                description_elem = soup.find('.description')
            
            full_description = ""
            if description_elem:
                full_description = clean_text(description_elem.get_text())
            
            # Additional details
            details = {
                'job_description': full_description,
                'employment_type': extract_employment_type(full_description) or 'Full-time'
            }
            
            wait_random_time(1, 2)
            return details
            
        except Exception as e:
            print(f"Error getting RemoteOK job details from {job_url}: {e}")
            return None
    
    def get_trending_tags(self) -> List[str]:
        """Get trending job tags/skills from RemoteOK"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find trending tags
            tag_elems = soup.find_all('.tag')[:20]  # Get top 20 tags
            tags = [clean_text(tag.get_text()) for tag in tag_elems if tag.get_text().strip()]
            
            return list(set(tags))  # Remove duplicates
            
        except Exception as e:
            print(f"Error getting trending tags: {e}")
            return [] 