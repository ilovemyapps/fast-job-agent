#!/usr/bin/env python3
"""
Logging utility functions
"""

import logging
from typing import List, Dict
from pathlib import Path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from models import JobStats
import config


# Emoji constants
EMOJI_SEARCH = "🔍"
EMOJI_STATS = "📊"
EMOJI_SUCCESS = "✅"
EMOJI_ERROR = "❌"
EMOJI_WARNING = "⚠️"


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Setup logger with consistent formatting
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(config.LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    
    # File handler
    file_handler = logging.FileHandler(config.LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(config.LOG_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


def log_job_statistics(company_name: str, stats: JobStats, logger: logging.Logger) -> None:
    """
    Log job statistics in a consistent format
    
    Args:
        company_name: Name of the company
        stats: JobStats object with statistics
        logger: Logger instance to use
    """
    logger.info(f"{EMOJI_STATS} {company_name} Statistics:")
    logger.info(f"  Total jobs scraped: {stats.total_jobs}")
    logger.info(f"  US jobs: {stats.us_jobs}")
    logger.info(f"  Non-US jobs: {stats.non_us_jobs}")
    
    if stats.non_us_locations:
        logger.info(f"  Non-US locations: {', '.join(stats.non_us_locations)}")


def log_scraper_start(company_name: str, scraper_type: str, logger: logging.Logger) -> None:
    """
    Log scraper start in a consistent format
    
    Args:
        company_name: Name of the company
        scraper_type: Type of scraper (Ashby, Greenhouse, etc.)
        logger: Logger instance to use
    """
    logger.info(f"{EMOJI_SEARCH} Starting async {scraper_type} scrape of {company_name}...")


def log_scraper_summary(total_jobs: int, source: str, logger: logging.Logger) -> None:
    """
    Log scraper summary
    
    Args:
        total_jobs: Total number of jobs found
        source: Source of jobs
        logger: Logger instance to use
    """
    if total_jobs > 0:
        logger.info(f"{EMOJI_SUCCESS} Found {total_jobs} {source} FDE jobs")
    else:
        logger.info(f"{EMOJI_ERROR} No {source} FDE jobs found")