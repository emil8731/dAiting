"""
Platform factory module for creating platform-specific components.
Provides a unified interface for creating authenticators and scrapers.
"""

import logging
from typing import Dict, Any, Optional, Union

from .auth import BaseAuthenticator
from .scraper import BaseProfileScraper
from .tinder_auth import TinderAuthenticator
from .tinder_scraper import TinderProfileScraper
from .hinge_auth import HingeAuthenticator
from .hinge_scraper import HingeProfileScraper

logger = logging.getLogger('platform.factory')

class PlatformFactory:
    """Factory for creating platform-specific components."""
    
    @staticmethod
    def create_authenticator(platform: str, credentials_file: str = None) -> BaseAuthenticator:
        """
        Create a platform-specific authenticator.
        
        Args:
            platform: Platform name ('tinder' or 'hinge')
            credentials_file: Path to credentials file
            
        Returns:
            BaseAuthenticator: Platform-specific authenticator
            
        Raises:
            ValueError: If platform is not supported
        """
        platform = platform.lower()
        
        if platform == 'tinder':
            return TinderAuthenticator(credentials_file)
        elif platform == 'hinge':
            return HingeAuthenticator(credentials_file)
        else:
            logger.error(f"Unsupported platform: {platform}")
            raise ValueError(f"Unsupported platform: {platform}")
    
    @staticmethod
    def create_scraper(platform: str, authenticator: Optional[BaseAuthenticator] = None, 
                      credentials_file: str = None) -> BaseProfileScraper:
        """
        Create a platform-specific profile scraper.
        
        Args:
            platform: Platform name ('tinder' or 'hinge')
            authenticator: Platform-specific authenticator (optional)
            credentials_file: Path to credentials file (used if authenticator not provided)
            
        Returns:
            BaseProfileScraper: Platform-specific profile scraper
            
        Raises:
            ValueError: If platform is not supported
        """
        platform = platform.lower()
        
        # Create authenticator if not provided
        if authenticator is None:
            authenticator = PlatformFactory.create_authenticator(platform, credentials_file)
        
        # Ensure authenticator is for the correct platform
        if platform == 'tinder' and not isinstance(authenticator, TinderAuthenticator):
            logger.warning("Provided authenticator is not a TinderAuthenticator. Creating new authenticator.")
            authenticator = TinderAuthenticator(credentials_file)
        elif platform == 'hinge' and not isinstance(authenticator, HingeAuthenticator):
            logger.warning("Provided authenticator is not a HingeAuthenticator. Creating new authenticator.")
            authenticator = HingeAuthenticator(credentials_file)
        
        # Create and return the appropriate scraper
        if platform == 'tinder':
            return TinderProfileScraper(authenticator)
        elif platform == 'hinge':
            return HingeProfileScraper(authenticator)
        else:
            logger.error(f"Unsupported platform: {platform}")
            raise ValueError(f"Unsupported platform: {platform}")
