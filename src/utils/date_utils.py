#!/usr/bin/env python3
"""
Date utility functions
"""

from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string in various formats
    
    Args:
        date_str: Date string to parse
        
    Returns:
        datetime object or None if parsing fails
    """
    if not date_str or not date_str.strip():
        return None
    
    # Common date formats to try
    date_formats = [
        '%Y-%m-%d',           # 2025-07-10
        '%Y-%m-%dT%H:%M:%S',  # 2025-07-10T15:30:00
        '%Y-%m-%d %H:%M:%S',  # 2025-07-10 15:30:00
        '%m/%d/%Y',           # 07/10/2025
        '%d/%m/%Y',           # 10/07/2025
        '%Y-%m-%dT%H:%M:%SZ', # ISO format with Z
        '%Y-%m-%dT%H:%M:%S.%fZ', # ISO format with milliseconds
    ]
    
    # Clean the date string (remove timezone info after parsing)
    clean_date_str = date_str.split('T')[0] if 'T' in date_str else date_str
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            try:
                # Try with just the date part
                return datetime.strptime(clean_date_str, fmt.split('T')[0].split(' ')[0])
            except ValueError:
                continue
    
    logger.debug(f"Could not parse date: {date_str}")
    return None


def timestamp_to_date(timestamp: int, divisor: int = 1000) -> str:
    """
    Convert timestamp to date string
    
    Args:
        timestamp: Unix timestamp
        divisor: Divisor for timestamp (1000 for milliseconds, 1 for seconds)
        
    Returns:
        Date string in YYYY-MM-DD format
    """
    try:
        return datetime.fromtimestamp(timestamp / divisor).strftime('%Y-%m-%d')
    except (ValueError, OSError, TypeError):
        logger.debug(f"Could not convert timestamp: {timestamp}")
        return ""


def is_recent_job(date_str: str, days: int = 365) -> bool:
    """
    Check if job is recent (within specified days)
    
    Args:
        date_str: Date string to check
        days: Number of days to consider as recent
        
    Returns:
        True if job is recent, False otherwise
    """
    parsed_date = parse_date(date_str)
    if not parsed_date:
        # If no date, consider it recent to be safe
        return True
    
    cutoff_date = datetime.now() - timedelta(days=days)
    return parsed_date >= cutoff_date