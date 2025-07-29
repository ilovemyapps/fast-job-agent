#!/usr/bin/env python3
"""
Data models for Fast Job Agent
"""

from dataclasses import dataclass, field
from typing import List, TypedDict
from enum import Enum


class JobSource(Enum):
    """Enum for job sources"""
    ASHBY = "Ashby"
    GREENHOUSE = "Greenhouse"
    LEVER = "Lever"


class JobDict(TypedDict):
    """Type definition for job dictionary"""
    role_name: str
    company_name: str
    location: str
    job_link: str
    employment_type: str
    team: str
    published_date: str
    compensation: str
    source: str
    job_id: str


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