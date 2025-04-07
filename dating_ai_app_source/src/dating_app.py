"""
Main module for the dating app AI assistant.
Provides a unified interface for the application functionality.
"""

import os
import logging
import uuid
from typing import Dict, List, Any, Optional

from src.platform.factory import PlatformFactory
from src.storage import DataStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='dating_app.log'
)
logger = logging.getLogger('dating_app')

class DatingAppAI:
    """Main class for the dating app AI assistant."""
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the dating app AI assistant.
        
        Args:
            storage_path: Path to the storage database
        """
        self.storage = DataStorage(storage_path)
        self.platform_factory = PlatformFactory()
        self.authenticators = {}
        self.scrapers = {}
        
        logger.info("Dating App AI Assistant initialized")
    
    def authenticate_platform(self, platform: str, **auth_params) -> bool:
        """
        Authenticate with a dating platform.
        
        Args:
            platform: Platform name ('tinder' or 'hinge')
            **auth_params: Platform-specific authentication parameters
            
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        try:
            # Create authenticator if not already created
            if platform not in self.authenticators:
                self.authenticators[platform] = self.platform_factory.create_authenticator(platform)
            
            # Authenticate
            result = self.authenticators[platform].authenticate(**auth_params)
            
            if result:
                logger.info(f"Successfully authenticated with {platform}")
                
                # Create scraper if authentication was successful
                self.scrapers[platform] = self.platform_factory.create_scraper(
                    platform, self.authenticators[platform]
                )
            else:
                logger.warning(f"Authentication with {platform} failed")
                
            return result
            
        except Exception as e:
            logger.error(f"Error authenticating with {platform}: {str(e)}")
            return False
    
    def is_authenticated(self, platform: str) -> bool:
        """
        Check if authenticated with a platform.
        
        Args:
            platform: Platform name
            
        Returns:
            bool: True if authenticated, False otherwise
        """
        return (
            platform in self.authenticators and 
            self.authenticators[platform].is_authenticated()
        )
    
    def get_user_profile(self, platform: str) -> Optional[Dict[str, Any]]:
        """
        Get the user's profile from a platform.
        
        Args:
            platform: Platform name
            
        Returns:
            Dict or None: User profile if available, None otherwise
        """
        if not self.is_authenticated(platform):
            logger.warning(f"Not authenticated with {platform}")
            return None
        
        try:
            profile = self.scrapers[platform].get_user_profile()
            logger.info(f"Retrieved user profile from {platform}")
            return profile
        except Exception as e:
            logger.error(f"Error getting user profile from {platform}: {str(e)}")
            return None
    
    def get_matches(self, platform: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get matches from a platform.
        
        Args:
            platform: Platform name
            limit: Maximum number of matches to retrieve
            
        Returns:
            List[Dict]: List of matches
        """
        if not self.is_authenticated(platform):
            logger.warning(f"Not authenticated with {platform}")
            return []
        
        try:
            matches = self.scrapers[platform].get_matches(limit)
            logger.info(f"Retrieved {len(matches)} matches from {platform}")
            
            # Normalize and store matches
            normalized_matches = []
            for match in matches:
                normalized = self.scrapers[platform].normalize_profile(match)
                normalized['platform'] = platform
                normalized['platform_id'] = match.get('_id', match.get('id', ''))
                
                # Store in database
                self.storage.save_match(normalized)
                
                normalized_matches.append(normalized)
            
            return normalized_matches
        except Exception as e:
            logger.error(f"Error getting matches from {platform}: {str(e)}")
            return []
    
    def get_conversations(self, platform: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get conversations from a platform.
        
        Args:
            platform: Platform name
            limit: Maximum number of conversations to retrieve
            
        Returns:
            List[Dict]: List of conversations
        """
        if not self.is_authenticated(platform):
            logger.warning(f"Not authenticated with {platform}")
            return []
        
        try:
            conversations = self.scrapers[platform].get_conversations(limit)
            logger.info(f"Retrieved {len(conversations)} conversations from {platform}")
            
            # Store conversations
            for conv in conversations:
                conversation_data = {
                    'platform': platform,
                    'platform_id': conv.get('_id', conv.get('id', '')),
                    'match_id': conv.get('match_id', conv.get('participants', [''])[0]),
                    'started_at': conv.get('created_date', ''),
                    'last_message_at': conv.get('last_activity_date', ''),
                    'status': 'active',
                    'message_count': conv.get('message_count', 0)
                }
                
                self.storage.save_conversation(conversation_data)
            
            return conversations
        except Exception as e:
            logger.error(f"Error getting conversations from {platform}: {str(e)}")
            return []
    
    def get_conversation_messages(self, platform: str, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get messages from a conversation.
        
        Args:
            platform: Platform name
            conversation_id: Conversation ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List[Dict]: List of messages
        """
        if not self.is_authenticated(platform):
            logger.warning(f"Not authenticated with {platform}")
            return []
        
        try:
            messages = self.scrapers[platform].get_conversation_messages(conversation_id, limit)
            logger.info(f"Retrieved {len(messages)} messages from conversation {conversation_id}")
            
            # Store messages
            for msg in messages:
                message_data = {
                    'conversation_id': conversation_id,
                    'sender_type': 'match' if msg.get('from', '') != self.get_user_id(platform) else 'user',
                    'content': msg.get('message', msg.get('text', '')),
                    'sent_at': msg.get('created_date', msg.get('timestamp', '')),
                    'platform_id': msg.get('_id', msg.get('id', ''))
                }
                
                self.storage.save_message(message_data)
            
            return messages
        except Exception as e:
            logger.error(f"Error getting messages from {platform}: {str(e)}")
            return []
    
    def get_user_id(self, platform: str) -> str:
        """
        Get the user's ID from a platform.
        
        Args:
            platform: Platform name
            
        Returns:
            str: User ID
        """
        if not self.is_authenticated(platform):
            return ''
        
        try:
            profile = self.get_user_profile(platform)
            if profile:
                return profile.get('_id', profile.get('id', ''))
            return ''
        except Exception:
            return ''
    
    def close(self):
        """Close connections and clean up resources."""
        self.storage.close()
        logger.info("Dating App AI Assistant closed")
