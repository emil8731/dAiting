# Tinder API Research

## Overview
This document contains research findings about the Tinder API, authentication methods, and data extraction capabilities for the Dating App AI Assistant project.

## API Base URL
- Live Server: `https://api.gotinder.com`

## Authentication
Tinder uses Basic Authentication with tokens in UUID format to secure their API. A request needs an `X-Auth-Token` header in order to be authenticated.

### Getting a Token
1. Login to Tinder in your browser
2. Open the network tab and filter for `api.gotinder.com`
3. Choose any GET or POST request and go to the Request Headers
4. Find the `X-Auth-Token` header containing the auth token
5. Note: You might need to perform some actions first (for example liking a user) before you see any requests

### Token Lifetime
- Tokens have a lifetime of approximately 4 days if no logout occurs
- This is an empirical value observed over 3 months of testing

## Profile Endpoint
- Endpoint: `GET https://api.gotinder.com/profile`
- Returns information about the self user

### Profile Data Structure
The profile endpoint returns a JSON object with the following key fields:
- `id`: string - User ID
- `age_filter_max`: number - Maximum age filter setting
- `age_filter_min`: number - Minimum age filter setting
- `badges`: array[object] - Profile badges
- `bio`: string - User biography
- `birth_date`: string - User birth date
- `create_date`: string - Account creation date
- `distance_filter`: number - Distance filter setting
- `email`: string - User email
- `gender`: number - User gender
- `gender_filter`: number - Gender filter setting
- `instagram`: object - Connected Instagram account information
  - `last_fetch_time`: string
  - `completed_initial_fetch`: boolean
  - `photos`: array[object] - Instagram photos
- `interested_in`: array[object] - User interests
- `jobs`: array[object] - Company and job title information
  - `company`: object
  - `title`: object
- `name`: string - User name
- `photos`: array[object] - Profile photos
  - `id`: string - Photo ID
  - `assets`: array[object] - Photo assets
  - `type`: string - Photo type

## Legal and Ethical Considerations
- Tinder does not provide an official public API
- Using unofficial APIs may violate Tinder's Terms of Service
- Accounts may be banned for automated usage or scraping
- Authentication tokens should be stored securely
- User data should be handled with privacy in mind
- Automated messaging should be transparent to avoid deceptive practices

## Technical Implementation Challenges
- Token expiration requires re-authentication
- Rate limiting may be in place to prevent excessive requests
- Platform structure changes may break API functionality
- IP-based blocking for automated access
- Need for regular updates to adapt to platform changes

## References
- [Tinder API Documentation on GitHub](https://gist.github.com/rtt/10403467)
- [Unofficial Tinder API Documentation](https://rednit.stoplight.io/)
