"""
Integration module for the dating app AI assistant.
Connects the webscraping and message generation modules.
"""

import os
import logging
from typing import Dict, List, Any, Optional

from src.dating_app import DatingAppAI
from src.message_generator import MessageGenerator
from src.storage import DataStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='dating_app.log'
)
logger = logging.getLogger('integration')

class DatingAssistant:
    """Main integration class for the dating app AI assistant."""
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the dating assistant.
        
        Args:
            storage_path: Path to the storage database
        """
        self.dating_app = DatingAppAI(storage_path)
        self.message_generator = MessageGenerator()
        self.storage = self.dating_app.storage
        
        logger.info("Dating Assistant initialized")
    
    def authenticate(self, platform: str, **auth_params) -> bool:
        """
        Authenticate with a dating platform.
        
        Args:
            platform: Platform name ('tinder' or 'hinge')
            **auth_params: Platform-specific authentication parameters
            
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        return self.dating_app.authenticate_platform(platform, **auth_params)
    
    def is_authenticated(self, platform: str) -> bool:
        """
        Check if authenticated with a platform.
        
        Args:
            platform: Platform name
            
        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.dating_app.is_authenticated(platform)
    
    def get_matches(self, platform: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get matches from a platform.
        
        Args:
            platform: Platform name
            limit: Maximum number of matches to retrieve
            
        Returns:
            List[Dict]: List of matches
        """
        return self.dating_app.get_matches(platform, limit)
    
    def analyze_match(self, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a match's profile.
        
        Args:
            match_id: Match ID
            
        Returns:
            Dict or None: Analysis results if successful, None otherwise
        """
        # Get match profile from storage
        match_profile = self.storage.get_match(match_id)
        
        if not match_profile:
            logger.warning(f"Match {match_id} not found in storage")
            return None
        
        # Analyze profile
        analysis = self.message_generator.profile_analyzer.analyze_profile(match_profile)
        logger.info(f"Analyzed profile for match {match_id}")
        
        return analysis
    
    def generate_initial_message(self, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate an initial message for a match.
        
        Args:
            match_id: Match ID
            
        Returns:
            Dict or None: Generated message if successful, None otherwise
        """
        # Get match profile from storage
        match_profile = self.storage.get_match(match_id)
        
        if not match_profile:
            logger.warning(f"Match {match_id} not found in storage")
            return None
        
        # Generate message
        message = self.message_generator.generate_initial_message(match_profile)
        logger.info(f"Generated initial message for match {match_id}")
        
        return message
    
    def generate_response(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate a response for a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dict or None: Generated message if successful, None otherwise
        """
        # Get conversation messages from storage
        messages = self.storage.get_conversation_messages(conversation_id)
        
        if not messages:
            logger.warning(f"No messages found for conversation {conversation_id}")
            return None
        
        # Get match ID from conversation
        cursor = self.storage.conn.cursor()
        cursor.execute("SELECT match_id FROM conversations WHERE id = ?", (conversation_id,))
        result = cursor.fetchone()
        
        if not result:
            logger.warning(f"Conversation {conversation_id} not found in storage")
            return None
        
        match_id = result[0]
        
        # Get match profile from storage
        match_profile = self.storage.get_match(match_id)
        
        if not match_profile:
            logger.warning(f"Match {match_id} not found in storage")
            return None
        
        # Generate response
        message = self.message_generator.generate_response(messages, match_profile)
        logger.info(f"Generated response for conversation {conversation_id}")
        
        return message
    
    def send_message(self, platform: str, match_id: str, message: str) -> bool:
        """
        Send a message to a match.
        
        Args:
            platform: Platform name
            match_id: Match ID
            message: Message text
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_authenticated(platform):
            logger.warning(f"Not authenticated with {platform}")
            return False
        
        try:
            # Get platform-specific match ID
            cursor = self.storage.conn.cursor()
            cursor.execute("SELECT platform_id FROM matches WHERE id = ?", (match_id,))
            result = cursor.fetchone()
            
            if not result:
                logger.warning(f"Match {match_id} not found in storage")
                return False
            
            platform_match_id = result[0]
            
            # Get conversation ID
            cursor.execute(
                "SELECT id FROM conversations WHERE match_id = ? AND platform = ?", 
                (match_id, platform)
            )
            result = cursor.fetchone()
            
            conversation_id = result[0] if result else None
            
            # Send message using platform-specific API
            # This would call the appropriate platform API to send the message
            # For now, we'll just log it and store it locally
            
            # Store message in database
            message_data = {
                "conversation_id": conversation_id,
                "sender_type": "user",
                "content": message,
                "ai_generated": True,
                "ai_approved": True
            }
            
            self.storage.save_message(message_data)
            
            logger.info(f"Sent message to match {match_id} on {platform}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    def approve_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Approve an AI-generated message.
        
        Args:
            message_data: Generated message data
            
        Returns:
            Dict: Updated message data
        """
        message_data["ai_approved"] = True
        logger.info(f"Approved message for match {message_data.get('match_id')}")
        return message_data
    
    def edit_message(self, message_data: Dict[str, Any], new_content: str) -> Dict[str, Any]:
        """
        Edit an AI-generated message.
        
        Args:
            message_data: Generated message data
            new_content: New message content
            
        Returns:
            Dict: Updated message data
        """
        message_data["content"] = new_content
        message_data["ai_approved"] = True
        logger.info(f"Edited message for match {message_data.get('match_id')}")
        return message_data
    
    def close(self):
        """Close connections and clean up resources."""
        self.dating_app.close()
        logger.info("Dating Assistant closed")
