#!/usr/bin/env python3
"""
Data processor for deduplicating job results from multiple sources (pandas version)
"""

import csv
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import pandas as pd
from location_filter import is_us_location_sync

logger = logging.getLogger(__name__)


class JobDataProcessor:
    def __init__(self):
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def filter_us_locations(self, jobs: List[Dict]) -> List[Dict]:
        """
        Filter jobs to only include US-based positions using intelligent detection
        """
        if not jobs:
            return []
            
        us_jobs = []
        non_us_jobs = []
        
        for job in jobs:
            location = job.get('location', '')
            if is_us_location_sync(location):
                us_jobs.append(job)
            else:
                non_us_jobs.append(job)
                logger.debug(f"Filtered out job at location: {location}")
        
        # Log detailed statistics
        total_jobs = len(jobs)
        us_count = len(us_jobs)
        non_us_count = len(non_us_jobs)
        
        logger.info(f"📊 Location Filtering Statistics:")
        logger.info(f"  Total jobs: {total_jobs}")
        logger.info(f"  US jobs: {us_count}")
        logger.info(f"  Non-US jobs: {non_us_count}")
        
        if non_us_jobs:
            non_us_locations = [job.get('location', 'Unknown') for job in non_us_jobs]
            logger.info(f"  Non-US locations: {', '.join(non_us_locations)}")
            
        return us_jobs
    
    def filter_recent_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Filter jobs to only include those published within the last year
        """
        if not jobs:
            return []
            
        one_year_ago = datetime.now() - timedelta(days=365)
        recent_jobs = []
        old_jobs = []
        
        for job in jobs:
            published_date_str = job.get('published_date', '')
            
            # Skip jobs without published date (keep them to be safe)
            if not published_date_str or not published_date_str.strip():
                recent_jobs.append(job)
                continue
            
            try:
                # Try to parse different date formats
                published_date = None
                
                # Common formats to try
                date_formats = [
                    '%Y-%m-%d',           # 2025-07-10
                    '%Y-%m-%dT%H:%M:%S',  # 2025-07-10T15:30:00
                    '%Y-%m-%d %H:%M:%S',  # 2025-07-10 15:30:00
                    '%m/%d/%Y',           # 07/10/2025
                    '%d/%m/%Y',           # 10/07/2025
                ]
                
                for fmt in date_formats:
                    try:
                        published_date = datetime.strptime(published_date_str.split('T')[0], fmt)
                        break
                    except ValueError:
                        continue
                
                if published_date:
                    if published_date >= one_year_ago:
                        recent_jobs.append(job)
                    else:
                        old_jobs.append(job)
                else:
                    # If we can't parse the date, keep the job to be safe
                    recent_jobs.append(job)
                    logger.debug(f"Could not parse date '{published_date_str}', keeping job")
                    
            except Exception as e:
                # If any error, keep the job to be safe
                recent_jobs.append(job)
                logger.debug(f"Error parsing date '{published_date_str}': {e}, keeping job")
        
        # Log statistics
        total_jobs = len(jobs)
        recent_count = len(recent_jobs)
        old_count = len(old_jobs)
        
        logger.info(f"📅 Date Filtering Statistics:")
        logger.info(f"  Total jobs: {total_jobs}")
        logger.info(f"  Recent jobs (< 1 year): {recent_count}")
        logger.info(f"  Old jobs (> 1 year): {old_count}")
        
        if old_jobs:
            old_job_details = [f"{job.get('role_name', 'Unknown')} at {job.get('company_name', 'Unknown')} ({job.get('published_date', 'No date')})" for job in old_jobs]
            logger.info(f"  Filtered old jobs: {'; '.join(old_job_details)}")
            
        return recent_jobs
        
    def deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Smart deduplication with location consolidation:
        1. Same company + role name + location: remove exact duplicates
        2. Same company + role name but different locations: merge locations, keep one job
        """
        if not jobs:
            return []
        
        # Create DataFrame for easier processing
        df = pd.DataFrame(jobs)
        
        # Step 1: Remove exact duplicates (same company + role + location)
        df['exact_dedup_key'] = df['company_name'].str.lower() + '|' + df['role_name'].str.lower() + '|' + df['location'].str.lower()
        df = df.drop_duplicates(subset=['exact_dedup_key'], keep='first')
        df = df.drop('exact_dedup_key', axis=1)
        
        # Step 2: Group by company + role name for location consolidation
        role_dedup_key = df['company_name'].str.lower() + '|' + df['role_name'].str.lower()
        df['role_dedup_key'] = role_dedup_key
        
        # Group jobs by company + role
        grouped = df.groupby('role_dedup_key')
        consolidated_jobs = []
        
        total_before = len(df)
        location_consolidations = 0
        
        for group_key, group_df in grouped:
            if len(group_df) == 1:
                # Single job, no consolidation needed
                job_dict = group_df.iloc[0].to_dict()
                if 'role_dedup_key' in job_dict:
                    del job_dict['role_dedup_key']
                consolidated_jobs.append(job_dict)
            else:
                # Multiple jobs with same company + role, consolidate locations
                location_consolidations += len(group_df) - 1
                
                # Sort by location to have consistent selection
                group_df_sorted = group_df.sort_values('location')
                
                # Use the first job as base (after sorting by location)
                base_job = group_df_sorted.iloc[0].to_dict()
                
                # Collect all unique locations
                all_locations = []
                all_links = []
                for _, row in group_df_sorted.iterrows():
                    location = row['location'].strip()
                    if location and location not in all_locations:
                        all_locations.append(location)
                    
                    link = row.get('job_link', '').strip()
                    if link and link not in all_links:
                        all_links.append(link)
                
                # Consolidate locations with semicolon separator
                base_job['location'] = '; '.join(all_locations)
                
                # Use the first job link (from sorted order)
                if all_links:
                    base_job['job_link'] = all_links[0]
                
                # Clean up temporary key
                if 'role_dedup_key' in base_job:
                    del base_job['role_dedup_key']
                
                consolidated_jobs.append(base_job)
                
                # Log the consolidation
                company = base_job.get('company_name', 'Unknown')
                role = base_job.get('role_name', 'Unknown')
                logger.info(f"🔄 Consolidated {len(group_df)} jobs for {company} - {role} into locations: {base_job['location']}")
        
        total_after = len(consolidated_jobs)
        
        if location_consolidations > 0:
            logger.info(f"✅ Location consolidation: {location_consolidations} duplicate roles merged ({total_before} -> {total_after} jobs)")
        else:
            logger.info(f"No location consolidations needed ({total_before} jobs)")
            
        return consolidated_jobs
    def merge_and_deduplicate(self, ashby_jobs: List[Dict], greenhouse_jobs: List[Dict], lever_jobs: List[Dict] = None) -> List[Dict]:
        """
        Merge jobs from multiple sources, filter non-US locations, filter old jobs, and remove duplicates
        """
        if lever_jobs is None:
            lever_jobs = []
            
        logger.info(f"Merging {len(ashby_jobs)} Ashby jobs, {len(greenhouse_jobs)} Greenhouse jobs, and {len(lever_jobs)} Lever jobs")
        
        # Combine all jobs
        all_jobs = ashby_jobs + greenhouse_jobs + lever_jobs
        
        # Filter out non-US locations first
        us_jobs = self.filter_us_locations(all_jobs)
        
        # Filter out old jobs (> 1 year)
        recent_jobs = self.filter_recent_jobs(us_jobs)
        
        # Deduplicate
        deduplicated_jobs = self.deduplicate_jobs(recent_jobs)
        
        logger.info(f"Final result: {len(deduplicated_jobs)} unique recent US jobs")
        
        return deduplicated_jobs
    
    def save_to_csv(self, jobs: List[Dict], filename: str = None) -> str:
        """
        Save jobs to CSV file
        """
        if not jobs:
            logger.warning("No jobs to save")
            return ""
            
        if filename is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            filename = f"fde_jobs_{timestamp}.csv"
            
        filepath = self.output_dir / filename
        
        # Define column order
        columns = [
            'role_name', 'company_name', 'location', 'job_link', 
            'employment_type', 'team', 'published_date', 'compensation', 
            'source', 'job_id'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            
            for job in jobs:
                # Ensure all required fields exist
                row = {col: job.get(col, '') for col in columns}
                writer.writerow(row)
        
        logger.info(f"Saved {len(jobs)} jobs to {filepath}")
        return str(filepath)


def main():
    """Test the data processor"""
    processor = JobDataProcessor()
    
    # Test with sample data including non-US locations
    ashby_jobs = [
        {
            'role_name': 'Forward Deployed Engineer',
            'company_name': 'TestCorp',
            'location': 'San Francisco',
            'job_link': 'https://example.com/job1',
            'employment_type': 'FullTime',
            'team': 'Engineering',
            'published_date': '2025-07-08',
            'compensation': '$150K-$200K',
            'source': 'Ashby',
            'job_id': 'ashby_123'
        },
        {
            'role_name': 'Software Engineer',
            'company_name': 'GlobalTech',
            'location': 'London, UK',
            'job_link': 'https://example.com/job3',
            'employment_type': 'FullTime',
            'team': 'Engineering',
            'published_date': '2025-07-08',
            'compensation': '£80K-£120K',
            'source': 'Ashby',
            'job_id': 'ashby_124'
        }
    ]
    
    greenhouse_jobs = [
        {
            'role_name': 'Forward Deployed Engineer',
            'company_name': 'TestCorp',
            'location': 'San Francisco',
            'job_link': 'https://example.com/job2',
            'employment_type': 'FullTime',
            'team': 'Engineering',
            'published_date': '2025-07-08',
            'compensation': '$150K-$200K',
            'source': 'Greenhouse',
            'job_id': 'greenhouse_456'
        },
        {
            'role_name': 'Data Scientist',
            'company_name': 'TechBrasil',
            'location': 'São Paulo, Brazil',
            'job_link': 'https://example.com/job4',
            'employment_type': 'FullTime',
            'team': 'Data',
            'published_date': '2025-07-08',
            'compensation': 'R$200K-R$300K',
            'source': 'Greenhouse',
            'job_id': 'greenhouse_457'
        },
        {
            'role_name': 'Product Manager',
            'company_name': 'KoreaInc',
            'location': 'Seoul, South Korea',
            'job_link': 'https://example.com/job5',
            'employment_type': 'FullTime',
            'team': 'Product',
            'published_date': '2025-07-08',
            'compensation': '₩50M-₩70M',
            'source': 'Greenhouse',
            'job_id': 'greenhouse_458'
        }
    ]
    
    # Test deduplication and location filtering
    result = processor.merge_and_deduplicate(ashby_jobs, greenhouse_jobs)
    print(f"Result: {len(result)} US jobs after filtering and deduplication")
    for job in result:
        print(f"  - {job['role_name']} at {job['company_name']} in {job['location']} ({job['source']})")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()