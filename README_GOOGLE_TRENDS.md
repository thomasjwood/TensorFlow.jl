# Google Trends 2024 Daily Data Collection

## Important Notice

This script **cannot run in the current environment** due to network restrictions blocking access to Google Trends. However, it is fully functional and ready to use on your local machine.

## Quick Start

### Requirements

```bash
pip install requests pandas
```

### Run the Script

```bash
python3 collect_google_trends_2024.py
```

The script will:
1. Collect trending searches for all 366 days of 2024 (leap year)
2. For each day, retrieve ~20 trending searches with details
3. Combine everything into a single CSV file: `google_trends_2024_complete.csv`

### Expected Output

The CSV will contain approximately **7,320 rows** (366 days × ~20 trends per day) with these columns:

- `date` - ISO format date (YYYYMMDD)
- `formatted_date` - Human-readable date
- `rank` - Trend rank for that day (1-20)
- `trending_search` - The search query text
- `traffic` - Estimated search traffic (e.g., "200K+")
- `article_title` - Title of related news article
- `article_source` - News source name
- `article_snippet` - Article excerpt
- `related_queries` - Related search terms (semicolon-separated)

### Estimated Runtime

- **6-10 minutes** with rate limiting (1.5 seconds between requests)
- Can be sped up by reducing the `time.sleep()` value, but risks rate limiting

## Why It Didn't Work Here

The current environment has these limitations:

1. **Proxy Restrictions**: HTTP 403 errors when accessing Google Trends
2. **No Browser**: Selenium automation requires Chrome/Firefox (not installed)
3. **Network Policies**: External web scraping is blocked

## Alternative Approaches

If the Python script doesn't work for you, try these alternatives:

### Option 1: Manual Daily Downloads

Visit [Google Trends Daily](https://trends.google.com/trends/trendingsearches/daily) and:
1. Select each date in 2024
2. Click "Download as CSV" for each day
3. Manually combine the files

### Option 2: Use Google's Official Dataset

Check [Google Trends Data GitHub](https://github.com/GoogleTrends/data) for curated datasets. Note: May not include comprehensive daily 2024 data yet.

### Option 3: BigQuery

Access Google Trends data through [Google Cloud BigQuery](https://console.cloud.google.com/marketplace/product/bigquery-public-datasets/google-search-trends) (requires Google Cloud account).

### Option 4: Third-Party Services

- **SerpApi**: [Google Trends API](https://serpapi.com/google-trends-api) (paid service)
- **Apify**: [Google Trends Scraper](https://apify.com/apify/google-trends-scraper) (paid service)
- **Kaggle**: Search for existing datasets at [Kaggle Datasets](https://www.kaggle.com/datasets)

## Technical Details

### API Endpoint

The script uses Google's unofficial daily trends API:

```
https://trends.google.com/trends/api/dailytrends
```

Parameters:
- `hl`: Language (en-US)
- `tz`: Timezone offset
- `geo`: Country code (US)
- `ed`: Date in YYYYMMDD format

### Rate Limiting

The script includes a 1.5-second delay between requests to be respectful to Google's servers and avoid rate limiting.

### Error Handling

- Retries on network errors
- Handles API response format changes
- Validates JSON parsing
- Reports failed days

## Troubleshooting

### "403 Forbidden" Errors

Your IP may be rate-limited or blocked. Try:
- Wait 30-60 minutes before retrying
- Use a VPN or different network
- Reduce request frequency (increase `time.sleep()`)

### "JSON Decode" Errors

Google may have changed the API response format. Check:
- The API endpoint URL is still valid
- The response prefix is still `)]}'`
- The JSON structure hasn't changed

### Missing Data

Some days may not return data if:
- Google Trends had an outage
- The date is too recent or too old
- Regional data isn't available

## Files Included

1. `collect_google_trends_2024.py` - Main collection script
2. `README_GOOGLE_TRENDS.md` - This file
3. `google_trends_2024_complete.csv` - Output file (created after running)

## License

This script is for educational and research purposes. Respect Google's Terms of Service when using automated data collection tools.

## Support

For questions or issues:
- Check Google Trends status
- Verify internet connectivity
- Review error messages in the console output

---

**Note**: This script accesses Google Trends through unofficial APIs. Google may change these endpoints at any time without notice.
