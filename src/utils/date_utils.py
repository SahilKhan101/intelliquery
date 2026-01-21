"""
Date utility functions for handling Excel serial dates and date conversions
"""
from datetime import datetime, timedelta
from typing import Optional, Union
import pandas as pd


def excel_date_to_datetime(excel_date: Union[int, float, str]) -> Optional[datetime]:
    """
    Convert Excel serial date to Python datetime
    
    Excel stores dates as the number of days since 1900-01-01
    Note: Excel incorrectly treats 1900 as a leap year
    
    Args:
        excel_date: Excel serial number (e.g., 46079 = 2026-02-15)
        
    Returns:
        datetime object or None if conversion fails
        
    Examples:
        >>> excel_date_to_datetime(46079)
        datetime.datetime(2026, 2, 15, 0, 0)
        >>> excel_date_to_datetime(45680)
        datetime.datetime(2025, 1, 1, 0, 0)
    """
    if pd.isna(excel_date) or excel_date == '' or excel_date is None:
        return None
    
    try:
        # Convert to float if it's a string
        if isinstance(excel_date, str):
            excel_date = float(excel_date)
        
        # Excel epoch is 1900-01-01, but we use 1899-12-30 to account for Excel's leap year bug
        excel_epoch = datetime(1899, 12, 30)
        return excel_epoch + timedelta(days=int(excel_date))
    except (ValueError, TypeError, OverflowError):
        return None


def format_date(date_obj: Optional[datetime], format_str: str = "%Y-%m-%d") -> str:
    """
    Format datetime object to string
    
    Args:
        date_obj: datetime object
        format_str: strftime format string
        
    Returns:
        Formatted date string or empty string if None
    """
    if date_obj is None:
        return ""
    return date_obj.strftime(format_str)


def parse_date_flexible(date_value: Union[str, int, float, datetime]) -> Optional[datetime]:
    """
    Parse date from various formats (Excel serial, ISO string, datetime)
    
    Args:
        date_value: Date in any supported format
        
    Returns:
        datetime object or None
    """
    if pd.isna(date_value) or date_value is None or date_value == '':
        return None
    
    # Already a datetime
    if isinstance(date_value, datetime):
        return date_value
    
    # Try Excel serial number first (if numeric)
    if isinstance(date_value, (int, float)):
        return excel_date_to_datetime(date_value)
    
    # Try parsing as string
    if isinstance(date_value, str):
        # Try Excel serial as string
        try:
            return excel_date_to_datetime(float(date_value))
        except ValueError:
            pass
        
        # Try pandas date parser
        try:
            return pd.to_datetime(date_value)
        except (ValueError, TypeError):
            return None
    
    return None


def get_quarter(date_obj: Union[datetime, pd.Timestamp]) -> str:
    """
    Get quarter string (e.g., 'Q1 2024') from date
    """
    if not date_obj or pd.isna(date_obj):
        return "Unknown"
        
    quarter = (date_obj.month - 1) // 3 + 1
    return f"Q{quarter} {date_obj.year}"


def get_month_year(date_obj: Union[datetime, pd.Timestamp]) -> str:
    """
    Get month-year string (e.g., 'Jan 2024') from date
    """
    if not date_obj or pd.isna(date_obj):
        return "Unknown"
        
    return date_obj.strftime("%b %Y")


def days_between(date1: Optional[datetime], date2: Optional[datetime]) -> Optional[int]:
    """
    Calculate days between two dates
    
    Args:
        date1: First datetime
        date2: Second datetime
        
    Returns:
        Number of days or None if either date is None
    """
    if date1 is None or date2 is None:
        return None
    
    return abs((date2 - date1).days)


def is_overdue(target_date: Optional[datetime], reference_date: Optional[datetime] = None) -> bool:
    """
    Check if a target date is overdue relative to reference date
    
    Args:
        target_date: Date to check
        reference_date: Reference date (defaults to today)
        
    Returns:
        True if overdue, False otherwise
    """
    if target_date is None:
        return False
    
    if reference_date is None:
        reference_date = datetime.now()
    
    return target_date < reference_date
