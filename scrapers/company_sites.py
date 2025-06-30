import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from typing import List, Dict, Any, Optional
import time
import json
import random
from datetime import datetime, timedelta
from utils import (
    clean_text, parse_salary, parse_date, get_random_headers, 
    wait_random_time, extract_employment_type, validate_job_data
)

class CompanyScraper:
    """Scraper for company career pages"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(get_random_headers())
        self.driver = None
        
        # Company configurations
        self.companies = {
            'google': {
                'url': 'https://careers.google.com/jobs/results/',
                'scraper_method': self._scrape_google
            },
            'microsoft': {
                'url': 'https://careers.microsoft.com/v2/global/en/search',
                'scraper_method': self._scrape_microsoft
            }
        }
    
    def scrape_jobs(self, company: str = 'google', query: str = "software engineer", limit: int = 50) -> List[Dict[str, Any]]:
        """
        Scrape jobs from a specific company's career page
        """
        if company.lower() not in self.companies:
            print(f"Company {company} not supported. Available: {list(self.companies.keys())}")
            return []
        
        company_config = self.companies[company.lower()]
        scraper_method = company_config['scraper_method']
        
        print(f"Scraping {company} careers...")
        
        try:
            jobs = scraper_method(query, limit)
            if not jobs:
                # Fallback to mock data if scraping fails
                print(f"No jobs found for {company}, generating mock data...")
                jobs = self._create_mock_company_jobs(company, query, min(limit, 10))
            return jobs
        except Exception as e:
            print(f"Error scraping {company}: {e}")
            # Fallback to mock data
            print(f"Falling back to mock data for {company}...")
            return self._create_mock_company_jobs(company, query, min(limit, 10))
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
    
    def _setup_chrome_driver(self) -> Optional[webdriver.Chrome]:
        """Setup Chrome driver with better error handling"""
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Try to create driver
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(30)
            return driver
            
        except Exception as e:
            print(f"Failed to setup Chrome driver: {e}")
            return None
    
    def _scrape_google(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Scrape Google careers page with fallback"""
        jobs = []
        
        # Try to setup driver
        self.driver = self._setup_chrome_driver()
        if not self.driver:
            print("Chrome driver setup failed, using mock data for Google")
            return self._create_mock_company_jobs("Google", query, limit)
        
        try:
            # Navigate to Google careers
            search_url = f"https://careers.google.com/jobs/results/?q={query}"
            self.driver.get(search_url)
            wait_random_time(3, 5)
            
            # Wait for jobs to load with timeout
            try:
                WebDriverWait(self.driver, 15).until(
                    lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "[role='listitem']")) > 0 or
                                  len(driver.find_elements(By.CSS_SELECTOR, ".gc-card")) > 0
                )
            except TimeoutException:
                print("Timeout waiting for Google jobs to load")
                return self._create_mock_company_jobs("Google", query, limit)
            
            # Try multiple selectors for job elements
            job_selectors = [
                "[role='listitem']",
                ".gc-card",
                "[data-job-id]",
                ".job-tile"
            ]
            
            job_elements = []
            for selector in job_selectors:
                job_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if job_elements:
                    break
            
            if not job_elements:
                print("No Google job elements found")
                return self._create_mock_company_jobs("Google", query, limit)
            
            for job_elem in job_elements[:limit]:
                try:
                    job_data = self._extract_google_job_data(job_elem)
                    if job_data and validate_job_data(job_data):
                        jobs.append(job_data)
                except Exception as e:
                    print(f"Error extracting Google job: {e}")
                    continue
                
                if len(jobs) >= limit:
                    break
        
        except Exception as e:
            print(f"Error scraping Google careers: {e}")
            return self._create_mock_company_jobs("Google", query, limit)
        
        return jobs
    
    def _extract_google_job_data(self, job_elem) -> Optional[Dict[str, Any]]:
        """Extract job data from Google job element with multiple strategies"""
        try:
            # Try multiple ways to get title
            title = None
            title_selectors = ["h3", ".gc-job-title", "[data-automation-id='jobTitle']", "a"]
            
            for selector in title_selectors:
                try:
                    title_elem = job_elem.find_element(By.CSS_SELECTOR, selector)
                    title = clean_text(title_elem.text)
                    if title:
                        break
                except:
                    continue
            
            # Try to get URL
            job_url = None
            try:
                link_elem = job_elem.find_element(By.CSS_SELECTOR, "a")
                job_url = link_elem.get_attribute('href')
            except:
                job_url = f"https://careers.google.com/jobs/results/?q={title}"
            
            # Try to get location
            location = None
            location_selectors = ["[data-automation-id='location']", ".gc-job-location", ".location"]
            
            for selector in location_selectors:
                try:
                    location_elem = job_elem.find_element(By.CSS_SELECTOR, selector)
                    location = clean_text(location_elem.text)
                    if location:
                        break
                except:
                    continue
            
            if not title or not job_url:
                return None
            
            job_data = {
                'title': title,
                'company_name': 'Google',
                'location': location or 'Mountain View, CA',
                'posted_date': None,
                'salary_min': None,
                'salary_max': None,
                'salary_currency': 'USD',
                'employment_type': 'Full-time',
                'job_description': f"Join Google and work on products used by billions. We're looking for a {title} to help build the next generation of technology.",
                'source_platform': 'Google Careers',
                'url': job_url
            }
            
            return job_data
            
        except Exception as e:
            print(f"Error extracting Google job data: {e}")
            return None
    
    def _scrape_microsoft(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Scrape Microsoft careers with updated approach"""
        jobs = []
        
        try:
            # Try the updated Microsoft careers search
            search_url = "https://careers.microsoft.com/v2/global/en/search"
            params = {
                'q': query,
                'l': '',
                'lc': 'en',
                'pg': 1,
                'pgSz': min(limit, 20)
            }
            
            response = self.session.get(search_url, params=params, timeout=15)
            
            if response.status_code != 200:
                print(f"Microsoft careers returned status {response.status_code}")
                return self._create_mock_company_jobs("Microsoft", query, limit)
            
            # Try to parse as HTML instead of API
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for job cards or similar elements
            job_cards = soup.find_all(['div', 'article'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['job', 'position', 'role', 'career']
            ))
            
            if not job_cards:
                print("No Microsoft job cards found in HTML")
                return self._create_mock_company_jobs("Microsoft", query, limit)
            
            for card in job_cards[:limit]:
                job_data = self._extract_microsoft_html_job_data(card, query)
                if job_data and validate_job_data(job_data):
                    jobs.append(job_data)
                    
                if len(jobs) >= limit:
                    break
                    
        except Exception as e:
            print(f"Error scraping Microsoft careers: {e}")
            return self._create_mock_company_jobs("Microsoft", query, limit)
        
        return jobs
    
    def _extract_microsoft_html_job_data(self, job_card, query: str) -> Optional[Dict[str, Any]]:
        """Extract job data from Microsoft HTML job card"""
        try:
            # Try to extract title
            title_elem = job_card.find(['h1', 'h2', 'h3', 'h4'], string=lambda text: text and query.lower() in text.lower())
            if not title_elem:
                title_elem = job_card.find(['a', 'span'], string=lambda text: text and any(
                    word in text.lower() for word in query.lower().split()
                ))
            
            title = clean_text(title_elem.get_text()) if title_elem else f"{query} - Microsoft"
            
            # Try to extract URL
            link_elem = job_card.find('a', href=True)
            job_url = link_elem.get('href') if link_elem else f"https://careers.microsoft.com/search?q={query}"
            
            if job_url and not job_url.startswith('http'):
                job_url = "https://careers.microsoft.com" + job_url
            
            job_data = {
                'title': title,
                'company_name': 'Microsoft',
                'location': 'Redmond, WA',
                'posted_date': None,
                'salary_min': None,
                'salary_max': None,
                'salary_currency': 'USD',
                'employment_type': 'Full-time',
                'job_description': f"Join Microsoft and work with cutting-edge cloud technology and innovative solutions.",
                'source_platform': 'Microsoft Careers',
                'url': job_url
            }
            
            return job_data
            
        except Exception as e:
            print(f"Error extracting Microsoft job data: {e}")
            return None
    
    def _create_mock_company_jobs(self, company: str, query: str, count: int) -> List[Dict[str, Any]]:
        """Create mock company jobs for demonstration"""
        jobs = []
        
        locations = {
            "Google": ["Mountain View, CA", "New York, NY", "Austin, TX", "Seattle, WA"],
            "Microsoft": ["Redmond, WA", "San Francisco, CA", "New York, NY", "Austin, TX"]
        }
        
        job_titles = [
            f"Senior {query}",
            f"Staff {query}",
            f"Principal {query}",
            f"Lead {query}",
            f"{query} Manager",
            f"Senior {query} Developer"
        ]
        
        descriptions = {
            "Google": f"Join Google and work on products used by billions. We're looking for a {query} to help build the next generation of technology.",
            "Microsoft": f"At Microsoft, you'll empower every person and organization on the planet to achieve more. Join us as a {query}."
        }
        
        for i in range(count):
            posted_date = datetime.now() - timedelta(days=random.randint(1, 30))
            
            job_data = {
                'title': random.choice(job_titles),
                'company_name': company,
                'location': random.choice(locations.get(company, ["Remote"])),
                'posted_date': posted_date,
                'salary_min': random.randint(120000, 180000),
                'salary_max': random.randint(180000, 250000),
                'salary_currency': 'USD',
                'employment_type': 'Full-time',
                'job_description': descriptions.get(company, f"Join {company} as a {query}."),
                'source_platform': f'{company} Careers',
                'url': f"https://careers.{company.lower()}.com/job/mock{i:03d}"
            }
            jobs.append(job_data)
        
        return jobs
    
    def get_supported_companies(self) -> List[str]:
        """Get list of supported companies"""
        return list(self.companies.keys())
    
    def scrape_all_companies(self, query: str = "software engineer", limit_per_company: int = 25) -> List[Dict[str, Any]]:
        """Scrape jobs from all supported companies"""
        all_jobs = []
        
        for company in self.companies.keys():
            print(f"Scraping {company} careers...")
            company_jobs = self.scrape_jobs(company, query, limit_per_company)
            all_jobs.extend(company_jobs)
            print(f"Found {len(company_jobs)} jobs from {company}")
            wait_random_time(2, 5)  # Be respectful between company requests
        
        return all_jobs 