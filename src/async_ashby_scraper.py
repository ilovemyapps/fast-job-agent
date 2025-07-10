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
from async_base_scraper import AsyncBaseScraper
from location_filter import is_us_location
import config

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
    
    async def scrape_company(self, session: aiohttp.ClientSession, company: Dict) -> List[Dict]:
        """Scrape jobs from a single company asynchronously"""
        logger.info(f"🔍 Starting async scrape of {company['name']}...")
        
        try:
            async with session.get(company['url']) as response:
                if response.status != 200:
                    logger.error(f"HTTP {response.status} for {company['name']}")
                    return []
                
                html_content = await response.text()
            
            # Extract data
            app_data = self._extract_job_data(html_content)
            if not app_data:
                logger.error(f"Failed to extract data from {company['name']}")
                return []
            
            # Get job listings
            job_board = app_data.get('jobBoard', {}) if app_data else {}
            job_postings = job_board.get('jobPostings', []) if job_board else []
            logger.info(f"Found {len(job_postings)} jobs from {company['name']}")
            
            # Filter FDE related jobs
            fde_jobs = self._filter_fde_jobs(job_postings)
            logger.info(f"Filtered {len(fde_jobs)} FDE related jobs from {company['name']}")
            
            # Format data
            formatted_jobs = []
            for job in fde_jobs:
                # For VC portfolio, use departmentName as company name
                if company.get('is_vc_portfolio', False):
                    company_name = job.get('departmentName', company['name'])
                else:
                    company_name = company['name']
                
                formatted_job = {
                    'role_name': job.get('title', ''),
                    'company_name': company_name,
                    'location': job.get('locationName', ''),
                    'job_link': f"https://jobs.ashbyhq.com/{company['job_board_name']}/{job.get('id', '')}",
                    'employment_type': job.get('employmentType', ''),
                    'team': job.get('teamName', ''),
                    'published_date': job.get('publishedDate', ''),
                    'compensation': job.get('compensationTierSummary', 'Not disclosed'),
                    'source': 'Ashby',
                    'job_id': job.get('id', '')
                }
                formatted_jobs.append(formatted_job)
            
            # Filter US-only jobs and collect statistics
            us_jobs = []
            non_us_jobs = []
            
            for job in formatted_jobs:
                location = job.get('location', '')
                if is_us_location(location):
                    us_jobs.append(job)
                else:
                    non_us_jobs.append(job)
            
            # Log detailed statistics
            total_jobs = len(formatted_jobs)
            us_count = len(us_jobs)
            non_us_count = len(non_us_jobs)
            
            logger.info(f"📊 {company['name']} Statistics:")
            logger.info(f"  Total jobs scraped: {total_jobs}")
            logger.info(f"  US jobs: {us_count}")
            logger.info(f"  Non-US jobs: {non_us_count}")
            
            if non_us_jobs:
                non_us_locations = [job.get('location', 'Unknown') for job in non_us_jobs]
                logger.info(f"  Non-US locations: {', '.join(non_us_locations)}")
                
            return us_jobs
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout while scraping {company['name']}")
            return []
        except Exception as e:
            logger.error(f"Error scraping {company['name']}: {e}")
            return []


async def main():
    """Test the async Ashby scraper independently"""
    import asyncio
    
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
    import asyncio
    asyncio.run(main())