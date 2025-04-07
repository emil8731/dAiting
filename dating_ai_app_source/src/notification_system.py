"""
Notification system module for the dating app AI assistant.
Provides functionality for notifying users of new messages and events.
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='dating_app.log'
)
logger = logging.getLogger('notification_system')

class NotificationSystem:
    """Manages notifications for the dating app AI assistant."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the notification system.
        
        Args:
            config_path: Path to notification configuration file
        """
        self.config_path = config_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            'data', 
            'notification_config.json'
        )
        self.config = self._load_config()
        self.notification_history = []
        
        logger.info("Notification System initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load notification configuration from file.
        
        Returns:
            Dict: Notification configuration
        """
        default_config = {
            "enabled": True,
            "notification_types": {
                "new_message": True,
                "new_match": True,
                "conversation_inactive": True,
                "suggested_response": True
            },
            "channels": {
                "console": True,
                "email": False,
                "push": False
            },
            "email_settings": {
                "smtp_server": "",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_address": ""
            },
            "quiet_hours": {
                "enabled": False,
                "start_hour": 22,
                "end_hour": 8
            }
        }
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Check if config file exists
            if not os.path.exists(self.config_path):
                # Create default config file
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                logger.info(f"Created default notification config at {self.config_path}")
                return default_config
            
            # Load config from file
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded notification config from {self.config_path}")
                return config
                
        except Exception as e:
            logger.error(f"Error loading notification config: {str(e)}")
            return default_config
    
    def save_config(self) -> bool:
        """
        Save notification configuration to file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved notification config to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving notification config: {str(e)}")
            return False
    
    def is_notification_enabled(self, notification_type: str) -> bool:
        """
        Check if a notification type is enabled.
        
        Args:
            notification_type: Type of notification
            
        Returns:
            bool: True if enabled, False otherwise
        """
        if not self.config.get('enabled', True):
            return False
        
        return self.config.get('notification_types', {}).get(notification_type, True)
    
    def is_channel_enabled(self, channel: str) -> bool:
        """
        Check if a notification channel is enabled.
        
        Args:
            channel: Notification channel
            
        Returns:
            bool: True if enabled, False otherwise
        """
        return self.config.get('channels', {}).get(channel, False)
    
    def is_quiet_hours(self) -> bool:
        """
        Check if current time is within quiet hours.
        
        Returns:
            bool: True if within quiet hours, False otherwise
        """
        quiet_hours = self.config.get('quiet_hours', {})
        
        if not quiet_hours.get('enabled', False):
            return False
        
        current_hour = datetime.now().hour
        start_hour = quiet_hours.get('start_hour', 22)
        end_hour = quiet_hours.get('end_hour', 8)
        
        if start_hour <= end_hour:
            return start_hour <= current_hour < end_hour
        else:
            # Handle case where quiet hours span midnight
            return current_hour >= start_hour or current_hour < end_hour
    
    def notify_new_message(self, conversation_id: str, message_data: Dict[str, Any]) -> bool:
        """
        Notify user of a new message.
        
        Args:
            conversation_id: Conversation ID
            message_data: Message data
            
        Returns:
            bool: True if notification was sent, False otherwise
        """
        if not self.is_notification_enabled('new_message'):
            return False
        
        if self.is_quiet_hours() and not message_data.get('urgent', False):
            logger.info(f"Skipping notification during quiet hours for conversation {conversation_id}")
            return False
        
        # Create notification data
        notification = {
            "type": "new_message",
            "timestamp": datetime.now().isoformat(),
            "conversation_id": conversation_id,
            "sender": message_data.get('sender_type', 'unknown'),
            "content_preview": self._get_content_preview(message_data.get('content', '')),
            "match_name": message_data.get('match_name', 'Someone')
        }
        
        # Add to history
        self.notification_history.append(notification)
        
        # Send through enabled channels
        sent = False
        
        if self.is_channel_enabled('console'):
            self._send_console_notification(notification)
            sent = True
        
        if self.is_channel_enabled('email'):
            self._send_email_notification(notification)
            sent = True
        
        if self.is_channel_enabled('push'):
            self._send_push_notification(notification)
            sent = True
        
        logger.info(f"Sent new message notification for conversation {conversation_id}")
        return sent
    
    def notify_new_match(self, match_data: Dict[str, Any]) -> bool:
        """
        Notify user of a new match.
        
        Args:
            match_data: Match data
            
        Returns:
            bool: True if notification was sent, False otherwise
        """
        if not self.is_notification_enabled('new_match'):
            return False
        
        if self.is_quiet_hours():
            logger.info(f"Skipping notification during quiet hours for new match")
            return False
        
        # Create notification data
        notification = {
            "type": "new_match",
            "timestamp": datetime.now().isoformat(),
            "match_id": match_data.get('id', ''),
            "match_name": match_data.get('name', 'Someone'),
            "platform": match_data.get('platform', 'unknown')
        }
        
        # Add to history
        self.notification_history.append(notification)
        
        # Send through enabled channels
        sent = False
        
        if self.is_channel_enabled('console'):
            self._send_console_notification(notification)
            sent = True
        
        if self.is_channel_enabled('email'):
            self._send_email_notification(notification)
            sent = True
        
        if self.is_channel_enabled('push'):
            self._send_push_notification(notification)
            sent = True
        
        logger.info(f"Sent new match notification for {notification['match_name']}")
        return sent
    
    def notify_conversation_inactive(self, conversation_id: str, match_name: str) -> bool:
        """
        Notify user of an inactive conversation.
        
        Args:
            conversation_id: Conversation ID
            match_name: Match name
            
        Returns:
            bool: True if notification was sent, False otherwise
        """
        if not self.is_notification_enabled('conversation_inactive'):
            return False
        
        if self.is_quiet_hours():
            logger.info(f"Skipping notification during quiet hours for inactive conversation")
            return False
        
        # Create notification data
        notification = {
            "type": "conversation_inactive",
            "timestamp": datetime.now().isoformat(),
            "conversation_id": conversation_id,
            "match_name": match_name
        }
        
        # Add to history
        self.notification_history.append(notification)
        
        # Send through enabled channels
        sent = False
        
        if self.is_channel_enabled('console'):
            self._send_console_notification(notification)
            sent = True
        
        if self.is_channel_enabled('email'):
            self._send_email_notification(notification)
            sent = True
        
        if self.is_channel_enabled('push'):
            self._send_push_notification(notification)
            sent = True
        
        logger.info(f"Sent inactive conversation notification for {match_name}")
        return sent
    
    def notify_suggested_response(self, conversation_id: str, match_name: str) -> bool:
        """
        Notify user of a suggested response.
        
        Args:
            conversation_id: Conversation ID
            match_name: Match name
            
        Returns:
            bool: True if notification was sent, False otherwise
        """
        if not self.is_notification_enabled('suggested_response'):
            return False
        
        if self.is_quiet_hours():
            logger.info(f"Skipping notification during quiet hours for suggested response")
            return False
        
        # Create notification data
        notification = {
            "type": "suggested_response",
            "timestamp": datetime.now().isoformat(),
            "conversation_id": conversation_id,
            "match_name": match_name
        }
        
        # Add to history
        self.notification_history.append(notification)
        
        # Send through enabled channels
        sent = False
        
        if self.is_channel_enabled('console'):
            self._send_console_notification(notification)
            sent = True
        
        if self.is_channel_enabled('email'):
            self._send_email_notification(notification)
            sent = True
        
        if self.is_channel_enabled('push'):
            self._send_push_notification(notification)
            sent = True
        
        logger.info(f"Sent suggested response notification for {match_name}")
        return sent
    
    def get_notification_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get notification history.
        
        Args:
            limit: Maximum number of notifications to retrieve
            
        Returns:
            List[Dict]: List of notifications
        """
        return self.notification_history[-limit:]
    
    def clear_notification_history(self) -> bool:
        """
        Clear notification history.
        
        Returns:
            bool: True if successful, False otherwise
        """
        self.notification_history = []
        logger.info("Cleared notification history")
        return True
    
    def _get_content_preview(self, content: str, max_length: int = 50) -> str:
        """
        Get a preview of message content.
        
        Args:
            content: Message content
            max_length: Maximum preview length
            
        Returns:
            str: Content preview
        """
        if len(content) <= max_length:
            return content
        
        return content[:max_length - 3] + "..."
    
    def _send_console_notification(self, notification: Dict[str, Any]) -> bool:
        """
        Send notification to console.
        
        Args:
            notification: Notification data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            notification_type = notification.get('type', 'unknown')
            
            if notification_type == 'new_message':
                print(f"[NEW MESSAGE] {notification.get('match_name')}: {notification.get('content_preview')}")
            elif notification_type == 'new_match':
                print(f"[NEW MATCH] You matched with {notification.get('match_name')} on {notification.get('platform')}")
            elif notification_type == 'conversation_inactive':
                print(f"[INACTIVE] Your conversation with {notification.get('match_name')} has been inactive")
            elif notification_type == 'suggested_response':
                print(f"[SUGGESTION] A response has been suggested for {notification.get('match_name')}")
            else:
                print(f"[NOTIFICATION] {notification}")
            
            return True
        except Exception as e:
            logger.error(f"Error sending console notification: {str(e)}")
            return False
    
    def _send_email_notification(self, notification: Dict[str, Any]) -> bool:
        """
        Send notification via email.
        
        Args:
            notification: Notification data
            
        Returns:
            bool: True if successful, False otherwise
        """
        # In a real implementation, this would send an email
        # For this prototype, we'll just log it
        logger.info(f"Would send email notification: {notification}")
        return True
    
    def _send_push_notification(self, notification: Dict[str, Any]) -> bool:
        """
        Send push notification.
        
        Args:
            notification: Notification data
            
        Returns:
            bool: True if successful, False otherwise
        """
        # In a real implementation, this would send a push notification
        # For this prototype, we'll just log it
        logger.info(f"Would send push notification: {notification}")
        return True
