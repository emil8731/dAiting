"""
Message generation module for the dating app AI assistant.
Provides functionality for analyzing profiles and generating personalized messages.
"""

import os
import json
import logging
import random
from typing import Dict, List, Any, Optional, Tuple
import openai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='dating_app.log'
)
logger = logging.getLogger('message_generator')

class ProfileAnalyzer:
    """Analyzes dating profiles to identify conversation hooks and topics."""
    
    def __init__(self):
        """Initialize the profile analyzer."""
        self.openai_client = None
        self._initialize_openai()
        
    def _initialize_openai(self):
        """Initialize the OpenAI client if API key is available."""
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key:
            self.openai_client = openai.OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized")
        else:
            logger.warning("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
    
    def analyze_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a profile to identify conversation hooks and topics.
        
        Args:
            profile_data: Normalized profile data
            
        Returns:
            Dict: Analysis results including topics, hooks, and tone
        """
        # Extract key profile elements
        name = profile_data.get('name', '')
        bio = profile_data.get('bio', '')
        interests = profile_data.get('interests', [])
        job = profile_data.get('job', {})
        education = profile_data.get('education', '')
        
        # Initialize analysis results
        analysis = {
            'topics': [],
            'hooks': [],
            'tone': 'friendly',
            'interests_score': {},
            'created_at': '',
            'match_id': profile_data.get('id', '')
        }
        
        # Basic analysis without OpenAI
        if not self.openai_client:
            analysis = self._basic_analysis(profile_data, analysis)
            logger.info(f"Completed basic profile analysis for {name}")
            return analysis
        
        # Advanced analysis with OpenAI
        try:
            # Prepare profile summary for OpenAI
            profile_summary = f"Name: {name}\nBio: {bio}\nInterests: {', '.join(interests)}\n"
            if job:
                profile_summary += f"Job: {job.get('title', '')} at {job.get('company', '')}\n"
            if education:
                profile_summary += f"Education: {education}\n"
            
            # Create prompt for OpenAI
            prompt = f"""
            Analyze this dating profile and identify:
            1. Potential conversation topics (with relevance score 1-10)
            2. Specific conversation hooks or questions to ask
            3. Appropriate conversation tone
            
            Profile:
            {profile_summary}
            
            Format your response as JSON with the following structure:
            {{
                "topics": [
                    {{"name": "topic1", "score": 8, "reason": "why this is relevant"}},
                    ...
                ],
                "hooks": [
                    {{"text": "specific question or comment", "type": "question/comment"}},
                    ...
                ],
                "tone": "friendly/humorous/intellectual/etc."
            }}
            """
            
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert dating profile analyzer."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            # Update analysis with OpenAI results
            analysis['topics'] = result.get('topics', [])
            analysis['hooks'] = result.get('hooks', [])
            analysis['tone'] = result.get('tone', 'friendly')
            
            # Create interests score dictionary
            for topic in analysis['topics']:
                analysis['interests_score'][topic['name']] = topic['score']
            
            logger.info(f"Completed OpenAI profile analysis for {name}")
            
        except Exception as e:
            logger.error(f"Error in OpenAI profile analysis: {str(e)}")
            # Fall back to basic analysis
            analysis = self._basic_analysis(profile_data, analysis)
            
        return analysis
    
    def _basic_analysis(self, profile_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform basic profile analysis without OpenAI.
        
        Args:
            profile_data: Normalized profile data
            analysis: Initial analysis structure
            
        Returns:
            Dict: Updated analysis results
        """
        name = profile_data.get('name', '')
        bio = profile_data.get('bio', '')
        interests = profile_data.get('interests', [])
        
        # Extract potential topics from interests
        for interest in interests:
            topic = {
                "name": interest,
                "score": random.randint(6, 9),
                "reason": f"Explicitly mentioned in profile"
            }
            analysis['topics'].append(topic)
            analysis['interests_score'][interest] = topic['score']
        
        # Extract potential topics from bio
        if bio:
            bio_words = bio.lower().split()
            common_topics = ["travel", "music", "food", "movies", "books", "sports", "hiking", "cooking"]
            
            for topic in common_topics:
                if topic in bio_words:
                    topic_entry = {
                        "name": topic,
                        "score": random.randint(5, 8),
                        "reason": f"Mentioned in bio"
                    }
                    analysis['topics'].append(topic_entry)
                    analysis['interests_score'][topic] = topic_entry['score']
        
        # Generate basic hooks
        if interests:
            interest = random.choice(interests)
            analysis['hooks'].append({
                "text": f"I see you're into {interest}. What got you interested in that?",
                "type": "question"
            })
        
        if profile_data.get('job', {}).get('title'):
            job_title = profile_data['job']['title']
            analysis['hooks'].append({
                "text": f"How do you like working as a {job_title}?",
                "type": "question"
            })
        
        # Add generic hooks if needed
        if len(analysis['hooks']) < 2:
            analysis['hooks'].append({
                "text": f"Hey {name}, what's been the highlight of your week so far?",
                "type": "question"
            })
        
        return analysis


class MessageGenerator:
    """Generates personalized messages based on profile analysis."""
    
    def __init__(self, templates_path: str = None):
        """
        Initialize the message generator.
        
        Args:
            templates_path: Path to message templates file
        """
        self.templates_path = templates_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            'data', 
            'message_templates.json'
        )
        self.templates = self._load_templates()
        self.profile_analyzer = ProfileAnalyzer()
        self.openai_client = None
        self._initialize_openai()
    
    def _initialize_openai(self):
        """Initialize the OpenAI client if API key is available."""
        api_key = os.environ.get('OPENAI_API_KEY')
        if api_key:
            self.openai_client = openai.OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized")
        else:
            logger.warning("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
    
    def _load_templates(self) -> Dict[str, List[str]]:
        """
        Load message templates from file.
        
        Returns:
            Dict: Message templates by category
        """
        default_templates = {
            "opener": [
                "Hey {name}, {hook}",
                "Hi {name}! I noticed {interest} in your profile. {hook}",
                "Hello {name}! {hook} How's your day going?"
            ],
            "follow_up": [
                "That's really interesting! {hook}",
                "I can relate to that. {hook}",
                "I'd love to hear more about {interest}. {hook}"
            ],
            "question": [
                "What do you enjoy most about {interest}?",
                "How did you get into {interest}?",
                "What's your favorite thing about {interest}?"
            ],
            "generic": [
                "How's your week going so far?",
                "Any exciting plans for the weekend?",
                "What's been keeping you busy lately?"
            ]
        }
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.templates_path), exist_ok=True)
            
            # Check if templates file exists
            if not os.path.exists(self.templates_path):
                # Create default templates file
                with open(self.templates_path, 'w') as f:
                    json.dump(default_templates, f, indent=2)
                logger.info(f"Created default templates file at {self.templates_path}")
                return default_templates
            
            # Load templates from file
            with open(self.templates_path, 'r') as f:
                templates = json.load(f)
                logger.info(f"Loaded templates from {self.templates_path}")
                return templates
                
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
            return default_templates
    
    def generate_initial_message(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an initial message for a match.
        
        Args:
            profile_data: Normalized profile data
            
        Returns:
            Dict: Generated message data
        """
        # Analyze profile
        analysis = self.profile_analyzer.analyze_profile(profile_data)
        
        # Generate message using OpenAI if available
        if self.openai_client:
            try:
                return self._generate_with_openai(profile_data, analysis)
            except Exception as e:
                logger.error(f"Error generating message with OpenAI: {str(e)}")
                # Fall back to template-based generation
        
        # Template-based generation
        return self._generate_with_templates(profile_data, analysis)
    
    def _generate_with_openai(self, profile_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a message using OpenAI.
        
        Args:
            profile_data: Normalized profile data
            analysis: Profile analysis results
            
        Returns:
            Dict: Generated message data
        """
        name = profile_data.get('name', '')
        
        # Prepare profile summary
        profile_summary = f"Name: {name}\n"
        if profile_data.get('bio'):
            profile_summary += f"Bio: {profile_data['bio']}\n"
        if profile_data.get('interests'):
            profile_summary += f"Interests: {', '.join(profile_data['interests'])}\n"
        if profile_data.get('job', {}).get('title'):
            profile_summary += f"Job: {profile_data['job']['title']}"
            if profile_data['job'].get('company'):
                profile_summary += f" at {profile_data['job']['company']}"
            profile_summary += "\n"
        if profile_data.get('education'):
            profile_summary += f"Education: {profile_data['education']}\n"
        
        # Prepare analysis summary
        analysis_summary = "Profile Analysis:\n"
        if analysis.get('topics'):
            topics = sorted(analysis['topics'], key=lambda x: x.get('score', 0), reverse=True)
            top_topics = topics[:3]
            analysis_summary += f"Top Topics: {', '.join([t['name'] for t in top_topics])}\n"
        if analysis.get('hooks'):
            analysis_summary += f"Potential Hooks: {', '.join([h['text'] for h in analysis['hooks']])}\n"
        if analysis.get('tone'):
            analysis_summary += f"Suggested Tone: {analysis['tone']}\n"
        
        # Create prompt for OpenAI
        prompt = f"""
        Create an engaging initial message for a dating app match based on their profile.
        
        Profile:
        {profile_summary}
        
        {analysis_summary}
        
        Guidelines:
        - Keep it friendly, respectful, and conversational
        - Reference something specific from their profile
        - Include a question to encourage a response
        - Keep it relatively brief (1-3 sentences)
        - Use the suggested tone from the analysis
        - Don't be overly formal or use generic pickup lines
        - Don't mention the analysis directly
        
        Return only the message text, without any explanations or formatting.
        """
        
        # Call OpenAI API
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at writing engaging dating app messages."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Get message text
        message_text = response.choices[0].message.content.strip()
        
        # Create message data
        message_data = {
            "content": message_text,
            "match_id": profile_data.get('id', ''),
            "ai_generated": True,
            "ai_approved": False,
            "analysis_used": analysis
        }
        
        logger.info(f"Generated OpenAI message for {name}")
        return message_data
    
    def _generate_with_templates(self, profile_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a message using templates.
        
        Args:
            profile_data: Normalized profile data
            analysis: Profile analysis results
            
        Returns:
            Dict: Generated message data
        """
        name = profile_data.get('name', '')
        
        # Get template variables
        variables = {
            "name": name,
            "interest": "",
            "hook": ""
        }
        
        # Select an interest if available
        if profile_data.get('interests'):
            variables["interest"] = random.choice(profile_data['interests'])
        elif analysis.get('topics'):
            top_topic = sorted(analysis['topics'], key=lambda x: x.get('score', 0), reverse=True)[0]
            variables["interest"] = top_topic['name']
        else:
            variables["interest"] = "what you shared"
        
        # Select a hook if available
        if analysis.get('hooks'):
            hook = random.choice(analysis['hooks'])
            variables["hook"] = hook['text']
        else:
            # Use a generic question
            variables["hook"] = random.choice(self.templates.get("question", ["What's your favorite hobby?"]))
        
        # Select template category and template
        category = "opener"
        templates = self.templates.get(category, [])
        
        if not templates:
            templates = [
                "Hey {name}, I noticed {interest} in your profile. {hook}",
                "Hi {name}! {hook}",
                "Hello {name}! I'm interested in {interest} too. {hook}"
            ]
        
        template = random.choice(templates)
        
        # Fill in template
        message_text = template.format(**variables)
        
        # Create message data
        message_data = {
            "content": message_text,
            "match_id": profile_data.get('id', ''),
            "ai_generated": True,
            "ai_approved": False,
            "analysis_used": analysis
        }
        
        logger.info(f"Generated template message for {name}")
        return message_data
    
    def generate_response(self, conversation_history: List[Dict[str, Any]], profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a response message based on conversation history.
        
        Args:
            conversation_history: List of previous messages
            profile_data: Normalized profile data
            
        Returns:
            Dict: Generated message data
        """
        # Generate response using OpenAI if available
        if self.openai_client and conversation_history:
            try:
                return self._generate_response_with_openai(conversation_history, profile_data)
            except Exception as e:
                logger.error(f"Error generating response with OpenAI: {str(e)}")
                # Fall back to template-based generation
        
        # Template-based response generation
        return self._generate_response_with_templates(conversation_history, profile_data)
    
    def _generate_response_with_openai(self, conversation_history: List[Dict[str, Any]], profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a response using OpenAI.
        
        Args:
            conversation_history: List of previous messages
            profile_data: Normalized profile data
            
        Returns:
            Dict: Generated message data
        """
        name = profile_data.get('name', '')
        
        # Format conversation history
        formatted_history = []
        for msg in conversation_history:
            role = "assistant" if msg.get('sender_type') == 'user' else "user"
            formatted_history.append({
                "role": role,
                "content": msg.get('content', '')
            })
        
        # Create prompt for OpenAI
        system_prompt = f"""
        You are helping someone have a conversation on a dating app with {name}.
        
        Your task is to write a thoughtful, engaging response to keep the conversation going.
        
        Guidelines:
        - Keep it friendly, respectful, and conversational
        - Respond directly to what they said in their last message
        - Include a question to keep the conversation going
        - Keep it relatively brief (1-3 sentences)
        - Don't be overly formal or use generic responses
        - Be authentic and show genuine interest
        
        Return only the message text, without any explanations or formatting.
        """
        
        # Call OpenAI API
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(formatted_history)
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        
        # Get message text
        message_text = response.choices[0].message.content.strip()
        
        # Create message data
        message_data = {
            "content": message_text,
            "match_id": profile_data.get('id', ''),
            "ai_generated": True,
            "ai_approved": False
        }
        
        logger.info(f"Generated OpenAI response for {name}")
        return message_data
    
    def _generate_response_with_templates(self, conversation_history: List[Dict[str, Any]], profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a response using templates.
        
        Args:
            conversation_history: List of previous messages
            profile_data: Normalized profile data
            
        Returns:
            Dict: Generated message data
        """
        name = profile_data.get('name', '')
        
        # Get last message from match
        last_message = None
        for msg in reversed(conversation_history):
            if msg.get('sender_type') == 'match':
                last_message = msg.get('content', '')
                break
        
        # Get template variables
        variables = {
            "name": name,
            "interest": "",
            "hook": ""
        }
        
        # Select an interest if available
        if profile_data.get('interests'):
            variables["interest"] = random.choice(profile_data['interests'])
        
        # Select a hook
        variables["hook"] = random.choice(self.templates.get("question", ["What's your favorite hobby?"]))
        
        # Select template category and template
        category = "follow_up" if last_message else "generic"
        templates = self.templates.get(category, [])
        
        if not templates:
            templates = [
                "That's interesting! {hook}",
                "I'd love to hear more about that. {hook}",
                "Thanks for sharing. {hook}"
            ]
        
        template = random.choice(templates)
        
        # Fill in template
        message_text = template.format(**variables)
        
        # Create message data
        message_data = {
            "content": message_text,
            "match_id": profile_data.get('id', ''),
            "ai_generated": True,
            "ai_approved": False
        }
        
        logger.info(f"Generated template response for {name}")
        return message_data
    
    def add_template(self, category: str, template: str) -> bool:
        """
        Add a new message template.
        
        Args:
            category: Template category
            template: Template text
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if category not in self.templates:
                self.templates[category] = []
            
            self.templates[category].append(template)
            
            # Save templates to file
            with open(self.templates_path, 'w') as f:
                json.dump(self.templates, f, indent=2)
            
            logger.info(f"Added template to category {category}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding template: {str(e)}")
            return False
