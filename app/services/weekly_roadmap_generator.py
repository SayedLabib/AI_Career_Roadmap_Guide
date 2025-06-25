from fastapi import Depends
from datetime import date, timedelta, datetime
import json

from app.models.weekly_roadmap import MonthlyRoadmap, WeekPlan, WeeklyTask
from app.utils.gemini_client import GeminiClient
from app.utils.tavily_client import TavilySearchClient
from app.utils.validation import validate_monthly_roadmap

class WeeklyRoadmapGeneratorService:
    def __init__(self, gemini_client: GeminiClient = Depends(), tavily_client: TavilySearchClient = Depends()):
        self.gemini_client = gemini_client
        self.tavily_client = tavily_client
        
    async def generate_weekly_roadmap(self, persona_type: str, duration_months: int, user_id: str = None, current_month: int = 1) -> MonthlyRoadmap:
        """Generate a personalized roadmap with weekly themes and quests
        
        Args:
            persona_type: The personality type to tailor the roadmap for
            duration_months: Total number of months in the program (also determines parallel generation)
            user_id: Optional user identifier
            current_month: Which specific month to generate (if not generating in parallel)
            
        Returns:
            A MonthlyRoadmap for the specified month
        """
        # Calculate date range for this specific month
        start_date = date.today() + timedelta(days=(current_month-1)*30)
        end_date = start_date + timedelta(days=30)
        
        # Create a prompt for Gemini that highlights the month position in the program
        # This ensures progression in difficulty and avoids repetition
        prompt = f"""
        Create a personalized roadmap for someone with a {persona_type} personality type.
        This is month {current_month} of a {duration_months}-month program.
        The roadmap should be for this specific month, starting from {start_date}.
        
        {'This is the beginning of the program. Focus on foundational concepts.' if current_month == 1 else ''}
        {'This is the middle of the program. Build upon earlier concepts and increase complexity.' if current_month > 1 and current_month < duration_months else ''}
        {'This is the final month of the program. Focus on advanced techniques and practical application of all previous learning.' if current_month == duration_months and duration_months > 1 else ''}
        
        Please structure the roadmap with:
        1. Overall goals (include both short-term and long-term goals as a simple flat list of strings)
        2. Weekly themes, where each week has a different focus
        3. For each week, create 2-3 "quests" - specific learning tasks or activities
        4. Each quest should have: 
           - task_type: Type of task (Learn/Build/Reflect/Collaborate/etc.)
           - task_name: Specific, descriptive name of the task
           - time_slot: ONLY the specific time of day when this could be done (e.g., "9:00 AM - 10:30 AM", "Evening: 7:00 PM - 8:00 PM")
           - time_commitment: ONLY the total weekly time investment (e.g., "5 hours/week", "2 hours every weekend")
           - activity: A step-by-step guide formatted as a numbered list (1., 2., 3., etc.) with each step on a new line
           - DO NOT include resources for now, I will search for them separately
        
        Return your response as a JSON with the following structure:
        {{
          "user_id": "{user_id if user_id else 'user123'}",
          "persona_type": "{persona_type}",
          "start_date": "{start_date.isoformat()}",
          "end_date": "{end_date.isoformat()}",
          "duration_months": {duration_months},
          "current_month": {current_month},
          "overall_goals": [
            "Goal 1",
            "Goal 2", 
            "Goal 3"
          ],
          "weeks": [
            {{
              "week_number": {(current_month-1)*4 + 1},
              "theme": "Theme for Week {(current_month-1)*4 + 1}",
              "quests": [
                {{
                  "task_type": "Learn",
                  "task_name": "Specific task name",
                  "time_slot": "9:00 AM - 10:30 AM",
                  "time_commitment": "4 hours/week",
                  "activity": "1. First step to complete this task\n2. Second step with more details\n3. Final step with expected outcome"
                }}
              ]
            }}
          ]
        }}
        
        Tailor the content specifically to the {persona_type} personality type.
        {'Since this is month ' + str(current_month) + ' of the program, make sure to provide more ADVANCED content than what would be in month ' + str(current_month-1) + '.' if current_month > 1 else 'Provide foundational content appropriate for beginners.'}
        {'The resources, tasks and activities should be significantly more advanced than previous months, focusing on mastery and real-world application.' if current_month > 2 else ''}
        Make the activities specific, challenging but achievable, and appropriate for the persona type.
        
        IMPORTANT FORMATTING NOTES:
        1. For overall_goals, provide a simple flat list of strings. DO NOT use a dictionary structure.
        2. Keep time_slot ONLY for the time of day (e.g. "8:00 AM - 9:30 AM") 
        3. Keep time_commitment ONLY for weekly duration (e.g. "3 hours/week")
        4. DO NOT combine time_slot and time_commitment into a single field.
        5. Activity MUST be formatted as numbered steps (1., 2., 3., etc.), with each step on a new line.
           VERY IMPORTANT: For the activity field, use explicit \n for newlines in the JSON as shown in this example:
           "activity": "1. Research the fundamentals of the topic\\n2. Complete practice exercises\\n3. Review and reflect on what was learned"
           
           DO NOT include actual line breaks in the JSON value - use the \\n escape sequence instead.
        Create exactly 4 weeks of content for this month.
        For week numbers, use {(current_month-1)*4 + 1} to {current_month*4} to ensure continuity across the program.
        Important: For task_type, choose a specific category that best describes the activity (Learn, Build, Practice, Reflect, Research, Analyze, Collaborate, Network, Teach, Design, etc.) based on the actual content of each task.
        """

        try:
            # Call Gemini API and parse response            git commit -m "Add weekly roadmap generator with multi-month support"
            response_data = await self.gemini_client.generate_content(prompt)
            
            # Validate response structure
            if "weeks" not in response_data or "overall_goals" not in response_data:
                raise Exception("Invalid response structure: missing required fields")
            
            # Process the response
            processed_weeks = []
            
            for week_data in response_data["weeks"]:
                try:
                    # Validate week structure
                    required_week_fields = ["week_number", "theme", "quests"]
                    for field in required_week_fields:
                        if field not in week_data:
                            print(f"Missing required field '{field}' in week data")
                            raise Exception(f"Missing required field '{field}' in week data")
                    
                    processed_tasks = []
                    for quest in week_data["quests"]:
                        try:
                            # Validate quest structure
                            required_task_fields = ["task_type", "task_name", "time_slot", "time_commitment", "activity"]
                            for field in required_task_fields:
                                if field not in quest:
                                    print(f"Missing required field '{field}' in quest")
                                    raise Exception(f"Missing required field '{field}' in quest")
                            
                            # Generate resources based on task information
                            # Pass the current_month parameter to get progressively more advanced resources
                            web_resources = await self.enrich_resources_with_web_search(
                                quest["task_name"], quest["activity"], current_month
                            )
                            
                            # Extract activity from the quest
                            activity = quest["activity"]
                                
                            # The format_activity function will handle all formatting
                            from app.utils.validation import format_activity
                            formatted_activity = format_activity(activity)
                            
                            processed_task = WeeklyTask(
                                task_name=quest["task_name"],
                                resources=web_resources,
                                time_slot=quest["time_slot"],
                                time_commitment=quest["time_commitment"],
                                practice=formatted_activity
                            )
                            processed_tasks.append(processed_task)
                        except Exception as e:
                            print(f"Error processing quest: {str(e)}")
                            # Skip this quest but continue processing others
                            continue
                    
                    # Ensure we have tasks
                    if not processed_tasks:
                        print(f"No valid quests for week {week_data['week_number']}")
                        raise Exception(f"No valid quests for week {week_data['week_number']}")
                    
                    processed_week = WeekPlan(
                        week_number=week_data["week_number"],
                        tasks=processed_tasks
                    )
                    processed_weeks.append(processed_week)
                except Exception as e:
                    print(f"Error processing week: {str(e)}")
                    # Skip this week but continue processing others
                    continue
                 # Check if we have any processed weeks
            if not processed_weeks:
                raise Exception("No valid weeks could be processed")
                
            # Process overall_goals to ensure it's in the correct format (list of strings)
            overall_goals = []
            raw_goals = response_data.get("overall_goals", [])
            
            # Handle case where overall_goals might be a dictionary with nested lists
            if isinstance(raw_goals, dict):
                # Extract goals from dictionary format (e.g., {"short_term": [...], "long_term": [...]})
                for goal_type, goals in raw_goals.items():
                    if isinstance(goals, list):
                        overall_goals.extend(goals)
                    elif isinstance(goals, str):
                        # Handle case where the value itself is a string not a list
                        overall_goals.append(f"{goal_type}: {goals}")
            elif isinstance(raw_goals, list):
                # Already the right format
                overall_goals = raw_goals
            else:
                # Fallback - create an empty list
                overall_goals = []
                
            # Create the personalized roadmap
            roadmap = MonthlyRoadmap(
                user_id=user_id,
                persona_type=persona_type,
                duration_months=duration_months,
                requested_month=current_month,  # Use the specified month
                start_date=start_date,
                end_date=end_date,
                weeks=processed_weeks,
                overall_goals=overall_goals
            )
            
            # Validate and ensure proper formatting of all activities
            roadmap = validate_monthly_roadmap(roadmap)
            return roadmap
            
        except Exception as e:
            print(f"Error generating weekly roadmap: {str(e)}")
            raise Exception(f"Failed to generate weekly roadmap: {str(e)}")
    
    async def enrich_resources_with_web_search(self, task_name: str, practice, current_month: int = 1) -> list:
        """
        Enhances task resources by performing a web search using Tavily API
        
        Args:
            task_name: The name of the task
            practice: The practice instructions for the task (string or list of steps)
            current_month: Current month in the program to adjust resource complexity
            
        Returns:
            List of resource URLs
        """
        try:
            # Create a search query based on the task details and current month
            difficulty_level = ""
            if current_month > 1:
                if current_month <= 2:
                    difficulty_level = "intermediate"
                elif current_month <= 4:
                    difficulty_level = "advanced"
                else:
                    difficulty_level = "expert"
            
            # Convert practice to string if it's a list
            if isinstance(practice, list):
                # Use only the first item if it's a list
                if len(practice) > 0:
                    practice = practice[0]
                else:
                    practice = ""
            
            # Truncate task_name and practice to avoid exceeding the 400-character limit
            # Use only the first part of the activity text to stay within limits
            truncated_task = task_name[:80] if task_name else ""
            
            # Extract just the first point from the practice if it contains numbered steps
            truncated_practice = ""
            if practice and isinstance(practice, str) and "1." in practice:
                first_step = practice.split("2.")[0] if "2." in practice else practice
                # Remove the "1. " prefix if present
                if first_step.startswith("1."):
                    first_step = first_step[2:].strip()
                truncated_practice = first_step[:100]  # Limit to 100 chars
            elif practice and isinstance(practice, str):
                truncated_practice = practice[:100] if practice else ""
            else:
                truncated_practice = str(practice)[:100] if practice else ""
            
            # Build the search query with constraints to stay under 400 chars
            search_query = f"{truncated_task} {difficulty_level}".strip()
            
            # Only add keywords from practice if we haven't exceeded ~300 chars
            # This leaves room for the difficulty level and ensures we stay under the limit
            if len(search_query) < 300:
                search_query = f"{truncated_task}: {truncated_practice} {difficulty_level}".strip()
                
            # Final safety check - hard limit at 390 chars (buffer of 10)
            if len(search_query) > 390:
                search_query = search_query[:390]
            
            # Perform web search with increased depth for later months
            search_depth = "basic" if current_month <= 2 else "advanced"
            max_results = 3 + min(current_month, 4)  # More resources for later months (up to 7)
            
            # Perform web search
            search_results = await self.tavily_client.search(
                query=search_query, 
                search_depth=search_depth,
                max_results=max_results
            )
            
            # Extract useful resources
            resources = await self.tavily_client.extract_resource_info(search_results)
            
            # Return resource URLs
            return [resource["url"] for resource in resources] if resources else []
        except Exception as e:
            print(f"Error enriching resources with web search: {str(e)}")
            return []
