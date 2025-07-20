#!/usr/bin/env python3
"""
Async Ashby HQ Job Scraper
Scrape Forward Deployed Engineer related positions using aiohttp
"""

import asyncio
import json
import re
import logging
import aiohttp
from typing import List, Dict, Optional
from base_scraper import AsyncBaseScraper
import config
from models import Job, JobSource
from utils import log_scraper_start, with_error_handling
from constants import URLTemplates, LogMessages, CompensationDefaults

logger = logging.getLogger(__name__)


class AsyncAshbyScraper(AsyncBaseScraper):
    def __init__(self, config_path: str = None):
        super().__init__(config_path or str(config.ASHBY_CONFIG))
        
    def _extract_job_data(self, html_content: str) -> Optional[Dict]:
        """Extract job data from HTML"""
        # Find window.__appData = {...} 
        pattern = r'window\.__appData\s*=\s*({.*?});'
        match = re.search(pattern, html_content, re.DOTALL)
        
        if not match:
            logger.error("window.__appData not found")
            return None
            
        try:
            # Parse JSON data
            app_data = json.loads(match.group(1))
            return app_data
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            return None
    
    @with_error_handling(default_return=[])
    async def scrape_company(self, session: aiohttp.ClientSession, company: Dict) -> List[Dict]:
        """Scrape jobs from a single company asynchronously"""
        log_scraper_start(company['name'], 'Ashby', logger)
        
        # Generate URL from job_board_name
        url = company.get('url') or URLTemplates.ASHBY.format(job_board_name=company['job_board_name'])
        
        async with session.get(url) as response:
            if response.status != 200:
                logger.error(LogMessages.HTTP_ERROR.format(status=response.status, company=company['name']))
                return []
            
            html_content = await response.text()
        
        # Extract data
        app_data = self._extract_job_data(html_content)
        if not app_data:
            logger.error(LogMessages.EXTRACTION_ERROR.format(company=company['name']))
            return []
        
        # Get job listings
        job_board = app_data.get('jobBoard', {}) if app_data else {}
        job_postings = job_board.get('jobPostings', []) if job_board else []
        logger.info(LogMessages.FOUND_JOBS.format(count=len(job_postings), company=company['name']))
        
        # Filter FDE related jobs
        fde_jobs = self._filter_fde_jobs(job_postings)
        logger.info(LogMessages.FILTERED_JOBS.format(count=len(fde_jobs), company=company['name']))
        
        # Format data
        formatted_jobs = []
        for job in fde_jobs:
            # Create base job dict
            formatted_job = self.create_job_dict(job, company, JobSource.ASHBY)
            
            # Override with Ashby-specific fields
            if company.get('is_vc_portfolio', False):
                formatted_job['company_name'] = job.get('departmentName', company['name'])
            
            formatted_job.update({
                'role_name': job.get('title', ''),
                'location': job.get('locationName', ''),
                'job_link': URLTemplates.ASHBY_JOB.format(job_board_name=company['job_board_name'], job_id=job.get('id', '')),
                'employment_type': job.get('employmentType', 'FullTime'),
                'team': job.get('teamName', ''),
                'published_date': job.get('publishedDate', ''),
                'compensation': job.get('compensationTierSummary', CompensationDefaults.NOT_DISCLOSED),
            })
            
            formatted_jobs.append(formatted_job)
        
        # Filter US-only jobs and collect statistics
        us_jobs, stats = self.filter_and_collect_stats(formatted_jobs, company['name'])
        return us_jobs


async def main():
    """Test the async Ashby scraper independently"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format=config.LOG_FORMAT
    )
    
    # Scrape Ashby jobs
    scraper = AsyncAshbyScraper()
    jobs = await scraper.scrape_all(max_concurrent=10)
    
    # Show results
    if jobs:
        print(f"\n✅ Async Ashby scraping completed! Found {len(jobs)} FDE related jobs")
        print("\nSample jobs:")
        for job in jobs[:5]:
            print(f"  • {job['role_name']} at {job['company_name']} ({job['location']})")
        if len(jobs) > 5:
            print(f"  ... and {len(jobs) - 5} more jobs")
    else:
        print("\n❌ No FDE related jobs found")


if __name__ == "__main__":
    asyncio.run(main())