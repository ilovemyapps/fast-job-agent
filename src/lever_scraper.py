#!/usr/bin/env python3
"""
Async Lever Job Scraper
Scrape Forward Deployed Engineer related positions from Lever using aiohttp
"""

import asyncio
import json
import logging
import aiohttp
from typing import List, Dict
from base_scraper import AsyncBaseScraper
import config
from models import Job, JobSource
from utils import log_scraper_start, with_error_handling, timestamp_to_date

logger = logging.getLogger(__name__)


class AsyncLeverScraper(AsyncBaseScraper):
    def __init__(self, config_path: str = None):
        super().__init__(config_path or str(config.LEVER_CONFIG))
    
    @with_error_handling(default_return=[])
    async def scrape_company(self, session: aiohttp.ClientSession, company: Dict) -> List[Dict]:
        """Scrape jobs from a single company asynchronously"""
        log_scraper_start(company['name'], 'Lever', logger)
            # Use Lever API
            api_url = config.LEVER_API_URL.format(company_name=company['lever_name'])
            
            async with session.get(api_url) as response:
                if response.status != 200:
                    logger.error(f"HTTP {response.status} for {company['name']}")
                    return []
                
                all_jobs = await response.json()
            
            logger.info(f"Found {len(all_jobs)} jobs from {company['name']}")
            
            # Filter FDE related jobs
            fde_jobs = self._filter_fde_jobs(all_jobs)
            logger.info(f"Filtered {len(fde_jobs)} FDE related jobs from {company['name']}")
            
            # Format data
            formatted_jobs = []
            for job in fde_jobs:
                # Create base job dict
                formatted_job = self.create_job_dict(job, company, JobSource.LEVER)
                
                # Extract location and other data from categories
                categories = job.get('categories', {})
                location = categories.get('location', '')
                
                # Convert timestamp to date
                created_timestamp = job.get('createdAt', 0)
                published_date = timestamp_to_date(created_timestamp) if created_timestamp else ''
                
                # Override with Lever-specific fields
                formatted_job.update({
                    'role_name': job.get('text', ''),
                    'location': location,
                    'job_link': f"https://jobs.lever.co/{company['lever_name']}/{job.get('id', '')}",
                    'employment_type': categories.get('commitment', 'FullTime'),
                    'team': categories.get('team', ''),
                    'published_date': published_date,
                })
                
                formatted_jobs.append(formatted_job)
            
            # Filter US-only jobs and collect statistics
            us_jobs, stats = self.filter_and_collect_stats(formatted_jobs, company['name'])
            return us_jobs


async def main():
    """Test the async Lever scraper"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format=config.LOG_FORMAT
    )
    
    scraper = AsyncLeverScraper()
    
    if not scraper.companies:
        print("No Lever companies configured")
        return
    
    # Scrape all jobs
    jobs = await scraper.scrape_all(max_concurrent=8)
    
    if jobs:
        print(f"✅ Found {len(jobs)} async Lever FDE jobs")
        for job in jobs[:5]:  # Show first 5
            print(f"  • {job['role_name']} at {job['company_name']} ({job['location']})")
    else:
        print("❌ No Lever FDE jobs found")


if __name__ == "__main__":
    asyncio.run(main())