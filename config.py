"""
Configuration settings for Amazon Ads Automation Platform
"""
import os
from typing import Dict, Any

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'amazon-ads-automation-secret-key'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # OpenAI settings
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_GEN_MODEL', 'gpt-4o-mini')
    
    # Embedding settings
    EMBEDDING_BACKEND = os.environ.get('EMBEDDING_BACKEND')
    EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL')
    
    # Application settings
    MAX_KEYWORDS_PER_SEGMENT = 20
    DEFAULT_TOP_K = 10
    DEFAULT_KEYWORD_WEIGHT = 0.4
    
    # File paths
    DATA_DIR = 'Data'
    PUBLIC_DIR = 'public'
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate required configuration settings"""
        missing = []
        required_vars = ['OPENAI_API_KEY', 'EMBEDDING_BACKEND', 'EMBEDDING_MODEL']
        
        for var in required_vars:
            if not getattr(cls, var):
                missing.append(var)
        
        return {
            'valid': len(missing) == 0,
            'missing': missing,
            'config_status': 'Complete' if len(missing) == 0 else 'Incomplete'
        }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}