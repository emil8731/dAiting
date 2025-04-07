"""
Analytics module for the dating app AI assistant.
Provides functionality for analyzing conversation data and generating insights.
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='dating_app.log'
)
logger = logging.getLogger('analytics')

class ConversationAnalytics:
    """Analyzes conversation data and generates insights."""
    
    def __init__(self, storage_conn: sqlite3.Connection):
        """
        Initialize the conversation analytics.
        
        Args:
            storage_conn: SQLite database connection
        """
        self.conn = storage_conn
        logger.info("Conversation Analytics initialized")
    
    def get_conversation_stats(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dict: Conversation statistics
        """
        try:
            cursor = self.conn.cursor()
            
            # Get basic conversation info
            cursor.execute("""
                SELECT c.started_at, c.last_message_at, c.message_count, c.platform, m.name
                FROM conversations c
                JOIN matches m ON c.match_id = m.id
                WHERE c.id = ?
            """, (conversation_id,))
            
            result = cursor.fetchone()
            if not result:
                return {"error": "Conversation not found"}
            
            started_at, last_message_at, message_count, platform, match_name = result
            
            # Get message counts by sender
            cursor.execute("""
                SELECT sender_type, COUNT(*) 
                FROM messages 
                WHERE conversation_id = ? 
                GROUP BY sender_type
            """, (conversation_id,))
            
            sender_counts = {}
            for sender_type, count in cursor.fetchall():
                sender_counts[sender_type] = count
            
            # Calculate response rates
            user_messages = sender_counts.get('user', 0)
            match_messages = sender_counts.get('match', 0)
            
            user_response_rate = 0
            if match_messages > 0:
                user_response_rate = min(1.0, user_messages / match_messages)
            
            match_response_rate = 0
            if user_messages > 0:
                match_response_rate = min(1.0, match_messages / user_messages)
            
            # Calculate conversation duration
            duration = 0
            try:
                start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(last_message_at.replace('Z', '+00:00'))
                duration = (end_time - start_time).total_seconds() / 3600  # in hours
            except (ValueError, TypeError):
                pass
            
            # Get AI message stats
            cursor.execute("""
                SELECT COUNT(*) 
                FROM messages 
                WHERE conversation_id = ? AND ai_generated = 1
            """, (conversation_id,))
            
            ai_generated_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM messages 
                WHERE conversation_id = ? AND ai_generated = 1 AND ai_approved = 1
            """, (conversation_id,))
            
            ai_approved_count = cursor.fetchone()[0]
            
            ai_approval_rate = 0
            if ai_generated_count > 0:
                ai_approval_rate = ai_approved_count / ai_generated_count
            
            return {
                "conversation_id": conversation_id,
                "match_name": match_name,
                "platform": platform,
                "started_at": started_at,
                "last_message_at": last_message_at,
                "duration_hours": duration,
                "message_count": message_count,
                "user_messages": user_messages,
                "match_messages": match_messages,
                "user_response_rate": user_response_rate,
                "match_response_rate": match_response_rate,
                "ai_generated_count": ai_generated_count,
                "ai_approved_count": ai_approved_count,
                "ai_approval_rate": ai_approval_rate
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation stats: {str(e)}")
            return {"error": str(e)}
    
    def get_user_stats(self, user_id: str = None) -> Dict[str, Any]:
        """
        Get statistics for a user.
        
        Args:
            user_id: User ID (optional)
            
        Returns:
            Dict: User statistics
        """
        try:
            cursor = self.conn.cursor()
            
            # Get match counts by platform
            if user_id:
                cursor.execute("""
                    SELECT platform, COUNT(*) 
                    FROM matches 
                    WHERE user_id = ? 
                    GROUP BY platform
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT platform, COUNT(*) 
                    FROM matches 
                    GROUP BY platform
                """)
            
            match_counts = {}
            for platform, count in cursor.fetchall():
                match_counts[platform] = count
            
            # Get conversation counts by platform
            if user_id:
                cursor.execute("""
                    SELECT platform, COUNT(*) 
                    FROM conversations 
                    WHERE user_id = ? 
                    GROUP BY platform
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT platform, COUNT(*) 
                    FROM conversations 
                    GROUP BY platform
                """)
            
            conversation_counts = {}
            for platform, count in cursor.fetchall():
                conversation_counts[platform] = count
            
            # Get message counts by platform
            if user_id:
                cursor.execute("""
                    SELECT c.platform, COUNT(m.id) 
                    FROM messages m
                    JOIN conversations c ON m.conversation_id = c.id
                    WHERE c.user_id = ? 
                    GROUP BY c.platform
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT c.platform, COUNT(m.id) 
                    FROM messages m
                    JOIN conversations c ON m.conversation_id = c.id
                    GROUP BY c.platform
                """)
            
            message_counts = {}
            for platform, count in cursor.fetchall():
                message_counts[platform] = count
            
            # Get AI message stats
            if user_id:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM messages m
                    JOIN conversations c ON m.conversation_id = c.id
                    WHERE c.user_id = ? AND m.ai_generated = 1
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM messages 
                    WHERE ai_generated = 1
                """)
            
            ai_generated_count = cursor.fetchone()[0]
            
            if user_id:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM messages m
                    JOIN conversations c ON m.conversation_id = c.id
                    WHERE c.user_id = ? AND m.ai_generated = 1 AND m.ai_approved = 1
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM messages 
                    WHERE ai_generated = 1 AND ai_approved = 1
                """)
            
            ai_approved_count = cursor.fetchone()[0]
            
            ai_approval_rate = 0
            if ai_generated_count > 0:
                ai_approval_rate = ai_approved_count / ai_generated_count
            
            return {
                "user_id": user_id,
                "total_matches": sum(match_counts.values()),
                "matches_by_platform": match_counts,
                "total_conversations": sum(conversation_counts.values()),
                "conversations_by_platform": conversation_counts,
                "total_messages": sum(message_counts.values()),
                "messages_by_platform": message_counts,
                "ai_generated_count": ai_generated_count,
                "ai_approved_count": ai_approved_count,
                "ai_approval_rate": ai_approval_rate
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return {"error": str(e)}
    
    def get_message_activity(self, days: int = 30, user_id: str = None) -> Dict[str, Any]:
        """
        Get message activity over time.
        
        Args:
            days: Number of days to analyze
            user_id: User ID (optional)
            
        Returns:
            Dict: Message activity data
        """
        try:
            cursor = self.conn.cursor()
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Format dates for SQLite
            start_date_str = start_date.isoformat()
            end_date_str = end_date.isoformat()
            
            # Get daily message counts
            if user_id:
                cursor.execute("""
                    SELECT date(sent_at) as day, COUNT(*) 
                    FROM messages m
                    JOIN conversations c ON m.conversation_id = c.id
                    WHERE c.user_id = ? AND sent_at BETWEEN ? AND ?
                    GROUP BY day
                    ORDER BY day
                """, (user_id, start_date_str, end_date_str))
            else:
                cursor.execute("""
                    SELECT date(sent_at) as day, COUNT(*) 
                    FROM messages 
                    WHERE sent_at BETWEEN ? AND ?
                    GROUP BY day
                    ORDER BY day
                """, (start_date_str, end_date_str))
            
            daily_counts = {}
            for day, count in cursor.fetchall():
                daily_counts[day] = count
            
            # Fill in missing days with zero counts
            current_date = start_date
            while current_date <= end_date:
                day_str = current_date.date().isoformat()
                if day_str not in daily_counts:
                    daily_counts[day_str] = 0
                current_date += timedelta(days=1)
            
            # Sort by date
            sorted_daily_counts = {k: daily_counts[k] for k in sorted(daily_counts.keys())}
            
            # Get hourly distribution
            if user_id:
                cursor.execute("""
                    SELECT strftime('%H', sent_at) as hour, COUNT(*) 
                    FROM messages m
                    JOIN conversations c ON m.conversation_id = c.id
                    WHERE c.user_id = ? AND sent_at BETWEEN ? AND ?
                    GROUP BY hour
                    ORDER BY hour
                """, (user_id, start_date_str, end_date_str))
            else:
                cursor.execute("""
                    SELECT strftime('%H', sent_at) as hour, COUNT(*) 
                    FROM messages 
                    WHERE sent_at BETWEEN ? AND ?
                    GROUP BY hour
                    ORDER BY hour
                """, (start_date_str, end_date_str))
            
            hourly_counts = {}
            for hour, count in cursor.fetchall():
                hourly_counts[hour] = count
            
            # Fill in missing hours with zero counts
            for hour in range(24):
                hour_str = f"{hour:02d}"
                if hour_str not in hourly_counts:
                    hourly_counts[hour_str] = 0
            
            # Sort by hour
            sorted_hourly_counts = {k: hourly_counts[k] for k in sorted(hourly_counts.keys())}
            
            return {
                "user_id": user_id,
                "days_analyzed": days,
                "start_date": start_date_str,
                "end_date": end_date_str,
                "total_messages": sum(daily_counts.values()),
                "daily_counts": sorted_daily_counts,
                "hourly_distribution": sorted_hourly_counts
            }
            
        except Exception as e:
            logger.error(f"Error getting message activity: {str(e)}")
            return {"error": str(e)}
    
    def get_conversation_insights(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get insights for a specific conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dict: Conversation insights
        """
        try:
            # Get basic stats
            stats = self.get_conversation_stats(conversation_id)
            
            if "error" in stats:
                return stats
            
            cursor = self.conn.cursor()
            
            # Get message content for analysis
            cursor.execute("""
                SELECT content, sender_type, sent_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY sent_at
            """, (conversation_id,))
            
            messages = []
            for content, sender_type, sent_at in cursor.fetchall():
                messages.append({
                    "content": content,
                    "sender_type": sender_type,
                    "sent_at": sent_at
                })
            
            # Simple content analysis
            word_counts = {}
            question_count = 0
            emoji_count = 0
            avg_message_length = 0
            
            total_words = 0
            for msg in messages:
                content = msg.get("content", "")
                words = content.split()
                total_words += len(words)
                
                # Count words
                for word in words:
                    word = word.lower().strip(".,!?;:()")
                    if word:
                        word_counts[word] = word_counts.get(word, 0) + 1
                
                # Count questions
                if "?" in content:
                    question_count += 1
                
                # Simple emoji detection
                emoji_count += content.count("😊") + content.count("😂") + content.count("❤️")
            
            if messages:
                avg_message_length = total_words / len(messages)
            
            # Get most common words (excluding stop words)
            stop_words = {"the", "and", "a", "to", "of", "in", "is", "that", "it", "for", "you", "i", "with", "on", "are", "be", "this", "was", "have", "not", "but", "at", "by", "an", "or", "as", "what", "from", "your", "my", "so", "we", "they", "would", "could", "should", "will", "can", "do", "does", "did", "has", "had", "been", "were", "am", "if", "then", "no", "yes", "when", "how", "all", "any", "some", "there", "their", "his", "her", "him", "she", "he", "me", "them", "who", "which", "where", "why", "just", "very", "really", "too", "much", "more", "most", "also", "only", "even", "such", "because", "since", "while", "though", "although", "however", "therefore", "thus", "hence", "accordingly", "consequently", "otherwise", "instead", "meanwhile", "nonetheless", "nevertheless", "still", "yet", "anyway", "besides", "indeed", "moreover", "furthermore", "additionally"}
            
            common_words = []
            for word, count in sorted(word_counts.items(), key=lambda x: x[1], reverse=True):
                if word not in stop_words and len(word) > 2:
                    common_words.append({"word": word, "count": count})
                    if len(common_words) >= 10:
                        break
            
            # Calculate response times
            response_times = []
            for i in range(1, len(messages)):
                current = messages[i]
                previous = messages[i-1]
                
                if (current.get('sender_type') != previous.get('sender_type') and
                    current.get('sent_at') and previous.get('sent_at')):
                    try:
                        current_time = datetime.fromisoformat(current.get('sent_at').replace('Z', '+00:00'))
                        previous_time = datetime.fromisoformat(previous.get('sent_at').replace('Z', '+00:00'))
                        
                        delta = (current_time - previous_time).total_seconds() / 60  # in minutes
                        if delta > 0:
                            response_times.append(delta)
                    except (ValueError, TypeError):
                        pass
            
            avg_response_time = 0
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
            
            # Determine conversation stage
            stage = "initial"
            if stats["message_count"] > 50:
                stage = "established"
            elif stats["message_count"] > 20:
                stage = "developing"
            elif stats["message_count"] > 5:
                stage = "early"
            
            # Generate insights
            insights = []
            
            if stats["match_response_rate"] < 0.5:
                insights.append({
                    "type": "warning",
                    "message": "Low response rate from match",
                    "details": f"Match is responding to only {stats['match_response_rate']*100:.1f}% of your messages"
                })
            
            if avg_response_time > 720:  # 12 hours
                insights.append({
                    "type": "info",
                    "message": "Slow response time",
                    "details": f"Average response time is {avg_response_time/60:.1f} hours"
                })
            
            if question_count < stats["message_count"] * 0.2:
                insights.append({
                    "type": "suggestion",
                    "message": "Low question count",
                    "details": "Try asking more questions to engage your match"
                })
            
            if avg_message_length > 50:
                insights.append({
                    "type": "suggestion",
                    "message": "Long messages",
                    "details": "Your messages are quite long. Consider shorter, more focused messages"
                })
            
            if stage == "early" and stats["duration_hours"] > 48:
                insights.append({
                    "type": "suggestion",
                    "message": "Slow conversation progression",
                    "details": "Consider suggesting a meeting or phone call to move the conversation forward"
                })
            
            return {
                "conversation_id": conversation_id,
                "match_name": stats["match_name"],
                "platform": stats["platform"],
                "message_count": stats["message_count"],
                "stage": stage,
                "avg_message_length": avg_message_length,
                "question_count": question_count,
                "emoji_count": emoji_count,
                "avg_response_time_minutes": avg_response_time,
                "common_words": common_words,
                "insights": insights
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation insights: {str(e)}")
            return {"error": str(e)}
