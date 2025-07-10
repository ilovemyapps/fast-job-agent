# Cron Job Configuration

## Setup Daily Task at 4:50 PM

### 1. Edit crontab
```bash
crontab -e
```

### 2. Add the following line (runs daily at 5:25 PM)
```bash
25 17 * * * /Users/shuai/fast-job-agent/run.sh >> /Users/shuai/fast-job-agent/logs/cron.log 2>&1
```

### 3. Cron time format explanation
```
min hour day month weekday
25  17   *   *     *
│   │    │   │     │
│   │    │   │     └─── Weekday (0-7, 0 and 7 are Sunday)
│   │    │   └───────── Month (1-12)
│   │    └─────────────── Day (1-31)
│   └──────────────────── Hour (0-23, 17 is 5 PM)
└────────────────────────── Minute (0-59, 25 is 25th minute)
```

### 4. Verify cron job
```bash
# View current user's cron jobs
crontab -l

# View cron logs (macOS)
tail -f /Users/shuai/fast-job-agent/logs/cron.log
```

### 5. Other time options
- Run once daily (5:25 PM): `25 17 * * *` ✅ Current setting
- Run every 2 days (5:25 PM): `25 17 */2 * *`
- Run on Mon, Wed, Fri: `25 17 * * 1,3,5`
- Run daily at 9 AM: `0 9 * * *`

### 6. Important notes
- Ensure `run.sh` has execute permission: `chmod +x run.sh`
- Cron uses different environment variables than terminal, if issues occur, add full paths in run.sh
- macOS may require granting Full Disk Access to Terminal app in System Preferences
- Project moved to /Users/shuai/fast-job-agent to avoid Desktop protection issues