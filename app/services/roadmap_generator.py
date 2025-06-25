from fastapi import Depends
from datetime import date, time, timedelta, datetime
import json

from app.models.roadmap import PersonalRoadmap, DailyCard, Task, TimeSlot
from app.utils.gemini_client import GeminiClient
from app.utils.tavily_client import TavilySearchClient

class RoadmapGeneratorService:
    def __init__(self, gemini_client: GeminiClient = Depends(), tavily_client: TavilySearchClient = Depends()):
        self.gemini_client = gemini_client
        self.tavily_client = tavily_client
        
    async def generate_roadmap(self, persona_type: str, duration_months: int, user_id: str = None) -> PersonalRoadmap:
        """Generate a personalized roadmap based on persona type"""
        # Calculate date range
        start_date = date.today()
        end_date = start_date + timedelta(days=30*duration_months)
        
        # Create a prompt for Gemini
        prompt = f"""
        Create a personalized daily roadmap for a person with the personality type: {persona_type}.
        The roadmap should cover {duration_months} months starting from {start_date}.
        
        For each day, create a card with 4-5 specific activities or tasks focused on skills, growth, and learning.
        Each task should have a specific time scheduled from morning to night, with start_time and end_time.
        
        Your response MUST be a valid JSON object with the following structure, and nothing else:
        {{
            "overall_goals": ["goal 1", "goal 2", "goal 3"],
            "daily_cards": [
                {{
                    "date": "YYYY-MM-DD",
                    "focus_area": "Focus area for the day",
                    "tasks": [
                        {{
                            "title": "Task title",
                            "description": "Detailed task description",
                            "start_time": "08:00",
                            "end_time": "09:30",
                            "time_slot": "morning", 
                            "estimated_time": "90 minutes",
                            "priority": 1,
                            "resources": ["https://resource1.com", "https://resource2.com"]
                        }},
                        ...
                    ],
                    "reflection_prompt": "A question for reflection at the end of the day"
                }},
                ...
            ]
        }}
        
        Note: For demonstration purposes, please generate cards for exactly 3 days. In production, we would generate cards for each day in the {duration_months}-month period.
        Make each task specific, actionable, and tailored to the {persona_type} personality type.
        Time slots MUST be one of: "morning", "afternoon", "evening", or "night".
        Each task MUST have exactly these fields: title, description, start_time, end_time, time_slot, estimated_time, priority, and resources.
        Each start_time and end_time MUST be in 24-hour format like "08:00" or "14:30".
        Each date MUST be in YYYY-MM-DD format.
        Each priority MUST be an integer between 1 and 5.
        """

        try:
            # Call Gemini API and parse response
            response_data = await self.gemini_client.generate_content(prompt)
            
            # Validate response structure
            if "daily_cards" not in response_data or "overall_goals" not in response_data:
                raise Exception("Invalid response structure: missing required fields")
            
            # Process the response to convert string dates and times to proper objects
            processed_cards = []
            
            for card in response_data["daily_cards"]:
                try:
                    # Validate card structure
                    required_card_fields = ["date", "focus_area", "tasks", "reflection_prompt"]
                    for field in required_card_fields:
                        if field not in card:
                            print(f"Missing required field '{field}' in card")
                            raise Exception(f"Missing required field '{field}' in card")
                    
                    processed_tasks = []
                    for task in card["tasks"]:
                        try:
                            # Validate task structure
                            required_task_fields = ["title", "description", "start_time", "end_time", 
                                                "time_slot", "estimated_time", "priority"]
                            for field in required_task_fields:
                                if field not in task:
                                    print(f"Missing required field '{field}' in task")
                                    raise Exception(f"Missing required field '{field}' in task")
                            
                            # Convert time strings to time objects
                            start_time_parts = task["start_time"].split(":")
                            end_time_parts = task["end_time"].split(":")
                            
                            # Validate time slot is one of the allowed values
                            if task["time_slot"].lower() not in [e.value for e in TimeSlot]:
                                print(f"Invalid time_slot value: {task['time_slot']}, using 'morning' as default")
                                time_slot = TimeSlot.MORNING
                            else:
                                time_slot = task["time_slot"].lower()
                                
                            # Get base resources
                            base_resources = task.get("resources", [])
                            
                            # Enrich with web search resources
                            web_resources = await self.enrich_resources_with_web_search(
                                task["title"], task["description"]
                            )
                            
                            # Combine resources, removing duplicates
                            combined_resources = list(set(base_resources + web_resources))
                            
                            processed_task = Task(
                                title=task["title"],
                                description=task["description"],
                                start_time=time(int(start_time_parts[0]), int(start_time_parts[1])),
                                end_time=time(int(end_time_parts[0]), int(end_time_parts[1])),
                                time_slot=time_slot,
                                estimated_time=task["estimated_time"],
                                priority=task["priority"],
                                resources=combined_resources
                            )
                            processed_tasks.append(processed_task)
                        except Exception as e:
                            print(f"Error processing task: {str(e)}")
                            # Skip this task but continue processing others
                            continue
                    
                    # Convert date string to date object
                    card_date = datetime.strptime(card["date"], "%Y-%m-%d").date()
                    
                    # Ensure we have enough tasks (4-5)
                    if len(processed_tasks) < 4:
                        print(f"Not enough valid tasks for card on {card['date']}")
                        raise Exception(f"Not enough valid tasks for card on {card['date']}")
                    
                    processed_card = DailyCard(
                        date=card_date,
                        focus_area=card["focus_area"],
                        tasks=processed_tasks,
                        reflection_prompt=card["reflection_prompt"]
                    )
                    processed_cards.append(processed_card)
                except Exception as e:
                    print(f"Error processing card: {str(e)}")
                    # Skip this card but continue processing others
                    continue
                    
            # Check if we have any processed cards
            if not processed_cards:
                raise Exception("No valid daily cards could be processed")
                
            # Create and return the roadmap
            roadmap = PersonalRoadmap(
                user_id=user_id,
                persona_type=persona_type,
                duration_months=duration_months,
                start_date=start_date,
                end_date=end_date,
                daily_cards=processed_cards,
                overall_goals=response_data["overall_goals"]
            )
            return roadmap
            
        except Exception as e:
            print(f"Error generating roadmap: {str(e)}")
            raise Exception(f"Failed to generate roadmap: {str(e)}")
        
        # Convert response to PersonalRoadmap
        roadmap = PersonalRoadmap(
            user_id=user_id,
            persona_type=persona_type,
            duration_months=duration_months,
            start_date=start_date,
            end_date=end_date,
            daily_cards=processed_cards,
            overall_goals=response_data["overall_goals"]
        )
        
        return roadmap
    
    async def enrich_resources_with_web_search(self, task_title: str, task_description: str) -> list:
        """
        Enhances task resources by performing a web search using Tavily API
        
        Args:
            task_title: The title of the task
            task_description: The description of the task
            
        Returns:
            List of resource URLs
        """
        try:
            # Create a search query based on the task details
            search_query = f"{task_title}: {task_description}"
            
            # Perform web search
            search_results = await self.tavily_client.search(query=search_query, max_results=3)
            
            # Extract useful resources
            resources = await self.tavily_client.extract_resource_info(search_results)
            
            # Return resource URLs
            return [resource["url"] for resource in resources] if resources else []
        except Exception as e:
            print(f"Error enriching resources with web search: {str(e)}")
            return []