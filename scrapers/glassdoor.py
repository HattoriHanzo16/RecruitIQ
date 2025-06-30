import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from typing import List, Dict, Any, Optional, Tuple
import time
import json
import random
import re
from datetime import datetime
from urllib.parse import quote, urljoin
from utils import (
    clean_text, parse_salary, get_random_headers, 
    wait_random_time
)

class GlassdoorScraper:
    """Scraper for Glassdoor salary data to enrich job postings"""
    
    def __init__(self):
        self.base_url = "https://www.glassdoor.com"
        self.salaries_url = "https://www.glassdoor.com/Salaries"
        self.session = requests.Session()
        self.driver = None
        
        # Enhanced headers for Glassdoor
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
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.glassdoor.com/'
        })
        
        # Salary cache to avoid repeated requests
        self._salary_cache = {}
    
    def get_salary_data(self, job_title: str, company_name: str, location: str = "United States") -> Optional[Dict[str, Any]]:
        """
        Get salary data for a specific job title and company
        
        Args:
            job_title: The job title to search for
            company_name: The company name
            location: Location for salary data
            
        Returns:
            Dictionary with salary information or None
        """
        # Create cache key
        cache_key = f"{job_title.lower()}_{company_name.lower()}_{location.lower()}"
        
        if cache_key in self._salary_cache:
            return self._salary_cache[cache_key]
        
        print(f"Getting salary data for {job_title} at {company_name}...")
        
        # Try different approaches in order of preference
        approaches = [
            self._get_salary_with_selenium,
            self._get_salary_with_requests,
            self._get_estimated_salary
        ]
        
        salary_data = None
        for approach in approaches:
            try:
                print(f"Trying {approach.__name__}...")
                salary_data = approach(job_title, company_name, location)
                if salary_data:
                    print(f"Successfully found salary data using {approach.__name__}")
                    break
                else:
                    print(f"No salary data found with {approach.__name__}, trying next approach...")
            except Exception as e:
                print(f"Error with {approach.__name__}: {e}")
                continue
        
        if not salary_data:
            print("All approaches failed, using estimated salary...")
            salary_data = self._get_estimated_salary(job_title, company_name, location)
        
        # Cache the result
        if salary_data:
            self._salary_cache[cache_key] = salary_data
        
        return salary_data
    
    def _setup_glassdoor_driver(self) -> Optional[webdriver.Chrome]:
        """Setup Chrome driver optimized for Glassdoor"""
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
            
            # Additional Glassdoor-specific options
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
            print(f"Failed to setup Glassdoor Chrome driver: {e}")
            return None
    
    def _get_salary_with_selenium(self, job_title: str, company_name: str, location: str) -> Optional[Dict[str, Any]]:
        """Get salary data using Selenium"""
        self.driver = self._setup_glassdoor_driver()
        if not self.driver:
            raise Exception("Chrome driver setup failed")
        
        try:
            # Search for salary data
            search_query = f"{job_title} {company_name}"
            search_url = f"{self.salaries_url}/search?keyword={quote(search_query)}&location={quote(location)}"
            
            self.driver.get(search_url)
            wait_random_time(3, 6)
            
            # Wait for salary data to load
            try:
                WebDriverWait(self.driver, 15).until(
                    lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "[data-test='salary-card']")) > 0 or
                                  len(driver.find_elements(By.CSS_SELECTOR, ".salaryCard")) > 0
                )
            except TimeoutException:
                print("Timeout waiting for Glassdoor salary data to load")
                raise Exception("Salary data not found")
            
            # Extract salary information
            salary_data = self._extract_salary_from_page()
            
            if salary_data:
                return salary_data
            else:
                raise Exception("No salary data extracted")
            
        except Exception as e:
            print(f"Error in Selenium Glassdoor scraping: {e}")
            raise e
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
    
    def _extract_salary_from_page(self) -> Optional[Dict[str, Any]]:
        """Extract salary data from current Glassdoor page"""
        try:
            # Try multiple selectors for salary cards
            salary_selectors = [
                "[data-test='salary-card']",
                ".salaryCard",
                ".salary-card",
                ".css-1w3vdkr"
            ]
            
            salary_elements = []
            for selector in salary_selectors:
                salary_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if salary_elements:
                    break
            
            if not salary_elements:
                return None
            
            # Get the first salary card
            salary_card = salary_elements[0]
            
            # Extract salary range
            salary_text = ""
            salary_text_selectors = [
                "[data-test='salary-estimate']",
                ".salary-estimate",
                ".css-1uodvoj",
                ".salary-range"
            ]
            
            for selector in salary_text_selectors:
                try:
                    salary_elem = salary_card.find_element(By.CSS_SELECTOR, selector)
                    salary_text = salary_elem.text
                    if salary_text:
                        break
                except:
                    continue
            
            if not salary_text:
                # Try to get any text that looks like salary
                all_text = salary_card.text
                salary_match = re.search(r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?', all_text)
                if salary_match:
                    salary_text = salary_match.group()
            
            # Parse salary information
            if salary_text:
                salary_info = parse_salary(salary_text)
                
                # Extract additional information
                job_title_elem = None
                title_selectors = [
                    "[data-test='job-title']",
                    ".job-title",
                    "h3",
                    "h2"
                ]
                
                for selector in title_selectors:
                    try:
                        job_title_elem = salary_card.find_element(By.CSS_SELECTOR, selector)
                        if job_title_elem.text:
                            break
                    except:
                        continue
                
                return {
                    'salary_min': salary_info.get('min'),
                    'salary_max': salary_info.get('max'),
                    'salary_currency': salary_info.get('currency', 'USD'),
                    'salary_source': 'Glassdoor',
                    'salary_title': clean_text(job_title_elem.text) if job_title_elem else None,
                    'salary_updated': datetime.now().isoformat()
                }
            
            return None
            
        except Exception as e:
            print(f"Error extracting salary from Glassdoor page: {e}")
            return None
    
    def _get_salary_with_requests(self, job_title: str, company_name: str, location: str) -> Optional[Dict[str, Any]]:
        """Get salary data using requests (fallback method)"""
        try:
            # Try Glassdoor's public search
            search_url = f"{self.salaries_url}/search"
            params = {
                'keyword': f"{job_title} {company_name}",
                'location': location
            }
            
            response = self.session.get(search_url, params=params, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for salary information
                salary_elements = soup.find_all(['div', 'span'], class_=lambda x: x and any(
                    keyword in x.lower() for keyword in ['salary', 'pay', 'wage', 'compensation']
                ))
                
                for elem in salary_elements:
                    text = elem.get_text()
                    if '$' in text and any(char.isdigit() for char in text):
                        salary_info = parse_salary(text)
                        if salary_info.get('min') or salary_info.get('max'):
                            return {
                                'salary_min': salary_info.get('min'),
                                'salary_max': salary_info.get('max'),
                                'salary_currency': salary_info.get('currency', 'USD'),
                                'salary_source': 'Glassdoor',
                                'salary_title': job_title,
                                'salary_updated': datetime.now().isoformat()
                            }
            else:
                raise Exception(f"Requests returned status {response.status_code}")
                
        except Exception as e:
            print(f"Requests approach failed: {e}")
            raise e
        
        return None
    
    def _get_estimated_salary(self, job_title: str, company_name: str, location: str) -> Dict[str, Any]:
        """Generate estimated salary based on job title and company"""
        
        # Salary estimation based on job titles and companies
        title_lower = job_title.lower()
        company_lower = company_name.lower()
        
        # Base salary ranges by job level/type
        salary_ranges = {
            'intern': (40000, 80000),
            'junior': (60000, 90000),
            'entry': (65000, 95000),
            'software engineer': (80000, 130000),
            'senior': (120000, 180000),
            'staff': (160000, 220000),
            'principal': (180000, 260000),
            'lead': (140000, 200000),
            'manager': (130000, 190000),
            'senior manager': (160000, 230000),
            'director': (200000, 300000),
            'vp': (250000, 400000),
            'cto': (300000, 500000),
            'architect': (140000, 210000),
            'data scientist': (90000, 160000),
            'product manager': (100000, 170000),
            'designer': (70000, 130000),
            'devops': (90000, 150000),
            'security': (95000, 165000),
            'mobile': (85000, 145000),
            'frontend': (75000, 135000),
            'backend': (85000, 145000),
            'fullstack': (80000, 140000)
        }
        
        # Company tier multipliers
        tier1_companies = [
            'google', 'apple', 'microsoft', 'amazon', 'meta', 'facebook', 'netflix', 
            'tesla', 'nvidia', 'openai', 'anthropic'
        ]
        tier2_companies = [
            'uber', 'airbnb', 'spotify', 'slack', 'zoom', 'salesforce', 'oracle', 
            'ibm', 'intel', 'linkedin', 'twitter', 'snap', 'pinterest'
        ]
        
        # Determine base salary range
        base_min, base_max = salary_ranges.get('software engineer', (80000, 130000))
        
        for keyword, (min_sal, max_sal) in salary_ranges.items():
            if keyword in title_lower:
                base_min, base_max = min_sal, max_sal
                break
        
        # Apply company tier multiplier
        if any(company in company_lower for company in tier1_companies):
            multiplier = random.uniform(1.3, 1.6)  # 30-60% premium for tier 1
        elif any(company in company_lower for company in tier2_companies):
            multiplier = random.uniform(1.1, 1.4)  # 10-40% premium for tier 2
        else:
            multiplier = random.uniform(0.9, 1.2)  # -10% to +20% for other companies
        
        # Apply location multiplier
        location_lower = location.lower()
        if any(loc in location_lower for loc in ['san francisco', 'sf', 'bay area', 'palo alto']):
            location_multiplier = random.uniform(1.2, 1.4)
        elif any(loc in location_lower for loc in ['new york', 'nyc', 'manhattan']):
            location_multiplier = random.uniform(1.15, 1.35)
        elif any(loc in location_lower for loc in ['seattle', 'boston', 'los angeles', 'austin']):
            location_multiplier = random.uniform(1.05, 1.25)
        elif 'remote' in location_lower:
            location_multiplier = random.uniform(1.0, 1.2)
        else:
            location_multiplier = random.uniform(0.85, 1.1)
        
        # Calculate final salary range
        final_min = int(base_min * multiplier * location_multiplier)
        final_max = int(base_max * multiplier * location_multiplier)
        
        # Add some randomness
        variance = 0.1  # 10% variance
        final_min = int(final_min * random.uniform(1 - variance, 1 + variance))
        final_max = int(final_max * random.uniform(1 - variance, 1 + variance))
        
        return {
            'salary_min': final_min,
            'salary_max': final_max,
            'salary_currency': 'USD',
            'salary_source': 'Glassdoor (Estimated)',
            'salary_title': job_title,
            'salary_updated': datetime.now().isoformat(),
            'is_estimated': True
        }
    
    def enrich_jobs_with_salary_data(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich a list of job postings with Glassdoor salary data
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            List of job dictionaries with added salary information
        """
        enriched_jobs = []
        
        print(f"Enriching {len(jobs)} jobs with Glassdoor salary data...")
        
        for i, job in enumerate(jobs):
            print(f"Processing job {i+1}/{len(jobs)}: {job.get('title', 'Unknown')} at {job.get('company_name', 'Unknown')}")
            
            # Skip if job already has detailed salary info
            if job.get('salary_min') and job.get('salary_max'):
                enriched_jobs.append(job)
                continue
            
            # Get salary data from Glassdoor
            salary_data = self.get_salary_data(
                job.get('title', ''),
                job.get('company_name', ''),
                job.get('location', 'United States')
            )
            
            # Merge salary data into job
            if salary_data:
                enriched_job = job.copy()
                # Only update if we don't have salary data or if Glassdoor data is better
                if not enriched_job.get('salary_min') or salary_data.get('salary_source') == 'Glassdoor':
                    enriched_job.update({
                        'salary_min': salary_data.get('salary_min'),
                        'salary_max': salary_data.get('salary_max'),
                        'salary_currency': salary_data.get('salary_currency', 'USD'),
                        'salary_source': salary_data.get('salary_source'),
                        'salary_updated': salary_data.get('salary_updated'),
                        'is_salary_estimated': salary_data.get('is_estimated', False)
                    })
                enriched_jobs.append(enriched_job)
            else:
                enriched_jobs.append(job)
            
            # Add delay between requests to be respectful
            if i < len(jobs) - 1:  # Don't wait after the last job
                wait_random_time(1, 3)
        
        print(f"Completed salary enrichment for {len(enriched_jobs)} jobs")
        return enriched_jobs
    
    def get_company_salary_insights(self, company_name: str, job_titles: List[str] = None) -> Dict[str, Any]:
        """
        Get salary insights for a specific company
        
        Args:
            company_name: Name of the company
            job_titles: Optional list of job titles to focus on
            
        Returns:
            Dictionary with salary insights
        """
        if not job_titles:
            job_titles = ["Software Engineer", "Senior Software Engineer", "Product Manager", "Data Scientist"]
        
        insights = {
            'company_name': company_name,
            'salary_data': [],
            'average_salary_range': None,
            'updated': datetime.now().isoformat()
        }
        
        total_min = 0
        total_max = 0
        count = 0
        
        for title in job_titles:
            salary_data = self.get_salary_data(title, company_name)
            if salary_data and salary_data.get('salary_min') and salary_data.get('salary_max'):
                insights['salary_data'].append({
                    'job_title': title,
                    'salary_min': salary_data['salary_min'],
                    'salary_max': salary_data['salary_max'],
                    'salary_source': salary_data.get('salary_source')
                })
                total_min += salary_data['salary_min']
                total_max += salary_data['salary_max']
                count += 1
        
        if count > 0:
            insights['average_salary_range'] = {
                'min': round(total_min / count),
                'max': round(total_max / count),
                'currency': 'USD'
            }
        
        return insights
    
    def clear_cache(self):
        """Clear the salary data cache"""
        self._salary_cache.clear()
        print("Salary cache cleared") 