"""
Tinder-specific authentication module.
Implements authentication for the Tinder platform.
"""

import requests
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from .auth import BaseAuthenticator, AuthenticationError

logger = logging.getLogger('platform.tinder_auth')

class TinderAuthenticator(BaseAuthenticator):
    """Authenticator for the Tinder platform."""
    
    BASE_URL = "https://api.gotinder.com"
    
    def __init__(self, credentials_file: str = None):
        """
        Initialize the Tinder authenticator.
        
        Args:
            credentials_file: Path to the credentials file
        """
        super().__init__(credentials_file)
    
    def _build_auth_headers(self) -> Dict[str, str]:
        """Build Tinder-specific authentication headers."""
        return {
            "X-Auth-Token": self.token,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def authenticate(self, token: str = None, **kwargs) -> bool:
        """
        Authenticate with Tinder using an X-Auth-Token.
        
        Args:
            token: X-Auth-Token obtained from browser network inspection
            **kwargs: Additional arguments
            
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        if token:
            # Use provided token
            self.token = token
        elif 'token' in self.credentials:
            # Use stored token
            self.token = self.credentials.get('token')
        else:
            raise AuthenticationError("No authentication token provided. Please provide a token.")
        
        # Verify the token by making a test request
        try:
            response = requests.get(
                f"{self.BASE_URL}/profile",
                headers=self._build_auth_headers()
            )
            
            if response.status_code == 200:
                # Token is valid, save it
                self.credentials['token'] = self.token
                # Set token expiry to 4 days from now (based on research)
                self.token_expiry = (datetime.now() + timedelta(days=4)).isoformat()
                self.credentials['token_expiry'] = self.token_expiry
                self._save_credentials()
                logger.info("Successfully authenticated with Tinder")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Request error during authentication: {str(e)}")
            return False
    
    def refresh_token(self) -> bool:
        """
        Refresh the authentication token.
        
        Note: Tinder doesn't provide a direct token refresh mechanism.
        Users need to re-authenticate with a new token.
        
        Returns:
            bool: Always False as manual re-authentication is required
        """
        logger.info("Tinder doesn't support token refresh. Manual re-authentication required.")
        return False
    
    def get_profile(self) -> Optional[Dict[str, Any]]:
        """
        Get the user's profile information.
        
        Returns:
            Dict or None: Profile information if successful, None otherwise
        """
        if not self.is_authenticated():
            logger.error("Not authenticated. Cannot get profile.")
            return None
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/profile",
                headers=self.get_auth_headers()
            )
            
            if response.status_code == 200:
                profile_data = response.json()
                logger.info("Successfully retrieved profile data")
                return profile_data
            else:
                logger.error(f"Failed to get profile: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Request error while getting profile: {str(e)}")
            return None
