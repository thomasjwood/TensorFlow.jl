#!/usr/bin/env python3
"""
Fetch Google Trends daily trending searches for every day in 2024.
This script attempts to get historical daily trends data.
"""

import pandas as pd
from pytrends.request import TrendReq
from datetime import datetime, timedelta
import time
import sys
import json

def fetch_daily_trends_realtime(pytrends, date):
    """
    Attempt to fetch daily trends. Note: pytrends may only provide current data,
    not historical data for past dates through the unofficial API.
    """
    try:
        # Try to get trending searches (this typically returns current trends)
        df = pytrends.trending_searches(pn='united_states')
        if df is not None and not df.empty:
            df.columns = ['trending_search']
            df['date'] = date.strftime('%Y-%m-%d')
            df['rank'] = range(1, len(df) + 1)
            return df
    except Exception as e:
        print(f"  Error with trending_searches: {e}", file=sys.stderr)

    try:
        # Try realtime trending searches
        df = pytrends.realtime_trending_searches(pn='US')
        if df is not None and not df.empty:
            # Extract title from the data structure
            if 'title' in df.columns:
                df = df[['title']].copy()
                df.columns = ['trending_search']
                df['date'] = date.strftime('%Y-%m-%d')
                df['rank'] = range(1, len(df) + 1)
                return df
    except Exception as e:
        print(f"  Error with realtime_trending_searches: {e}", file=sys.stderr)

    return None

def main():
    print("=" * 70)
    print("Google Trends Data Collection for 2024")
    print("=" * 70)
    print("\nIMPORTANT NOTE:")
    print("The unofficial Google Trends API (pytrends) has limitations:")
    print("- It may only provide current/recent trending searches")
    print("- Historical daily trends for past dates may not be available")
    print("- Google Trends doesn't officially provide a historical daily API")
    print("\nThis script will attempt to collect what data is available...")
    print("=" * 70)
    print()

    # Initialize pytrends
    pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))

    # Let's try to get current trending searches first to see what we get
    print("Testing current trending searches...")
    try:
        current_trends = pytrends.trending_searches(pn='united_states')
        print(f"✓ Successfully retrieved {len(current_trends)} current trending searches")
        print(f"\nSample of current trends:")
        print(current_trends.head(10))
        print()
    except Exception as e:
        print(f"✗ Error getting current trends: {e}")
        print("This suggests API access issues. Proceeding anyway...")

    # Ask user if they want to continue
    print("\nDue to API limitations, we cannot get true historical daily data.")
    print("Would you like to:")
    print("1. Proceed and document the limitation")
    print("2. Create a note about alternative data sources")
    print()

    # For now, let's create a sample with available data and document limitations
    print("Creating dataset with available data and documentation...\n")

    # Create a documentation file
    doc_content = """
# Google Trends 2024 Data Collection - Important Limitations

## Summary
This data collection attempted to fetch daily trending searches for every day in 2024.

## Limitations Encountered

1. **API Constraints**: The unofficial Google Trends API (pytrends) does not provide
   access to historical daily trending searches for specific past dates.

2. **Data Available**:
   - Current/recent trending searches: Available
   - Historical daily trends by specific date: NOT available through API

3. **Google Trends Official Limitations**:
   - Google Trends does not provide an official API for historical daily trends
   - The web interface shows historical data, but it's not programmatically accessible
   - Daily Search Trends RSS feed only contains recent days (typically last 1-2 days)

## Alternative Approaches

To get complete 2024 daily trending data, you would need to:

1. **Manual Download**: Visit Google Trends daily and download CSVs
   - URL: https://trends.google.com/trends/trendingsearches/daily

2. **Web Scraping**: Use Selenium/Playwright to automate browser interactions
   - This would require simulating actual browser visits to the Trends page
   - May violate Terms of Service
   - Unreliable due to site changes and anti-bot measures

3. **Third-Party Data Providers**:
   - Some commercial services archive Google Trends data
   - Academic datasets (e.g., from research institutions)

4. **Real-time Collection**: Set up a daily cron job to collect trends going forward
   - Won't help with 2024 historical data but works for future dates

## Current Data Included

The attached CSV contains trending searches data that WAS accessible at the time
of running this script. This represents a snapshot of available trends, not
comprehensive historical daily data for 2024.

## Data Sources Attempted

- pytrends.trending_searches() - Returns current US trending searches
- pytrends.realtime_trending_searches() - Returns current realtime trends
- pytrends.today_searches() - Returns current day trends (if available)

Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open('GOOGLE_TRENDS_DATA_LIMITATIONS.txt', 'w') as f:
        f.write(doc_content)

    print("✓ Created documentation file: GOOGLE_TRENDS_DATA_LIMITATIONS.txt")

    # Collect what data we CAN get
    print("\nAttempting to collect available trending data...")

    all_data = []

    # Get current trending searches
    try:
        print("- Fetching current trending searches...")
        current = pytrends.trending_searches(pn='united_states')
        if current is not None and not current.empty:
            current.columns = ['trending_search']
            current['date'] = datetime.now().strftime('%Y-%m-%d')
            current['data_type'] = 'current_trending'
            current['rank'] = range(1, len(current) + 1)
            all_data.append(current)
            print(f"  ✓ Got {len(current)} trending searches")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    # Get realtime trending
    try:
        print("- Fetching realtime trending searches...")
        realtime = pytrends.realtime_trending_searches(pn='US')
        if realtime is not None and not realtime.empty:
            if 'title' in realtime.columns:
                rt_df = realtime[['title']].copy()
                rt_df.columns = ['trending_search']
                rt_df['date'] = datetime.now().strftime('%Y-%m-%d')
                rt_df['data_type'] = 'realtime_trending'
                rt_df['rank'] = range(1, len(rt_df) + 1)
                all_data.append(rt_df)
                print(f"  ✓ Got {len(rt_df)} realtime trending searches")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    # Try today's searches
    try:
        print("- Fetching today's trending searches...")
        today = pytrends.today_searches(pn='US')
        if today is not None and not today.empty:
            today.columns = ['trending_search']
            today['date'] = datetime.now().strftime('%Y-%m-%d')
            today['data_type'] = 'today_trending'
            today['rank'] = range(1, len(today) + 1)
            all_data.append(today)
            print(f"  ✓ Got {len(today)} today trending searches")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    # Combine and save what we got
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = combined_df[['date', 'rank', 'trending_search', 'data_type']]

        output_file = 'google_trends_available_data.csv'
        combined_df.to_csv(output_file, index=False)

        print(f"\n✓ Saved available data to: {output_file}")
        print(f"  Total records: {len(combined_df)}")
        print(f"\nFirst 10 rows:")
        print(combined_df.head(10))
        print(f"\nLast 10 rows:")
        print(combined_df.tail(10))
    else:
        print("\n✗ No data could be collected!")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("Due to Google Trends API limitations, complete historical daily data")
    print("for all of 2024 is NOT available through programmatic access.")
    print("\nFiles created:")
    print("1. google_trends_available_data.csv - Available trending data")
    print("2. GOOGLE_TRENDS_DATA_LIMITATIONS.txt - Detailed explanation")
    print("=" * 70)

if __name__ == "__main__":
    main()
