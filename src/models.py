#!/usr/bin/env python3
"""
Data models for Fast Job Agent
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class JobSource(Enum):
    """Enum for job sources"""
    ASHBY = "Ashby"
    GREENHOUSE = "Greenhouse"
    LEVER = "Lever"


class EmploymentType(Enum):
    """Enum for employment types"""
    FULLTIME = "FullTime"
    PARTTIME = "PartTime"
    CONTRACT = "Contract"
    INTERNSHIP = "Internship"
    UNKNOWN = "Unknown"


@dataclass
class Job:
    """Standard job data model"""
    role_name: str
    company_name: str
    location: str
    job_link: str
    source: JobSource
    job_id: str
    employment_type: str = "FullTime"
    team: str = ""
    published_date: str = ""
    compensation: str = "Not disclosed"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for CSV export"""
        return {
            'role_name': self.role_name,
            'company_name': self.company_name,
            'location': self.location,
            'job_link': self.job_link,
            'employment_type': self.employment_type,
            'team': self.team,
            'published_date': self.published_date,
            'compensation': self.compensation,
            'source': self.source.value,
            'job_id': self.job_id
        }
    
    def get_unique_id(self) -> str:
        """Generate unique identifier for deduplication"""
        return f"{self.source.value}_{self.job_id}"


@dataclass
class JobStats:
    """Statistics for job filtering"""
    total_jobs: int = 0
    us_jobs: int = 0
    non_us_jobs: int = 0
    non_us_locations: List[str] = field(default_factory=list)
    
    def add_us_job(self):
        """Increment US job count"""
        self.us_jobs += 1
        self.total_jobs += 1
    
    def add_non_us_job(self, location: str):
        """Increment non-US job count and track location"""
        self.non_us_jobs += 1
        self.total_jobs += 1
        if location:
            self.non_us_locations.append(location)


