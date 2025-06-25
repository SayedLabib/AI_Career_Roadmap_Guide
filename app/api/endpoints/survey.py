from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict

from app.models.survey import SurveySubmission, SurveyQuestion
from app.models.persona import PersonaResult
from app.services.persona_detector import PersonaDetectorService
from app.services.career_matcher import CareerMatcherService

router = APIRouter()

@router.get("/questions", response_model=Dict[str, List[SurveyQuestion]])
async def get_survey_questions():
    """Retrieve the survey questions"""
    # In a real app, these might come from a database
    questions = [
        SurveyQuestion(
            id="q1",
            text="How do you typically approach problem-solving?",
            type="multiple_choice",
            options=[
                "Break it down logically step by step",
                "Consider how it affects everyone involved",
                "Act quickly and decisively",
                "Explore multiple creative possibilities"
            ]
        ),
        SurveyQuestion(
            id="q2",
            text="In a group setting, you are most likely to:",
            type="multiple_choice",
            options=[
                "Lead the discussion and make decisions",
                "Facilitate and ensure everyone is heard",
                "Analyze and provide critical insights",
                "Generate creative ideas and possibilities"
            ]
        ),
        SurveyQuestion(
            id="q3",
            text="When facing a setback, your first reaction is to:",
            type="multiple_choice",
            options=[
                "Analyze what went wrong and create a plan",
                "Consider how everyone is feeling",
                "Push harder and overcome the obstacle",
                "Step back and look for alternative approaches"
            ]
        ),
        SurveyQuestion(
            id="q4",
            text="What energizes you most?",
            type="multiple_choice",
            options=[
                "Solving complex problems",
                "Meaningful conversations with others",
                "Achieving goals and getting results",
                "Exploring new ideas and possibilities"
            ]
        ),
        SurveyQuestion(
            id="q5",
            text="In your ideal career, what would you value most?",
            type="multiple_choice",
            options=[
                "Intellectual challenge and expertise",
                "Making a difference in people's lives",
                "Leadership and achievement",
                "Innovation and creativity"
            ]
        ),
        SurveyQuestion(
            id="q6",
            text="How do you make important decisions?",
            type="multiple_choice",
            options=[
                "Analyze all data and consider logical consequences",
                "Consider how it will impact others and align with values",
                "Make a quick decision based on what will get results",
                "Consider multiple alternatives and follow intuition"
            ]
        ),
        SurveyQuestion(
            id="q7",
            text="When learning something new, you prefer to:",
            type="multiple_choice",
            options=[
                "Understand the underlying principles and structure",
                "Learn alongside others in a supportive environment",
                "Jump in and learn through trial and error",
                "Explore connections to other concepts and possibilities"
            ]
        ),
        SurveyQuestion(
            id="q8",
            text="What type of work environment helps you thrive?",
            type="multiple_choice",
            options=[
                "Quiet, organized, and structured",
                "Collaborative, harmonious, and supportive",
                "Fast-paced, challenging, and results-oriented",
                "Flexible, innovative, and open to new ideas"
            ]
        )
    ]
    return {"questions": questions}

@router.post("/submit", response_model=PersonaResult)
async def submit_survey(
    submission: SurveySubmission,
    persona_detector: PersonaDetectorService = Depends(),
    career_matcher: CareerMatcherService = Depends()
):
    """Submit survey answers and get persona detection results"""
    try:
        # Detect persona
        persona = await persona_detector.detect_persona(submission.responses)
        
        # Match careers
        careers = await career_matcher.match_careers(persona)
        
        # Combine results
        result = PersonaResult(
            user_id=submission.user_id,
            primary_persona=persona["primary"],
            secondary_persona=persona.get("secondary"),
            career_matches=careers,
            analysis=persona["analysis"]
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))