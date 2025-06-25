from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, time
from enum import Enum

class TimeSlot(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"

class Task(BaseModel):
    title: str
    description: str
    start_time: time
    end_time: time
    time_slot: TimeSlot
    estimated_time: str  # e.g., "30 minutes", "1 hour"
    priority: int = Field(..., ge=1, le=5)  # Priority from 1-5
    resources: Optional[List[str]] = None  # Optional resources links

class DailyCard(BaseModel):
    date: date
    focus_area: str
    tasks: List[Task] = Field(..., min_items=4, max_items=5)
    reflection_prompt: str

class PersonalRoadmap(BaseModel):
    user_id: Optional[str] = None
    persona_type: str
    duration_months: int = Field(..., ge=1, le=6)
    start_date: date
    end_date: date
    daily_cards: List[DailyCard]
    overall_goals: List[str]