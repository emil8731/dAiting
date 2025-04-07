# Dating App AI Assistant - Developer Documentation

## Architecture Overview

The Dating App AI Assistant is built with a modular architecture that separates concerns and allows for easy extension and maintenance. This document provides an overview of the system architecture, component interactions, and implementation details for developers.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Module Descriptions](#module-descriptions)
3. [Data Models](#data-models)
4. [Component Interactions](#component-interactions)
5. [Extension Points](#extension-points)
6. [Development Guidelines](#development-guidelines)
7. [Testing](#testing)

## System Architecture

The application follows a layered architecture with the following main components:

1. **Platform Integration Layer**: Handles authentication and interaction with dating platforms
2. **Data Management Layer**: Manages storage and retrieval of profiles, conversations, and messages
3. **AI Processing Layer**: Analyzes profiles and generates personalized messages
4. **Conversation Management Layer**: Tracks and manages ongoing conversations
5. **User Interface Layer**: Provides interfaces for user interaction (CLI, potential web UI)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Dating App AI Assistant                     │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Main Application (app.py)                    │
└─────────────────────────────────────────────────────────────────┘
                                  │
                 ┌────────────────┼────────────────┐
                 │                │                │
                 ▼                ▼                ▼
┌───────────────────────┐ ┌──────────────┐ ┌──────────────────────┐
│ Platform Integration  │ │    Storage   │ │ Message Generation   │
│  - Authentication     │ │  - Database  │ │  - Profile Analysis  │
│  - Profile Scraping   │ │  - Data      │ │  - Template-based    │
│  - Message Sending    │ │    Models    │ │  - AI-powered        │
└───────────────────────┘ └──────────────┘ └──────────────────────┘
          │                      │                    │
          └──────────────────────┼────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Conversation Management                       │
│  - Message History Tracking                                      │
│  - Response Generation                                           │
│  - Conversation Flow Management                                  │
│  - Notification System                                           │
│  - Analytics                                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Module Descriptions

### Platform Integration (`src/platform/`)

The platform integration layer handles authentication and interaction with dating platforms. It includes:

- **BaseAuthenticator** (`auth.py`): Abstract base class for platform authentication
- **TinderAuthenticator** (`tinder_auth.py`): Tinder-specific authentication
- **HingeAuthenticator** (`hinge_auth.py`): Hinge-specific authentication
- **BaseProfileScraper** (`scraper.py`): Abstract base class for profile scraping
- **TinderProfileScraper** (`tinder_scraper.py`): Tinder-specific profile scraping
- **HingeProfileScraper** (`hinge_scraper.py`): Hinge-specific profile scraping
- **PlatformFactory** (`factory.py`): Factory for creating platform-specific components

### Data Management (`src/storage.py`)

The data management layer handles storage and retrieval of profiles, conversations, and messages. It includes:

- **DataStorage**: Main class for database operations
- SQLite database with tables for matches, conversations, and messages

### AI Processing (`src/message_generator.py`)

The AI processing layer analyzes profiles and generates personalized messages. It includes:

- **ProfileAnalyzer**: Analyzes match profiles to identify interests, hooks, and topics
- **MessageGenerator**: Generates personalized messages using templates and AI

### Conversation Management (`src/conversation_manager.py`, `src/notification_system.py`, `src/analytics.py`)

The conversation management layer tracks and manages ongoing conversations. It includes:

- **ConversationManager**: Tracks conversations and generates responses
- **NotificationSystem**: Manages notifications for new messages and events
- **ConversationAnalytics**: Analyzes conversation data and generates insights

### User Interface (`src/app.py`, `cli.py`)

The user interface layer provides interfaces for user interaction. It includes:

- **DatingAppAIAssistant** (`app.py`): Main application class that integrates all components
- **CLI** (`cli.py`): Command-line interface for the application

## Data Models

### Match

Represents a match from a dating platform:

- `id`: Unique identifier
- `platform`: Platform name (tinder, hinge)
- `platform_id`: Platform-specific identifier
- `name`: Match name
- `bio`: Match bio/description
- `interests`: List of interests
- `photos`: List of photo URLs
- `job`: Job information
- `education`: Education information
- `location`: Location information
- `age`: Age
- `gender`: Gender

### Conversation

Represents a conversation with a match:

- `id`: Unique identifier
- `match_id`: Match identifier
- `platform`: Platform name
- `platform_id`: Platform-specific identifier
- `status`: Conversation status (active, archived)
- `started_at`: Start timestamp
- `last_message_at`: Last message timestamp
- `message_count`: Number of messages

### Message

Represents a message in a conversation:

- `id`: Unique identifier
- `conversation_id`: Conversation identifier
- `sender_type`: Sender type (user, match)
- `content`: Message content
- `sent_at`: Sent timestamp
- `ai_generated`: Whether the message was AI-generated
- `ai_approved`: Whether the AI-generated message was approved

## Component Interactions

### Authentication Flow

1. User provides platform-specific authentication parameters
2. `DatingAppAIAssistant` calls `authenticate` on the appropriate authenticator
3. Authenticator validates credentials and stores authentication token
4. Token is used for subsequent API requests

### Profile Scraping Flow

1. User requests matches from a platform
2. `DatingAppAIAssistant` calls `get_matches` on the appropriate scraper
3. Scraper retrieves match profiles from the platform API
4. Profiles are normalized and stored in the database

### Message Generation Flow

1. User requests a message for a match
2. `DatingAppAIAssistant` calls `generate_initial_message` or `generate_response`
3. `MessageGenerator` analyzes the match profile and/or conversation history
4. `MessageGenerator` generates a personalized message using templates or AI
5. Message is returned to the user for approval

### Conversation Management Flow

1. User approves and sends a message
2. `DatingAppAIAssistant` calls `approve_and_send_message`
3. Message is sent to the platform API and stored in the database
4. `ConversationManager` tracks the conversation and monitors for new messages
5. `NotificationSystem` notifies the user of new messages or events
6. `ConversationAnalytics` generates insights about the conversation

## Extension Points

The Dating App AI Assistant is designed to be extensible. Here are the main extension points:

### Adding a New Dating Platform

1. Create a new authenticator class that extends `BaseAuthenticator`
2. Create a new scraper class that extends `BaseProfileScraper`
3. Update `PlatformFactory` to support the new platform

### Customizing Message Generation

1. Edit message templates in `src/data/message_templates.json`
2. Extend `ProfileAnalyzer` to extract additional information from profiles
3. Modify `MessageGenerator` to use different AI models or techniques

### Adding New Analytics

1. Add new methods to `ConversationAnalytics` for additional insights
2. Update the database schema to store additional data if needed

## Development Guidelines

### Coding Standards

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all classes and methods
- Use meaningful variable and function names

### Error Handling

- Use exceptions for error conditions
- Catch and handle exceptions at appropriate levels
- Log errors with sufficient context for debugging

### Logging

- Use the Python logging module
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Include relevant context in log messages

### Security

- Never hardcode credentials or tokens
- Use environment variables for sensitive information
- Encrypt stored tokens and credentials
- Validate and sanitize user input

## Testing

The Dating App AI Assistant includes comprehensive tests:

### Unit Tests

Unit tests for individual components:

- `tests/test_auth.py`: Tests for authenticators
- `tests/test_scraper.py`: Tests for scrapers
- `tests/test_message_generator.py`: Tests for message generation
- `tests/test_conversation_manager.py`: Tests for conversation management
- `tests/test_notification_system.py`: Tests for notifications
- `tests/test_analytics.py`: Tests for analytics

### Integration Tests

Integration tests for component interactions:

- `tests/test_integration.py`: Tests for component integration

### End-to-End Tests

End-to-end tests for complete workflows:

- `tests/test_integration.py`: Includes end-to-end flow tests

### Running Tests

Run all tests with the test runner:

```
python run_tests.py
```

Run specific tests with unittest:

```
python -m unittest tests/test_auth.py
```
