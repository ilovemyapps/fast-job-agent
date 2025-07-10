# Fast Job Agent - Ashby HQ Job Scraper

Automatically scrape Forward Deployed Engineer related positions from Ashby HQ.

## Features

- 🔍 Auto-scrape FDE related positions from specified companies
- 📊 Export to CSV format with job title, company, location, link and other info
- ⏰ Support cron scheduled tasks, run daily automatically
- 📝 Detailed logging
- 🚀 No authentication required, get data directly from public pages

## Quick Start

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Configure Company List
Edit `config/companies.yaml` to add companies to monitor:
```yaml
companies:
  - name: Company Name
    job_board_name: ashby_url_name
    url: https://jobs.ashbyhq.com/ashby_url_name
```

### 3. Run Scraper
```bash
# Single run
python3 src/ashby_scraper.py

# Or use script
./run.sh
```

### 4. View Results
Results are saved in `data/output/` directory with filename format `fde_jobs_YYYY-MM-DD_HH-MM.csv`

## Directory Structure

```
fast-job-agent/
├── config/
│   └── companies.yaml      # Company configuration file
├── src/
│   └── ashby_scraper.py   # Main scraping logic
├── data/
│   └── output/            # CSV output files
├── logs/                  # Log files
├── run.sh                 # Run script
└── CRON_SETUP.md         # Cron setup instructions
```

## Job Filtering Keywords

Currently filters jobs containing these keywords:
- Forward Deployed Engineer
- Forward Deployed
- FDE
- Field Engineer
- Customer Engineer
- Solutions Engineer

## Output Format

CSV file contains following fields:
- `role_name`: Job title
- `company_name`: Company name
- `location`: Work location
- `job_link`: Job URL
- `employment_type`: Employment type
- `team`: Team name
- `published_date`: Published date
- `compensation`: Salary range

## Scheduled Task Setup

See [CRON_SETUP.md](CRON_SETUP.md) for how to setup scheduled tasks.

## Adding New Companies

1. Visit `https://jobs.ashbyhq.com/company_name` to confirm page exists
2. Add new company to `config/companies.yaml`
3. Run test to ensure scraping works correctly

## Important Notes

- Please follow website terms of use and robots.txt
- Set reasonable scraping frequency to avoid server load
- Some companies may use different page structures, check logs if issues occur

## Troubleshooting

1. **No job data found**: Check if company URL is correct
2. **JSON parsing failed**: Page structure may have changed, need to update regex
3. **Request failed**: Check network connection or wait and retry later

## TODO

### Future Enhancements
- [ ] **Add Notion AI-based filtering**: Use Notion AI to further filter and categorize job postings
- [ ] **Add more VC portfolio job boards**: Expand beyond Ashby to include more VC investment portfolio job sites
- [ ] **add lever sites ** https://jobs.lever.co/palantir
- [ ] **Weekly Summary Report**
• New openings this week: 15
• Top companies: OpenAI (5), Databricks (3)
• Top regions: SF (8), NYC (4) 

### VC Portfolio Job Boards (Pending Implementation)
These VC job boards are identified but not yet implemented:

**Getro Platform:**
- [ ] Index Ventures — https://indexventures.getro.com/jobs
- [ ] Backed VC — https://talent.backed.vc/talent-network

**Custom/Self-built Platforms:**
- [ ] Andreessen Horowitz (a16z) — https://portfoliojobs.a16z.com
- [ ] Sequoia Capital — https://www.sequoiacap.com/jobs
- [ ] Bessemer Venture Partners — https://jobs.bvp.com
- [ ] Redpoint Ventures — https://careers.redpoint.com/jobs
- [ ] First Round Capital — https://jobs.firstround.com
- [ ] Earlybird Venture Capital — https://jobs.earlybird.com/talent-network
- [ ] Accel — https://jobs.accel.com
- [ ] YC jobs -  https://www.ycombinator.com/jobs

**Implementation Priority:**
1. Getro platform (2 sites) - Medium complexity
2. Custom platforms (7 sites) - High complexity, each may need individual handling
3. lever.co 