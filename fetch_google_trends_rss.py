#!/usr/bin/env python3
"""
Attempt to fetch Google Trends data using RSS feeds and direct requests.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import time
import json

def fetch_daily_trends_rss(date):
    """
    Try to fetch daily trends from RSS feed for a specific date.
    """
    # Google Trends RSS URL
    # Format: https://trends.google.com/trends/trendingsearches/daily/rss?geo=US
    url = "https://trends.google.com/trends/trendingsearches/daily/rss"
    params = {
        'geo': 'US',
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        # Parse XML
        root = ET.fromstring(response.content)

        trends = []
        # Find all items in RSS feed
        for item in root.findall('.//item'):
            title = item.find('title')
            pubDate = item.find('pubDate')
            traffic = item.find('.//ht:approx_traffic', {'ht': 'http://www.google.com/trends/hottrends'})

            if title is not None:
                trend_data = {
                    'title': title.text,
                    'pubDate': pubDate.text if pubDate is not None else '',
                    'traffic': traffic.text if traffic is not None else ''
                }
                trends.append(trend_data)

        return trends
    except Exception as e:
        print(f"Error fetching RSS for {date}: {e}")
        return None

def fetch_trends_api(date_str):
    """
    Try to fetch trends using internal Google Trends API endpoints.
    This uses undocumented endpoints and may not work.
    """
    # Try the daily trends API endpoint
    url = "https://trends.google.com/trends/api/dailytrends"
    params = {
        'hl': 'en-US',
        'tz': '-360',
        'geo': 'US',
        'ns': '15',
        'ed': date_str  # Format: YYYYMMDD
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)

        # Google Trends API returns )]}' at the beginning, need to strip it
        content = response.text
        if content.startswith(")]}'"):
            content = content[4:]

        data = json.loads(content)
        return data
    except Exception as e:
        print(f"Error with API for {date_str}: {e}")
        return None

def main():
    print("=" * 70)
    print("Google Trends 2024 - Alternative Data Collection")
    print("=" * 70)
    print()

    # First, test if we can access current RSS feed
    print("Testing RSS feed access...")
    rss_data = fetch_daily_trends_rss(datetime.now())
    if rss_data:
        print(f"✓ RSS feed accessible - found {len(rss_data)} trends")
        for i, trend in enumerate(rss_data[:5], 1):
            print(f"  {i}. {trend['title']}")
    else:
        print("✗ RSS feed not accessible")

    print()

    # Try API endpoint for a specific date
    print("Testing API endpoint access...")
    test_date = "20241231"  # Dec 31, 2024
    api_data = fetch_trends_api(test_date)

    if api_data:
        print(f"✓ API endpoint accessible for date {test_date}")
        print(f"  Data structure: {type(api_data)}")

        # Try to extract trends from API response
        if isinstance(api_data, dict):
            print(f"  Keys: {list(api_data.keys())}")

            # Parse the data structure
            all_trends = []

            if 'default' in api_data and 'trendingSearchesDays' in api_data['default']:
                for day_data in api_data['default']['trendingSearchesDays']:
                    date = day_data.get('date', '')
                    formatted_date = day_data.get('formattedDate', '')

                    for trend_item in day_data.get('trendingSearches', []):
                        title = trend_item.get('title', {}).get('query', '')
                        traffic = trend_item.get('formattedTraffic', '')

                        all_trends.append({
                            'date': date,
                            'formatted_date': formatted_date,
                            'trending_search': title,
                            'traffic': traffic
                        })

                if all_trends:
                    print(f"  ✓ Successfully parsed {len(all_trends)} trends!")
                    print(f"\n  Sample trends:")
                    for trend in all_trends[:5]:
                        print(f"    - {trend['trending_search']} ({trend['traffic']})")

                    # Now try to collect data for all of 2024
                    print("\n" + "=" * 70)
                    print("Collecting data for all of 2024...")
                    print("=" * 70)
                    print()

                    all_2024_trends = []
                    start_date = datetime(2024, 1, 1)
                    end_date = datetime(2024, 12, 31)
                    current_date = start_date

                    days_collected = 0
                    days_failed = 0

                    while current_date <= end_date:
                        date_str = current_date.strftime('%Y%m%d')
                        print(f"Fetching {current_date.strftime('%Y-%m-%d')}...", end=' ')

                        day_data = fetch_trends_api(date_str)

                        if day_data and isinstance(day_data, dict):
                            if 'default' in day_data and 'trendingSearchesDays' in day_data['default']:
                                day_trends = []
                                for day_item in day_data['default']['trendingSearchesDays']:
                                    for trend_item in day_item.get('trendingSearches', []):
                                        title = trend_item.get('title', {}).get('query', '')
                                        traffic = trend_item.get('formattedTraffic', '')
                                        articles = trend_item.get('articles', [])

                                        # Get first article info if available
                                        article_title = ''
                                        article_source = ''
                                        if articles:
                                            article_title = articles[0].get('title', '')
                                            article_source = articles[0].get('source', '')

                                        day_trends.append({
                                            'date': current_date.strftime('%Y-%m-%d'),
                                            'trending_search': title,
                                            'traffic': traffic,
                                            'article_title': article_title,
                                            'article_source': article_source
                                        })

                                if day_trends:
                                    all_2024_trends.extend(day_trends)
                                    print(f"✓ Got {len(day_trends)} trends")
                                    days_collected += 1
                                else:
                                    print("✗ No trends found")
                                    days_failed += 1
                            else:
                                print("✗ Unexpected data structure")
                                days_failed += 1
                        else:
                            print("✗ Failed")
                            days_failed += 1

                        current_date += timedelta(days=1)

                        # Rate limiting
                        time.sleep(1)

                    # Save results
                    if all_2024_trends:
                        df = pd.DataFrame(all_2024_trends)
                        df = df[['date', 'trending_search', 'traffic', 'article_title', 'article_source']]

                        output_file = 'google_trends_2024_daily.csv'
                        df.to_csv(output_file, index=False)

                        print("\n" + "=" * 70)
                        print("COLLECTION COMPLETE!")
                        print("=" * 70)
                        print(f"✓ Successfully collected {days_collected} days")
                        print(f"✗ Failed to collect {days_failed} days")
                        print(f"Total trends: {len(all_2024_trends)}")
                        print(f"Output file: {output_file}")
                        print(f"\nDate range: {df['date'].min()} to {df['date'].max()}")
                        print(f"\nFirst 10 rows:")
                        print(df.head(10))
                        print(f"\nLast 10 rows:")
                        print(df.tail(10))
                    else:
                        print("\n✗ No data collected!")
                else:
                    print("  ✗ Could not parse trends from response")
            else:
                print("  ✗ Unexpected API response structure")
    else:
        print("✗ API endpoint not accessible")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
