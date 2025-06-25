from fastapi import Depends
from typing import List, Dict, Any

from app.models.survey import SurveyResponse
from app.utils.gemini_client import GeminiClient

class PersonaDetectorService:
    def __init__(self, gemini_client: GeminiClient = Depends()):
        self.gemini_client = gemini_client
        
    async def detect_persona(self, responses: List[SurveyResponse]) -> Dict[str, Any]:
        """Detects personality type/archetype based on survey responses"""
        # Convert responses to a format suitable for Gemini
        responses_text = self._format_responses(responses)
        
        # Create a prompt for Gemini
        prompt = f"""
        Based on the following survey responses, identify the person's primary personality 
        archetype (analytical, empathetic, aggressive, philosophical, etc.) and provide an analysis.
        
        Survey Responses:
        {responses_text}
        
        Please return a JSON with the following structure:
        {{
            "primary": {{
                "type": "personality type name",
                "confidence": 0.85,
                "description": "Description of this personality type"
            }},
            "secondary": {{
                "type": "secondary personality type",
                "confidence": 0.65,
                "description": "Description of this personality type"
            }},
            "analysis": "Detailed analysis of the person's responses and personality"
        }}
        """
        
        # Call Gemini API and parse response
        response = await self.gemini_client.generate_content(prompt)
        return response
    
    def _format_responses(self, responses: List[SurveyResponse]) -> str:
        """Format survey responses as text for Gemini"""
        formatted = []
        for resp in responses:
            formatted.append(f"Question ID: {resp.question_id}, Answer: {resp.answer}")
        return "\n".join(formatted)