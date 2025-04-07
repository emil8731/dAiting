#!/usr/bin/env python3
"""
Command-line interface for the Dating App AI Assistant.
"""

import os
import sys
import argparse
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.app import DatingAppAIAssistant

def auth_command(args):
    """Handle authentication commands."""
    app = DatingAppAIAssistant()
    
    if args.platform == 'tinder':
        if not args.token:
            print("Error: Tinder authentication requires a token.")
            return 1
        
        result = app.authenticate('tinder', token=args.token)
        if result:
            print("Successfully authenticated with Tinder!")
        else:
            print("Failed to authenticate with Tinder.")
            return 1
    
    elif args.platform == 'hinge':
        if not args.phone_number:
            print("Error: Hinge authentication requires a phone number.")
            return 1
        
        if args.verification_code:
            # Complete authentication with verification code
            result = app.authenticate('hinge', phone_number=args.phone_number, verification_code=args.verification_code)
            if result:
                print("Successfully authenticated with Hinge!")
            else:
                print("Failed to authenticate with Hinge.")
                return 1
        else:
            # Request verification code
            result = app.authenticate('hinge', phone_number=args.phone_number)
            if result:
                print("Verification code sent to your phone. Run the command again with --verification-code to complete authentication.")
            else:
                print("Failed to request verification code from Hinge.")
                return 1
    
    else:
        print(f"Error: Unsupported platform '{args.platform}'.")
        return 1
    
    return 0

def matches_command(args):
    """Handle matches commands."""
    app = DatingAppAIAssistant()
    
    try:
        matches = app.get_matches(args.platform, limit=args.limit)
        
        if not matches:
            print(f"No matches found on {args.platform}.")
            return 0
        
        print(f"Found {len(matches)} matches on {args.platform}:")
        for i, match in enumerate(matches, 1):
            print(f"{i}. {match['name']} (ID: {match['id']})")
            if 'bio' in match and match['bio']:
                print(f"   Bio: {match['bio'][:100]}...")
            if 'interests' in match and match['interests']:
                interests = match['interests'] if isinstance(match['interests'], list) else match['interests'].split(',')
                print(f"   Interests: {', '.join(interests)}")
            print()
        
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

def message_command(args):
    """Handle message commands."""
    app = DatingAppAIAssistant()
    
    try:
        # Generate initial message
        message = app.generate_initial_message(args.match_id)
        
        if not message:
            print(f"Failed to generate message for match {args.match_id}.")
            return 1
        
        print(f"Generated message: {message['content']}")
        
        # Ask for approval
        if not args.auto_approve:
            approval = input("Do you want to send this message? (y/n/e for edit): ").lower()
            
            if approval == 'n':
                print("Message not sent.")
                return 0
            
            elif approval == 'e':
                edited_content = input("Enter your edited message: ")
                result = app.edit_and_send_message(args.platform, args.match_id, message, edited_content)
            
            else:  # 'y' or any other input
                result = app.approve_and_send_message(args.platform, args.match_id, message)
        
        else:
            result = app.approve_and_send_message(args.platform, args.match_id, message)
        
        if result:
            print("Message sent successfully!")
        else:
            print("Failed to send message.")
            return 1
        
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

def conversation_command(args):
    """Handle conversation commands."""
    app = DatingAppAIAssistant()
    
    try:
        if args.action == 'list':
            conversations = app.get_active_conversations(args.platform, limit=args.limit)
            
            if not conversations:
                print(f"No active conversations found{' on ' + args.platform if args.platform else ''}.")
                return 0
            
            print(f"Active conversations{' on ' + args.platform if args.platform else ''}:")
            for i, conv in enumerate(conversations, 1):
                match_name = conv.get('match_name', 'Unknown')
                last_message = conv.get('last_message_at', 'Unknown')
                if isinstance(last_message, str):
                    try:
                        last_message = datetime.fromisoformat(last_message.replace('Z', '+00:00'))
                        last_message = last_message.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                
                print(f"{i}. {match_name} (ID: {conv['id']})")
                print(f"   Last message: {last_message}")
                print(f"   Message count: {conv.get('message_count', 0)}")
                print()
        
        elif args.action == 'view':
            if not args.conversation_id:
                print("Error: Conversation ID is required for 'view' action.")
                return 1
            
            messages = app.get_conversation_history(args.conversation_id, limit=args.limit)
            
            if not messages:
                print(f"No messages found in conversation {args.conversation_id}.")
                return 0
            
            print(f"Messages in conversation {args.conversation_id}:")
            for i, msg in enumerate(messages, 1):
                sender = "You" if msg['sender_type'] == 'user' else "Match"
                sent_at = msg.get('sent_at', 'Unknown')
                if isinstance(sent_at, str):
                    try:
                        sent_at = datetime.fromisoformat(sent_at.replace('Z', '+00:00'))
                        sent_at = sent_at.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                
                print(f"{i}. {sender} ({sent_at}):")
                print(f"   {msg['content']}")
                print()
        
        elif args.action == 'respond':
            if not args.conversation_id:
                print("Error: Conversation ID is required for 'respond' action.")
                return 1
            
            response = app.generate_response(args.conversation_id)
            
            if not response:
                print(f"Failed to generate response for conversation {args.conversation_id}.")
                return 1
            
            print(f"Generated response: {response['content']}")
            
            # Ask for approval
            if not args.auto_approve:
                approval = input("Do you want to send this response? (y/n/e for edit): ").lower()
                
                if approval == 'n':
                    print("Response not sent.")
                    return 0
                
                elif approval == 'e':
                    edited_content = input("Enter your edited response: ")
                    # Get match ID from conversation
                    match_id = app.get_match_id_from_conversation(args.conversation_id)
                    if not match_id:
                        print("Failed to get match ID from conversation.")
                        return 1
                    
                    platform = app.get_platform_from_conversation(args.conversation_id)
                    if not platform:
                        print("Failed to get platform from conversation.")
                        return 1
                    
                    result = app.edit_and_send_message(platform, match_id, response, edited_content)
                
                else:  # 'y' or any other input
                    # Get match ID from conversation
                    match_id = app.get_match_id_from_conversation(args.conversation_id)
                    if not match_id:
                        print("Failed to get match ID from conversation.")
                        return 1
                    
                    platform = app.get_platform_from_conversation(args.conversation_id)
                    if not platform:
                        print("Failed to get platform from conversation.")
                        return 1
                    
                    result = app.approve_and_send_message(platform, match_id, response)
            
            else:
                # Get match ID from conversation
                match_id = app.get_match_id_from_conversation(args.conversation_id)
                if not match_id:
                    print("Failed to get match ID from conversation.")
                    return 1
                
                platform = app.get_platform_from_conversation(args.conversation_id)
                if not platform:
                    print("Failed to get platform from conversation.")
                    return 1
                
                result = app.approve_and_send_message(platform, match_id, response)
            
            if result:
                print("Response sent successfully!")
            else:
                print("Failed to send response.")
                return 1
        
        elif args.action == 'monitor':
            if not args.conversation_id:
                print("Error: Conversation ID is required for 'monitor' action.")
                return 1
            
            platform = app.get_platform_from_conversation(args.conversation_id)
            if not platform:
                print("Failed to get platform from conversation.")
                return 1
            
            result = app.start_conversation_monitoring(args.conversation_id, platform)
            
            if result:
                print(f"Started monitoring conversation {args.conversation_id}.")
            else:
                print(f"Failed to start monitoring conversation {args.conversation_id}.")
                return 1
        
        elif args.action == 'stop':
            if not args.conversation_id:
                print("Error: Conversation ID is required for 'stop' action.")
                return 1
            
            result = app.stop_conversation_monitoring(args.conversation_id)
            
            if result:
                print(f"Stopped monitoring conversation {args.conversation_id}.")
            else:
                print(f"Failed to stop monitoring conversation {args.conversation_id}.")
                return 1
        
        elif args.action == 'insights':
            if not args.conversation_id:
                print("Error: Conversation ID is required for 'insights' action.")
                return 1
            
            insights = app.get_conversation_insights(args.conversation_id)
            
            if not insights:
                print(f"Failed to get insights for conversation {args.conversation_id}.")
                return 1
            
            print(f"Insights for conversation with {insights.get('match_name', 'Unknown')}:")
            print(f"- Message count: {insights.get('message_count', 0)}")
            print(f"- Conversation stage: {insights.get('stage', 'Unknown')}")
            print(f"- Average message length: {insights.get('avg_message_length', 0):.1f} characters")
            print(f"- Question count: {insights.get('question_count', 0)}")
            
            if 'common_words' in insights and insights['common_words']:
                print("- Common topics:")
                for word in insights['common_words'][:5]:
                    print(f"  * {word['word']} ({word['count']} occurrences)")
            
            if 'insights' in insights and insights['insights']:
                print("\nSuggestions and observations:")
                for insight in insights['insights']:
                    prefix = "⚠️ " if insight['type'] == 'warning' else "💡 " if insight['type'] == 'suggestion' else "ℹ️ "
                    print(f"{prefix} {insight['message']}")
        
        else:
            print(f"Error: Unsupported action '{args.action}'.")
            return 1
        
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

def stats_command(args):
    """Handle stats commands."""
    app = DatingAppAIAssistant()
    
    try:
        if args.type == 'user':
            stats = app.get_user_stats()
            
            print("User Statistics:")
            print(f"- Total matches: {stats.get('total_matches', 0)}")
            print(f"- Total conversations: {stats.get('total_conversations', 0)}")
            print(f"- Total messages: {stats.get('total_messages', 0)}")
            
            if 'matches_by_platform' in stats and stats['matches_by_platform']:
                print("\nMatches by platform:")
                for platform, count in stats['matches_by_platform'].items():
                    print(f"- {platform.capitalize()}: {count}")
            
            if 'ai_generated_count' in stats and 'ai_approved_count' in stats:
                print(f"\nAI-generated messages: {stats.get('ai_generated_count', 0)}")
                print(f"AI-approved messages: {stats.get('ai_approved_count', 0)}")
                approval_rate = stats.get('ai_approval_rate', 0) * 100
                print(f"AI approval rate: {approval_rate:.1f}%")
        
        elif args.type == 'activity':
            activity = app.get_message_activity(days=args.days)
            
            print(f"Message Activity (Last {args.days} days):")
            print(f"- Total messages: {activity.get('total_messages', 0)}")
            
            if 'daily_counts' in activity and activity['daily_counts']:
                print("\nDaily message counts:")
                sorted_days = sorted(activity['daily_counts'].keys())
                for day in sorted_days[-min(7, len(sorted_days)):]:
                    count = activity['daily_counts'][day]
                    print(f"- {day}: {count}")
            
            if 'hourly_distribution' in activity and activity['hourly_distribution']:
                print("\nHourly distribution:")
                for hour in range(24):
                    hour_str = str(hour)
                    count = activity['hourly_distribution'].get(hour_str, 0)
                    bar = '█' * min(count, 20)
                    print(f"- {hour:02d}:00: {bar} ({count})")
        
        else:
            print(f"Error: Unsupported stats type '{args.type}'.")
            return 1
        
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Dating App AI Assistant CLI")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Authentication command
    auth_parser = subparsers.add_parser('auth', help='Authenticate with a dating platform')
    auth_parser.add_argument('platform', choices=['tinder', 'hinge'], help='Platform to authenticate with')
    auth_parser.add_argument('--token', help='Authentication token (for Tinder)')
    auth_parser.add_argument('--phone-number', help='Phone number (for Hinge)')
    auth_parser.add_argument('--verification-code', help='Verification code (for Hinge)')
    
    # Matches command
    matches_parser = subparsers.add_parser('matches', help='Get matches from a platform')
    matches_parser.add_argument('platform', choices=['tinder', 'hinge'], help='Platform to get matches from')
    matches_parser.add_argument('--limit', type=int, default=10, help='Maximum number of matches to retrieve')
    
    # Message command
    message_parser = subparsers.add_parser('message', help='Generate and send a message to a match')
    message_parser.add_argument('platform', choices=['tinder', 'hinge'], help='Platform to send message on')
    message_parser.add_argument('match_id', help='ID of the match to message')
    message_parser.add_argument('--auto-approve', action='store_true', help='Automatically approve and send the message')
    
    # Conversation command
    conversation_parser = subparsers.add_parser('conversation', help='Manage conversations')
    conversation_parser.add_argument('action', choices=['list', 'view', 'respond', 'monitor', 'stop', 'insights'], 
                                    help='Action to perform')
    conversation_parser.add_argument('--platform', choices=['tinder', 'hinge'], help='Platform to filter by (for list)')
    conversation_parser.add_argument('--conversation-id', help='ID of the conversation (for view, respond, monitor, stop, insights)')
    conversation_parser.add_argument('--limit', type=int, default=20, help='Maximum number of items to retrieve')
    conversation_parser.add_argument('--auto-approve', action='store_true', help='Automatically approve and send responses')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Get statistics')
    stats_parser.add_argument('type', choices=['user', 'activity'], help='Type of statistics to retrieve')
    stats_parser.add_argument('--days', type=int, default=30, help='Number of days to include in activity stats')
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 0
    
    # Dispatch to the appropriate command handler
    if args.command == 'auth':
        return auth_command(args)
    elif args.command == 'matches':
        return matches_command(args)
    elif args.command == 'message':
        return message_command(args)
    elif args.command == 'conversation':
        return conversation_command(args)
    elif args.command == 'stats':
        return stats_command(args)
    else:
        print(f"Error: Unknown command '{args.command}'.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
