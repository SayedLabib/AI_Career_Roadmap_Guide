import json
import google.generativeai as genai
from typing import Dict, Any

from app.core.config import settings
from app.utils.json_sanitizer import safe_parse_json, sanitize_json_string

class GeminiClient:
    def __init__(self):
        # Configure the Gemini client
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    # We've moved the JSON normalization code to the json_sanitizer.py utility
        
    async def generate_content(self, prompt: str) -> Dict[str, Any]:
        """Generate content using Gemini AI"""
        try:
            print(f"Sending prompt to Gemini: {prompt[:100]}...")
            response = self.model.generate_content(prompt)
            
            # Parse the response as JSON
            response_text = response.text
            print(f"Received response from Gemini: {response_text[:100]}...")
            
            # Handle potential formatting issues
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.rfind("```")
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.rfind("```")
                response_text = response_text[json_start:json_end].strip()
                
            try:
                # Use our specialized JSON parser with multiple fallback methods
                return safe_parse_json(response_text)
            except Exception as json_err:
                print(f"JSON Decode Error: {str(json_err)}")
                print(f"Response text: {response_text}")
                
                # Even if safe_parse_json fails, try one more time with a direct sanitization
                try:
                    sanitized_text = sanitize_json_string(response_text)
                    return json.loads(sanitized_text)
                except Exception as e:
                    print(f"All parsing attempts failed: {str(e)}")
                    raise Exception(f"Failed to parse JSON response: {str(json_err)}")
        except Exception as e:
            # Log the error and return a simplified error response
            print(f"Error generating content: {str(e)}")
            raise Exception(f"Failed to generate content: {str(e)}")