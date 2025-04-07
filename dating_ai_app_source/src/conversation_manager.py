"""
Conversation management module for the dating app AI assistant.
Provides functionality for tracking conversations and managing message flow.
"""

import os
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from threading import Thread, Event

from src.storage import DataStorage
from src.message_generator import MessageGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='dating_app.log'
)
logger = logging.getLogger('conversation_manager')

class ConversationManager:
    """Manages conversations and message flow."""
    
    def __init__(self, storage: DataStorage, message_generator: MessageGenerator):
        """
        Initialize the conversation manager.
        
        Args:
            storage: Data storage instance
            message_generator: Message generator instance
        """
        self.storage = storage
        self.message_generator = message_generator
        self.active_conversations = {}
        self.monitoring_threads = {}
        self.stop_events = {}
        
        logger.info("Conversation Manager initialized")
    
    def get_conversation_history(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get conversation history.
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List[Dict]: List of messages in the conversation
        """
        return self.storage.get_conversation_messages(conversation_id, limit)
    
    def get_active_conversations(self, user_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get active conversations.
        
        Args:
            user_id: User ID (optional)
            limit: Maximum number of conversations to retrieve
            
        Returns:
            List[Dict]: List of active conversations
        """
        return self.storage.get_active_conversations(user_id, limit)
    
    def track_conversation(self, conversation_id: str) -> bool:
        """
        Start tracking a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if conversation_id in self.active_conversations:
            logger.info(f"Conversation {conversation_id} is already being tracked")
            return True
        
        # Get conversation from storage
        cursor = self.storage.conn.cursor()
        cursor.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,))
        row = cursor.fetchone()
        
        if not row:
            logger.warning(f"Conversation {conversation_id} not found in storage")
            return False
        
        # Convert row to dictionary
        columns = [col[0] for col in cursor.description]
        conversation = dict(zip(columns, row))
        
        # Add to active conversations
        self.active_conversations[conversation_id] = {
            "conversation": conversation,
            "last_checked": datetime.now(),
            "messages": self.get_conversation_history(conversation_id)
        }
        
        logger.info(f"Started tracking conversation {conversation_id}")
        return True
    
    def stop_tracking_conversation(self, conversation_id: str) -> bool:
        """
        Stop tracking a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if conversation_id not in self.active_conversations:
            logger.warning(f"Conversation {conversation_id} is not being tracked")
            return False
        
        # Remove from active conversations
        del self.active_conversations[conversation_id]
        
        # Stop monitoring thread if exists
        if conversation_id in self.stop_events:
            self.stop_events[conversation_id].set()
            del self.stop_events[conversation_id]
            del self.monitoring_threads[conversation_id]
        
        logger.info(f"Stopped tracking conversation {conversation_id}")
        return True
    
    def archive_conversation(self, conversation_id: str) -> bool:
        """
        Archive a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Update conversation status in storage
            cursor = self.storage.conn.cursor()
            cursor.execute(
                "UPDATE conversations SET status = 'archived' WHERE id = ?", 
                (conversation_id,)
            )
            self.storage.conn.commit()
            
            # Stop tracking if active
            if conversation_id in self.active_conversations:
                self.stop_tracking_conversation(conversation_id)
            
            logger.info(f"Archived conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error archiving conversation: {str(e)}")
            return False
    
    def start_monitoring_conversation(self, conversation_id: str, platform: str, 
                                     check_interval: int = 60) -> bool:
        """
        Start monitoring a conversation for new messages.
        
        Args:
            conversation_id: Conversation ID
            platform: Platform name
            check_interval: Interval between checks in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        if conversation_id in self.monitoring_threads and self.monitoring_threads[conversation_id].is_alive():
            logger.info(f"Conversation {conversation_id} is already being monitored")
            return True
        
        # Create stop event
        stop_event = Event()
        self.stop_events[conversation_id] = stop_event
        
        # Create and start monitoring thread
        thread = Thread(
            target=self._monitor_conversation,
            args=(conversation_id, platform, check_interval, stop_event)
        )
        thread.daemon = True
        thread.start()
        
        self.monitoring_threads[conversation_id] = thread
        
        logger.info(f"Started monitoring conversation {conversation_id}")
        return True
    
    def stop_monitoring_conversation(self, conversation_id: str) -> bool:
        """
        Stop monitoring a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if conversation_id not in self.stop_events:
            logger.warning(f"Conversation {conversation_id} is not being monitored")
            return False
        
        # Set stop event
        self.stop_events[conversation_id].set()
        
        # Wait for thread to terminate
        if self.monitoring_threads[conversation_id].is_alive():
            self.monitoring_threads[conversation_id].join(timeout=5)
        
        # Clean up
        del self.stop_events[conversation_id]
        del self.monitoring_threads[conversation_id]
        
        logger.info(f"Stopped monitoring conversation {conversation_id}")
        return True
    
    def _monitor_conversation(self, conversation_id: str, platform: str, 
                             check_interval: int, stop_event: Event) -> None:
        """
        Monitor a conversation for new messages.
        
        Args:
            conversation_id: Conversation ID
            platform: Platform name
            check_interval: Interval between checks in seconds
            stop_event: Event to signal thread to stop
        """
        from src.dating_app import DatingAppAI
        
        # Create dating app instance
        dating_app = DatingAppAI()
        
        # Get platform-specific conversation ID
        cursor = self.storage.conn.cursor()
        cursor.execute("SELECT platform_id FROM conversations WHERE id = ?", (conversation_id,))
        result = cursor.fetchone()
        
        if not result:
            logger.error(f"Conversation {conversation_id} not found in storage")
            return
        
        platform_conversation_id = result[0]
        
        # Get current message count
        cursor.execute("SELECT message_count FROM conversations WHERE id = ?", (conversation_id,))
        result = cursor.fetchone()
        current_message_count = result[0] if result else 0
        
        while not stop_event.is_set():
            try:
                # Check if authenticated
                if not dating_app.is_authenticated(platform):
                    logger.warning(f"Not authenticated with {platform}, cannot check for new messages")
                    time.sleep(check_interval)
                    continue
                
                # Get messages from platform
                messages = dating_app.get_conversation_messages(
                    platform, platform_conversation_id, limit=20
                )
                
                # Check if new messages
                if len(messages) > current_message_count:
                    logger.info(f"New messages detected in conversation {conversation_id}")
                    
                    # Update message count
                    current_message_count = len(messages)
                    
                    # Notify listeners (would be implemented in a real application)
                    self._notify_new_messages(conversation_id)
                
                # Sleep until next check
                time.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Error monitoring conversation: {str(e)}")
                time.sleep(check_interval)
    
    def _notify_new_messages(self, conversation_id: str) -> None:
        """
        Notify listeners of new messages.
        
        Args:
            conversation_id: Conversation ID
        """
        # In a real application, this would notify the UI or send push notifications
        # For this prototype, we'll just log it
        logger.info(f"New messages notification for conversation {conversation_id}")
    
    def generate_response(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate a response for a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dict or None: Generated message if successful, None otherwise
        """
        # Get conversation history
        messages = self.get_conversation_history(conversation_id)
        
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
        
        # Get match profile
        match_profile = self.storage.get_match(match_id)
        
        if not match_profile:
            logger.warning(f"Match {match_id} not found in storage")
            return None
        
        # Generate response
        message = self.message_generator.generate_response(messages, match_profile)
        
        # Add conversation ID
        message["conversation_id"] = conversation_id
        
        logger.info(f"Generated response for conversation {conversation_id}")
        return message
    
    def analyze_conversation_flow(self, conversation_id: str) -> Dict[str, Any]:
        """
        Analyze conversation flow and engagement.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dict: Analysis results
        """
        # Get conversation history
        messages = self.get_conversation_history(conversation_id)
        
        if not messages:
            return {
                "engagement_level": 0,
                "response_rate": 0,
                "average_response_time": 0,
                "message_count": 0,
                "topics_discussed": [],
                "sentiment": "neutral"
            }
        
        # Calculate basic metrics
        user_messages = [m for m in messages if m.get('sender_type') == 'user']
        match_messages = [m for m in messages if m.get('sender_type') == 'match']
        
        message_count = len(messages)
        user_message_count = len(user_messages)
        match_message_count = len(match_messages)
        
        # Calculate response rate
        response_rate = 0
        if user_message_count > 0:
            response_rate = match_message_count / user_message_count
        
        # Calculate average response time
        avg_response_time = 0
        response_times = []
        
        for i in range(1, len(messages)):
            current = messages[i]
            previous = messages[i-1]
            
            if (current.get('sender_type') != previous.get('sender_type') and
                current.get('sent_at') and previous.get('sent_at')):
                try:
                    current_time = datetime.fromisoformat(current.get('sent_at').replace('Z', '+00:00'))
                    previous_time = datetime.fromisoformat(previous.get('sent_at').replace('Z', '+00:00'))
                    
                    delta = (current_time - previous_time).total_seconds()
                    if delta > 0:
                        response_times.append(delta)
                except (ValueError, TypeError):
                    pass
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
        
        # Calculate engagement level
        engagement_level = 0
        if message_count > 0:
            # Simple engagement formula based on message count and response rate
            engagement_level = min(1.0, (message_count / 10) * (response_rate))
        
        # Extract topics (simplified)
        topics_discussed = []
        for msg in messages:
            content = msg.get('content', '').lower()
            common_topics = ["travel", "music", "food", "movies", "books", "sports", "hiking", "cooking"]
            
            for topic in common_topics:
                if topic in content and topic not in topics_discussed:
                    topics_discussed.append(topic)
        
        # Determine sentiment (simplified)
        sentiment = "neutral"
        positive_words = ["love", "like", "enjoy", "happy", "great", "good", "fun", "excited"]
        negative_words = ["hate", "dislike", "bad", "sad", "boring", "annoying", "disappointed"]
        
        positive_count = 0
        negative_count = 0
        
        for msg in messages:
            content = msg.get('content', '').lower()
            
            for word in positive_words:
                if word in content:
                    positive_count += 1
            
            for word in negative_words:
                if word in content:
                    negative_count += 1
        
        if positive_count > negative_count * 2:
            sentiment = "positive"
        elif negative_count > positive_count * 2:
            sentiment = "negative"
        
        return {
            "engagement_level": engagement_level,
            "response_rate": response_rate,
            "average_response_time": avg_response_time,
            "message_count": message_count,
            "topics_discussed": topics_discussed,
            "sentiment": sentiment
        }
    
    def get_conversation_context(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get conversation context for message generation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dict: Conversation context
        """
        # Get conversation history
        messages = self.get_conversation_history(conversation_id, limit=20)
        
        # Get match ID from conversation
        cursor = self.storage.conn.cursor()
        cursor.execute("SELECT match_id FROM conversations WHERE id = ?", (conversation_id,))
        result = cursor.fetchone()
        
        if not result:
            return {"context_available": False}
        
        match_id = result[0]
        
        # Get match profile
        match_profile = self.storage.get_match(match_id)
        
        if not match_profile:
            return {"context_available": False}
        
        # Analyze conversation flow
        flow_analysis = self.analyze_conversation_flow(conversation_id)
        
        # Extract recent topics
        recent_topics = []
        if messages:
            # Look at last 5 messages
            recent_messages = messages[:5]
            for msg in recent_messages:
                content = msg.get('content', '').lower()
                common_topics = ["travel", "music", "food", "movies", "books", "sports", "hiking", "cooking"]
                
                for topic in common_topics:
                    if topic in content and topic not in recent_topics:
                        recent_topics.append(topic)
        
        # Create context
        context = {
            "context_available": True,
            "match_name": match_profile.get('name', ''),
            "match_interests": match_profile.get('interests', []),
            "recent_topics": recent_topics,
            "all_topics": flow_analysis.get('topics_discussed', []),
            "engagement_level": flow_analysis.get('engagement_level', 0),
            "sentiment": flow_analysis.get('sentiment', 'neutral'),
            "message_count": flow_analysis.get('message_count', 0)
        }
        
        return context
    
    def suggest_conversation_actions(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Suggest actions for a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List[Dict]: Suggested actions
        """
        # Get conversation context
        context = self.get_conversation_context(conversation_id)
        
        if not context.get('context_available', False):
            return [{"action": "start_conversation", "reason": "No conversation history found"}]
        
        suggestions = []
        
        # Check engagement level
        engagement = context.get('engagement_level', 0)
        
        if engagement < 0.3:
            suggestions.append({
                "action": "increase_engagement",
                "reason": "Low engagement detected",
                "details": "Try asking more personal questions or sharing more about yourself"
            })
        
        # Check message count
        message_count = context.get('message_count', 0)
        
        if message_count >= 20:
            suggestions.append({
                "action": "suggest_meeting",
                "reason": "Conversation has good momentum",
                "details": "Consider suggesting a phone call or meeting in person"
            })
        
        # Check sentiment
        sentiment = context.get('sentiment', 'neutral')
        
        if sentiment == 'negative':
            suggestions.append({
                "action": "improve_tone",
                "reason": "Conversation has negative sentiment",
                "details": "Try shifting to more positive topics or using more upbeat language"
            })
        
        # If no specific suggestions, add general ones
        if not suggestions:
            if message_count < 5:
                suggestions.append({
                    "action": "ask_question",
                    "reason": "Keep conversation flowing",
                    "details": "Ask about their interests or recent activities"
                })
            else:
                suggestions.append({
                    "action": "deepen_conversation",
                    "reason": "Conversation is established",
                    "details": "Move beyond small talk to more meaningful topics"
                })
        
        return suggestions
