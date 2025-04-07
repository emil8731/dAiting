#!/usr/bin/env python3
"""
Setup script for the Dating App AI Assistant.
Creates the database, initializes tables, and generates default configuration files.
"""

import os
import json
import sqlite3
import argparse
from pathlib import Path

def create_database(db_path):
    """Create the SQLite database and initialize tables."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create matches table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS matches (
        id TEXT PRIMARY KEY,
        platform TEXT NOT NULL,
        platform_id TEXT NOT NULL,
        name TEXT,
        bio TEXT,
        interests TEXT,
        photos TEXT,
        job TEXT,
        education TEXT,
        location TEXT,
        age INTEGER,
        gender INTEGER,
        user_id TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    
    # Create conversations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        match_id TEXT NOT NULL,
        platform TEXT NOT NULL,
        platform_id TEXT NOT NULL,
        status TEXT NOT NULL,
        started_at TEXT,
        last_message_at TEXT,
        message_count INTEGER DEFAULT 0,
        user_id TEXT,
        FOREIGN KEY (match_id) REFERENCES matches (id)
    )
    ''')
    
    # Create messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        conversation_id TEXT NOT NULL,
        sender_type TEXT NOT NULL,
        content TEXT NOT NULL,
        sent_at TEXT,
        ai_generated INTEGER DEFAULT 0,
        ai_approved INTEGER DEFAULT 0,
        FOREIGN KEY (conversation_id) REFERENCES conversations (id)
    )
    ''')
    
    # Create tokens table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tokens (
        id TEXT PRIMARY KEY,
        platform TEXT NOT NULL,
        token TEXT NOT NULL,
        expires_at TEXT,
        created_at TEXT
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"Database created at {db_path}")

def create_config_files(config_dir):
    """Create default configuration files."""
    # Create main config
    main_config = {
        "database_path": "dating_app.db",
        "log_level": "INFO",
        "log_file": "dating_app.log",
        "template_path": "src/data/message_templates.json",
        "openai": {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 150
        }
    }
    
    with open(os.path.join(config_dir, "config.json"), "w") as f:
        json.dump(main_config, f, indent=2)
    
    # Create notification config
    notification_config = {
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
    
    with open(os.path.join(config_dir, "notification_config.json"), "w") as f:
        json.dump(notification_config, f, indent=2)
    
    print(f"Configuration files created in {config_dir}")

def create_data_directories(data_dir):
    """Create necessary data directories."""
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    # Create subdirectories
    os.makedirs(os.path.join(data_dir, "profiles"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "conversations"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "logs"), exist_ok=True)
    
    print(f"Data directories created in {data_dir}")

def create_message_templates(template_path):
    """Create default message templates."""
    templates_dir = os.path.dirname(template_path)
    os.makedirs(templates_dir, exist_ok=True)
    
    templates = {
        "opener": [
            "Hey {name}, I noticed you like {interest}. {hook}",
            "Hi {name}! {hook} I see you're into {interest}, that's awesome!",
            "Hello {name}! {hook}",
            "Hi there {name}! I couldn't help but notice {interest} in your profile. {hook}"
        ],
        "follow_up": [
            "That's really interesting! {hook}",
            "I can relate to that. {hook}",
            "I'd love to hear more about that. {hook}",
            "That sounds amazing! {hook}"
        ],
        "question": [
            "What do you enjoy most about {interest}?",
            "How did you get into {interest}?",
            "What's your favorite thing about {interest}?",
            "Have you been doing {interest} for long?"
        ],
        "generic": [
            "How's your week going so far?",
            "Any exciting plans for the weekend?",
            "What's been the highlight of your week?",
            "What do you like to do for fun?"
        ],
        "travel": [
            "What's your favorite place you've traveled to?",
            "Any travel destinations on your bucket list?",
            "What's the most memorable trip you've taken?",
            "If you could travel anywhere tomorrow, where would you go?"
        ],
        "food": [
            "What's your favorite type of cuisine?",
            "Are you a foodie? Any favorite restaurants?",
            "Do you enjoy cooking or are you more of a restaurant person?",
            "What's the best meal you've had recently?"
        ],
        "music": [
            "What kind of music are you into?",
            "Been to any good concerts lately?",
            "Who are some of your favorite artists?",
            "Do you play any instruments?"
        ],
        "movies": [
            "What's the last great movie you watched?",
            "Any favorite films or directors?",
            "What kind of movies do you enjoy most?",
            "Seen anything good on Netflix lately?"
        ],
        "books": [
            "What are you reading right now?",
            "Who are some of your favorite authors?",
            "What's a book that really impacted you?",
            "Do you prefer fiction or non-fiction?"
        ],
        "sports": [
            "Do you follow any sports teams?",
            "What sports do you enjoy playing?",
            "Been to any good games recently?",
            "Do you prefer watching or playing sports?"
        ],
        "outdoor": [
            "What's your favorite outdoor activity?",
            "Been on any good hikes lately?",
            "What's the most beautiful outdoor place you've visited?",
            "Are you more of a beach or mountains person?"
        ]
    }
    
    with open(template_path, "w") as f:
        json.dump(templates, f, indent=2)
    
    print(f"Message templates created at {template_path}")

def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Setup the Dating App AI Assistant")
    parser.add_argument("--db-path", default="dating_app.db", help="Path to the database file")
    parser.add_argument("--config-dir", default=".", help="Directory for configuration files")
    parser.add_argument("--data-dir", default="data", help="Directory for data files")
    parser.add_argument("--template-path", default="src/data/message_templates.json", help="Path to message templates file")
    
    args = parser.parse_args()
    
    # Create database
    create_database(args.db_path)
    
    # Create config files
    create_config_files(args.config_dir)
    
    # Create data directories
    create_data_directories(args.data_dir)
    
    # Create message templates
    create_message_templates(args.template_path)
    
    print("Setup complete! The Dating App AI Assistant is ready to use.")

if __name__ == "__main__":
    main()
