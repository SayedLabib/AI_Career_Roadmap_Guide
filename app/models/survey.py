from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TEXT = "text"
    SCALE = "scale"

class SurveyQuestion(BaseModel):
    id: str
    text: str
    type: QuestionType
    options: Optional[List[str]] = None

class SurveyResponse(BaseModel):
    question_id: str
    answer: str

class SurveySubmission(BaseModel):
    user_id: Optional[str] = None
    responses: List[SurveyResponse] = Field(..., min_items=5, max_items=10)