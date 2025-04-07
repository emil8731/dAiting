"""
Main application module for the dating app AI assistant.
Integrates all components and provides a unified interface.
"""

import os
import logging
from typing import Dict, List, Any, Optional

from src.assistant import DatingAssistant
from src.conversation_manager import ConversationManager
from src.notification_system import NotificationSystem
from src.analytics import ConversationAnalytics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='dating_app.log'
)
logger = logging.getLogger('app')

class DatingAppAIAssistant:
    """Main application class for the dating app AI assistant."""
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the dating app AI assistant.
        
        Args:
            storage_path: Path to the storage database
        """
        self.assistant = DatingAssistant(storage_path)
        self.conversation_manager = ConversationManager(
            self.assistant.storage, 
            self.assistant.message_generator
        )
        self.notification_system = NotificationSystem()
        self.analytics = ConversationAnalytics(self.assistant.storage.conn)
        
        logger.info("Dating App AI Assistant initialized")
    
    def authenticate(self, platform: str, **auth_params) -> bool:
        """
        Authenticate with a dating platform.
        
        Args:
            platform: Platform name ('tinder' or 'hinge')
            **auth_params: Platform-specific authentication parameters
            
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        return self.assistant.authenticate(platform, **auth_params)
    
    def is_authenticated(self, platform: str) -> bool:
        """
        Check if authenticated with a platform.
        
        Args:
            platform: Platform name
            
        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.assistant.is_authenticated(platform)
    
    def get_matches(self, platform: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get matches from a platform.
        
        Args:
            platform: Platform name
            limit: Maximum number of matches to retrieve
            
        Returns:
            List[Dict]: List of matches
        """
        matches = self.assistant.get_matches(platform, limit)
        
        # Notify for new matches
        for match in matches:
            # Check if this is a new match (simplified)
            # In a real implementation, we would track which matches have been seen
            self.notification_system.notify_new_match(match)
        
        return matches
    
    def analyze_match(self, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a match's profile.
        
        Args:
            match_id: Match ID
            
        Returns:
            Dict or None: Analysis results if successful, None otherwise
        """
        return self.assistant.analyze_match(match_id)
    
    def generate_initial_message(self, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate an initial message for a match.
        
        Args:
            match_id: Match ID
            
        Returns:
            Dict or None: Generated message if successful, None otherwise
        """
        return self.assistant.generate_initial_message(match_id)
    
    def generate_response(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate a response for a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dict or None: Generated message if successful, None otherwise
        """
        message = self.conversation_manager.generate_response(conversation_id)
        
        if message:
            # Get match name for notification
            cursor = self.assistant.storage.conn.cursor()
            cursor.execute("""
                SELECT m.name 
                FROM matches m
                JOIN conversations c ON m.id = c.match_id
                WHERE c.id = ?
            """, (conversation_id,))
            
            result = cursor.fetchone()
            match_name = result[0] if result else "Match"
            
            # Notify of suggested response
            self.notification_system.notify_suggested_response(conversation_id, match_name)
        
        return message
    
    def approve_and_send_message(self, platform: str, match_id: str, message_data: Dict[str, Any]) -> bool:
        """
        Approve and send an AI-generated message.
        
        Args:
            platform: Platform name
            match_id: Match ID
            message_data: Generated message data
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Approve message
        message_data = self.assistant.approve_message(message_data)
        
        # Send message
        return self.assistant.send_message(platform, match_id, message_data.get('content', ''))
    
    def edit_and_send_message(self, platform: str, match_id: str, message_data: Dict[str, Any], 
                             new_content: str) -> bool:
        """
        Edit and send an AI-generated message.
        
        Args:
            platform: Platform name
            match_id: Match ID
            message_data: Generated message data
            new_content: New message content
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Edit message
        message_data = self.assistant.edit_message(message_data, new_content)
        
        # Send message
        return self.assistant.send_message(platform, match_id, message_data.get('content', ''))
    
    def start_conversation_monitoring(self, conversation_id: str, platform: str) -> bool:
        """
        Start monitoring a conversation for new messages.
        
        Args:
            conversation_id: Conversation ID
            platform: Platform name
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Track conversation
        self.conversation_manager.track_conversation(conversation_id)
        
        # Start monitoring
        return self.conversation_manager.start_monitoring_conversation(conversation_id, platform)
    
    def stop_conversation_monitoring(self, conversation_id: str) -> bool:
        """
        Stop monitoring a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.conversation_manager.stop_monitoring_conversation(conversation_id)
    
    def get_conversation_insights(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get insights for a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dict: Conversation insights
        """
        return self.analytics.get_conversation_insights(conversation_id)
    
    def get_user_stats(self) -> Dict[str, Any]:
        """
        Get user statistics.
        
        Returns:
            Dict: User statistics
        """
        return self.analytics.get_user_stats()
    
    def get_message_activity(self, days: int = 30) -> Dict[str, Any]:
        """
        Get message activity over time.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict: Message activity data
        """
        return self.analytics.get_message_activity(days)
    
    def get_conversation_suggestions(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get suggestions for a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List[Dict]: Suggested actions
        """
        return self.conversation_manager.suggest_conversation_actions(conversation_id)
    
    def close(self):
        """Close connections and clean up resources."""
        self.assistant.close()
        logger.info("Dating App AI Assistant closed")
