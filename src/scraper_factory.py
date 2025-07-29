#!/usr/bin/env python3
"""
Simplified Scraper Factory for Fast Job Agent
"""

from typing import Dict, Type, List
from models import JobSource
from base_scraper import AsyncBaseScraper
from ashby_scraper import AsyncAshbyScraper
from greenhouse_scraper import AsyncGreenhouseScraper
from lever_scraper import AsyncLeverScraper
import config


# Registry of scraper classes and their configurations
SCRAPER_REGISTRY = {
    JobSource.ASHBY: {
        'class': AsyncAshbyScraper,
        'config': config.COMPANIES_CONFIG,
        'config_key': 'ashby'
    },
    JobSource.GREENHOUSE: {
        'class': AsyncGreenhouseScraper,
        'config': config.COMPANIES_CONFIG,
        'config_key': 'greenhouse'
    },
    JobSource.LEVER: {
        'class': AsyncLeverScraper,
        'config': config.COMPANIES_CONFIG,
        'config_key': 'lever'
    },
    # Future extensions can be added here:
    # JobSource.HACKERNEWS: {
    #     'class': AsyncHackerNewsScraper,
    #     'config': config.COMPANIES_CONFIG,
    #     'config_key': 'hackernews'
    # },
}


def create_scraper(source: JobSource, config_path: str = None) -> AsyncBaseScraper:
    """
    Create a scraper for the specified source
    
    Args:
        source: Job source (Ashby, Greenhouse, Lever)
        config_path: Optional custom config path
        
    Returns:
        Configured scraper instance
        
    Raises:
        ValueError: If source is not supported
    """
    if source not in SCRAPER_REGISTRY:
        available = list(SCRAPER_REGISTRY.keys())
        raise ValueError(f"Unsupported scraper source: {source}. Available: {available}")
    
    registry_entry = SCRAPER_REGISTRY[source]
    scraper_class = registry_entry['class']
    config_path = config_path or str(registry_entry['config'])
    config_key = registry_entry['config_key']
    
    return scraper_class(config_path, config_key)


def create_all_scrapers() -> List[AsyncBaseScraper]:
    """
    Create instances of all available scrapers
    
    Returns:
        List of all scraper instances
    """
    scrapers = []
    for source in SCRAPER_REGISTRY:
        try:
            scraper = create_scraper(source)
            scrapers.append(scraper)
        except Exception as e:
            print(f"Failed to create {source.value} scraper: {e}")
    return scrapers


def get_available_sources() -> List[JobSource]:
    """
    Get list of available scraper sources
    
    Returns:
        List of supported job sources
    """
    return list(SCRAPER_REGISTRY.keys())


def register_scraper(source: JobSource, scraper_class: Type[AsyncBaseScraper], config_path: str, config_key: str = None):
    """
    Register a new scraper type (for future extensions)
    
    Args:
        source: Job source enum
        scraper_class: Scraper class
        config_path: Path to config file
        config_key: Key in config file for this scraper's data
    """
    SCRAPER_REGISTRY[source] = {
        'class': scraper_class,
        'config': config_path,
        'config_key': config_key or source.value.lower()
    }


# Legacy class wrapper for backward compatibility
class ScraperFactory:
    """Legacy wrapper - use module-level functions instead"""
    
    @classmethod
    def create_scraper(cls, source: JobSource, config_path: str = None) -> AsyncBaseScraper:
        return create_scraper(source, config_path)
    
    @classmethod
    def create_all_scrapers(cls) -> List[AsyncBaseScraper]:
        return create_all_scrapers()
    
    @classmethod
    def get_available_sources(cls) -> List[JobSource]:
        return get_available_sources()