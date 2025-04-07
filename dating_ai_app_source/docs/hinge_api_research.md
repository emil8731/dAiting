# Hinge API Research

## Overview
This document contains research findings about the Hinge API, authentication methods, and data extraction capabilities for the Dating App AI Assistant project.

## API Base URL
- Live Server: `https://prod-api.hingeaws.net/`

## Authentication Flow
Based on the reverse-engineered "squeaky-hinge" project, Hinge's authentication flow involves:

1. Generate a UUID to represent the installation of Hinge
2. Post the UUID to `https://prod-api.hingeaws.net/identity/install`
3. Use Firebase web API key (hardcoded in Hinge APK) to get a reCAPTCHA config from Google Identity Platform
4. Solve reCAPTCHA to get a token
5. Use the token to request an SMS verification code sent to the user's phone
6. Submit the verification code to complete authentication
7. Store the resulting API credentials for future requests

## Message Retrieval
Hinge uses SendBird as their messaging platform. The authentication flow provides access to:
- Fetch conversations
- Retrieve message history
- Monitor for new messages

## Profile Data Extraction
While specific endpoint details aren't fully documented, the reverse-engineered client suggests the ability to access:
- Match profiles
- Conversation history
- User information

## Implementation Approach
The "squeaky-hinge" project demonstrates a working implementation with these components:
- Authentication module (`auth.py`)
- Conversation retrieval (`conversations.py`)
- Message reading functionality (`reader.py`)
- Main application logic (`squeaky_hinge.py`)

## Technical Implementation Challenges
- Complex authentication flow involving third-party services (Google Identity Platform, reCAPTCHA)
- Need for SMS verification during authentication
- Potential for detection and blocking when accessing from non-mobile IPs
- Regular updates required to adapt to platform changes

## Legal and Ethical Considerations
- Hinge does not provide an official public API
- Using unofficial APIs may violate Hinge's Terms of Service
- Accounts may be banned for automated usage or scraping
- Authentication tokens should be stored securely
- User data should be handled with privacy in mind
- Automated messaging should be transparent to avoid deceptive practices

## References
- [Squeaky Hinge GitHub Repository](https://github.com/radian-software/squeaky-hinge)
- [Google Identity Platform Documentation](https://cloud.google.com/identity-platform/docs)
