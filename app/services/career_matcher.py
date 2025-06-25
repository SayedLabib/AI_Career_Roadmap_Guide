from fastapi import Depends
from typing import Dict, List, Any

from app.models.persona import CareerMatch
from app.utils.gemini_client import GeminiClient

class CareerMatcherService:
    def __init__(self, gemini_client: GeminiClient = Depends()):
        self.gemini_client = gemini_client
        
    async def match_careers(self, persona: Dict[str, Any]) -> List[CareerMatch]:
        """Match careers to a detected persona"""
        # Create a prompt for Gemini
        prompt = f"""
        Based on the following personality profile, suggest the top 5 career matches:
        
        Primary personality type: {persona["primary"]["type"]}
        Description: {persona["primary"]["description"]}
        
        Secondary personality type: {persona.get("secondary", {}).get("type", "None")}
        
        Return a JSON array with the following structure for each career:
        [
            {{
                "career": "career name",
                "confidence": 0.92,
                "description": "Why this career is a good match for the personality"
            }},
            ...
        ]
        """
        
        # Call Gemini API and parse response
        response = await self.gemini_client.generate_content(prompt)
        return response