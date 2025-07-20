#!/usr/bin/env python3
"""
Async Base Scraper Class
Common functionality for all async job scrapers using aiohttp
"""

import asyncio
import aiohttp
import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Tuple
import yaml
import config
from location_filter import is_us_location
from models import Job, JobStats, JobSource
from utils import log_job_statistics, log_scraper_start, with_error_handling
from utils.logging_utils import EMOJI_SUCCESS, EMOJI_ERROR

logger = logging.getLogger(__name__)


class AsyncBaseScraper(ABC):
    """Async base class for all job scrapers"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.companies = self._load_companies()
        
    def _load_companies(self) -> List[Dict]:
        """Load company configuration"""
        config_file = Path(self.config_path)
        if not config_file.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            return []
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config.get('companies', [])
    
    def _filter_fde_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Filter Forward Deployed Engineer related positions"""
        fde_keywords = config.FDE_KEYWORDS
        
        filtered_jobs = []
        for job in jobs:
            # Get title field - different scrapers use different field names
            title = job.get('title', '') or job.get('text', '') or job.get('role_name', '')
            title_lower = title.lower()
            
            # Check if job title contains keywords
            if any(keyword in title_lower for keyword in fde_keywords):
                filtered_jobs.append(job)
                
        return filtered_jobs
    
    def filter_and_collect_stats(self, jobs: List[Dict], company_name: str) -> Tuple[List[Dict], JobStats]:
        """
        Filter US jobs and collect statistics
        
        Args:
            jobs: List of job dictionaries
            company_name: Name of the company for logging
            
        Returns:
            Tuple of (us_jobs, stats)
        """
        stats = JobStats()
        us_jobs = []
        
        for job in jobs:
            location = job.get('location', '')
            if is_us_location(location):
                us_jobs.append(job)
                stats.add_us_job()
            else:
                stats.add_non_us_job(location)
        
        # Log statistics
        log_job_statistics(company_name, stats, logger)
        
        return us_jobs, stats
    
    def create_job_dict(self, raw_job: Dict, company: Dict, source: JobSource) -> Dict:
        """
        Create standardized job dictionary from raw job data
        
        Args:
            raw_job: Raw job data from API
            company: Company configuration
            source: Job source (Ashby, Greenhouse, Lever)
            
        Returns:
            Standardized job dictionary
        """
        # Default field mapping - subclasses can override
        return {
            'role_name': raw_job.get('title', raw_job.get('text', '')),
            'company_name': company['name'],
            'location': raw_job.get('location', ''),
            'job_link': '',  # Subclasses must set this
            'employment_type': 'FullTime',
            'team': '',
            'published_date': '',
            'compensation': 'Not disclosed',
            'source': source.value,
            'job_id': str(raw_job.get('id', ''))
        }
    
    @abstractmethod
    async def scrape_company(self, session: aiohttp.ClientSession, company: Dict) -> List[Dict]:
        """Scrape jobs from a single company - must be implemented by subclasses"""
        pass
    
    async def scrape_all(self, max_concurrent: int = 5) -> List[Dict]:
        """Scrape jobs from all companies concurrently"""
        if not self.companies:
            logger.warning("No companies configured")
            return []
        
        connector = aiohttp.TCPConnector(limit=20, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        ) as session:
            # Create semaphore to limit concurrent requests
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def scrape_with_semaphore(company):
                async with semaphore:
                    try:
                        return await self.scrape_company(session, company)
                    except Exception as e:
                        logger.error(f"Failed to scrape {company.get('name', 'Unknown')}: {e}")
                        return []
            
            # Create tasks for all companies
            tasks = [scrape_with_semaphore(company) for company in self.companies]
            
            # Run all tasks concurrently
            logger.info(f"🚀 Starting async scraping of {len(tasks)} companies with max {max_concurrent} concurrent requests")
            start_time = time.time()
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            logger.info(f"⚡ Async scraping completed in {end_time - start_time:.2f} seconds")
            
            # Flatten results and filter out exceptions
            all_jobs = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Task failed with exception: {result}")
                elif isinstance(result, list):
                    all_jobs.extend(result)
            
            return all_jobs