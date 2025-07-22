#!/usr/bin/env python3
"""
Clear Notion sync cache
Use this when you recreate the Notion database
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from notion_sync import NotionSync

def main():
    try:
        print("🧹 Clearing Notion sync cache...")
        
        sync = NotionSync()
        cleared_count = sync.clear_all_cache()
        
        print(f"✅ Successfully cleared {cleared_count} cached job IDs")
        print("🚀 Now you can run the job aggregator fresh!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure NOTION_API_TOKEN and NOTION_DATABASE_ID are set in .env file")

if __name__ == "__main__":
    main()