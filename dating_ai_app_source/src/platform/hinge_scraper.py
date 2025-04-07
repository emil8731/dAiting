"""
Hinge-specific profile scraper module.
Implements profile scraping for the Hinge platform.
"""

import requests
import logging
import json
from typing import Dict, List, Any, Optional

from .scraper import BaseProfileScraper, ScrapingError
from .hinge_auth import HingeAuthenticator

logger = logging.getLogger('platform.hinge_scraper')

class HingeProfileScraper(BaseProfileScraper):
    """Profile scraper for the Hinge platform."""
    
    BASE_URL = "https://prod-api.hingeaws.net"
    SENDBIRD_URL = "https://api-{app_id}.sendbird.com/v3"
    SENDBIRD_APP_ID = "2D7B4CDB-932F-458D-9CBF-2781B4E0C241"  # From app
    
    def __init__(self, authenticator: HingeAuthenticator):
        """
        Initialize the Hinge profile scraper.
        
        Args:
            authenticator: Hinge authenticator
        """
        super().__init__(authenticator)
        self.authenticator = authenticator  # Type hint for IDE
        self.sendbird_token = self.authenticator.credentials.get('sendbird_token')
    
    def get_user_profile(self) -> Dict[str, Any]:
        """
        Get the authenticated user's profile.
        
        Returns:
            Dict: User profile data
        """
        if not self.authenticator.is_authenticated():
            raise ScrapingError("Not authenticated. Cannot get user profile.")
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/users/me",
                headers=self.authenticator.get_auth_headers()
            )
            
            if response.status_code == 200:
                profile_data = response.json()
                logger.info("Successfully retrieved user profile data")
                return profile_data
            else:
                logger.error(f"Failed to get user profile: {response.status_code} - {response.text}")
                raise ScrapingError(f"Failed to get user profile: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Request error while getting user profile: {str(e)}")
            raise ScrapingError(f"Request error: {str(e)}")
    
    def get_matches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the user's matches.
        
        Args:
            limit: Maximum number of matches to retrieve
            
        Returns:
            List[Dict]: List of match profiles
        """
        if not self.authenticator.is_authenticated():
            raise ScrapingError("Not authenticated. Cannot get matches.")
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/relationships",
                params={"type": "match", "page_size": limit},
                headers=self.authenticator.get_auth_headers()
            )
            
            if response.status_code == 200:
                matches_data = response.json()
                matches = matches_data.get('results', [])
                logger.info(f"Successfully retrieved {len(matches)} matches")
                return matches
            else:
                logger.error(f"Failed to get matches: {response.status_code} - {response.text}")
                raise ScrapingError(f"Failed to get matches: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Request error while getting matches: {str(e)}")
            raise ScrapingError(f"Request error: {str(e)}")
    
    def get_match_profile(self, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific match's profile.
        
        Args:
            match_id: ID of the match
            
        Returns:
            Dict or None: Match profile data if found, None otherwise
        """
        if not self.authenticator.is_authenticated():
            raise ScrapingError("Not authenticated. Cannot get match profile.")
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/users/{match_id}",
                headers=self.authenticator.get_auth_headers()
            )
            
            if response.status_code == 200:
                profile_data = response.json()
                logger.info(f"Successfully retrieved profile for match {match_id}")
                return profile_data
            elif response.status_code == 404:
                logger.warning(f"Match {match_id} not found")
                return None
            else:
                logger.error(f"Failed to get match profile: {response.status_code} - {response.text}")
                raise ScrapingError(f"Failed to get match profile: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Request error while getting match profile: {str(e)}")
            raise ScrapingError(f"Request error: {str(e)}")
    
    def get_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the user's conversations.
        
        Args:
            limit: Maximum number of conversations to retrieve
            
        Returns:
            List[Dict]: List of conversations
        """
        if not self.authenticator.is_authenticated():
            raise ScrapingError("Not authenticated. Cannot get conversations.")
        
        # Ensure we have a SendBird token
        if not self.sendbird_token:
            self._get_sendbird_token()
        
        try:
            # Get conversations from SendBird
            response = requests.get(
                f"{self.SENDBIRD_URL.format(app_id=self.SENDBIRD_APP_ID)}/users/me/group_channels",
                params={"limit": limit},
                headers=self._get_sendbird_headers()
            )
            
            if response.status_code == 200:
                conversations_data = response.json()
                conversations = conversations_data.get('channels', [])
                logger.info(f"Successfully retrieved {len(conversations)} conversations")
                return conversations
            else:
                logger.error(f"Failed to get conversations: {response.status_code} - {response.text}")
                raise ScrapingError(f"Failed to get conversations: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Request error while getting conversations: {str(e)}")
            raise ScrapingError(f"Request error: {str(e)}")
    
    def get_conversation_messages(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get messages from a specific conversation.
        
        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of messages to retrieve
            
        Returns:
            List[Dict]: List of messages
        """
        if not self.authenticator.is_authenticated():
            raise ScrapingError("Not authenticated. Cannot get conversation messages.")
        
        # Ensure we have a SendBird token
        if not self.sendbird_token:
            self._get_sendbird_token()
        
        try:
            # Get messages from SendBird
            response = requests.get(
                f"{self.SENDBIRD_URL.format(app_id=self.SENDBIRD_APP_ID)}/group_channels/{conversation_id}/messages",
                params={"limit": limit},
                headers=self._get_sendbird_headers()
            )
            
            if response.status_code == 200:
                messages_data = response.json()
                messages = messages_data.get('messages', [])
                logger.info(f"Successfully retrieved {len(messages)} messages for conversation {conversation_id}")
                return messages
            else:
                logger.error(f"Failed to get messages: {response.status_code} - {response.text}")
                raise ScrapingError(f"Failed to get messages: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Request error while getting messages: {str(e)}")
            raise ScrapingError(f"Request error: {str(e)}")
    
    def _get_sendbird_token(self) -> None:
        """
        Get a SendBird token for messaging.
        
        Raises:
            ScrapingError: If token retrieval fails
        """
        if not self.authenticator.is_authenticated():
            raise ScrapingError("Not authenticated. Cannot get SendBird token.")
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/chat/token",
                headers=self.authenticator.get_auth_headers()
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.sendbird_token = token_data.get('token')
                
                if not self.sendbird_token:
                    logger.error("SendBird token response did not contain token")
                    raise ScrapingError("Failed to get SendBird token: No token in response")
                
                # Save token in authenticator credentials
                self.authenticator.credentials['sendbird_token'] = self.sendbird_token
                self.authenticator._save_credentials()
                
                logger.info("Successfully retrieved SendBird token")
            else:
                logger.error(f"Failed to get SendBird token: {response.status_code} - {response.text}")
                raise ScrapingError(f"Failed to get SendBird token: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Request error while getting SendBird token: {str(e)}")
            raise ScrapingError(f"Request error: {str(e)}")
    
    def _get_sendbird_headers(self) -> Dict[str, str]:
        """
        Get headers for SendBird API requests.
        
        Returns:
            Dict[str, str]: Headers for SendBird API
        """
        return {
            "Authorization": f"Bearer {self.sendbird_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def normalize_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Hinge profile data to a standard format.
        
        Args:
            profile_data: Raw profile data from Hinge
            
        Returns:
            Dict: Normalized profile data
        """
        if not profile_data:
            return {}
            
        # Extract basic information
        normalized = {
            'id': profile_data.get('id', ''),
            'name': profile_data.get('first_name', ''),
            'bio': self.extract_bio(profile_data),
            'age': profile_data.get('age', 0),
            'gender': profile_data.get('gender', 0),
            'photos': [],
            'interests': self.extract_interests(profile_data),
            'job': {
                'title': '',
                'company': ''
            },
            'education': '',
            'location': '',
            'last_active': profile_data.get('last_active', ''),
            'platform': 'hinge'
        }
        
        # Extract photos
        if 'photos' in profile_data:
            for photo in profile_data['photos']:
                if 'url' in photo:
                    normalized['photos'].append({
                        'id': photo.get('id', ''),
                        'url': photo.get('url', '')
                    })
        
        # Extract job information
        if 'work' in profile_data:
            normalized['job']['title'] = profile_data.get('work', {}).get('position', '')
            normalized['job']['company'] = profile_data.get('work', {}).get('company_name', '')
        
        # Extract education information
        if 'education' in profile_data:
            schools = []
            for edu in profile_data.get('education', []):
                if 'school_name' in edu:
                    schools.append(edu.get('school_name', ''))
            normalized['education'] = ', '.join(schools)
        
        # Extract location
        if 'location' in profile_data:
            normalized['location'] = profile_data.get('location', {}).get('city', '')
        
        return normalized
    
    def extract_interests(self, profile_data: Dict[str, Any]) -> List[str]:
        """
        Extract interests from Hinge profile data.
        
        Args:
            profile_data: Raw profile data
            
        Returns:
            List[str]: List of interests
        """
        interests = []
        
        # Extract from vitals if available
        if 'vitals' in profile_data:
            vitals = profile_data.get('vitals', {})
            
            # Add interests from various vitals fields
            if 'drinking' in vitals:
                interests.append(f"Drinking: {vitals['drinking']}")
            if 'smoking' in vitals:
                interests.append(f"Smoking: {vitals['smoking']}")
            if 'religion' in vitals:
                interests.append(f"Religion: {vitals['religion']}")
            if 'politics' in vitals:
                interests.append(f"Politics: {vitals['politics']}")
        
        # Extract from prompts if available
        if 'prompts' in profile_data:
            for prompt in profile_data.get('prompts', []):
                if 'prompt_type' in prompt and 'answer' in prompt:
                    if prompt['answer'] and prompt['answer'].strip():
                        interests.append(prompt['answer'].strip())
        
        return interests
    
    def extract_bio(self, profile_data: Dict[str, Any]) -> str:
        """
        Extract bio text from Hinge profile data.
        
        Args:
            profile_data: Raw profile data
            
        Returns:
            str: Bio text
        """
        bio_parts = []
        
        # Extract from prompts
        if 'prompts' in profile_data:
            for prompt in profile_data.get('prompts', []):
                if 'prompt_type' in prompt and 'answer' in prompt:
                    if prompt['answer'] and prompt['answer'].strip():
                        prompt_text = f"{prompt.get('prompt_type', '')}: {prompt['answer']}"
                        bio_parts.append(prompt_text)
        
        return "\n".join(bio_parts)
