#!/usr/bin/env python3
"""
Notion API Sync Module
Sync job data to Notion database
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Set
from notion_client import Client
from dotenv import load_dotenv
import config

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class NotionSync:
    def __init__(self):
        self.notion_token = os.getenv('NOTION_API_TOKEN')
        self.database_id = os.getenv('NOTION_DATABASE_ID')
        
        if not self.notion_token or not self.database_id:
            raise ValueError("NOTION_API_TOKEN and NOTION_DATABASE_ID must be set in .env file")
        
        self.client = Client(auth=self.notion_token)
        
        # Initialize incremental sync
        self.sync_cache_file = config.DATA_DIR / "synced_jobs.json"
        self.synced_jobs = self._load_synced_jobs()
        
    def _create_job_page(self, job: Dict) -> Dict:
        """Create a new job page in Notion database"""
        properties = {
            "Role Name": {
                "title": [{"text": {"content": job.get('role_name', '')}}]
            },
            "Company": {
                "select": {"name": job.get('company_name', '')}
            },
            "Location": {
                "rich_text": [{"text": {"content": job.get('location', '')}}]
            },
            "Job Link": {
                "url": job.get('job_link', '')
            },
            "Employment Type": {
                "select": {"name": job.get('employment_type', '')}
            },
            "Team": {
                "rich_text": [{"text": {"content": job.get('team', '')}}]
            },
            "Compensation": {
                "rich_text": [{"text": {"content": job.get('compensation') or 'Not disclosed'}}]
            },
            "Scraped At": {
                "date": {"start": datetime.now().isoformat()}
            }
        }
        
        # Add published date if available
        if job.get('published_date'):
            try:
                # Try to parse the date (format: YYYY-MM-DD)
                pub_date = datetime.strptime(job['published_date'], '%Y-%m-%d')
                properties["Published Date"] = {
                    "date": {"start": pub_date.isoformat()}
                }
            except ValueError:
                # If parsing fails, store as text
                logger.warning(f"Could not parse published date: {job['published_date']}")
        
        return properties
    
    def _load_synced_jobs(self) -> Set[str]:
        """Load the set of already synced job IDs from cache file"""
        if not self.sync_cache_file.exists():
            return set()
        
        try:
            with open(self.sync_cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('synced_job_ids', []))
        except Exception as e:
            logger.warning(f"Failed to load sync cache: {e}")
            return set()
    
    def _save_synced_jobs(self) -> None:
        """Save the set of synced job IDs to cache file"""
        try:
            # Ensure directory exists
            self.sync_cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'synced_job_ids': list(self.synced_jobs),
                'last_sync': datetime.now().isoformat(),
                'total_synced': len(self.synced_jobs)
            }
            
            with open(self.sync_cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved {len(self.synced_jobs)} synced job IDs to cache")
            
        except Exception as e:
            logger.error(f"Failed to save sync cache: {e}")
    
    def _generate_job_id(self, job: Dict) -> str:
        """Generate a unique job ID from job data"""
        source = job.get('source', 'unknown')
        job_id = job.get('job_id', '')
        
        # If no job_id, use a combination of company + role + location as fallback
        if not job_id:
            company = job.get('company_name', '')
            role = job.get('role_name', '')
            location = job.get('location', '')
            job_id = f"{company}_{role}_{location}".replace(' ', '_').lower()
        
        return f"{source}_{job_id}"
    
    def _job_exists(self, job_link: str) -> Optional[str]:
        """Check if a job already exists in the database by job link"""
        try:
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Job Link",
                    "url": {"equals": job_link}
                }
            )
            
            if response['results']:
                return response['results'][0]['id']
            return None
            
        except Exception as e:
            logger.error(f"Error checking if job exists: {e}")
            return None
    
    def sync_jobs(self, jobs: List[Dict]) -> Dict:
        """Sync jobs to Notion database using incremental updates"""
        stats = {
            'total': len(jobs),
            'new': 0,
            'existing': 0,
            'cached_skip': 0,
            'errors': 0
        }
        
        # Filter out jobs that are already synced (from local cache)
        new_jobs = []
        for job in jobs:
            unique_job_id = self._generate_job_id(job)
            
            if unique_job_id in self.synced_jobs:
                stats['cached_skip'] += 1
                logger.debug(f"Skipping cached job: {job.get('role_name', '')} at {job.get('company_name', '')}")
            else:
                new_jobs.append(job)
        
        logger.info(f"📊 Sync Stats: {len(jobs)} total jobs, {len(new_jobs)} new jobs to check, {stats['cached_skip']} cached skips")
        
        # Process only new jobs
        for job in new_jobs:
            try:
                job_link = job.get('job_link', '')
                unique_job_id = self._generate_job_id(job)
                
                if not job_link:
                    logger.warning("Job has no link, skipping")
                    stats['errors'] += 1
                    continue
                
                # Double-check with Notion API (in case cache is outdated)
                existing_id = self._job_exists(job_link)
                
                if existing_id:
                    logger.info(f"Job already exists in Notion: {job.get('role_name', '')} at {job.get('company_name', '')}")
                    stats['existing'] += 1
                    # Add to cache to avoid future API calls
                    self.synced_jobs.add(unique_job_id)
                else:
                    # Create new job page
                    properties = self._create_job_page(job)
                    
                    self.client.pages.create(
                        parent={"database_id": self.database_id},
                        properties=properties
                    )
                    
                    logger.info(f"✅ Created new job: {job.get('role_name', '')} at {job.get('company_name', '')}")
                    stats['new'] += 1
                    
                    # Add to synced cache
                    self.synced_jobs.add(unique_job_id)
                    
            except Exception as e:
                logger.error(f"Error syncing job {job.get('role_name', '')}: {e}")
                stats['errors'] += 1
        
        # Save updated cache
        self._save_synced_jobs()
        
        # Log final stats
        logger.info(f"🎯 Sync completed: {stats['new']} new, {stats['existing']} existing, {stats['cached_skip']} cached, {stats['errors']} errors")
        
        return stats
    
    def cleanup_old_cache(self, days_threshold: int = 90) -> int:
        """
        Clean up job IDs that are older than threshold days from cache
        This prevents the cache from growing indefinitely with old job posts
        Returns number of items removed
        """
        if not self.sync_cache_file.exists():
            return 0
        
        try:
            with open(self.sync_cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            last_sync_str = data.get('last_sync', '')
            if not last_sync_str:
                return 0
            
            last_sync = datetime.fromisoformat(last_sync_str.replace('Z', '+00:00'))
            threshold_date = datetime.now() - timedelta(days=days_threshold)
            
            if last_sync < threshold_date:
                # Cache is old, clear it
                old_count = len(self.synced_jobs)
                self.synced_jobs.clear()
                self._save_synced_jobs()
                
                logger.info(f"🧹 Cleaned up old cache: removed {old_count} job IDs older than {days_threshold} days")
                return old_count
            
            return 0
            
        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics for monitoring"""
        stats = {
            'cached_jobs': len(self.synced_jobs),
            'cache_file_exists': self.sync_cache_file.exists()
        }
        
        if self.sync_cache_file.exists():
            try:
                with open(self.sync_cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                stats['last_sync'] = data.get('last_sync', 'Unknown')
                stats['total_synced'] = data.get('total_synced', 0)
            except Exception:
                pass
        
        return stats
    
    def test_connection(self) -> bool:
        """Test connection to Notion API"""
        try:
            # Try to retrieve database info
            response = self.client.databases.retrieve(database_id=self.database_id)
            logger.info(f"Connected to Notion database: {response.get('title', [{}])[0].get('text', {}).get('content', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Notion: {e}")
            return False


def main():
    """Test the Notion sync functionality"""
    try:
        notion = NotionSync()
        
        # Test connection
        if notion.test_connection():
            print("✅ Notion API connection successful!")
        else:
            print("❌ Notion API connection failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()