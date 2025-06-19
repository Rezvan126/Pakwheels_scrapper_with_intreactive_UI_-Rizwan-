"""
Web interface for PakWheels scraper
Provides a simple web UI to configure and run the scraper
"""

from flask import Flask, render_template, request, jsonify, send_file
import threading
import os
import json
from typing import Optional, List, Dict
from pakwheels_scraper import PakWheelsScraper
from config import *
import logging

app = Flask(__name__)

# Global variables to track scraping status
scraping_status = {
    'is_running': False,
    'progress': 0,
    'total_pages': 0,
    'current_page': 0,
    'cars_found': 0,
    'message': 'Ready to start scraping'
}

class WebScraper(PakWheelsScraper):
    """Extended scraper class for web interface"""
    
    def __init__(self):
        super().__init__()
        self.web_status = scraping_status
    
    def scrape_page(self, page_num: int, custom_url: Optional[str] = None):
        """Override to update web status"""
        self.web_status['current_page'] = page_num
        self.web_status['progress'] = (page_num / self.web_status['total_pages']) * 100
        self.web_status['message'] = f'Scraping page {page_num} of {self.web_status["total_pages"]}'
        
        cars_data = super().scrape_page(page_num, custom_url)
        self.web_status['cars_found'] += len(cars_data)
        
        return cars_data
    
    def run_web_scraping(self, max_pages=MAX_PAGES, base_url=BASE_URL):
        """Run scraping with web status updates"""
        global scraping_status
        
        try:
            scraping_status['is_running'] = True
            scraping_status['total_pages'] = max_pages
            scraping_status['current_page'] = 0
            scraping_status['cars_found'] = 0
            scraping_status['message'] = 'Starting scraper...'
            
            # Log the URL being used for scraping
            self.logger.info(f"Starting scraping with URL: {base_url}")
            
            # Scrape data with custom URL support
            all_data = self.scrape_multiple_pages(max_pages, base_url)
            
            if all_data:
                self.save_to_csv(all_data)
                scraping_status['message'] = f'Scraping completed! Found {len(all_data)} cars. Data saved to {OUTPUT_FILE}'
            else:
                scraping_status['message'] = 'Scraping completed but no data found. Please check the URL and filters.'
                
        except Exception as e:
            scraping_status['message'] = f'Error during scraping: {str(e)}'
            self.logger.error(f"Web scraping error: {str(e)}")
        finally:
            scraping_status['is_running'] = False
            scraping_status['progress'] = 100

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/start_scraping', methods=['POST'])
def start_scraping():
    """Start the scraping process"""
    global scraping_status
    
    if scraping_status['is_running']:
        return jsonify({'error': 'Scraping is already in progress'})
    
    try:
        data = request.get_json()
        max_pages = min(int(data.get('pages', MAX_PAGES)), 400)  # Limit to 400 pages max
        base_url = data.get('url', BASE_URL).strip()
        
        # Validate URL
        if not base_url.startswith('http'):
            return jsonify({'error': 'Invalid URL format'})
        
        # Start scraping in background thread
        scraper = WebScraper()
        thread = threading.Thread(
            target=scraper.run_web_scraping,
            args=(max_pages, base_url)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': 'Scraping started'})
        
    except Exception as e:
        return jsonify({'error': f'Failed to start scraping: {str(e)}'})

@app.route('/status')
def get_status():
    """Get current scraping status"""
    return jsonify(scraping_status)

@app.route('/download')
def download_csv():
    """Download the scraped data CSV file"""
    if os.path.exists(OUTPUT_FILE):
        return send_file(OUTPUT_FILE, as_attachment=True)
    else:
        return jsonify({'error': 'No data file found'}), 404

@app.route('/logs')
def get_logs():
    """Get recent log entries"""
    try:
        if os.path.exists('scraper.log'):
            with open('scraper.log', 'r') as f:
                lines = f.readlines()
                # Return last 50 lines
                recent_logs = lines[-50:] if len(lines) > 50 else lines
                return jsonify({'logs': recent_logs})
        else:
            return jsonify({'logs': []})
    except Exception as e:
        return jsonify({'error': f'Failed to read logs: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
