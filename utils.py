"""
Utility functions for the PakWheels scraper
"""

import re
import logging
from typing import Optional, Dict, Any

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Clean and normalize text data"""
    if not text:
        return ""
    
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might cause CSV issues
    text = re.sub(r'[^\w\s\-\.\,\(\)]', '', text)
    
    return text

def extract_year(text: str) -> Optional[str]:
    """Extract year from text using regex"""
    if not text:
        return None
    
    # Look for 4-digit year (1900-2099)
    year_match = re.search(r'\b(19|20)\d{2}\b', text)
    return year_match.group() if year_match else None

def extract_mileage(text: str) -> Optional[str]:
    """Extract mileage from text"""
    if not text:
        return None
    
    # Look for patterns like "50,000 km" or "50000 KM"
    mileage_patterns = [
        r'(\d{1,3}(?:,\d{3})*)\s*(?:km|KM|miles|MILES)',
        r'(\d+)\s*(?:km|KM|miles|MILES)',
    ]
    
    for pattern in mileage_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return None

def extract_price(text: str) -> Optional[str]:
    """Extract price from text"""
    if not text:
        return None
    
    # Look for patterns like "PKR 1,500,000" or "Rs. 15 Lacs"
    price_patterns = [
        r'(?:PKR|Rs\.?)\s*([\d,]+(?:\.\d+)?)\s*(?:Lacs?|Crores?)?',
        r'([\d,]+(?:\.\d+)?)\s*(?:Lacs?|Crores?)',
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def normalize_car_data(data: Dict[str, Any]) -> Dict[str, str]:
    """Normalize extracted car data"""
    normalized = {}
    
    for key, value in data.items():
        if value is None:
            normalized[key] = "N/A"
        else:
            normalized[key] = clean_text(str(value))
    
    return normalized

def validate_car_data(data: Dict[str, str]) -> bool:
    """Validate if car data has minimum required fields"""
    required_fields = ['Car Model']
    
    for field in required_fields:
        if not data.get(field) or data[field] == "N/A":
            return False
    
    # Check if the car model looks like a real car listing
    car_model = data.get('Car Model', '').lower()
    
    # Filter out non-car entries
    invalid_patterns = [
        'post an ad', 'create quick alerts', 'how many used cars',
        'what is the starting price', 'what are the popular',
        'let us know whats wrong'
    ]
    
    # Check for empty or just "n/a" car models
    if not car_model or car_model in ['na', 'n/a', 'n a']:
        return False
    
    for pattern in invalid_patterns:
        if pattern and pattern in car_model:
            return False
    
    # Should contain car-related terms
    car_terms = ['for sale', 'honda', 'toyota', 'suzuki', 'hyundai', 'kia', 
                 'nissan', 'bmw', 'audi', 'mercedes', 'corolla', 'civic', 
                 'city', 'alto', 'cultus', 'prado', 'vitz', 'mehran', 'camry',
                 'hilux', 'fortuner', 'innova', 'swift', 'baleno']
    
    if any(term in car_model for term in car_terms):
        return True
    
    # If model year is present and valid, it's likely a valid car listing
    model_year = data.get('Model Year', '')
    if (model_year != 'N/A' and model_year not in ['', 'N/A'] and 
        model_year.isdigit() and 1990 <= int(model_year) <= 2025):
        return True
    
    # If transmission is specified, it's likely a car
    transmission = data.get('Transmission', '')
    if transmission != 'N/A' and transmission in ['Automatic', 'Manual', 'CVT']:
        return True
    
    return False
