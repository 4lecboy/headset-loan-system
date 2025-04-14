"""
Environment variable loader utility
"""
import os
from pathlib import Path
from dotenv import load_dotenv

def load_env():
    """
    Load environment variables from .env file
    
    Returns:
        bool: True if the file was loaded, False otherwise
    """
    # Find the .env file in the project root
    env_path = Path('.') / '.env'
    
    # Load the .env file
    return load_dotenv(dotenv_path=env_path)

def get_env(key, default=None):
    """
    Get environment variable value
    
    Args:
        key (str): Environment variable name
        default: Default value if not found
        
    Returns:
        str: Environment variable value or default
    """
    return os.environ.get(key, default)