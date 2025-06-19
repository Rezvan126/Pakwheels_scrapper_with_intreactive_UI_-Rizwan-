# PakWheels Car Scraper

A comprehensive web scraper for extracting car listing data from PakWheels, Pakistan's largest automotive marketplace. The application features both a command-line interface and a user-friendly web interface.

## Features

- **Web Interface**: Easy-to-use Flask-based web UI with real-time progress tracking
- **Advanced Filtering**: Filter cars by make, transmission, year range, price range, and city
- **High-Quality Data Extraction**: Uses JSON-LD structured data for accurate information
- **Real-time Progress**: Live status updates during scraping operations
- **CSV Export**: Download scraped data in CSV format
- **Responsive Design**: Modern Bootstrap UI that works on all devices

## Data Extracted

- Car Model
- Color
- Transmission Type
- Mileage
- Model Year
- Registration City
- Price
- Listing URL

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd pakwheels-scraper
```

2. Install dependencies:
```bash
pip install flask requests beautifulsoup4 lxml
```

## Usage

### Web Interface (Recommended)

1. Start the web server:
```bash
python web_interface.py
```

2. Open your browser and go to `http://localhost:5000`

3. Configure your scraping parameters:
   - Select car make (Toyota, Honda, Suzuki, etc.)
   - Choose transmission type
   - Set year and price ranges
   - Specify number of pages to scrape

4. Click "Start Scraping" and monitor progress in real-time

5. Download the CSV file when complete

### Command Line Interface

```bash
python pakwheels_scraper.py
```

## Configuration

Edit `config.py` to modify:
- Default number of pages to scrape
- Request delays
- Output file names
- Log levels

## File Structure

```
pakwheels-scraper/
├── pakwheels_scraper.py    # Core scraper logic
├── web_interface.py        # Flask web application
├── config.py              # Configuration settings
├── utils.py               # Utility functions
├── templates/             # HTML templates
│   └── index.html
├── static/               # CSS and static files
│   └── style.css
└── README.md
```

## Technical Details

- **Python 3.11+** required
- Uses **BeautifulSoup4** for HTML parsing
- **Flask** for web interface
- **JSON-LD** structured data extraction for accuracy
- Rate limiting to respect website resources

## Legal Notice

This scraper is for educational and research purposes. Please respect PakWheels' terms of service and implement appropriate rate limiting. The developers are not responsible for any misuse of this tool.

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.