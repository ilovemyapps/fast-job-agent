#!/usr/bin/env python3
"""
Async Job aggregator that runs all scrapers concurrently and processes results
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from scraper_factory import create_scraper
from models import JobSource
from data_processor_pandas import JobDataProcessor
from notion_sync import NotionSync

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/run.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


async def run_all_scrapers_async():
    """Run all scrapers concurrently for maximum performance"""
    
    # Initialize async scrapers using factory
    ashby_scraper = create_scraper(JobSource.ASHBY)
    greenhouse_scraper = create_scraper(JobSource.GREENHOUSE)
    lever_scraper = create_scraper(JobSource.LEVER)
    
    logger.info("🚀 Starting async scraping of all platforms...")
    start_time = time.time()
    
    # Run all scrapers concurrently
    tasks = [
        ashby_scraper.scrape_all(max_concurrent=10),
        greenhouse_scraper.scrape_all(max_concurrent=8),
        lever_scraper.scrape_all(max_concurrent=8)
    ]
    
    # Wait for all scrapers to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = time.time()
    logger.info(f"⚡ All async scraping completed in {end_time - start_time:.2f} seconds")
    
    # Extract results
    ashby_jobs = results[0] if not isinstance(results[0], Exception) else []
    greenhouse_jobs = results[1] if not isinstance(results[1], Exception) else []
    lever_jobs = results[2] if not isinstance(results[2], Exception) else []
    
    # Log any exceptions
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            scraper_names = ['Ashby', 'Greenhouse', 'Lever']
            logger.error(f"{scraper_names[i]} scraper failed: {result}")
    
    logger.info(f"📊 Scraping results: {len(ashby_jobs)} Ashby, {len(greenhouse_jobs)} Greenhouse, {len(lever_jobs)} Lever jobs")
    
    return ashby_jobs, greenhouse_jobs, lever_jobs


async def main():
    """Main async function"""
    try:
        logger.info("🚀 Starting async job aggregation process")
        
        # Run all scrapers concurrently
        ashby_jobs, greenhouse_jobs, lever_jobs = await run_all_scrapers_async()
        
        # Process and deduplicate (this is still sync since pandas is sync)
        logger.info("📊 Processing and deduplicating results...")
        processor = JobDataProcessor()
        final_jobs = processor.merge_and_deduplicate(ashby_jobs, greenhouse_jobs, lever_jobs)
        
        # Save to CSV
        csv_path = processor.save_to_csv(final_jobs)
        
        # Sync to Notion if available
        try:
            notion_sync = NotionSync()
            
            # Periodic cache cleanup (every 30 days)
            notion_sync.cleanup_old_cache(days_threshold=30)
            
            # Log cache stats
            cache_stats = notion_sync.get_cache_stats()
            logger.info(f"📊 Notion cache stats: {cache_stats}")
            
            # Sync jobs
            sync_stats = notion_sync.sync_jobs(final_jobs)
            logger.info(f"✅ Notion sync completed: {sync_stats}")
            
        except Exception as e:
            logger.warning(f"Notion sync failed: {e}")
        
        logger.info(f"🎯 Async job aggregation completed successfully. Results saved to {csv_path}")
        
    except Exception as e:
        logger.error(f"❌ Async job aggregation failed: {e}")
        sys.exit(1)


def sync_main():
    """Synchronous entry point for compatibility"""
    asyncio.run(main())


if __name__ == "__main__":
    sync_main()