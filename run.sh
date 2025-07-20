#!/usr/bin/env bash
# Fast Job Agent run script

# Change to script directory
cd "$(dirname "$0")"

# Create logs directory if it doesn't exist
mkdir -p logs

# Clean up old run log to prevent file bloat
rm -f logs/run.log

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

# Run job aggregator (includes all scrapers + deduplication)
python3 src/job_aggregator.py >> logs/run.log 2>&1

# Record run time
echo "Completed at: $(date)" >> logs/run.log