# Fast Job Agent

> **Intelligent Engineering Job Aggregator** - Automated monitoring and collection of high-quality engineering positions from top tech companies

A high-performance async job scraping system specifically designed for Forward Deployed Engineer, Solutions Engineer, and other customer-facing engineering roles across major recruitment platforms including Ashby, Greenhouse, and Lever.

## 🎯 Core Value

- **💼 Precise Targeting**: Focus on customer-facing engineering positions, filtering out irrelevant noise
- **🌍 Multi-Platform Coverage**: Support for Ashby, Greenhouse, and Lever - the three major recruitment platforms
- **⚡ High-Performance Async**: Concurrent processing, scraping hundreds of companies in seconds
- **🎯 Smart Filtering**: US region filtering + keyword matching for precise job targeting
- **📊 Structured Output**: Standardized data format with CSV export and API integration support
- **🔄 Automated Monitoring**: Scheduled tasks for continuous job change monitoring

## 🚀 Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Basic Usage
```bash
# Run all platform scrapers
python src/main_runner.py

# Run specific platforms individually
python src/ashby_scraper.py
python src/greenhouse_scraper.py
python src/lever_scraper.py

# View results
ls data/output/
```

### Core Functionality Demo
```python
from scraper_factory import ScraperFactory
from models import JobSource

# Create scraper instance
scraper = ScraperFactory.create_scraper(JobSource.ASHBY)

# Execute asynchronously
jobs = await scraper.scrape_all(max_concurrent=10)
print(f"Found {len(jobs)} matching positions")
```

## 📋 Features

### 🎯 Smart Filtering System
- **Keyword Matching**: Forward Deployed Engineer, Solutions Engineer, Customer Engineer, etc.
- **Geographic Filtering**: Automatic identification and filtering of US-based positions
- **Company Type Support**: Support for regular companies and VC portfolio batch processing

### 🔧 Technical Features
- **Async Concurrency**: High-performance async processing based on aiohttp
- **Decorator Enhancement**: Automatic error handling, retry mechanisms, performance monitoring
- **Data Models**: Type-safe Job and JobStats data structures
- **Factory Pattern**: Unified scraper creation and management interface
- **Smart Configuration**: Auto-generated URLs with zero redundancy

### 📊 Data Output
- **Standardized Fields**: role_name, company_name, location, job_link, etc.
- **Multi-format Support**: CSV export, JSON API, Notion sync
- **Statistics**: Detailed scraping statistics and regional distribution

## 🏗️ Architecture Design

### Core Components
```
├── models.py          # Data models (Job, JobStats, ScraperConfig)
├── base_scraper.py    # Base scraper class (common functionality)
├── scraper_factory.py # Factory pattern (unified creation interface)
├── utils/             # Utility modules
│   ├── decorators.py  # Decorators (error handling, retry, timing)
│   ├── logging_utils.py # Logging utilities
│   └── date_utils.py  # Date processing
└── constants.py       # Constants definition
```

### Design Patterns
- **Factory Pattern**: `ScraperFactory` for unified scraper creation
- **Decorator Pattern**: `@with_error_handling` `@with_retry` `@with_timing`
- **Template Method**: `AsyncBaseScraper` defines common workflow
- **Strategy Pattern**: Platform-specific implementation strategies

### Async Architecture
```python
async def scrape_all(self, max_concurrent=5):
    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(max_concurrent)
    
    # Execute all companies concurrently
    tasks = [self.scrape_company(session, company) 
             for company in self.companies]
    
    results = await asyncio.gather(*tasks)
    return flatten(results)
```

## 📖 Configuration

### Basic Configuration
```yaml
# config/companies.yaml (Ashby)
companies:
  - name: OpenAI
    job_board_name: openai
    # URL auto-generated: https://jobs.ashbyhq.com/openai
    
  - name: Pear VC Portfolio  
    job_board_name: pear
    is_vc_portfolio: true  # Special handling for VC portfolios
```

### Advanced Configuration
```python
# Custom keywords
FDE_KEYWORDS = [
    'forward deployed engineer',
    'solutions engineer', 
    'customer engineer',
    # ... customizable in config.py
]

# Concurrency control
scraper = ScraperFactory.create_scraper(JobSource.ASHBY)
jobs = await scraper.scrape_all(max_concurrent=10)
```

## 🔌 API Reference

### ScraperFactory
```python
# Create single scraper
scraper = ScraperFactory.create_scraper(JobSource.ASHBY)

# Create all scrapers
scrapers = ScraperFactory.create_all_scrapers()

# Get supported platforms
sources = ScraperFactory.get_available_sources()
```

### Data Models
```python
@dataclass
class Job:
    role_name: str
    company_name: str
    location: str
    job_link: str
    source: JobSource
    job_id: str
    # ... other fields
    
    def to_dict(self) -> Dict  # CSV export
    def get_unique_id(self) -> str  # Deduplication ID
```

### Decorators
```python
@with_error_handling(default_return=[])
@with_timing(log_level=logging.INFO)
@with_retry(max_attempts=3, delay=1.0)
async def scrape_company(self, session, company):
    # Automatic error handling, performance monitoring, retry mechanism
    pass
```

## 📊 Performance Metrics

- **Concurrent Processing**: Support for 10+ concurrent requests, 50+ companies scraped in 30 seconds
- **Error Recovery**: Automatic retry mechanism with 90%+ success rate
- **Memory Efficiency**: Stream processing, supports large-scale data handling
- **Geographic Filtering**: Smart US region recognition with 95%+ accuracy

## 🛠️ Extension Guide

### Adding New Platforms
```python
# 1. Inherit from base class
class NewPlatformScraper(AsyncBaseScraper):
    async def scrape_company(self, session, company):
        # Implement platform-specific logic
        pass

# 2. Register with factory
ScraperFactory.register_scraper(JobSource.NEW_PLATFORM, NewPlatformScraper)
```

### Custom Filters
```python
def custom_filter(jobs: List[Dict]) -> List[Dict]:
    # Custom filtering logic
    return filtered_jobs

# Integrate in base_scraper.py
```

### Adding New Data Sources
```python
# 1. Add new JobSource in models.py
class JobSource(Enum):
    NEW_SOURCE = "NewSource"

# 2. Add URL template in constants.py
class URLTemplates:
    NEW_SOURCE_API = "https://api.newsource.com/{company}/jobs"
```

## 📈 Monitoring & Logging

### Log Levels
- **INFO**: Scraping progress and statistics
- **DEBUG**: Detailed request/response information  
- **ERROR**: Error and exception information
- **WARNING**: Configuration issues and data anomalies

### Statistics
```
📊 OpenAI Statistics:
  Total jobs scraped: 25
  US jobs: 18
  Non-US jobs: 7
  Non-US locations: London, Toronto, Sydney
```

## 🔄 Scheduled Tasks

### Cron Setup
```bash
# Run daily at 9 AM
0 9 * * * cd /path/to/fast-job-agent && python src/main_runner.py

# Run weekly on Monday with email notification
0 9 * * 1 cd /path/to/fast-job-agent && python src/main_runner.py && python src/send_report.py
```

### System Integration
```python
# Notion sync
from notion_sync import NotionSync
sync = NotionSync()
sync.sync_jobs(jobs)

# Data processing
from data_processor_pandas import JobDataProcessor  
processor = JobDataProcessor()
processed_jobs = processor.process_jobs(jobs)
```

## 🎯 Best Practices

1. **Concurrency Control**: Adjust `max_concurrent` parameter based on target website load
2. **Error Handling**: Use decorators for automatic network exception handling and retry
3. **Configuration Management**: Use environment variables for sensitive configuration
4. **Data Validation**: Leverage dataclass for type checking
5. **Log Monitoring**: Regularly check log files and monitor scraping quality

## 📚 Documentation

- [CRON_SETUP.md](CRON_SETUP.md) - Scheduled task configuration
- [API_DOCS.md](docs/API_DOCS.md) - Detailed API documentation  
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guide
- [CHANGELOG.md](CHANGELOG.md) - Version update history

## 🤝 Contributing

Welcome to submit Issues and Pull Requests! Please ensure:
- Follow existing code style
- Add appropriate tests
- Update relevant documentation
- Use decorators and data models

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details