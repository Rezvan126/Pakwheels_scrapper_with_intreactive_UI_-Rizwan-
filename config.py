"""
Configuration file for PakWheels scraper
"""

import os

# Base URL for PakWheels (update this with the actual URL)
BASE_URL = os.getenv("PAKWHEELS_URL", "https://www.pakwheels.com/used-cars/search/-/ct_islamabad/")

# Scraping configuration
MAX_PAGES = 10
REQUEST_DELAY = 2  # seconds between requests
TIMEOUT = 30  # request timeout in seconds

# User agent to mimic a real browser
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Headers for requests
HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Output configuration
OUTPUT_FILE = "pakwheels_cars_data.csv"

# CSV column headers
CSV_HEADERS = [
    'Car Model',
    'Color',
    'Transmission',
    'Mileage',
    'Model Year',
    'Registration City',
    'Price',
    'URL'
]
