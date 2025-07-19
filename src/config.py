#!/usr/bin/env python3
"""
Centralized configuration for Fast Job Agent
"""

from pathlib import Path

# Base directories
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = DATA_DIR / "output"
CONFIG_DIR = PROJECT_ROOT / "config"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Configuration file paths
ASHBY_CONFIG = CONFIG_DIR / "companies.yaml"
GREENHOUSE_CONFIG = CONFIG_DIR / "greenhouse_companies.yaml"
LEVER_CONFIG = CONFIG_DIR / "lever_companies.yaml"

# API endpoints
GREENHOUSE_API_URL = "https://boards-api.greenhouse.io/v1/boards/{board_name}/jobs"
LEVER_API_URL = "https://api.lever.co/v0/postings/{company_name}?mode=json"

# Scraping settings
REQUEST_DELAY = 2  # seconds between requests
REQUEST_TIMEOUT = 10  # seconds

# Logging settings
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = LOGS_DIR / "run.log"

# CSV export settings
CSV_FIELDS = [
    'role_name', 'company_name', 'location', 'job_link',
    'employment_type', 'team', 'published_date', 'compensation',
    'source', 'job_id'
]

# FDE job keywords
FDE_KEYWORDS = [
    #customer facing engineer keywords
    'forward deployed engineer',
    'forward deployed',
    'customer engineer',
    'solutions engineer',
    'solution engineer',
    'forward deployment engineer',
    'forward deployed ai engineer',
    'field engineer',
    'technical account manager',
    'customer success engineer',
    'implementation engineer',
    'deployment engineer',
    #ai engineer keywords
    'ai engineer',
    'genai engineer',
    'ai developer',
    'machine learning engineer',
    'agent engineer',

    #others 
    'software engineer',
    'full stack engineer',
    'backend engineer',
    'frontend engineer',
    'product engineer',

    #devops engineer',
    # 'data engineer',
    # 'data scientist',
]

# Non-US location keywords
NON_US_LOCATIONS = [
    # Europe
    'london', 'uk', 'united kingdom', 'england', 'britain',
    'germany', 'munich', 'berlin', 'france', 'paris',
    'netherlands', 'amsterdam', 'sweden', 'stockholm',
    'switzerland', 'zurich', 'norway', 'oslo',
    'spain', 'madrid', 'barcelona', 'italy', 'rome', 'milan',
    'poland', 'warsaw', 'czech', 'prague', 'austria', 'vienna',
    'belgium', 'brussels', 'portugal', 'lisbon', 'greece', 'athens',
    'hungary', 'budapest', 'finland', 'helsinki', 'denmark', 'copenhagen',
    'ireland', 'dublin', 'scotland', 'edinburgh', 'wales',
    'romania', 'bucharest', 'bulgaria', 'sofia',
    
    # Asia
    'singapore', 'tokyo', 'japan', 'china', 'beijing', 'shanghai',
    'india', 'bangalore', 'mumbai', 'delhi', 'hyderabad',
    'israel', 'tel aviv', 'turkey', 'istanbul',
    'korea', 'seoul', 'taiwan', 'taipei', 'hong kong',
    'thailand', 'bangkok', 'vietnam', 'philippines', 'manila',
    'malaysia', 'kuala lumpur', 'indonesia', 'jakarta',
    
    # Americas (non-US)
    'canada', 'toronto', 'vancouver', 'montreal', 'ottawa',
    'mexico', 'brazil', 'sao paulo', 'argentina', 'buenos aires',
    'chile', 'santiago', 'colombia', 'bogota', 'peru', 'lima',
    
    # Oceania
    'australia', 'sydney', 'melbourne', 'brisbane', 'perth',
    'new zealand', 'auckland', 'wellington',
    
    # Other
    'russia', 'moscow', 'ukraine', 'kiev', 'south africa', 'cape town'
]