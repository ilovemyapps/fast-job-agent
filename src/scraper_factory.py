#!/usr/bin/env python3
"""
Scraper Factory for Fast Job Agent
"""

from typing import Dict, Type, List
from models import JobSource, ScraperConfig
from base_scraper import AsyncBaseScraper
from ashby_scraper import AsyncAshbyScraper
from greenhouse_scraper import AsyncGreenhouseScraper
from lever_scraper import AsyncLeverScraper
import config


class ScraperFactory:
    """Factory for creating scrapers"""
    
    # Registry of scraper classes
    _scrapers: Dict[JobSource, Type[AsyncBaseScraper]] = {
        JobSource.ASHBY: AsyncAshbyScraper,
        JobSource.GREENHOUSE: AsyncGreenhouseScraper,
        JobSource.LEVER: AsyncLeverScraper,
    }
    
    # Default configurations
    _configs: Dict[JobSource, ScraperConfig] = {
        JobSource.ASHBY: ScraperConfig(
            name="Ashby",
            config_path=str(config.ASHBY_CONFIG),
            source=JobSource.ASHBY
        ),
        JobSource.GREENHOUSE: ScraperConfig(
            name="Greenhouse",
            config_path=str(config.GREENHOUSE_CONFIG),
            source=JobSource.GREENHOUSE,
            api_url_template=config.GREENHOUSE_API_URL
        ),
        JobSource.LEVER: ScraperConfig(
            name="Lever",
            config_path=str(config.LEVER_CONFIG),
            source=JobSource.LEVER,
            api_url_template=config.LEVER_API_URL
        ),
    }
    
    @classmethod
    def create_scraper(cls, source: JobSource, config_path: str = None) -> AsyncBaseScraper:
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
        if source not in cls._scrapers:
            raise ValueError(f"Unsupported scraper source: {source}")
        
        scraper_class = cls._scrapers[source]
        config_path = config_path or cls._configs[source].config_path
        
        return scraper_class(config_path)
    
    @classmethod
    def create_all_scrapers(cls) -> List[AsyncBaseScraper]:
        """
        Create instances of all available scrapers
        
        Returns:
            List of all scraper instances
        """
        scrapers = []
        for source in cls._scrapers:
            try:
                scraper = cls.create_scraper(source)
                scrapers.append(scraper)
            except Exception as e:
                print(f"Failed to create {source.value} scraper: {e}")
        return scrapers
    
    @classmethod
    def get_available_sources(cls) -> List[JobSource]:
        """
        Get list of available scraper sources
        
        Returns:
            List of supported job sources
        """
        return list(cls._scrapers.keys())
    
    @classmethod
    def register_scraper(cls, source: JobSource, scraper_class: Type[AsyncBaseScraper]):
        """
        Register a new scraper type
        
        Args:
            source: Job source
            scraper_class: Scraper class to register
        """
        cls._scrapers[source] = scraper_class