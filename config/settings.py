"""
Configuration settings for IntelliQuery
"""
# Load environment variables from project root
import os
from dotenv import load_dotenv

# Get absolute path to .env file
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)

class Config:
    """Application configuration"""
    
    # Monday.com Configuration
    MONDAY_API_KEY = os.getenv('MONDAY_API_KEY')
    MONDAY_API_URL = 'https://api.monday.com/v2'
    DEAL_BOARD_ID = os.getenv('DEAL_BOARD_ID')
    WORK_ORDER_BOARD_ID = os.getenv('WORK_ORDER_BOARD_ID')
    
    # Google Gemini Configuration
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    # Use a specific version that is known to work with the API
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash-001')
    
    # Application Settings
    APP_TITLE = os.getenv('APP_TITLE', 'IntelliQuery - Business Intelligence Agent')
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
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
                f"Missing required environment variables: {', '.join(missing)}\\n"
                f"Please configure these in your .env file"
            )
        
        return True
