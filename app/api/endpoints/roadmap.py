from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Union, List
import asyncio

from app.models.weekly_roadmap import MonthlyRoadmap, MultiMonthRoadmap
from app.services.weekly_roadmap_generator import WeeklyRoadmapGeneratorService
from app.utils.validation import validate_monthly_roadmap

router = APIRouter()

# Removed the daily roadmap generator endpoint (/generate)

@router.post("/generate", response_model=Union[MonthlyRoadmap, MultiMonthRoadmap])
async def generate_weekly_roadmap(
    persona_type: str,
    duration_months: int = 1,
    user_id: Optional[str] = None,
    roadmap_generator: WeeklyRoadmapGeneratorService = Depends()
):
    """Generate a personalized roadmap based on persona type
    
    Args:
        persona_type: The personality type for roadmap generation
        duration_months: Number of months to generate (if >1, generates in parallel)
        user_id: Optional user identifier
    
    Returns:
        MonthlyRoadmap if duration_months=1, MultiMonthRoadmap if duration_months>1
    """
    try:
        if not persona_type:
            raise HTTPException(status_code=400, detail="Persona type cannot be empty")
        
        if duration_months < 1:
            raise HTTPException(status_code=400, detail="Duration months must be a positive integer")            # If duration_months is 1, generate a single month roadmap
        if duration_months == 1:
            print(f"Generating single month roadmap for persona: {persona_type}, user_id: {user_id}")
            roadmap = await roadmap_generator.generate_weekly_roadmap(persona_type, duration_months, user_id, current_month=1)
            # Validate the roadmap to ensure proper formatting
            validated_roadmap = validate_monthly_roadmap(roadmap)
            print(f"Roadmap generated successfully with {len(validated_roadmap.weeks)} weeks")
            return validated_roadmap
        
        # If duration_months > 1, generate multiple months in parallel
        print(f"Generating {duration_months} months of weekly roadmaps in parallel for persona: {persona_type}, user_id: {user_id}")
        
        # Special handling for large duration_months: use batching
        if duration_months >= 12:
            print(f"Using batched processing for {duration_months} months (batch size: 6)")
            batch_size = 6
            monthly_roadmaps = []
            
            # Process in batches of 6
            for batch_start in range(1, duration_months + 1, batch_size):
                batch_end = min(batch_start + batch_size, duration_months + 1)
                batch_months = list(range(batch_start, batch_end))
                
                print(f"Processing batch: months {batch_months}")
                
                # Create tasks for this batch
                batch_tasks = []
                for current_month in batch_months:
                    task = roadmap_generator.generate_weekly_roadmap(persona_type, duration_months, user_id, current_month=current_month)
                    batch_tasks.append(task)
                
                # Execute batch in parallel and wait for completion
                batch_results = await asyncio.gather(*batch_tasks)
                monthly_roadmaps.extend(batch_results)
                
                print(f"Completed batch: months {batch_months}")
        else:
            # For smaller duration_months, process all in parallel
            tasks = []
            for current_month in range(1, duration_months + 1):
                task = roadmap_generator.generate_weekly_roadmap(persona_type, duration_months, user_id, current_month=current_month)
                tasks.append(task)
            
            # Execute all tasks in parallel
            monthly_roadmaps = await asyncio.gather(*tasks)            # Apply validation to each monthly roadmap
        validated_roadmaps = []
        for roadmap in monthly_roadmaps:
            validated_roadmaps.append(validate_monthly_roadmap(roadmap))
            
        # Combine all monthly roadmaps
        combined_goals = []
        for roadmap in validated_roadmaps:
            combined_goals.extend(roadmap.overall_goals)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_goals = []
        for goal in combined_goals:
            if goal not in seen:
                seen.add(goal)
                unique_goals.append(goal)
        
        # Create multi-month roadmap response
        multi_month_roadmap = MultiMonthRoadmap(
            user_id=user_id,
            persona_type=persona_type,
            total_months=duration_months,
            monthly_roadmaps=validated_roadmaps,
            combined_goals=unique_goals,
            start_date=validated_roadmaps[0].start_date,
            end_date=validated_roadmaps[-1].end_date
        )
        
        print(f"Multi-month roadmap generated successfully with {len(monthly_roadmaps)} months")
        return multi_month_roadmap
        
    except HTTPException as he:
        # Re-raise HTTP exceptions as-is
        raise he
    except Exception as e:
        print(f"Error in generate_weekly_roadmap endpoint: {str(e)}")
        if "API key" in str(e).lower():
            raise HTTPException(status_code=500, detail="API key error: Please check your Gemini API key configuration")
        elif "parse json" in str(e).lower() or "control character" in str(e).lower() or "decode" in str(e).lower():
            # More specific error for JSON parsing issues
            error_msg = "Error parsing AI response: The AI model returned malformed JSON. "
            error_msg += "This is often due to control characters or improper formatting in the activity fields. "
            error_msg += "Please try again or contact support if the issue persists."
            raise HTTPException(status_code=500, detail=error_msg)
        else:
            raise HTTPException(status_code=500, detail=f"An error occurred while generating the weekly roadmap: {str(e)}")