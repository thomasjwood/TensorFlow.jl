#!/usr/bin/env python3
"""
Google Trends 2024 Daily Data Collector

This script collects daily trending searches from Google Trends for every day
in 2024 and combines them into a single CSV file.

Requirements:
- Run this on a machine with unrestricted internet access to Google Trends
- pip install requests pandas

Usage:
    python3 collect_google_trends_2024.py

Output:
    google_trends_2024_complete.csv - All trending searches for 2024
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import sys

def fetch_daily_trends(date_str):
    """
    Fetch Google Trends daily trending searches for a specific date.

    Args:
        date_str: Date in YYYYMMDD format (e.g., '20240101')

    Returns:
        List of dictionaries containing trend data, or None if failed
    """
    url = "https://trends.google.com/trends/api/dailytrends"
    params = {
        'hl': 'en-US',
        'tz': '-360',
        'geo': 'US',
        'ns': '15',
        'ed': date_str
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://trends.google.com/trends/trendingsearches/daily',
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()

        # Google Trends API returns )]}' prefix, strip it
        content = response.text
        if content.startswith(")]}'"):
            content = content[5:]

        data = json.loads(content)

        trends = []

        if 'default' in data and 'trendingSearchesDays' in data['default']:
            for day_data in data['default']['trendingSearchesDays']:
                date = day_data.get('date', '')
                formatted_date = day_data.get('formattedDate', '')

                for rank, trend_item in enumerate(day_data.get('trendingSearches', []), 1):
                    # Extract basic trend info
                    query = trend_item.get('title', {}).get('query', '')
                    traffic = trend_item.get('formattedTraffic', '')

                    # Extract article information
                    articles = trend_item.get('articles', [])
                    article_title = ''
                    article_source = ''
                    article_snippet = ''

                    if articles:
                        first_article = articles[0]
                        article_title = first_article.get('title', '')
                        article_source = first_article.get('source', '')
                        article_snippet = first_article.get('snippet', '')

                    # Extract related queries
                    related_queries = []
                    for related in trend_item.get('relatedQueries', []):
                        related_queries.append(related.get('query', ''))

                    trends.append({
                        'date': date,
                        'formatted_date': formatted_date,
                        'rank': rank,
                        'trending_search': query,
                        'traffic': traffic,
                        'article_title': article_title,
                        'article_source': article_source,
                        'article_snippet': article_snippet,
                        'related_queries': '; '.join(related_queries) if related_queries else ''
                    })

        return trends if trends else None

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Network error: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON parse error: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}", file=sys.stderr)
        return None


def main():
    print("=" * 80)
    print(" Google Trends 2024 - Complete Daily Data Collection")
    print("=" * 80)
    print()
    print("This script will collect trending searches for all 366 days of 2024")
    print("(2024 is a leap year)")
    print()
    print("Estimated time: ~6-10 minutes (with rate limiting)")
    print()
    print("=" * 80)
    print()

    # Date range for 2024
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    total_days = (end_date - start_date).days + 1

    all_trends = []
    current_date = start_date
    successful_days = 0
    failed_days = 0

    print(f"Starting collection for {total_days} days...\n")

    while current_date <= end_date:
        date_str = current_date.strftime('%Y%m%d')
        display_date = current_date.strftime('%Y-%m-%d')
        day_num = (current_date - start_date).days + 1

        print(f"[{day_num}/{total_days}] {display_date}... ", end='', flush=True)

        trends = fetch_daily_trends(date_str)

        if trends:
            all_trends.extend(trends)
            print(f"✓ {len(trends)} trends collected")
            successful_days += 1
        else:
            print("✗ Failed to collect")
            failed_days += 1

        current_date += timedelta(days=1)

        # Rate limiting - be respectful to Google's servers
        time.sleep(1.5)

    # Save to CSV
    print()
    print("=" * 80)
    print(" Collection Complete!")
    print("=" * 80)
    print()
    print(f"Days successfully collected: {successful_days}/{total_days}")
    print(f"Days failed: {failed_days}/{total_days}")
    print(f"Total trend records: {len(all_trends)}")
    print()

    if all_trends:
        # Create DataFrame
        df = pd.DataFrame(all_trends)

        # Reorder columns for better readability
        column_order = [
            'date',
            'formatted_date',
            'rank',
            'trending_search',
            'traffic',
            'article_title',
            'article_source',
            'article_snippet',
            'related_queries'
        ]

        df = df[column_order]

        # Save to CSV
        output_file = 'google_trends_2024_complete.csv'
        df.to_csv(output_file, index=False, encoding='utf-8')

        print(f"✓ Data saved to: {output_file}")
        print()
        print("File info:")
        print(f"  - Size: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"  - Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"  - Unique dates: {df['date'].nunique()}")
        print()
        print("Preview of first 10 rows:")
        print("-" * 80)
        print(df.head(10).to_string())
        print()
        print("Preview of last 10 rows:")
        print("-" * 80)
        print(df.tail(10).to_string())
        print()
        print("=" * 80)
        print(" SUCCESS! Your CSV file is ready.")
        print("=" * 80)

    else:
        print("✗ ERROR: No data was collected!")
        print()
        print("Possible issues:")
        print("  1. Network connectivity problems")
        print("  2. Google Trends API changes")
        print("  3. Rate limiting or blocking")
        print()
        print("Try running the script again, or check your internet connection.")
        sys.exit(1)


if __name__ == "__main__":
    main()
