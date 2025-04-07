"""
Base authentication module for dating platforms.
Provides abstract classes and common functionality for platform-specific authentication.
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='dating_app.log'
)
logger = logging.getLogger('platform.auth')

class AuthenticationError(Exception):
    """Exception raised for authentication errors."""
    pass

class BaseAuthenticator(ABC):
    """Abstract base class for platform authenticators."""
    
    def __init__(self, credentials_file: str = None):
        """
        Initialize the authenticator.
        
        Args:
            credentials_file: Path to the credentials file
        """
        self.credentials_file = credentials_file or self._get_default_credentials_file()
        self.credentials = self._load_credentials()
        self.token = self.credentials.get('token')
        self.token_expiry = self.credentials.get('token_expiry')
    
    def _get_default_credentials_file(self) -> str:
        """Get the default credentials file path."""
        platform_name = self.__class__.__name__.lower().replace('authenticator', '')
        return os.path.join(os.path.expanduser('~'), f'.{platform_name}_credentials.json')
    
    def _load_credentials(self) -> Dict[str, Any]:
        """Load credentials from file if it exists."""
        if not os.path.exists(self.credentials_file):
            logger.info(f"Credentials file {self.credentials_file} not found. Starting with empty credentials.")
            return {}
        
        try:
            with open(self.credentials_file, 'r') as f:
                credentials = json.load(f)
                logger.info(f"Loaded credentials from {self.credentials_file}")
                return credentials
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading credentials: {str(e)}")
            return {}
    
    def _save_credentials(self) -> None:
        """Save credentials to file."""
        try:
            os.makedirs(os.path.dirname(self.credentials_file), exist_ok=True)
            with open(self.credentials_file, 'w') as f:
                json.dump(self.credentials, f)
                logger.info(f"Saved credentials to {self.credentials_file}")
        except IOError as e:
            logger.error(f"Error saving credentials: {str(e)}")
            raise AuthenticationError(f"Failed to save credentials: {str(e)}")
    
    def is_authenticated(self) -> bool:
        """Check if the current token is valid and not expired."""
        if not self.token:
            logger.info("No authentication token found")
            return False
        
        if not self.token_expiry:
            logger.info("No token expiry information found")
            return False
        
        # Parse token expiry and check if it's still valid
        try:
            expiry = datetime.fromisoformat(self.token_expiry)
            if expiry <= datetime.now():
                logger.info(f"Token expired at {expiry}")
                return False
            
            logger.info(f"Token valid until {expiry}")
            return True
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing token expiry: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        if not self.is_authenticated():
            raise AuthenticationError("Not authenticated. Please authenticate first.")
        
        return self._build_auth_headers()
    
    @abstractmethod
    def _build_auth_headers(self) -> Dict[str, str]:
        """Build platform-specific authentication headers."""
        pass
    
    @abstractmethod
    def authenticate(self, **kwargs) -> bool:
        """
        Authenticate with the platform.
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def refresh_token(self) -> bool:
        """
        Refresh the authentication token.
        
        Returns:
            bool: True if token refresh was successful, False otherwise
        """
        pass
    
    def logout(self) -> bool:
        """
        Log out from the platform.
        
        Returns:
            bool: True if logout was successful, False otherwise
        """
        self.token = None
        self.token_expiry = None
        self.credentials = {}
        self._save_credentials()
        logger.info("Logged out successfully")
        return True
