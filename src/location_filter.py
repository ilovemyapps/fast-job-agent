#!/usr/bin/env python3
"""
Smart Location Filter
Intelligent US location detection with multiple fallback strategies
"""

import re
import logging
from typing import Optional, Dict, Any
import requests

logger = logging.getLogger(__name__)


class LocationFilter:
    """Smart location filter with multiple detection strategies"""
    
    def __init__(self):
        # Cache for API results
        self._cache: Dict[str, bool] = {}
        
        # High-confidence patterns
        self.us_patterns = [
            r'\b(remote|us\s*-?\s*remote)\b',
            r'\b\w+,\s*(al|ak|az|ar|ca|co|ct|de|fl|ga|hi|id|il|in|ia|ks|ky|la|me|md|ma|mi|mn|ms|mo|mt|ne|nv|nh|nj|nm|ny|nc|nd|oh|ok|or|pa|ri|sc|sd|tn|tx|ut|vt|va|wa|wv|wi|wy)\b',
            r'\b(new york|san francisco|los angeles|chicago|boston|seattle|austin|denver|atlanta|miami)\b',
            r'\b(california|texas|florida|new york|washington)\b',
            r'\b(silicon valley|bay area|nyc|sf)\b'
        ]
        
        self.non_us_patterns = [
            r'\b(london|uk|united kingdom|england|britain)\b',
            r'\b(singapore|germany|france|canada|australia|japan|china|india)\b',
            r'\b(toronto|vancouver|sydney|melbourne|tokyo|beijing|mumbai|bangalore)\b'
        ]
    
    def is_us_location(self, location: str) -> bool:
        """
        Determine if a location is in the US using multiple strategies
        
        Strategy priority:
        1. Cache lookup
        2. Pattern matching (high confidence)
        3. Geocoding API (with caching)
        4. Conservative fallback (assume US)
        """
        if not location or not location.strip():
            return True
            
        location = location.strip()
        location_key = location.lower()
        
        # 1. Check cache
        if location_key in self._cache:
            return self._cache[location_key]
        
        # 2. Pattern matching (high confidence)
        result = self._pattern_match(location_key)
        if result is not None:
            self._cache[location_key] = result
            return result
        
        # 3. Try geocoding API (with timeout and error handling)
        result = self._geocode_location(location)
        if result is not None:
            self._cache[location_key] = result
            return result
        
        # 4. Conservative fallback: assume US
        logger.debug(f"Unknown location '{location}', assuming US")
        self._cache[location_key] = True
        return True
    
    def _pattern_match(self, location_lower: str) -> Optional[bool]:
        """Fast pattern-based detection for common cases"""
        
        # Check US patterns
        for pattern in self.us_patterns:
            if re.search(pattern, location_lower, re.IGNORECASE):
                logger.debug(f"Location '{location_lower}' matched US pattern: {pattern}")
                return True
        
        # Check non-US patterns
        for pattern in self.non_us_patterns:
            if re.search(pattern, location_lower, re.IGNORECASE):
                logger.debug(f"Location '{location_lower}' matched non-US pattern: {pattern}")
                return False
        
        return None  # No pattern match
    
    def _geocode_location(self, location: str) -> Optional[bool]:
        """Use geocoding API as fallback"""
        try:
            # Use free Nominatim API (OpenStreetMap)
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': location,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            headers = {
                'User-Agent': 'FastJobAgent/1.0 (job-scraper)'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=3)
            if response.status_code == 200:
                data = response.json()
                
                if data:
                    address = data[0].get('address', {})
                    country_code = address.get('country_code', '').upper()
                    
                    if country_code:
                        is_us = country_code == 'US'
                        logger.debug(f"Geocoded '{location}' -> {country_code} -> {'US' if is_us else 'non-US'}")
                        return is_us
                        
        except Exception as e:
            logger.debug(f"Geocoding failed for '{location}': {e}")
        
        return None  # API failed
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for debugging"""
        total = len(self._cache)
        us_count = sum(1 for is_us in self._cache.values() if is_us)
        
        return {
            'total_cached': total,
            'us_locations': us_count,
            'non_us_locations': total - us_count,
            'cache_hit_rate': '%.1f%%' % (100.0 * total / max(total, 1))
        }


# Global instance
_location_filter = LocationFilter()

def is_us_location(location: str) -> bool:
    """Convenience function for location filtering"""
    return _location_filter.is_us_location(location)

def get_location_cache_stats() -> Dict[str, Any]:
    """Get location filter cache statistics"""
    return _location_filter.get_cache_stats()


if __name__ == "__main__":
    # Test the location filter
    test_locations = [
        "New York, NY",
        "San Francisco, CA", 
        "Remote",
        "US - Remote",
        "London, UK",
        "Singapore",
        "Toronto, Canada",
        "Austin, TX",
        "Some Unknown City",
        ""
    ]
    
    filter_instance = LocationFilter()
    
    print("🧪 Testing Location Filter:")
    for location in test_locations:
        result = filter_instance.is_us_location(location)
        print(f"  {location:<20} -> {'🇺🇸 US' if result else '🌍 Non-US'}")
    
    print(f"\n📊 Cache Stats: {filter_instance.get_cache_stats()}")