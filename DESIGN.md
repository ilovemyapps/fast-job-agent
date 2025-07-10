# Fast Job Agent - Ashby HQ Job Scraper Design Document

## 1. Project Overview

### Objective
Create an automated agent that runs twice daily to scrape "Forward Deployed Engineer" positions from specified companies on Ashby HQ website and generate CSV reports.

### Core Features
- Periodically scrape job listings from multiple companies on Ashby HQ
- Filter for "Forward Deployed Engineer" related positions
- Extract key information: job title, company name, location, job link
- Generate CSV format reports
- Local cron task scheduling

## 2. Technical Architecture

### Technology Stack
- **Programming Language**: Python 3.8+
- **Web Scraping**: 
  - requests (HTTP requests)
  - BeautifulSoup4 (HTML parsing)
  - Optional: Selenium (if JavaScript rendering needed)
- **Data Processing**: pandas
- **Scheduling**: cron (Linux/Mac) or Task Scheduler (Windows)
- **Logging**: Python logging

### Project Structure
```
fast-job-agent/
├── config/
│   ├── companies.json      # Company list configuration
│   └── settings.py         # Global configuration
├── src/
│   ├── scraper.py         # Scraping logic
│   ├── parser.py          # Data parsing
│   ├── exporter.py        # CSV export
│   └── main.py            # Main program entry
├── data/
│   ├── raw/               # Raw scraped data
│   └── output/            # CSV output files
├── logs/                  # Log files
├── requirements.txt       # Dependencies list
└── run.sh                # Execution script
```

## 3. Core Module Design

### 3.1 Configuration Management (config/companies.json)
```json
{
  "companies": [
    {
      "name": "Baseten",
      "url": "https://jobs.ashbyhq.com/baseten",
      "enabled": true
    },
    {
      "name": "CompanyB",
      "url": "https://jobs.ashbyhq.com/companyb",
      "enabled": true
    }
  ],
  "job_filters": {
    "keywords": ["Forward Deployed Engineer", "FDE"],
    "case_sensitive": false
  }
}
```

### 3.2 Scraper (src/scraper.py)
Main functions:
- HTTP request management (with retry mechanism)
- User-Agent rotation
- Request rate limiting
- Error handling

### 3.3 Parser (src/parser.py)
Main functions:
- Parse Ashby HQ HTML structure
- Extract job listings
- Filter Forward Deployed Engineer positions
- Data cleaning and normalization

### 3.4 Exporter (src/exporter.py)
Main functions:
- Generate CSV files
- Support incremental updates (append new positions)
- Data deduplication
- Timestamp management

## 4. Data Flow

1. **Read Configuration** → Get company list
2. **Batch Scraping** → Visit each company's job page
3. **Data Parsing** → Extract job information
4. **Job Filtering** → Match "Forward Deployed Engineer"
5. **Data Integration** → Merge positions from all companies
6. **CSV Export** → Generate timestamped CSV file
7. **Logging** → Record execution status

## 5. Cron Configuration

### Run Frequency: Twice daily
```bash
# Run at 9 AM and 5 PM daily
0 9,17 * * * /Users/shuai/Desktop/fast-job-agent/run.sh
```

### run.sh Script
```bash
#!/bin/bash
cd /Users/shuai/Desktop/fast-job-agent
source venv/bin/activate
python src/main.py >> logs/cron.log 2>&1
```

## 6. Error Handling

### Expected Error Scenarios
1. Network connection failure
2. Website structure changes
3. Request throttling (429 error)
4. Data format anomalies

### Handling Strategy
- Retry mechanism (3 retries with exponential backoff)
- Email/notification alerts (optional)
- Detailed logging
- Continue processing other companies on partial failure

## 7. Output Format

### CSV File Naming
`fde_jobs_YYYY-MM-DD_HH-MM.csv`

### CSV Structure
| role_name | company_name | location | job_link |
|-----------|--------------|----------|----------|
| Forward Deployed Engineer | Baseten | San Francisco, CA | https://jobs.ashbyhq.com/baseten/... |

## 8. Extensibility Considerations

### Future Possible Features
1. Support more job sites (Lever, Greenhouse, etc.)
2. Job change notifications (new/removed positions)
3. More complex filtering criteria
4. API interface for data querying
5. Database storage for historical records

### Performance Optimization
1. Concurrent scraping (multi-threading/async)
2. Caching mechanism
3. Incremental updates

## 9. Security Considerations

1. No sensitive information storage
2. Comply with robots.txt
3. Reasonable request frequency
4. User-Agent identification

## 10. Implementation Plan

### Phase 1: Basic Features (Week 1)
- Implement single company scraping
- Basic CSV export
- Command line execution

### Phase 2: Batch Processing (Week 2)
- Multi-company support
- Configuration file management
- Error handling optimization

### Phase 3: Automation (Week 3)
- Cron task configuration
- Logging system
- Monitoring alerts

## Discussion Points

1. **Scraping Strategy**: Need to handle JavaScript-rendered content?
2. **Data Storage**: Need to save historical data for analysis?
3. **Notification System**: Need instant notifications when new positions found?
4. **Extensibility**: Consider supporting other job sites in future?
5. **Performance Requirements**: Company count scale? Need concurrent processing?