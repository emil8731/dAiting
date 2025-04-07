"""
Base profile scraper module for dating platforms.
Provides abstract classes and common functionality for platform-specific profile scraping.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

from .auth import BaseAuthenticator

# Configure logging
logger = logging.getLogger('platform.scraper')

class ScrapingError(Exception):
    """Exception raised for scraping errors."""
    pass

class BaseProfileScraper(ABC):
    """Abstract base class for platform profile scrapers."""
    
    def __init__(self, authenticator: BaseAuthenticator):
        """
        Initialize the profile scraper.
        
        Args:
            authenticator: Platform-specific authenticator
        """
        self.authenticator = authenticator
        if not self.authenticator.is_authenticated():
            logger.warning("Authenticator is not authenticated. Scraping may fail.")
    
    @abstractmethod
    def get_user_profile(self) -> Dict[str, Any]:
        """
        Get the authenticated user's profile.
        
        Returns:
            Dict: User profile data
        """
        pass
    
    @abstractmethod
    def get_matches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the user's matches.
        
        Args:
            limit: Maximum number of matches to retrieve
            
        Returns:
            List[Dict]: List of match profiles
        """
        pass
    
    @abstractmethod
    def get_match_profile(self, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific match's profile.
        
        Args:
            match_id: ID of the match
            
        Returns:
            Dict or None: Match profile data if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the user's conversations.
        
        Args:
            limit: Maximum number of conversations to retrieve
            
        Returns:
            List[Dict]: List of conversations
        """
        pass
    
    @abstractmethod
    def get_conversation_messages(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get messages from a specific conversation.
        
        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of messages to retrieve
            
        Returns:
            List[Dict]: List of messages
        """
        pass
    
    def normalize_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize profile data to a standard format.
        
        Args:
            profile_data: Raw profile data from the platform
            
        Returns:
            Dict: Normalized profile data
        """
        # Default implementation returns the original data
        # Platform-specific implementations should override this
        return profile_data
    
    def extract_interests(self, profile_data: Dict[str, Any]) -> List[str]:
        """
        Extract interests from profile data.
        
        Args:
            profile_data: Raw or normalized profile data
            
        Returns:
            List[str]: List of interests
        """
        # Default implementation returns an empty list
        # Platform-specific implementations should override this
        return []
    
    def extract_bio(self, profile_data: Dict[str, Any]) -> str:
        """
        Extract bio/about text from profile data.
        
        Args:
            profile_data: Raw or normalized profile data
            
        Returns:
            str: Bio text
        """
        # Default implementation returns an empty string
        # Platform-specific implementations should override this
        return ""
