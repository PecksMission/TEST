"""
Journey Generator Service
Handles multi-turn conversation with Claude to generate healthcare journeys

Uses Claude Opus for:
- Conversational guidance through journey creation
- Extracting structured data from user input
- Generating timeline entries
- Creating color schemes
- Generating SVG medical diagrams
- Writing captions for photos
"""

import json
import re
from datetime import datetime, date
from typing import Optional, Dict, List, Any
from anthropic import Anthropic

class JourneyGenerator:
    """
    Multi-turn conversation system for healthcare journey creation.
    
    Maintains conversation history and progressively gathers information
    about the user's health journey, then generates structured content.
    
    Example:
        generator = JourneyGenerator()
        
        # Turn 1
        result = generator.process_user_input("I had Chiari surgery on Feb 26, 2026")
        print(result['response'])  # AI asks follow-up questions
        
        # Turn 2
        result = generator.process_user_input("Recovery was 6 weeks, very painful initially")
        print(result['response'])  # AI asks more questions
        
        # When complete:
        if result['journey_structure']:
            journey_data = result['journey_structure']
            # Save to database
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Journey Generator
        
        Args:
            api_key: Anthropic API key. If None, uses ANTHROPIC_API_KEY env var
        """
        self.client = Anthropic(api_key=api_key)
        self.conversation_history = []
        self.journey_data = {
            'title': None,
            'condition': None,
            'procedure_type': None,
            'start_date': None,
            'end_date': None,
            'milestones': [],
            'has_faith_elements': False,
            'has_family_elements': False,
            'has_media': False,
        }
    
    def system_prompt(self) -> str:
        """
        System prompt for Journey Generator
        
        Tells Claude how to behave as a healthcare storyteller
        """
        return """You are a compassionate healthcare storyteller helping users document their medical journey.

Your role is to:
1. Ask clarifying questions about their condition, timeline, and milestones
2. Gather information conversationally (don't feel like an interrogation)
3. Help them structure their story into stages (pre-op, surgery, post-op, recovery, etc.)
4. Suggest color themes and visual elements
5. Generate suggested timeline entries for each stage
6. Create SVG medical diagrams to explain procedures
7. Offer to include faith/spiritual moments if appropriate
8. Offer to include family support moments if appropriate

When you have enough information to create a complete journey structure, respond with a JSON block like:
```json
{
  "title": "Chiari Malformation Surgery Recovery",
  "condition": "Chiari Type I Malformation",
  "procedure_type": "Suboccipital Craniectomy with C1 Laminectomy",
  "start_date": "2026-02-26",
  "end_date": "2026-03-15",
  "summary": "A 25-year-old combat medic documents recovery from Chiari surgery",
  "stages": [
    {
      "name": "Pre-Surgery",
      "description": "Diagnosis and preparation",
      "color": "#5b8fa8",
      "duration_days": 7
    },
    {
      "name": "Surgery Day",
      "description": "Craniectomy and duraplasty procedure",
      "color": "#5b8fa8",
      "duration_days": 1
    },
    {
      "name": "Immediate Recovery",
      "description": "Hospital stay and acute recovery",
      "color": "#5b8fa8",
      "duration_days": 5
    },
    {
      "name": "Week 2-3",
      "description": "Home recovery begins",
      "color": "#c9a84c",
      "duration_days": 14
    },
    {
      "name": "Ongoing Recovery",
      "description": "Physical therapy and healing",
      "color": "#a05c5c",
      "duration_days": 30
    }
  ],
  "timeline_entries": [
    {
      "date": "2026-02-26",
      "type": "clinical",
      "title": "Surgery Day",
      "content": "Admitted for suboccipital craniectomy with C1 laminectomy and duraplasty."
    },
    {
      "date": "2026-02-27",
      "type": "clinical",
      "title": "Post-Op Day 1",
      "content": "Intensive care recovery, pain management, monitoring for complications."
    },
    {
      "date": "2026-03-01",
      "type": "faith",
      "title": "Gratitude",
      "content": "Feeling blessed for successful surgery and supportive family."
    }
  ],
  "color_scheme": {
    "clinical": "#5b8fa8",
    "faith": "#a05c5c",
    "family": "#c9a84c",
    "accent": "#c9a84c"
  },
  "milestones": [
    "Surgery completed successfully",
    "Discharged from hospital",
    "First physical therapy session",
    "Return to light activities"
  ]
}
```

Guidelines:
- Be warm, compassionate, and respectful
- Acknowledge the difficulty of health journeys
- Never diagnose or provide medical advice
- Ask permission before including sensitive topics
- Keep responses conversational (not robotic)
- Ask one or two questions at a time, not five
- When the user shares something vulnerable, validate it
- If they seem uncomfortable with a topic, move on
"""
    
    def process_user_input(self, user_message: str) -> Dict[str, Any]:
        """
        Process user input and generate response
        
        Args:
            user_message: User's message in the conversation
        
        Returns:
            {
                'response': str - AI's response to display
                'journey_structure': Optional[dict] - Structured journey data if complete
                'needs_more_info': bool - Whether more info is needed
                'conversation_stage': str - 'gathering', 'clarifying', or 'complete'
            }
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Call Claude API
        response = self.client.messages.create(
            model="claude-opus-4-20250805",
            max_tokens=2000,
            system=self.system_prompt(),
            messages=self.conversation_history
        )
        
        assistant_message = response.content[0].text
        
        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        # Try to extract journey JSON if present
        journey_structure = self._extract_journey_json(assistant_message)
        
        # Determine conversation stage
        if journey_structure:
            conversation_stage = 'complete'
            needs_more_info = False
        elif len(self.conversation_history) < 8:  # Less than 4 user turns
            conversation_stage = 'gathering'
            needs_more_info = True
        else:
            conversation_stage = 'clarifying'
            needs_more_info = True
        
        return {
            'response': assistant_message,
            'journey_structure': journey_structure,
            'needs_more_info': needs_more_info,
            'conversation_stage': conversation_stage,
            'turn': len([m for m in self.conversation_history if m['role'] == 'user'])
        }
    
    def _extract_journey_json(self, response: str) -> Optional[Dict]:
        """
        Extract JSON journey structure from Claude's response
        
        Args:
            response: Claude's full response text
        
        Returns:
            Parsed JSON dict if found and valid, else None
        """
        # Look for JSON block in response (```json ... ```)
        json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        
        if not json_match:
            return None
        
        try:
            json_str = json_match.group(1)
            data = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['title', 'condition', 'start_date', 'stages', 'timeline_entries']
            if all(field in data for field in required_fields):
                # Convert date strings to date objects if possible
                if isinstance(data['start_date'], str):
                    data['start_date'] = data['start_date']
                if data.get('end_date') and isinstance(data['end_date'], str):
                    data['end_date'] = data['end_date']
                
                return data
        except json.JSONDecodeError:
            return None
        
        return None
    
    def generate_svg_diagram(self, procedure_description: str) -> str:
        """
        Ask Claude to generate SVG medical diagram
        
        Args:
            procedure_description: Description of the medical procedure
        
        Returns:
            SVG code as string
        """
        response = self.client.messages.create(
            model="claude-opus-4-20250805",
            max_tokens=3000,
            messages=[{
                "role": "user",
                "content": f"""Generate an SVG medical diagram for this procedure:

{procedure_description}

Requirements:
- Simple, clean style (no gradients or complex effects)
- Labeled parts and steps
- If multi-step, show progression left to right or top to bottom
- Maximum 600px width
- Use only these colors:
  - #5b8fa8 (clinical blue - primary)
  - #181b1e (dark background - for lines/text)
  - #e8e3d8 (cream - for labels/backgrounds)
  - #c9a84c (gold - for highlights)
- Include title as <text> element
- Clear labels for all parts
- Simple arrow indicators for steps
- ViewBox should be "0 0 600 400" or appropriate for content

Output ONLY the SVG code, starting with <svg and ending with </svg>.
No markdown, no explanations, no code fence, just raw SVG."""
            }]
        )
        
        return response.content[0].text
    
    def generate_timeline_entries(self, journey_info: Dict) -> List[Dict]:
        """
        Generate suggested timeline entries based on journey info
        
        Args:
            journey_info: Journey metadata dict with:
                - title, condition, start_date, end_date, milestones, stages
        
        Returns:
            List of suggested timeline entry dicts
        """
        milestones_text = "\n".join([f"  - {m}" for m in journey_info.get('milestones', [])])
        stages_text = "\n".join([f"  - {s['name']}: {s['description']}" for s in journey_info.get('stages', [])])
        
        prompt = f"""Create timeline entries for this health journey:

Title: {journey_info['title']}
Condition: {journey_info['condition']}
Procedure: {journey_info.get('procedure_type', 'Not specified')}
Start Date: {journey_info['start_date']}
End Date: {journey_info.get('end_date', 'Ongoing')}

Stages:
{stages_text}

Key Milestones:
{milestones_text}

Generate 8-15 suggested timeline entries covering:
- Pre-surgery preparation
- Surgery day (detailed)
- Immediate post-op recovery
- Weekly progress through recovery
- Key milestones
- Emotional/faith reflections
- Family support moments

For each entry, include:
- date (YYYY-MM-DD)
- type: 'clinical', 'faith', 'family', or 'milestone'
- title: brief headline
- content: 2-3 sentences

Format as JSON array only:
[
  {{"date": "2026-02-26", "type": "clinical", "title": "Surgery Day", "content": "..."}},
  ...
]

Include both clinical facts and human moments. Output ONLY JSON, no explanation."""
        
        response = self.client.messages.create(
            model="claude-opus-4-20250805",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            # Extract JSON from response
            text = response.content[0].text
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except (json.JSONDecodeError, AttributeError):
            pass
        
        return []
    
    def generate_photo_captions(self, journey_title: str, photo_description: str) -> str:
        """
        Generate AI caption for journey photo
        
        Args:
            journey_title: Title of the journey
            photo_description: What the user describes in the photo
        
        Returns:
            Generated caption
        """
        response = self.client.messages.create(
            model="claude-opus-4-20250805",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""Write a compassionate, specific caption (1-2 sentences) for a photo in this health journey:

Journey: {journey_title}
Photo description: {photo_description}

The caption should:
- Be warm and specific
- Highlight the human moment
- Be suitable for a shared, supportive community
- Not be overly clinical
- Include the approximate date if mentioned

Output only the caption, no quotes or extra text."""
            }]
        )
        
        return response.content[0].text.strip()
    
    def reset_conversation(self):
        """Reset conversation history for a new journey"""
        self.conversation_history = []
        self.journey_data = {
            'title': None,
            'condition': None,
            'procedure_type': None,
            'start_date': None,
            'end_date': None,
            'milestones': [],
            'has_faith_elements': False,
            'has_family_elements': False,
            'has_media': False,
        }
    
    def get_conversation_history(self) -> List[Dict]:
        """Get current conversation history"""
        return self.conversation_history.copy()
    
    @staticmethod
    def create_color_scheme(condition: str, journey_type: str = "general") -> Dict[str, str]:
        """
        Generate color scheme based on condition and type
        
        Args:
            condition: Medical condition (e.g., "cancer", "heart disease", "mental health")
            journey_type: Type of journey (e.g., "surgical", "ongoing", "recovery")
        
        Returns:
            Dict with clinical, faith, family, and accent colors
        """
        # Default scheme
        scheme = {
            "clinical": "#5b8fa8",  # Clinical blue
            "faith": "#a05c5c",     # Faith red/burgundy
            "family": "#c9a84c",    # Family gold
            "accent": "#c9a84c"     # Accent gold
        }
        
        # Condition-specific variations
        condition_lower = condition.lower()
        
        if 'cancer' in condition_lower:
            scheme['clinical'] = '#4a90a4'  # Darker blue for cancer
        elif 'heart' in condition_lower or 'cardiac' in condition_lower:
            scheme['clinical'] = '#c74543'  # Heart red
            scheme['accent'] = '#e8a8a0'
        elif 'mental' in condition_lower or 'psych' in condition_lower:
            scheme['clinical'] = '#7b68a8'  # Purple
            scheme['accent'] = '#7b68a8'
        elif 'pregnancy' in condition_lower or 'birth' in condition_lower:
            scheme['clinical'] = '#d4a574'  # Warm peach
            scheme['family'] = '#d4a574'
        
        return scheme


# Example usage in tests
if __name__ == '__main__':
    import os
    
    # Initialize generator
    generator = JourneyGenerator(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    # Simulate a conversation
    print("=== Surgery Day Builder - Test Conversation ===\n")
    
    # Turn 1
    print("User: I had Chiari malformation surgery in February 2026 and need help documenting my recovery.")
    result1 = generator.process_user_input(
        "I had Chiari malformation surgery in February 2026 and need help documenting my recovery."
    )
    print(f"\nAssistant: {result1['response']}\n")
    print(f"Stage: {result1['conversation_stage']} | Needs more info: {result1['needs_more_info']}\n")
    
    # Turn 2
    print("User: Surgery was on February 26th. They did a craniectomy and duraplasty. Recovery took about 6 weeks.")
    result2 = generator.process_user_input(
        "Surgery was on February 26th. They did a craniectomy and duraplasty. Recovery took about 6 weeks."
    )
    print(f"\nAssistant: {result2['response']}\n")
    
    # Turn 3
    print("User: Yes, faith was really important. My family was incredible support throughout.")
    result3 = generator.process_user_input(
        "Yes, faith was really important. My family was incredible support throughout. "
        "I want to include both the medical facts and the emotional journey."
    )
    print(f"\nAssistant: {result3['response']}\n")
    
    # Check if journey structure was generated
    if result3['journey_structure']:
        print("✓ Journey structure generated!")
        print(json.dumps(result3['journey_structure'], indent=2))
    else:
        print("Journey structure not yet generated. Would continue conversation...")
