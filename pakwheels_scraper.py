"""
PakWheels Car Listings Scraper

This script scrapes car listing data from PakWheels website across multiple pages
and extracts car details like model, color, transmission, mileage, year, and registration city.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import logging
import json
from typing import List, Dict, Optional
import sys
from urllib.parse import urljoin, urlparse

from config import *
from utils import *

class PakWheelsScraper:
    def __init__(self):
        self.logger = setup_logging()
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.scraped_data = []
        
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a single page"""
        try:
            self.logger.info(f"Fetching URL: {url}")
            response = self.session.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error parsing {url}: {str(e)}")
            return None
    
    def extract_car_details(self, car_element) -> Optional[Dict[str, str]]:
        """Extract car details from a car listing element"""
        try:
            car_data = {
                'Car Model': 'N/A',
                'Color': 'N/A',
                'Transmission': 'N/A',
                'Mileage': 'N/A',
                'Model Year': 'N/A',
                'Registration City': 'N/A',
                'Price': 'N/A',
                'URL': 'N/A'
            }
            
            # First try to extract from JSON-LD structured data
            json_script = car_element.find('script', {'type': 'application/ld+json'})
            if json_script and json_script.string:
                try:
                    json_data = json.loads(json_script.string.strip())
                    
                    # Extract basic info from JSON-LD
                    if json_data.get('name'):
                        car_data['Car Model'] = clean_text(json_data['name'])
                    
                    if json_data.get('modelDate'):
                        car_data['Model Year'] = str(json_data['modelDate'])
                    
                    if json_data.get('vehicleTransmission'):
                        car_data['Transmission'] = json_data['vehicleTransmission']
                    
                    if json_data.get('mileageFromOdometer'):
                        mileage_text = json_data['mileageFromOdometer']
                        mileage = extract_mileage(mileage_text)
                        if mileage:
                            car_data['Mileage'] = mileage
                        else:
                            car_data['Mileage'] = mileage_text
                    
                    if json_data.get('offers') and json_data['offers'].get('price'):
                        price = json_data['offers']['price']
                        car_data['Price'] = f"PKR {price:,}"
                    
                    if json_data.get('offers') and json_data['offers'].get('url'):
                        car_data['URL'] = json_data['offers']['url']
                    
                    # Try to extract color from JSON-LD description with context validation
                    description = json_data.get('description', '').lower()
                    import re
                    # Look for color mentioned with proper context
                    color_patterns = [
                        r'(white|black|silver|grey|gray|red|blue|green|yellow|brown|gold|beige|maroon|pearl)\s*(?:color|colour)',
                        r'(?:color|colour):\s*(white|black|silver|grey|gray|red|blue|green|yellow|brown|gold|beige|maroon|pearl)',
                    ]
                    
                    for pattern in color_patterns:
                        match = re.search(pattern, description)
                        if match:
                            car_data['Color'] = match.group(1).title()
                            break
                    
                    # Extract registration city from description or URL
                    cities = ['islamabad', 'karachi', 'lahore', 'rawalpindi', 'faisalabad',
                             'multan', 'peshawar', 'quetta', 'sialkot', 'gujranwala', 'hyderabad']
                    for city in cities:
                        if city in description or (car_data['URL'] and city in car_data['URL'].lower()):
                            car_data['Registration City'] = city.title()
                            break
                        
                except (json.JSONDecodeError, AttributeError, KeyError) as e:
                    self.logger.debug(f"Could not parse JSON-LD data: {e}")
            
            # Fix URL formatting if malformed
            if car_data['URL'] != 'N/A':
                url = car_data['URL']
                if not url.startswith('http'):
                    if url.startswith('www.pakwheels.com'):
                        car_data['URL'] = 'https://' + url
                    elif 'pakwheels.com' in url:
                        # Handle malformed URLs like 'httpswww.pakwheels.com...'
                        car_data['URL'] = 'https://www.pakwheels.com' + url.split('pakwheels.com')[-1]
            
            # Extract color from HTML content more accurately
            if car_data['Color'] == 'N/A':
                # Look for color-specific elements in the car listing
                color_found = False
                
                # Check for color in detailed specifications sections
                spec_sections = car_element.find_all(['ul', 'div', 'span'], 
                    class_=lambda x: x and any(word in str(x).lower() for word in ['detail', 'spec', 'info', 'feature']))
                
                colors = {
                    'white': ['white', 'safed'], 'black': ['black', 'kala'], 
                    'silver': ['silver', 'chandi'], 'grey': ['grey', 'gray', 'slaiti'],
                    'red': ['red', 'lal', 'maroon'], 'blue': ['blue', 'neela', 'navy'],
                    'green': ['green', 'hara'], 'yellow': ['yellow', 'peela'],
                    'brown': ['brown', 'bhura'], 'gold': ['gold', 'sona'],
                    'beige': ['beige', 'cream'], 'pearl': ['pearl']
                }
                
                for section in spec_sections:
                    section_text = section.get_text(strip=True).lower()
                    for color_name, variants in colors.items():
                        for variant in variants:
                            if variant in section_text and not color_found:
                                # Verify it's actually about color, not just containing the word
                                color_context = ['color', 'colour', 'rang', 'painted', 'finish']
                                if any(ctx in section_text for ctx in color_context) or len(section_text) < 50:
                                    car_data['Color'] = color_name.title()
                                    color_found = True
                                    break
                        if color_found:
                            break
                    if color_found:
                        break
                
                # If still not found, check the full listing text with stricter matching
                if not color_found:
                    full_text = car_element.get_text(strip=True).lower()
                    # Look for color mentioned near relevant keywords
                    import re
                    color_patterns = [
                        r'(white|black|silver|grey|gray|red|blue|green|yellow|brown|gold|beige|pearl)\s*(?:color|colour|painted)',
                        r'(?:color|colour):\s*(white|black|silver|grey|gray|red|blue|green|yellow|brown|gold|beige|pearl)',
                        r'(white|black|silver|grey|gray|red|blue|green|yellow|brown|gold|beige|pearl)\s*(?:exterior|body)',
                    ]
                    
                    for pattern in color_patterns:
                        match = re.search(pattern, full_text)
                        if match:
                            car_data['Color'] = match.group(1).title()
                            break
            
            return normalize_car_data(car_data)
            
        except Exception as e:
            self.logger.error(f"Error extracting car details: {str(e)}")
            return None
    
    def scrape_page(self, page_num: int, custom_url: Optional[str] = None) -> List[Dict[str, str]]:
        """Scrape a single page and return list of car data"""
        if custom_url:
            base_url = custom_url
        else:
            base_url = BASE_URL
            
        if page_num == 1:
            url = base_url
        else:
            # Handle pagination for filtered URLs
            if base_url.endswith('/'):
                url = f"{base_url}?page={page_num}"
            else:
                url = f"{base_url}/?page={page_num}"
        
        soup = self.get_page(url)
        if not soup:
            return []
        
        cars_data = []
        
        # Target the specific PakWheels car listing structure
        car_elements = soup.select('li.classified-listing')
        
        if car_elements:
            self.logger.info(f"Found {len(car_elements)} car listings using PakWheels selector")
        else:
            # Fallback selectors if the structure changes
            fallback_selectors = [
                'li[data-listing-id]',
                '.search-results li',
                '.classified-listing',
                'li[id*="main_ad"]'
            ]
            
            for selector in fallback_selectors:
                car_elements = soup.select(selector)
                if car_elements:
                    self.logger.info(f"Found {len(car_elements)} car listings using fallback selector: {selector}")
                    break
            
            if not car_elements:
                self.logger.warning(f"No car listings found on page {page_num}")
                return []
        
        for idx, car_element in enumerate(car_elements):
            try:
                car_data = self.extract_car_details(car_element)
                if car_data and validate_car_data(car_data):
                    cars_data.append(car_data)
                    self.logger.info(f"Extracted car {idx + 1}: {car_data['Car Model']}")
                else:
                    self.logger.warning(f"Invalid or incomplete car data for listing {idx + 1}")
                    
            except Exception as e:
                self.logger.error(f"Error processing car listing {idx + 1}: {str(e)}")
                continue
        
        self.logger.info(f"Page {page_num}: Successfully extracted {len(cars_data)} car listings")
        return cars_data
    
    def scrape_multiple_pages(self, max_pages: int = MAX_PAGES, custom_url: Optional[str] = None) -> List[Dict[str, str]]:
        """Scrape multiple pages and return all car data"""
        all_cars_data = []
        
        for page_num in range(1, max_pages + 1):
            self.logger.info(f"Scraping page {page_num} of {max_pages}")
            
            try:
                page_data = self.scrape_page(page_num, custom_url)
                all_cars_data.extend(page_data)
                
                self.logger.info(f"Page {page_num} completed. Total cars scraped so far: {len(all_cars_data)}")
                
                # Add delay between requests
                if page_num < max_pages:
                    time.sleep(REQUEST_DELAY)
                    
            except Exception as e:
                self.logger.error(f"Error scraping page {page_num}: {str(e)}")
                continue
        
        return all_cars_data
    
    def save_to_csv(self, data: List[Dict[str, str]], filename: str = OUTPUT_FILE):
        """Save scraped data to CSV file"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
                writer.writeheader()
                writer.writerows(data)
            
            self.logger.info(f"Data saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving data to CSV: {str(e)}")
    
    def generate_summary(self, data: List[Dict[str, str]]):
        """Generate and print summary of scraped data"""
        if not data:
            self.logger.info("No data to summarize")
            return
        
        total_cars = len(data)
        
        # Count by transmission type
        transmission_counts = {}
        for car in data:
            transmission = car.get('Transmission', 'N/A')
            transmission_counts[transmission] = transmission_counts.get(transmission, 0) + 1
        
        # Count by registration city
        city_counts = {}
        for car in data:
            city = car.get('Registration City', 'N/A')
            city_counts[city] = city_counts.get(city, 0) + 1
        
        print("\n" + "="*50)
        print("SCRAPING SUMMARY REPORT")
        print("="*50)
        print(f"Total cars scraped: {total_cars}")
        print(f"Output file: {OUTPUT_FILE}")
        
        print(f"\nTransmission breakdown:")
        for transmission, count in sorted(transmission_counts.items()):
            print(f"  {transmission}: {count}")
        
        print(f"\nRegistration city breakdown:")
        for city, count in sorted(city_counts.items()):
            print(f"  {city}: {count}")
        
        print("="*50)
    
    def run(self):
        """Main method to run the scraper"""
        self.logger.info("Starting PakWheels scraper")
        self.logger.info(f"Target pages: {MAX_PAGES}")
        self.logger.info(f"Base URL: {BASE_URL}")
        
        try:
            # Scrape data
            all_data = self.scrape_multiple_pages()
            
            if all_data:
                # Save to CSV
                self.save_to_csv(all_data)
                
                # Generate summary
                self.generate_summary(all_data)
                
                self.logger.info("Scraping completed successfully")
            else:
                self.logger.warning("No data was scraped. Please check the URL and selectors.")
                
        except Exception as e:
            self.logger.error(f"Fatal error during scraping: {str(e)}")
            sys.exit(1)

def main():
    """Main function"""
    scraper = PakWheelsScraper()
    scraper.run()

if __name__ == "__main__":
    main()
