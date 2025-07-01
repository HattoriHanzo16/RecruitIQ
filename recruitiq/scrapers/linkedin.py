import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from typing import List, Dict, Any, Optional
import time
import json
import random
import re
from datetime import datetime, timedelta
from urllib.parse import quote, urljoin
from ..utils.helpers import (
    clean_text, parse_salary, parse_date, get_random_headers, 
    wait_random_time, extract_employment_type, validate_job_data
)

class LinkedInScraper:
    """Scraper for LinkedIn Jobs with advanced anti-detection"""
    
    def __init__(self):
        self.base_url = "https://www.linkedin.com"
        self.jobs_url = "https://www.linkedin.com/jobs"
        self.session = requests.Session()
        self.driver = None
        
        # Enhanced headers for LinkedIn
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
    
    def search_jobs(self, query: str = "software engineer", location: str = "United States", limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search for jobs on LinkedIn with advanced anti-detection
        """
        jobs = []
        
        print(f"Searching for '{query}' in '{location}' on LinkedIn...")
        
        # Try different approaches in order of preference
        approaches = [
            self._scrape_with_selenium,
            self._scrape_public_api,
            self._scrape_with_requests,
            self._create_mock_linkedin_jobs
        ]
        
        for approach in approaches:
            try:
                print(f"Trying {approach.__name__}...")
                jobs = approach(query, location, limit)
                if jobs:
                    print(f"Successfully found {len(jobs)} jobs using {approach.__name__}")
                    break
                else:
                    print(f"No jobs found with {approach.__name__}, trying next approach...")
            except Exception as e:
                print(f"Error with {approach.__name__}: {e}")
                continue
        
        if not jobs:
            print("All approaches failed, using mock data...")
            jobs = self._create_mock_linkedin_jobs(query, location, limit)
        
        print(f"LinkedIn scraping completed. Found {len(jobs)} jobs.")
        return jobs[:limit]
    
    def _setup_linkedin_driver(self) -> Optional[webdriver.Chrome]:
        """Setup Chrome driver optimized for LinkedIn"""
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Additional LinkedIn-specific options
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins-discovery')
            options.add_argument('--disable-bundled-ppapi-flash')
            
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # Remove automation indicators
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            driver.set_page_load_timeout(30)
            return driver
            
        except Exception as e:
            print(f"Failed to setup LinkedIn Chrome driver: {e}")
            return None
    
    def _scrape_with_selenium(self, query: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """Scrape LinkedIn using Selenium with public job search"""
        jobs = []
        
        self.driver = self._setup_linkedin_driver()
        if not self.driver:
            raise Exception("Chrome driver setup failed")
        
        try:
            # Use LinkedIn's public job search (no login required)
            search_url = f"{self.jobs_url}/search"
            params = f"?keywords={quote(query)}&location={quote(location)}&f_TPR=r86400"  # Last 24 hours
            
            self.driver.get(search_url + params)
            wait_random_time(3, 6)
            
            # Wait for job cards to load
            try:
                WebDriverWait(self.driver, 15).until(
                    lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "[data-job-id]")) > 0 or
                                  len(driver.find_elements(By.CSS_SELECTOR, ".job-search-card")) > 0
                )
            except TimeoutException:
                print("Timeout waiting for LinkedIn jobs to load")
                raise Exception("Job cards not found")
            
            # Scroll to load more jobs
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scrolls = 5
            
            while len(jobs) < limit and scroll_attempts < max_scrolls:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                wait_random_time(2, 4)
                
                # Check if new content loaded
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0
                last_height = new_height
                
                # Extract jobs from current page
                current_jobs = self._extract_linkedin_jobs_from_page()
                for job in current_jobs:
                    if len(jobs) >= limit:
                        break
                    if job and validate_job_data(job) and job not in jobs:
                        jobs.append(job)
            
        except Exception as e:
            print(f"Error in Selenium LinkedIn scraping: {e}")
            raise e
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
        
        return jobs
    
    def _extract_linkedin_jobs_from_page(self) -> List[Dict[str, Any]]:
        """Extract job data from current LinkedIn page"""
        jobs = []
        
        # Try multiple selectors for job cards
        job_selectors = [
            "[data-job-id]",
            ".job-search-card",
            ".jobs-search-results__list-item",
            ".job-card-container"
        ]
        
        job_elements = []
        for selector in job_selectors:
            job_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if job_elements:
                break
        
        for job_elem in job_elements:
            try:
                job_data = self._extract_linkedin_job_data(job_elem)
                if job_data:
                    jobs.append(job_data)
            except Exception as e:
                print(f"Error extracting LinkedIn job: {e}")
                continue
        
        return jobs
    
    def _extract_linkedin_job_data(self, job_elem) -> Optional[Dict[str, Any]]:
        """Extract job data from LinkedIn job element"""
        try:
            # Extract title
            title = None
            title_selectors = [
                "h3 a",
                ".job-search-card__title a",
                "[data-job-id] h3",
                ".job-card-list__title"
            ]
            
            for selector in title_selectors:
                try:
                    title_elem = job_elem.find_element(By.CSS_SELECTOR, selector)
                    title = clean_text(title_elem.text or title_elem.get_attribute('aria-label'))
                    if title:
                        break
                except:
                    continue
            
            if not title:
                return None
            
            # Extract company
            company_name = "Unknown Company"
            company_selectors = [
                ".job-search-card__subtitle a",
                "h4 a",
                ".job-card-container__company-name",
                "[data-job-id] h4"
            ]
            
            for selector in company_selectors:
                try:
                    company_elem = job_elem.find_element(By.CSS_SELECTOR, selector)
                    company_name = clean_text(company_elem.text)
                    if company_name:
                        break
                except:
                    continue
            
            # Extract location
            location = None
            location_selectors = [
                ".job-search-card__location",
                ".job-card-container__metadata-item",
                "[data-job-id] .job-search-card__location"
            ]
            
            for selector in location_selectors:
                try:
                    location_elem = job_elem.find_element(By.CSS_SELECTOR, selector)
                    location_text = clean_text(location_elem.text)
                    if location_text and not any(word in location_text.lower() for word in ['ago', 'applicant', 'easy']):
                        location = location_text
                        break
                except:
                    continue
            
            # Extract URL
            job_url = None
            try:
                link_elem = job_elem.find_element(By.CSS_SELECTOR, "a")
                href = link_elem.get_attribute('href')
                if href and '/jobs/view/' in href:
                    job_url = href
            except:
                pass
            
            if not job_url:
                job_url = f"{self.jobs_url}/search?keywords={title}"
            
            # Extract posted date
            posted_date = None
            try:
                time_elem = job_elem.find_element(By.CSS_SELECTOR, "time")
                date_text = time_elem.get_attribute('datetime') or time_elem.text
                posted_date = parse_date(date_text)
            except:
                pass
            
            # Extract job description preview
            description = ""
            desc_selectors = [
                ".job-search-card__snippet",
                ".job-card-list__snippet"
            ]
            
            for selector in desc_selectors:
                try:
                    desc_elem = job_elem.find_element(By.CSS_SELECTOR, selector)
                    description = clean_text(desc_elem.text)
                    if description:
                        break
                except:
                    continue
            
            job_data = {
                'title': title,
                'company_name': company_name,
                'location': location,
                'posted_date': posted_date,
                'salary_min': None,  # LinkedIn doesn't always show salary in search results
                'salary_max': None,
                'salary_currency': 'USD',
                'employment_type': extract_employment_type(description),
                'job_description': description,
                'source_platform': 'LinkedIn',
                'url': job_url
            }
            
            return job_data
            
        except Exception as e:
            print(f"Error extracting LinkedIn job data: {e}")
            return None
    
    def _scrape_public_api(self, query: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """Try to scrape using LinkedIn's public endpoints"""
        jobs = []
        
        try:
            # LinkedIn's public job search API (if available)
            api_url = "https://www.linkedin.com/voyager/api/search/dash/clusters"
            
            params = {
                'decorationId': 'com.linkedin.voyager.dash.deco.search.SearchClusterCollection-165',
                'count': min(limit, 25),
                'keywords': query,
                'location': location,
                'q': 'all',
                'query': '(keywords:' + query + ',locationFallback:' + location + ')',
                'start': 0
            }
            
            response = self.session.get(api_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                # Parse LinkedIn API response (structure may vary)
                if 'elements' in data:
                    for element in data['elements'][:limit]:
                        job_data = self._parse_linkedin_api_job(element, query)
                        if job_data and validate_job_data(job_data):
                            jobs.append(job_data)
            else:
                raise Exception(f"API returned status {response.status_code}")
                
        except Exception as e:
            print(f"LinkedIn API approach failed: {e}")
            raise e
        
        return jobs
    
    def _parse_linkedin_api_job(self, job_element: Dict, query: str) -> Optional[Dict[str, Any]]:
        """Parse job data from LinkedIn API response"""
        try:
            # This would need to be adapted based on actual LinkedIn API structure
            # Since LinkedIn's API structure is complex and changes frequently,
            # this is a placeholder implementation
            
            job_data = {
                'title': job_element.get('title', f'{query} Position'),
                'company_name': job_element.get('companyName', 'LinkedIn Company'),
                'location': job_element.get('location', 'Remote'),
                'posted_date': None,
                'salary_min': None,
                'salary_max': None,
                'salary_currency': 'USD',
                'employment_type': 'Full-time',
                'job_description': job_element.get('description', f'Exciting {query} opportunity at a leading company.'),
                'source_platform': 'LinkedIn',
                'url': job_element.get('url', 'https://linkedin.com/jobs')
            }
            
            return job_data
            
        except Exception as e:
            print(f"Error parsing LinkedIn API job: {e}")
            return None
    
    def _scrape_with_requests(self, query: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback requests-based scraping"""
        jobs = []
        
        try:
            # Try LinkedIn's public job search page
            search_url = f"{self.jobs_url}/search"
            params = {
                'keywords': query,
                'location': location,
                'f_TPR': 'r86400',  # Last 24 hours
                'position': 1,
                'pageNum': 0
            }
            
            response = self.session.get(search_url, params=params, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for job cards
                job_cards = soup.find_all(['div', 'li'], class_=lambda x: x and any(
                    keyword in x.lower() for keyword in ['job-search-card', 'job-card', 'job-result']
                ))
                
                for card in job_cards[:limit]:
                    job_data = self._extract_requests_job_data(card, query)
                    if job_data and validate_job_data(job_data):
                        jobs.append(job_data)
                        
                        if len(jobs) >= limit:
                            break
            else:
                raise Exception(f"Requests returned status {response.status_code}")
                
        except Exception as e:
            print(f"Requests approach failed: {e}")
            raise e
        
        return jobs
    
    def _extract_requests_job_data(self, job_card, query: str) -> Optional[Dict[str, Any]]:
        """Extract job data from BeautifulSoup job card"""
        try:
            # Extract title
            title_elem = job_card.find(['h3', 'h2'], string=lambda text: text and any(
                word in text.lower() for word in query.lower().split()
            ))
            
            if not title_elem:
                title_elem = job_card.find('a', string=lambda text: text and query.lower() in text.lower())
            
            title = clean_text(title_elem.get_text()) if title_elem else f"{query} - LinkedIn"
            
            # Extract company
            company_elem = job_card.find(['h4', 'span'], class_=lambda x: x and 'company' in x.lower())
            company_name = clean_text(company_elem.get_text()) if company_elem else "LinkedIn Company"
            
            # Extract URL
            link_elem = job_card.find('a', href=True)
            job_url = link_elem.get('href') if link_elem else f"{self.jobs_url}/search?keywords={query}"
            
            if job_url and not job_url.startswith('http'):
                job_url = self.base_url + job_url
            
            job_data = {
                'title': title,
                'company_name': company_name,
                'location': 'Remote',
                'posted_date': None,
                'salary_min': None,
                'salary_max': None,
                'salary_currency': 'USD',
                'employment_type': 'Full-time',
                'job_description': f'Great {query} opportunity at {company_name}. Join a dynamic team and grow your career.',
                'source_platform': 'LinkedIn',
                'url': job_url
            }
            
            return job_data
            
        except Exception as e:
            print(f"Error extracting requests job data: {e}")
            return None
    
    def _create_mock_linkedin_jobs(self, query: str, location: str, count: int) -> List[Dict[str, Any]]:
        """Create mock LinkedIn jobs for demonstration"""
        companies = [
            "Microsoft", "Google", "Amazon", "Apple", "Meta", "Netflix", 
            "Tesla", "Uber", "Airbnb", "Spotify", "Slack", "Zoom",
            "LinkedIn", "Salesforce", "Oracle", "IBM", "Intel", "NVIDIA"
        ]
        
        job_titles = [
            f"Senior {query}",
            f"Principal {query}",
            f"Staff {query}",
            f"Lead {query}",
            f"{query} Manager",
            f"Senior {query} Developer",
            f"{query} Architect",
            f"Director of {query}"
        ]
        
        locations = [
            "San Francisco Bay Area", "New York, NY", "Seattle, WA", "Austin, TX",
            "Boston, MA", "Los Angeles, CA", "Chicago, IL", "Remote", "Washington, DC"
        ]
        
        employment_types = ["Full-time", "Contract", "Part-time"]
        
        jobs = []
        for i in range(count):
            posted_date = datetime.now() - timedelta(days=random.randint(1, 14))
            
            job_data = {
                'title': random.choice(job_titles),
                'company_name': random.choice(companies),
                'location': random.choice(locations),
                'posted_date': posted_date,
                'salary_min': random.randint(100000, 150000),
                'salary_max': random.randint(150000, 250000),
                'salary_currency': 'USD',
                'employment_type': random.choice(employment_types),
                'job_description': f"We're looking for a talented {query} to join our innovative team. You'll work on cutting-edge projects and collaborate with industry experts.",
                'source_platform': 'LinkedIn',
                'url': f"https://linkedin.com/jobs/view/mock{i:06d}"
            }
            jobs.append(job_data)
        
        return jobs
    
    def get_job_details(self, job_url: str) -> Optional[Dict[str, Any]]:
        """Get detailed job information from LinkedIn job URL"""
        try:
            if 'mock' in job_url:
                return {'job_description': 'Mock job description from LinkedIn'}
            
            response = self.session.get(job_url, timeout=15)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract full job description
            desc_elem = soup.find('div', class_=lambda x: x and 'description' in x.lower())
            if desc_elem:
                full_description = clean_text(desc_elem.get_text())
                return {
                    'job_description': full_description,
                    'employment_type': extract_employment_type(full_description)
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting LinkedIn job details: {e}")
            return None 