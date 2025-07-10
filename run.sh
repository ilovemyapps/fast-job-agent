#!/usr/bin/env bash
# Fast Job Agent run script

# Change to script directory
cd "$(dirname "$0")"

# Clean up old log files
echo "🧹 Cleaning up old log files..."
rm -f logs/run.log
rm -f logs/cron.log

# Activate virtual environment if exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
    
    # Check if dependencies are installed (optional)
    if ! python3 -c "import requests, yaml, bs4" &> /dev/null; then
        echo "⚠️  Dependencies missing, installing..."
        pip install -r requirements.txt
    fi
else
    echo "⚠️  Virtual environment not found, using system Python"
fi

# Run async job aggregator (includes all scrapers + deduplication)
python3 src/async_job_aggregator.py

# Record run time
echo "Completed at: $(date)" >> logs/run.log