from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class WeeklyTask(BaseModel):
    task_name: str
    resources: List[str]
    time_slot: str  # "9:00 AM - 10:30 AM"
    time_commitment: str  # "5 hours/week"
    practice: str

class WeekPlan(BaseModel):
    week_number: int
    tasks: List[WeeklyTask]

class MonthlyRoadmap(BaseModel):
    user_id: Optional[str] = None
    persona_type: str
    duration_months: int = Field(default=1)
    requested_month: int = Field(default=1)  # Month number requested (1 for first month, 2 for second, etc.)
    start_date: date
    end_date: date
    weeks: List[WeekPlan]
    overall_goals: List[str]

class MultiMonthRoadmap(BaseModel):
    user_id: Optional[str] = None
    persona_type: str
    total_months: int
    monthly_roadmaps: List[MonthlyRoadmap]
    # combined_goals: List[str]  # Combined goals from all months
    start_date: date
    end_date: date

