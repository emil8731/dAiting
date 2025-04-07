"""
Data storage module for the dating app AI assistant.
Provides functionality for storing and retrieving profile and conversation data.
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger('storage')

class DataStorage:
    """Data storage class for managing profile and conversation data."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize the data storage.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or os.path.join(os.path.expanduser('~'), 'dating_ai_app.db')
        self.conn = None
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize the SQLite database with required tables."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # Create users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT,
                password_hash TEXT,
                created_at TEXT,
                tinder_credentials TEXT,
                hinge_credentials TEXT,
                settings TEXT
            )
            ''')
            
            # Create matches table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id TEXT PRIMARY KEY,
                platform TEXT,
                platform_id TEXT,
                user_id TEXT,
                name TEXT,
                age INTEGER,
                bio TEXT,
                interests TEXT,
                photos TEXT,
                job TEXT,
                education TEXT,
                location TEXT,
                last_updated TEXT,
                is_active INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''')
            
            # Create conversations table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                match_id TEXT,
                user_id TEXT,
                platform TEXT,
                platform_id TEXT,
                started_at TEXT,
                last_message_at TEXT,
                status TEXT,
                ai_enabled INTEGER,
                message_count INTEGER,
                FOREIGN KEY (match_id) REFERENCES matches (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''')
            
            # Create messages table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT,
                sender_type TEXT,
                content TEXT,
                sent_at TEXT,
                delivered_at TEXT,
                read_at TEXT,
                ai_generated INTEGER,
                ai_approved INTEGER,
                platform_id TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
            ''')
            
            self.conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
            
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise
    
    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def save_match(self, match_data: Dict[str, Any]) -> bool:
        """
        Save a match to the database.
        
        Args:
            match_data: Normalized match data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            
            # Check if match already exists
            cursor.execute("SELECT id FROM matches WHERE platform = ? AND platform_id = ?", 
                          (match_data.get('platform'), match_data.get('platform_id')))
            existing = cursor.fetchone()
            
            # Convert complex fields to JSON
            interests_json = json.dumps(match_data.get('interests', []))
            photos_json = json.dumps(match_data.get('photos', []))
            job_json = json.dumps(match_data.get('job', {}))
            
            if existing:
                # Update existing match
                cursor.execute('''
                UPDATE matches SET
                    name = ?,
                    age = ?,
                    bio = ?,
                    interests = ?,
                    photos = ?,
                    job = ?,
                    education = ?,
                    location = ?,
                    last_updated = ?,
                    is_active = ?
                WHERE id = ?
                ''', (
                    match_data.get('name', ''),
                    match_data.get('age', 0),
                    match_data.get('bio', ''),
                    interests_json,
                    photos_json,
                    job_json,
                    match_data.get('education', ''),
                    match_data.get('location', ''),
                    datetime.now().isoformat(),
                    1 if match_data.get('is_active', True) else 0,
                    existing[0]
                ))
                logger.info(f"Updated match {existing[0]}")
            else:
                # Insert new match
                match_id = match_data.get('id') or f"{match_data.get('platform')}_{match_data.get('platform_id')}"
                cursor.execute('''
                INSERT INTO matches (
                    id, platform, platform_id, user_id, name, age, bio, interests,
                    photos, job, education, location, last_updated, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    match_id,
                    match_data.get('platform', ''),
                    match_data.get('platform_id', ''),
                    match_data.get('user_id', ''),
                    match_data.get('name', ''),
                    match_data.get('age', 0),
                    match_data.get('bio', ''),
                    interests_json,
                    photos_json,
                    job_json,
                    match_data.get('education', ''),
                    match_data.get('location', ''),
                    datetime.now().isoformat(),
                    1 if match_data.get('is_active', True) else 0
                ))
                logger.info(f"Inserted new match {match_id}")
            
            self.conn.commit()
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error saving match: {str(e)}")
            return False
    
    def save_message(self, message_data: Dict[str, Any]) -> bool:
        """
        Save a message to the database.
        
        Args:
            message_data: Message data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            
            # Check if message already exists
            cursor.execute("SELECT id FROM messages WHERE platform_id = ?", 
                          (message_data.get('platform_id'),))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing message
                cursor.execute('''
                UPDATE messages SET
                    delivered_at = ?,
                    read_at = ?
                WHERE id = ?
                ''', (
                    message_data.get('delivered_at', ''),
                    message_data.get('read_at', ''),
                    existing[0]
                ))
                logger.info(f"Updated message {existing[0]}")
            else:
                # Insert new message
                message_id = message_data.get('id') or f"msg_{datetime.now().timestamp()}"
                cursor.execute('''
                INSERT INTO messages (
                    id, conversation_id, sender_type, content, sent_at,
                    delivered_at, read_at, ai_generated, ai_approved, platform_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    message_id,
                    message_data.get('conversation_id', ''),
                    message_data.get('sender_type', ''),
                    message_data.get('content', ''),
                    message_data.get('sent_at', datetime.now().isoformat()),
                    message_data.get('delivered_at', ''),
                    message_data.get('read_at', ''),
                    1 if message_data.get('ai_generated', False) else 0,
                    1 if message_data.get('ai_approved', False) else 0,
                    message_data.get('platform_id', '')
                ))
                logger.info(f"Inserted new message {message_id}")
                
                # Update conversation last_message_at and message_count
                cursor.execute('''
                UPDATE conversations SET
                    last_message_at = ?,
                    message_count = message_count + 1
                WHERE id = ?
                ''', (
                    message_data.get('sent_at', datetime.now().isoformat()),
                    message_data.get('conversation_id', '')
                ))
            
            self.conn.commit()
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error saving message: {str(e)}")
            return False
    
    def save_conversation(self, conversation_data: Dict[str, Any]) -> bool:
        """
        Save a conversation to the database.
        
        Args:
            conversation_data: Conversation data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()
            
            # Check if conversation already exists
            cursor.execute("SELECT id FROM conversations WHERE platform = ? AND platform_id = ?", 
                          (conversation_data.get('platform'), conversation_data.get('platform_id')))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing conversation
                cursor.execute('''
                UPDATE conversations SET
                    last_message_at = ?,
                    status = ?,
                    ai_enabled = ?
                WHERE id = ?
                ''', (
                    conversation_data.get('last_message_at', ''),
                    conversation_data.get('status', 'active'),
                    1 if conversation_data.get('ai_enabled', False) else 0,
                    existing[0]
                ))
                logger.info(f"Updated conversation {existing[0]}")
            else:
                # Insert new conversation
                conversation_id = conversation_data.get('id') or f"conv_{datetime.now().timestamp()}"
                cursor.execute('''
                INSERT INTO conversations (
                    id, match_id, user_id, platform, platform_id,
                    started_at, last_message_at, status, ai_enabled, message_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    conversation_id,
                    conversation_data.get('match_id', ''),
                    conversation_data.get('user_id', ''),
                    conversation_data.get('platform', ''),
                    conversation_data.get('platform_id', ''),
                    conversation_data.get('started_at', datetime.now().isoformat()),
                    conversation_data.get('last_message_at', datetime.now().isoformat()),
                    conversation_data.get('status', 'active'),
                    1 if conversation_data.get('ai_enabled', False) else 0,
                    conversation_data.get('message_count', 0)
                ))
                logger.info(f"Inserted new conversation {conversation_id}")
            
            self.conn.commit()
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error saving conversation: {str(e)}")
            return False
    
    def get_match(self, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a match by ID.
        
        Args:
            match_id: Match ID
            
        Returns:
            Dict or None: Match data if found, None otherwise
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM matches WHERE id = ?", (match_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
                
            # Convert row to dictionary
            columns = [col[0] for col in cursor.description]
            match_data = dict(zip(columns, row))
            
            # Parse JSON fields
            match_data['interests'] = json.loads(match_data.get('interests', '[]'))
            match_data['photos'] = json.loads(match_data.get('photos', '[]'))
            match_data['job'] = json.loads(match_data.get('job', '{}'))
            match_data['is_active'] = bool(match_data.get('is_active', 0))
            
            return match_data
            
        except sqlite3.Error as e:
            logger.error(f"Error getting match: {str(e)}")
            return None
    
    def get_conversation_messages(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get messages for a conversation.
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List[Dict]: List of messages
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM messages WHERE conversation_id = ? ORDER BY sent_at DESC LIMIT ?", 
                (conversation_id, limit)
            )
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            columns = [col[0] for col in cursor.description]
            messages = []
            
            for row in rows:
                message_data = dict(zip(columns, row))
                message_data['ai_generated'] = bool(message_data.get('ai_generated', 0))
                message_data['ai_approved'] = bool(message_data.get('ai_approved', 0))
                messages.append(message_data)
            
            return messages
            
        except sqlite3.Error as e:
            logger.error(f"Error getting conversation messages: {str(e)}")
            return []
    
    def get_active_conversations(self, user_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get active conversations.
        
        Args:
            user_id: User ID (optional)
            limit: Maximum number of conversations to retrieve
            
        Returns:
            List[Dict]: List of conversations
        """
        try:
            cursor = self.conn.cursor()
            
            if user_id:
                cursor.execute(
                    "SELECT * FROM conversations WHERE user_id = ? AND status = 'active' ORDER BY last_message_at DESC LIMIT ?", 
                    (user_id, limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM conversations WHERE status = 'active' ORDER BY last_message_at DESC LIMIT ?", 
                    (limit,)
                )
                
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            columns = [col[0] for col in cursor.description]
            conversations = []
            
            for row in rows:
                conversation_data = dict(zip(columns, row))
                conversation_data['ai_enabled'] = bool(conversation_data.get('ai_enabled', 0))
                conversations.append(conversation_data)
            
            return conversations
            
        except sqlite3.Error as e:
            logger.error(f"Error getting active conversations: {str(e)}")
            return []
