# Dating App AI Assistant - User Documentation

## Introduction

The Dating App AI Assistant is a powerful tool designed to enhance your online dating experience by automating profile analysis, message generation, and conversation management. This application connects to popular dating platforms like Tinder and Hinge, analyzes your matches' profiles, and helps you create engaging conversations with personalized messages.

## Table of Contents

1. [Installation](#installation)
2. [Setup and Configuration](#setup-and-configuration)
3. [Authentication](#authentication)
4. [Basic Usage](#basic-usage)
5. [Features](#features)
6. [Troubleshooting](#troubleshooting)
7. [Privacy and Security](#privacy-and-security)
8. [Frequently Asked Questions](#frequently-asked-questions)

## Installation

### Prerequisites

Before installing the Dating App AI Assistant, ensure you have the following:

- Python 3.8 or higher
- pip (Python package installer)
- A Tinder or Hinge account
- OpenAI API key (for AI-powered message generation)

### Installation Steps

1. Clone the repository or download the source code:
   ```
   git clone https://github.com/yourusername/dating-app-ai-assistant.git
   cd dating-app-ai-assistant
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Setup and Configuration

### Initial Configuration

1. Run the setup script to create the necessary database and configuration files:
   ```
   python setup.py
   ```

2. Configure notification preferences in the generated `notification_config.json` file:
   ```json
   {
     "enabled": true,
     "notification_types": {
       "new_message": true,
       "new_match": true,
       "conversation_inactive": true,
       "suggested_response": true
     },
     "channels": {
       "console": true,
       "email": false,
       "push": false
     },
     "quiet_hours": {
       "enabled": false,
       "start_hour": 22,
       "end_hour": 8
     }
   }
   ```

3. Customize message templates in `src/data/message_templates.json` if desired.

## Authentication

The Dating App AI Assistant requires authentication with your dating platform accounts. The application supports two authentication methods:

### Tinder Authentication

1. Obtain your Tinder X-Auth-Token:
   - Log in to Tinder in your web browser
   - Open Developer Tools (F12 or right-click > Inspect)
   - Go to the Network tab
   - Refresh the page and look for any API requests
   - Find the `X-Auth-Token` header in the request headers

2. Authenticate with the assistant:
   ```python
   from src.app import DatingAppAIAssistant

   app = DatingAppAIAssistant()
   app.authenticate('tinder', token='your_x_auth_token')
   ```

### Hinge Authentication

1. Authenticate with your phone number:
   ```python
   from src.app import DatingAppAIAssistant

   app = DatingAppAIAssistant()
   # Request verification code
   app.authenticate('hinge', phone_number='+1234567890')
   
   # Complete authentication with verification code
   app.authenticate('hinge', phone_number='+1234567890', verification_code='123456')
   ```

**Note:** Authentication tokens have a limited lifetime. Tinder tokens typically last about 4 days, while Hinge tokens may require more frequent renewal.

## Basic Usage

### Getting Started

Here's a basic example of how to use the Dating App AI Assistant:

```python
from src.app import DatingAppAIAssistant

# Initialize the assistant
app = DatingAppAIAssistant()

# Authenticate with Tinder
app.authenticate('tinder', token='your_x_auth_token')

# Get recent matches
matches = app.get_matches('tinder', limit=10)

# Generate a message for a match
match_id = matches[0]['id']
message = app.generate_initial_message(match_id)

# Review and send the message
print(f"Generated message: {message['content']}")
app.approve_and_send_message('tinder', match_id, message)

# Start monitoring the conversation
conversation_id = "conversation_id_here"  # You'll get this from the database
app.start_conversation_monitoring(conversation_id, 'tinder')

# Get conversation insights
insights = app.get_conversation_insights(conversation_id)
print(insights)

# Generate a response to a new message
response = app.generate_response(conversation_id)
print(f"Generated response: {response['content']}")

# Edit and send the response
app.edit_and_send_message('tinder', match_id, response, "My edited response")

# Close the application
app.close()
```

### Command-Line Interface

The Dating App AI Assistant also includes a command-line interface for easier usage:

```
python cli.py --help
python cli.py auth tinder --token YOUR_TOKEN
python cli.py matches tinder --limit 5
python cli.py message tinder MATCH_ID
```

## Features

### Profile Analysis

The assistant analyzes match profiles to identify:
- Interests and hobbies
- Conversation hooks
- Potential topics for discussion
- Compatibility factors

### Message Generation

Generate personalized messages based on:
- Match profile information
- Shared interests
- Conversation context
- Your preferred tone and style

The message generator uses both template-based generation and AI-powered content creation to craft engaging messages.

### Conversation Management

The conversation manager helps you:
- Track active conversations
- Monitor for new messages
- Generate contextually appropriate responses
- Analyze conversation flow and engagement
- Receive suggestions for improving conversations

### Notifications

The notification system alerts you about:
- New matches
- New messages
- Suggested responses
- Inactive conversations

You can customize notification preferences and set quiet hours.

### Analytics

The analytics module provides insights into:
- Conversation statistics
- Message patterns
- Response rates
- Engagement metrics
- User activity over time

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Ensure your token is correct and not expired
   - Check your internet connection
   - Verify that the dating platform's API hasn't changed

2. **Message Generation Issues**
   - Verify your OpenAI API key is valid
   - Check your internet connection
   - Ensure the match profile contains sufficient information

3. **Database Errors**
   - Check file permissions for the database file
   - Ensure you have sufficient disk space
   - Try backing up and recreating the database

### Logging

The application creates a log file (`dating_app.log`) that can help diagnose issues. Check this file for error messages and warnings.

## Privacy and Security

### Data Storage

The Dating App AI Assistant stores the following data locally:
- Match profiles
- Conversation history
- Generated messages
- Authentication tokens (encrypted)

No data is sent to external servers except for:
- API requests to dating platforms
- OpenAI API requests for message generation

### Security Recommendations

1. Keep your authentication tokens secure
2. Don't share your `.env` file or database
3. Regularly update the application
4. Use a strong password for your dating platform accounts

## Frequently Asked Questions

**Q: Is using this application against dating platform terms of service?**
A: Dating platforms typically prohibit automated access to their services. Use this application at your own risk and be aware of the terms of service for each platform.

**Q: How often should I refresh my authentication tokens?**
A: Tinder tokens typically last about 4 days, while Hinge tokens may require more frequent renewal. The application will notify you when tokens need to be refreshed.

**Q: Can the assistant completely automate my dating experience?**
A: The assistant is designed to enhance your dating experience, not replace your personal involvement. We recommend reviewing and approving all messages before sending them.

**Q: How can I customize the message generation?**
A: You can edit the message templates in `src/data/message_templates.json` to match your preferred style and tone.

**Q: Is my data secure?**
A: All data is stored locally on your device. Authentication tokens are encrypted, but you should still take precautions to secure your computer and files.
