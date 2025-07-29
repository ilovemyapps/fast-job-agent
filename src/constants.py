#!/usr/bin/env python3
"""
Constants for Fast Job Agent
"""

from enum import Enum


class JobFields:
    """Standard field names for job data - use these to avoid typos"""
    ROLE_NAME = 'role_name'
    COMPANY_NAME = 'company_name'
    LOCATION = 'location'
    JOB_LINK = 'job_link'
    EMPLOYMENT_TYPE = 'employment_type'
    TEAM = 'team'
    PUBLISHED_DATE = 'published_date'
    COMPENSATION = 'compensation'
    SOURCE = 'source'
    JOB_ID = 'job_id'


class LogMessages:
    """Standard log message templates"""
    HTTP_ERROR = "HTTP {status} for {company}"
    EXTRACTION_ERROR = "Failed to extract data from {company}"
    FOUND_JOBS = "Found {count} jobs from {company}"
    FILTERED_JOBS = "Filtered {count} FDE related jobs from {company}"
    TIMEOUT_ERROR = "Timeout while scraping {company}"
    SCRAPER_ERROR = "Error scraping {company}: {error}"


class CompensationDefaults:
    """Default compensation values"""
    NOT_DISCLOSED = "Not disclosed"
    COMPETITIVE = "Competitive"
    UNKNOWN = "Unknown"


class EmploymentTypeDefaults:
    """Default employment type values"""
    FULL_TIME = "FullTime"
    PART_TIME = "PartTime"
    CONTRACT = "Contract"
    INTERNSHIP = "Internship"
    UNKNOWN = "Unknown"


class URLTemplates:
    """URL templates for different job boards"""
    ASHBY = "https://jobs.ashbyhq.com/{job_board_name}"
    ASHBY_JOB = "https://jobs.ashbyhq.com/{job_board_name}/{job_id}"
    LEVER_JOB = "https://jobs.lever.co/{lever_name}/{job_id}"
    GREENHOUSE_API = "https://boards-api.greenhouse.io/v1/boards/{board_name}/jobs"
    LEVER_API = "https://api.lever.co/v0/postings/{company_name}?mode=json"