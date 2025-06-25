from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class PersonaType(BaseModel):
    type: str  # e.g., "analytical", "empathetic", "aggressive", "philosophical"
    confidence: float = Field(..., ge=0.0, le=1.0)  # confidence score between 0 and 1
    description: str
    
class CareerMatch(BaseModel):
    career: str  # e.g., "doctor", "teacher", "artist", "athlete"
    confidence: float = Field(..., ge=0.0, le=1.0)  # confidence score between 0 and 1
    description: str
    
class PersonaResult(BaseModel):
    user_id: Optional[str] = None
    primary_persona: PersonaType
    secondary_persona: Optional[PersonaType] = None
    career_matches: List[CareerMatch]
    analysis: str