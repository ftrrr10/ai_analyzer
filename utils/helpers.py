"""
Helper Functions and Utilities
"""
import os
import re
from datetime import datetime
from typing import Optional
from pathlib import Path


def generate_complaint_number() -> str:
    """
    Generate unique complaint number
    Format: ADU-YYYYMMDDHHMMSS
    """
    return f"ADU-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove special characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename


def ensure_directory(directory: str) -> None:
    """
    Ensure directory exists, create if not
    
    Args:
        directory: Directory path
    """
    Path(directory).mkdir(parents=True, exist_ok=True)


def format_currency(amount: float) -> str:
    """
    Format number as Indonesian Rupiah
    
    Args:
        amount: Amount in rupiah
        
    Returns:
        Formatted string
    """
    return f"Rp {amount:,.0f}".replace(',', '.')


def parse_date(date_string: str) -> Optional[str]:
    """
    Parse various date formats to ISO format (YYYY-MM-DD)
    
    Args:
        date_string: Date in various formats
        
    Returns:
        ISO formatted date string or None
    """
    date_formats = [
        '%Y-%m-%d',
        '%d-%m-%Y',
        '%d/%m/%Y',
        '%d %B %Y',
        '%d %b %Y'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_string, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    return None


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to max length
    
    Args:
        text: Original text
        max_length: Maximum length
        
    Returns:
        Truncated text with ellipsis
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + '...'


def print_separator(char: str = '=', length: int = 70) -> None:
    """Print a separator line"""
    print(char * length)


def print_section_header(title: str) -> None:
    """Print formatted section header"""
    print_separator()
    print(f"  {title}")
    print_separator()
