#!/usr/bin/env python3
"""
Async Greenhouse Job Scraper
Scrape Forward Deployed Engineer related positions from Greenhouse using aiohttp
"""

import asyncio
import json
import logging
import aiohttp
from typing import List, Dict
from base_scraper import AsyncBaseScraper
import config
from models import Job, JobSource
from utils import log_scraper_start, with_error_handling

logger = logging.getLogger(__name__)


class AsyncGreenhouseScraper(AsyncBaseScraper):
    def __init__(self, config_path: str = None):
        super().__init__(config_path or str(config.GREENHOUSE_CONFIG))
    
    @with_error_handling(default_return=[])
    async def scrape_company(self, session: aiohttp.ClientSession, company: Dict) -> List[Dict]:
        """Scrape jobs from a single company asynchronously"""
        log_scraper_start(company['name'], 'Greenhouse', logger)
        
        # Use Greenhouse API
        api_url = config.GREENHOUSE_API_URL.format(board_name=company['board_name'])
        
        async with session.get(api_url) as response:
            if response.status != 200:
                logger.error(f"HTTP {response.status} for {company['name']}")
                return []
            
            data = await response.json()
        
        all_jobs = data.get('jobs', [])
        logger.info(f"Found {len(all_jobs)} jobs from {company['name']}")
        
        # Filter FDE related jobs
        fde_jobs = self._filter_fde_jobs(all_jobs)
        logger.info(f"Filtered {len(fde_jobs)} FDE related jobs from {company['name']}")
        
        # Format data
        formatted_jobs = []
        for job in fde_jobs:
            # Create base job dict
            formatted_job = self.create_job_dict(job, company, JobSource.GREENHOUSE)
            
            # Extract department info
            departments = job.get('departments', [])
            department_name = departments[0].get('name', '') if departments else ''
            
            # Override with Greenhouse-specific fields
            formatted_job.update({
                'role_name': job.get('title', ''),
                'location': job.get('location', {}).get('name', ''),
                'job_link': job.get('absolute_url', ''),
                'team': department_name,
                'published_date': job.get('updated_at', '').split('T')[0] if job.get('updated_at') else '',
            })
            
            formatted_jobs.append(formatted_job)
        
        # Filter US-only jobs and collect statistics
        us_jobs, stats = self.filter_and_collect_stats(formatted_jobs, company['name'])
        return us_jobs


async def main():
    """Test the async Greenhouse scraper"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format=config.LOG_FORMAT
    )
    
    scraper = AsyncGreenhouseScraper()
    
    if not scraper.companies:
        print("No Greenhouse companies configured")
        return
    
    # Scrape all jobs
    jobs = await scraper.scrape_all(max_concurrent=8)
    
    if jobs:
        print(f"✅ Found {len(jobs)} async Greenhouse FDE jobs")
        for job in jobs[:5]:  # Show first 5
            print(f"  • {job['role_name']} at {job['company_name']} ({job['location']})")
    else:
        print("❌ No Greenhouse FDE jobs found")


if __name__ == "__main__":
    asyncio.run(main())