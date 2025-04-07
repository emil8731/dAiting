"""
Hinge-specific authentication module.
Implements authentication for the Hinge platform.
"""

import requests
import logging
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from .auth import BaseAuthenticator, AuthenticationError

logger = logging.getLogger('platform.hinge_auth')

class HingeAuthenticator(BaseAuthenticator):
    """Authenticator for the Hinge platform."""
    
    BASE_URL = "https://prod-api.hingeaws.net"
    FIREBASE_API_KEY = "AIzaSyBBKvSaXe0Lx-XwrYYJlwRhGcHW0njxqXE"  # Public key from app
    
    def __init__(self, credentials_file: str = None):
        """
        Initialize the Hinge authenticator.
        
        Args:
            credentials_file: Path to the credentials file
        """
        super().__init__(credentials_file)
        self.install_id = self.credentials.get('install_id', str(uuid.uuid4()))
        
    def _build_auth_headers(self) -> Dict[str, str]:
        """Build Hinge-specific authentication headers."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Install-Id": self.install_id
        }
    
    def authenticate(self, phone_number: str = None, verification_code: str = None, **kwargs) -> bool:
        """
        Authenticate with Hinge using phone number and verification code.
        
        Args:
            phone_number: User's phone number in international format (e.g., +15555555555)
            verification_code: SMS verification code received
            **kwargs: Additional arguments
            
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        # If we already have a valid token, return True
        if self.is_authenticated():
            logger.info("Already authenticated with Hinge")
            return True
            
        # Check if we have stored credentials
        if not phone_number and 'phone_number' in self.credentials:
            phone_number = self.credentials.get('phone_number')
            
        if not phone_number:
            raise AuthenticationError("Phone number is required for authentication")
            
        # Step 1: Register installation if needed
        if 'install_id' not in self.credentials:
            self._register_installation()
            
        # Step 2: Request verification code if not provided
        if not verification_code:
            self._request_verification_code(phone_number)
            logger.info(f"Verification code requested for {phone_number}")
            return False  # Need to call authenticate again with verification code
            
        # Step 3: Verify code and get token
        try:
            response = requests.post(
                f"{self.BASE_URL}/identity/verify",
                headers={
                    "Content-Type": "application/json",
                    "X-Install-Id": self.install_id
                },
                json={
                    "phone_number": phone_number,
                    "verification_code": verification_code
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                
                if not self.token:
                    logger.error("Authentication response did not contain token")
                    return False
                    
                # Set token expiry to 3 days from now (based on research)
                self.token_expiry = (datetime.now() + timedelta(days=3)).isoformat()
                
                # Save credentials
                self.credentials['token'] = self.token
                self.credentials['token_expiry'] = self.token_expiry
                self.credentials['phone_number'] = phone_number
                self.credentials['install_id'] = self.install_id
                self._save_credentials()
                
                logger.info("Successfully authenticated with Hinge")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Request error during authentication: {str(e)}")
            return False
    
    def _register_installation(self) -> bool:
        """
        Register a new installation with Hinge.
        
        Returns:
            bool: True if registration was successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.BASE_URL}/identity/install",
                headers={
                    "Content-Type": "application/json"
                },
                json={
                    "install_id": self.install_id
                }
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully registered installation with ID {self.install_id}")
                return True
            else:
                logger.error(f"Installation registration failed: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Request error during installation registration: {str(e)}")
            return False
    
    def _request_verification_code(self, phone_number: str) -> bool:
        """
        Request a verification code to be sent to the phone number.
        
        Args:
            phone_number: User's phone number in international format
            
        Returns:
            bool: True if request was successful, False otherwise
        """
        try:
            # First, get reCAPTCHA config
            recaptcha_response = requests.post(
                f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/getRecaptchaParam",
                params={"key": self.FIREBASE_API_KEY}
            )
            
            if recaptcha_response.status_code != 200:
                logger.error(f"Failed to get reCAPTCHA config: {recaptcha_response.status_code} - {recaptcha_response.text}")
                return False
                
            # In a real implementation, we would need to solve the reCAPTCHA
            # For this prototype, we'll simulate it
            recaptcha_token = "simulated_recaptcha_token"
            
            # Request verification code
            response = requests.post(
                f"{self.BASE_URL}/identity/request",
                headers={
                    "Content-Type": "application/json",
                    "X-Install-Id": self.install_id
                },
                json={
                    "phone_number": phone_number,
                    "recaptcha_token": recaptcha_token
                }
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully requested verification code for {phone_number}")
                return True
            else:
                logger.error(f"Verification code request failed: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Request error during verification code request: {str(e)}")
            return False
    
    def refresh_token(self) -> bool:
        """
        Refresh the authentication token.
        
        Note: Hinge doesn't provide a direct token refresh mechanism.
        Users need to re-authenticate with a new verification code.
        
        Returns:
            bool: Always False as manual re-authentication is required
        """
        logger.info("Hinge doesn't support token refresh. Manual re-authentication required.")
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
