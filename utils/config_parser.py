"""
Configuration file parser
"""
import json
import os
import configparser
from pathlib import Path

class ConfigManager:
    """
    Manager for reading and parsing configuration files
    """
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance exists"""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the configuration manager"""
        if self._initialized:
            return
            
        self.config = {}
        self.config_dir = Path('config')
        self._load_configs()
        self._initialized = True
    
    def _load_configs(self):
        """Load all configuration files"""
        # Ensure config directory exists
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)
            
        # Load database config
        db_config_path = self.config_dir / 'database.ini'
        if db_config_path.exists():
            parser = configparser.ConfigParser()
            parser.read(db_config_path)
            self.config['database'] = {
                'host': parser.get('database', 'host', fallback='10.42.10.38'),
                'user': parser.get('database', 'user', fallback='root'),
                'password': parser.get('database', 'password', fallback=''),
                'database': parser.get('database', 'database', fallback='headsets')
            }
        else:
            # Create default database config
            self.config['database'] = {
                'host': '10.42.10.38',
                'user': 'root',
                'password': '',
                'database': 'headsets'
            }
            parser = configparser.ConfigParser()
            parser.add_section('database')
            for key, value in self.config['database'].items():
                parser.set('database', key, value)
            with open(db_config_path, 'w') as f:
                parser.write(f)
        
        # Load email config
        email_config_path = self.config_dir / 'email.json'
        if email_config_path.exists():
            with open(email_config_path, 'r') as f:
                self.config['email'] = json.load(f)
        else:
            # Create default email config
            self.config['email'] = {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': 'noreply@eastwestcallcenter.com',
                'receiver_email': 'ewsupport@eastwestbpo.com',
                'cc_emails': ['pdd@eastwestbpo.com', 'operationsmanagers@eastwestbpo.com']
            }
            with open(email_config_path, 'w') as f:
                json.dump(self.config['email'], f, indent=4)
        
        # Load application settings
        app_config_path = self.config_dir / 'application.json'
        if app_config_path.exists():
            with open(app_config_path, 'r') as f:
                self.config['application'] = json.load(f)
        else:
            # Create default application settings
            self.config['application'] = {
                'window_width': 1200,
                'window_height': 960,
                'theme': 'default',
                'max_login_attempts': 3,
                'session_timeout_minutes': 30,
                'debug_mode': False
            }
            with open(app_config_path, 'w') as f:
                json.dump(self.config['application'], f, indent=4)
    
    def get_database_config(self):
        """
        Get database configuration
        
        Returns:
            dict: Database configuration
        """
        return self.config.get('database', {})
    
    def get_email_config(self):
        """
        Get email configuration
        
        Returns:
            dict: Email configuration
        """
        return self.config.get('email', {})
    
    def get_application_config(self):
        """
        Get application settings
        
        Returns:
            dict: Application settings
        """
        return self.config.get('application', {})
    
    def update_config(self, section, key, value):
        """
        Update a configuration value
        
        Args:
            section (str): Configuration section
            key (str): Configuration key
            value: New value
            
        Returns:
            bool: True if successful, False otherwise
        """
        if section not in self.config:
            return False
            
        self.config[section][key] = value
        
        # Update the configuration file
        if section == 'database':
            parser = configparser.ConfigParser()
            parser.add_section('database')
            for k, v in self.config['database'].items():
                parser.set('database', k, str(v))
            with open(self.config_dir / 'database.ini', 'w') as f:
                parser.write(f)
        elif section in ['email', 'application']:
            with open(self.config_dir / f'{section}.json', 'w') as f:
                json.dump(self.config[section], f, indent=4)
        else:
            return False
            
        return True