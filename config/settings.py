"""
Configuration settings for IntelliQuery
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)

def get_config_value(key: str, default=None):
    """
    Get configuration value from Streamlit secrets (cloud) or environment variables (local)
    Priority: st.secrets > os.getenv > default
    """
    # Try Streamlit secrets first (Cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key in st.secrets:
            value = st.secrets[key]
            print(f"✓ Loaded {key} from Streamlit secrets")  # Debug
            return value
    except Exception as e:
        print(f"✗ Could not load {key} from Streamlit secrets: {e}")  # Debug
        pass
    
    # Fallback to environment variables (local development)
    value = os.getenv(key, default)
    if value:
        print(f"✓ Loaded {key} from environment variable")  # Debug
    else:
        print(f"✗ {key} not found in secrets or env")  # Debug
    return value

class Config:
    """Application configuration"""
    
    # Monday.com Configuration
    @property
    def MONDAY_API_KEY(self):
        return get_config_value('MONDAY_API_KEY')
    
    MONDAY_API_URL = 'https://api.monday.com/v2'
    
    @property
    def DEAL_BOARD_ID(self):
        return get_config_value('DEAL_BOARD_ID')
    
    @property
    def WORK_ORDER_BOARD_ID(self):
        return get_config_value('WORK_ORDER_BOARD_ID')
    
    # Google Gemini Configuration
    @property
    def GOOGLE_API_KEY(self):
        return get_config_value('GOOGLE_API_KEY')
    
    @property
    def GEMINI_MODEL(self):
        return get_config_value('GEMINI_MODEL', 'gemini-2.5-flash')
    
    # Application Settings
    @property
    def APP_TITLE(self):
        return get_config_value('APP_TITLE', 'IntelliQuery - Business Intelligence Agent')
    
    @property
    def DEBUG_MODE(self):
        return get_config_value('DEBUG_MODE', 'False').lower() == 'true'
    
    # Cache Settings
    CACHE_TTL = 3600  # 1 hour in seconds
    
    def validate(self):
        """Validate that all required settings are present"""
        required = {
            'MONDAY_API_KEY': self.MONDAY_API_KEY,
            'DEAL_BOARD_ID': self.DEAL_BOARD_ID,
            'WORK_ORDER_BOARD_ID': self.WORK_ORDER_BOARD_ID,
            'GOOGLE_API_KEY': self.GOOGLE_API_KEY
        }
        
        missing = [key for key, value in required.items() if not value]
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please configure these in your .env file or Streamlit secrets"
            )
        
        return True

# Create singleton instance
Config = Config()
