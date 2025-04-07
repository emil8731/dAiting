"""
Tinder-specific profile scraper module.
Implements profile scraping for the Tinder platform.
"""

import requests
import logging
from typing import Dict, List, Any, Optional

from .scraper import BaseProfileScraper, ScrapingError
from .tinder_auth import TinderAuthenticator

logger = logging.getLogger('platform.tinder_scraper')

class TinderProfileScraper(BaseProfileScraper):
    """Profile scraper for the Tinder platform."""
    
    BASE_URL = "https://api.gotinder.com"
    
    def __init__(self, authenticator: TinderAuthenticator):
        """
        Initialize the Tinder profile scraper.
        
        Args:
            authenticator: Tinder authenticator
        """
        super().__init__(authenticator)
        self.authenticator = authenticator  # Type hint for IDE
    
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
                f"{self.BASE_URL}/profile",
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
                f"{self.BASE_URL}/v2/matches",
                params={"count": limit},
                headers=self.authenticator.get_auth_headers()
            )
            
            if response.status_code == 200:
                matches_data = response.json()
                matches = matches_data.get('data', {}).get('matches', [])
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
                f"{self.BASE_URL}/user/{match_id}",
                headers=self.authenticator.get_auth_headers()
            )
            
            if response.status_code == 200:
                profile_data = response.json().get('results', {})
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
        # In Tinder, matches and conversations are the same endpoint
        return self.get_matches(limit)
    
    def get_conversation_messages(self, match_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get messages from a specific conversation.
        
        Args:
            match_id: ID of the match/conversation
            limit: Maximum number of messages to retrieve
            
        Returns:
            List[Dict]: List of messages
        """
        if not self.authenticator.is_authenticated():
            raise ScrapingError("Not authenticated. Cannot get conversation messages.")
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/v2/matches/{match_id}/messages",
                params={"count": limit},
                headers=self.authenticator.get_auth_headers()
            )
            
            if response.status_code == 200:
                messages_data = response.json()
                messages = messages_data.get('data', {}).get('messages', [])
                logger.info(f"Successfully retrieved {len(messages)} messages for match {match_id}")
                return messages
            else:
                logger.error(f"Failed to get messages: {response.status_code} - {response.text}")
                raise ScrapingError(f"Failed to get messages: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Request error while getting messages: {str(e)}")
            raise ScrapingError(f"Request error: {str(e)}")
    
    def normalize_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Tinder profile data to a standard format.
        
        Args:
            profile_data: Raw profile data from Tinder
            
        Returns:
            Dict: Normalized profile data
        """
        if not profile_data:
            return {}
            
        # Extract basic information
        normalized = {
            'id': profile_data.get('_id', ''),
            'name': profile_data.get('name', ''),
            'bio': profile_data.get('bio', ''),
            'age': self._calculate_age(profile_data.get('birth_date', '')),
            'gender': profile_data.get('gender', 0),
            'photos': [],
            'interests': self.extract_interests(profile_data),
            'job': {
                'title': '',
                'company': ''
            },
            'education': '',
            'location': profile_data.get('distance_mi', 0),
            'last_active': '',
            'platform': 'tinder'
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
        if 'jobs' in profile_data and profile_data['jobs']:
            for job in profile_data['jobs']:
                if 'title' in job:
                    normalized['job']['title'] = job.get('title', {}).get('name', '')
                if 'company' in job:
                    normalized['job']['company'] = job.get('company', {}).get('name', '')
        
        # Extract education information
        if 'schools' in profile_data and profile_data['schools']:
            schools = []
            for school in profile_data['schools']:
                if 'name' in school:
                    schools.append(school.get('name', ''))
            normalized['education'] = ', '.join(schools)
        
        return normalized
    
    def extract_interests(self, profile_data: Dict[str, Any]) -> List[str]:
        """
        Extract interests from Tinder profile data.
        
        Args:
            profile_data: Raw profile data
            
        Returns:
            List[str]: List of interests
        """
        interests = []
        
        # Extract from interests_v3 if available
        if 'interests_v3' in profile_data:
            for interest in profile_data['interests_v3']:
                if 'name' in interest:
                    interests.append(interest['name'])
        
        # Extract from user_interests if available
        elif 'user_interests' in profile_data:
            for interest in profile_data['user_interests'].get('selected_interests', []):
                if 'name' in interest:
                    interests.append(interest['name'])
        
        return interests
    
    def extract_bio(self, profile_data: Dict[str, Any]) -> str:
        """
        Extract bio text from Tinder profile data.
        
        Args:
            profile_data: Raw profile data
            
        Returns:
            str: Bio text
        """
        return profile_data.get('bio', '')
    
    def _calculate_age(self, birth_date: str) -> int:
        """
        Calculate age from birth date string.
        
        Args:
            birth_date: Birth date string in ISO format
            
        Returns:
            int: Age in years
        """
        if not birth_date:
            return 0
            
        try:
            from datetime import datetime
            birth = datetime.fromisoformat(birth_date.replace('Z', '+00:00'))
            today = datetime.now()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            return age
        except (ValueError, TypeError):
            logger.error(f"Error calculating age from birth date: {birth_date}")
            return 0
