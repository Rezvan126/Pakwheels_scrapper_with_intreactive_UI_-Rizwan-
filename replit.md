# PakWheels Car Scraper

## Overview

This is a web-based car scraper application designed to extract vehicle listing data from PakWheels, a popular Pakistani automotive marketplace. The application provides both a command-line scraper and a Flask-based web interface for easy configuration and monitoring of scraping operations.

## System Architecture

### Frontend Architecture
- **Framework**: Bootstrap 5.1.3 with Font Awesome icons
- **Structure**: Single-page application with responsive design
- **Interface**: HTML template with AJAX-based status updates
- **Styling**: Custom CSS with gradient backgrounds and hover effects

### Backend Architecture
- **Framework**: Flask web framework
- **Language**: Python 3.11
- **Structure**: Modular design with separate configuration, utilities, and scraper components
- **Threading**: Multi-threaded approach for non-blocking web interface during scraping operations

### Data Extraction
- **Web Scraping**: BeautifulSoup4 with requests for HTML parsing
- **Alternative Parser**: Trafilatura integration for robust content extraction
- **Rate Limiting**: Configurable delays between requests to respect website resources

## Key Components

### Core Modules
1. **pakwheels_scraper.py**: Main scraper class with page fetching and data extraction logic
2. **web_interface.py**: Flask application providing web UI and API endpoints
3. **config.py**: Centralized configuration management
4. **utils.py**: Utility functions for text processing and logging

### Data Models
The scraper extracts the following car attributes:
- Car Model
- Color
- Transmission type
- Mileage
- Model Year
- Registration City
- Price
- Listing URL

### Web Interface Features
- Real-time scraping progress tracking
- Configurable URL and page limits
- Status dashboard with statistics
- CSV download functionality
- Responsive Bootstrap UI

## Data Flow

1. **Configuration**: User sets scraping parameters via web interface or config file
2. **Initialization**: WebScraper class extends base PakWheelsScraper with status updates
3. **Page Fetching**: Sequential page requests with configurable delays
4. **Data Extraction**: BeautifulSoup parsing to extract structured car data
5. **Progress Tracking**: Real-time status updates through global state management
6. **Output Generation**: CSV file creation with extracted data
7. **Download**: Web interface provides direct CSV download

## External Dependencies

### Core Libraries
- **requests**: HTTP client for web scraping
- **beautifulsoup4**: HTML parsing and data extraction
- **flask**: Web framework for user interface
- **lxml**: XML/HTML parser backend

### Additional Dependencies
- **trafilatura**: Advanced content extraction
- **babel**: Internationalization support
- **certifi**: SSL certificate management

## Deployment Strategy

### Development Environment
- **Runtime**: Python 3.11 with Nix package management
- **Port**: Flask development server on port 5000
- **Process**: Single-threaded with background scraping tasks

### Production Considerations
- **Scalability**: Current design supports single-user operation
- **Performance**: Rate-limited to respect target website resources
- **Monitoring**: File-based logging with console output
- **Error Handling**: Comprehensive exception handling with graceful degradation

### Replit Configuration
- **Environment**: Nix-based Python 3.11 setup
- **Workflow**: Automated startup via .replit configuration
- **Dependencies**: UV lock file for reproducible builds

## Changelog

- June 18, 2025: Initial setup
- June 18, 2025: Fixed data extraction issues - improved scraper to use JSON-LD structured data from PakWheels for high-quality car information extraction, implemented better validation logic to filter out non-car listings, enhanced color extraction and URL formatting

## User Preferences

Preferred communication style: Simple, everyday language.