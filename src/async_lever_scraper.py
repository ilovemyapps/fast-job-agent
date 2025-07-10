#!/usr/bin/env python3
"""
Async Lever Job Scraper
Scrape Forward Deployed Engineer related positions from Lever using aiohttp
"""

import asyncio
import json
import logging
import aiohttp
from datetime import datetime
from typing import List, Dict
from async_base_scraper import AsyncBaseScraper
from location_filter import is_us_location
import config

logger = logging.getLogger(__name__)


class AsyncLeverScraper(AsyncBaseScraper):
    def __init__(self, config_path: str = None):
        super().__init__(config_path or str(config.LEVER_CONFIG))
    
    async def scrape_company(self, session: aiohttp.ClientSession, company: Dict) -> List[Dict]:
        """Scrape jobs from a single company asynchronously"""
        logger.info(f"🔍 Starting async Lever scrape of {company['name']}...")
        
        try:
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
                # Extract location from categories
                categories = job.get('categories', {})
                location = categories.get('location', '')
                
                # Convert timestamp to date
                created_timestamp = job.get('createdAt', 0)
                if created_timestamp:
                    published_date = datetime.fromtimestamp(created_timestamp/1000).strftime('%Y-%m-%d')
                else:
                    published_date = ''
                
                formatted_job = {
                    'role_name': job.get('text', ''),
                    'company_name': company['name'],
                    'location': location,
                    'job_link': f"https://jobs.lever.co/{company['lever_name']}/{job.get('id', '')}",
                    'employment_type': categories.get('commitment', 'FullTime'),
                    'team': categories.get('team', ''),
                    'published_date': published_date,
                    'compensation': 'Not disclosed',  # Lever API doesn't include compensation
                    'job_id': job.get('id', ''),
                    'source': 'Lever'
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
    """Test the async Lever scraper"""
    import asyncio
    
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
    import asyncio
    asyncio.run(main())