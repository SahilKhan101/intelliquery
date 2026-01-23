"""
Configuration settings for IntelliQuery
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)

# Try to import streamlit for cloud deployment
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

def get_config_value(key: str, default=None):
    """
    Get configuration value from Streamlit secrets (cloud) or environment variables (local)
    Priority: st.secrets > os.getenv > default
    """
    if HAS_STREAMLIT:
        try:
            return st.secrets.get(key, os.getenv(key, default))
        except:
            return os.getenv(key, default)
    return os.getenv(key, default)

class Config:
    """Application configuration"""
    
    # Monday.com Configuration
    MONDAY_API_KEY = get_config_value('MONDAY_API_KEY')
    MONDAY_API_URL = 'https://api.monday.com/v2'
    DEAL_BOARD_ID = get_config_value('DEAL_BOARD_ID')
    WORK_ORDER_BOARD_ID = get_config_value('WORK_ORDER_BOARD_ID')
    
    # Google Gemini Configuration
    GOOGLE_API_KEY = get_config_value('GOOGLE_API_KEY')
    GEMINI_MODEL = get_config_value('GEMINI_MODEL', 'gemini-2.5-flash')
    
    # Application Settings
    APP_TITLE = get_config_value('APP_TITLE', 'IntelliQuery - Business Intelligence Agent')
    DEBUG_MODE = get_config_value('DEBUG_MODE', 'False').lower() == 'true'
    
    # Cache Settings
    CACHE_TTL = 3600  # 1 hour in seconds
    
    @classmethod
    def validate(cls):
        """Validate that all required settings are present"""
        required = [
            'MONDAY_API_KEY',
            'DEAL_BOARD_ID',
            'WORK_ORDER_BOARD_ID',
            'GOOGLE_API_KEY'
        ]
        
        missing = []
        for key in required:
            if not getattr(cls, key):
                missing.append(key)
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please configure these in your .env file or Streamlit secrets"
            )
        
        return True
