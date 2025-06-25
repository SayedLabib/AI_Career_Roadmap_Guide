"""Utility functions for validating model data"""

import re
from typing import List, Union, Dict, Any
from app.models.weekly_roadmap import WeeklyTask, MonthlyRoadmap

def validate_activity_format(activity: str) -> bool:
    """
    Validates that an activity string is properly formatted as numbered steps
    
    Args:
        activity: The activity string to validate
        
    Returns:
        bool: True if properly formatted, False otherwise
    """
    if not activity:
        return False
    
    # Split into lines
    lines = [line.strip() for line in activity.split('\n') if line.strip()]
    
    # Must have at least one line
    if not lines:
        return False
    
    # Check if lines start with numbers
    numbered_lines = [re.match(r'^\d+\.', line) is not None for line in lines]
    
    # All lines should be numbered
    return all(numbered_lines)

def format_activity(activity: Union[str, List[str], Dict[str, Any], Any]) -> str:
    """
    Formats an activity as a properly numbered list with each step on a new line
    
    Args:
        activity: The activity to format (can be string, list, dict, etc.)
        
    Returns:
        str: Properly formatted activity string
    """
    # Handle different input types
    if isinstance(activity, list):
        if all(isinstance(item, str) for item in activity):
            activity = "\n".join(item.strip() for item in activity if item.strip())
        else:
            activity = "\n".join(str(item).strip() for item in activity if str(item).strip())
    elif not isinstance(activity, str):
        activity = str(activity)
    
    # Normalize line endings and remove problematic control characters
    activity = activity.replace('\r\n', '\n').replace('\r', '\n')
    activity = re.sub(r'[\x00-\x09\x0B\x0C\x0E-\x1F\x7F]', '', activity)
    
    # Check if the activity is already properly formatted
    if validate_activity_format(activity):
        # Make sure each numbered step is on its own line
        processed_activity = ""
        for i, line in enumerate(activity.split('\n')):
            stripped = line.strip()
            if stripped:
                # If this line starts with a number, add a newline before it (unless it's the first line)
                if re.match(r'^\d+\.', stripped) and i > 0:
                    processed_activity += f"\n{stripped}"
                else:
                    processed_activity += stripped
                
                # Add a space after each numbered step if there isn't one already
                if re.match(r'^\d+\.$', stripped):
                    processed_activity += " "
        
        # Ensure correct formatting with numbers on new lines
        for i in range(10, 0, -1):  # Start from 10 to avoid replacing parts of larger numbers
            processed_activity = processed_activity.replace(f"{i}. ", f"\n{i}. ")
        
        # Clean up any double newlines and leading newlines
        activity = processed_activity.replace("\n\n", "\n").lstrip("\n")
    else:
        # Not properly formatted, so format it as a numbered list
        lines = [line.strip() for line in activity.split("\n") if line.strip()]
        
        # Check if text has accidental line breaks within a single step
        merged_lines = []
        current_line = ""
        
        for line in lines:
            # If line starts with a number, it's a new step
            if re.match(r'^\d+\.', line):
                if current_line:  # Save the previous step if it exists
                    merged_lines.append(current_line)
                current_line = line
            else:
                # This line is a continuation of the previous step
                if current_line:
                    current_line += " " + line
                else:
                    current_line = line
        
        # Don't forget the last line
        if current_line:
            merged_lines.append(current_line)
        
        # Now number any lines that don't already have numbers
        numbered_lines = []
        counter = 1
        
        for line in merged_lines:
            if re.match(r'^\d+\.', line):
                # Line already has a number, keep it as is
                numbered_lines.append(line)
            else:
                # Add a number to this line
                numbered_lines.append(f"{counter}. {line}")
                counter += 1
        
        activity = "\n".join(numbered_lines)
    
    return activity

def validate_monthly_roadmap(roadmap: MonthlyRoadmap) -> MonthlyRoadmap:
    """
    Validates and fixes formatting issues in a monthly roadmap
    
    Args:
        roadmap: The roadmap to validate
        
    Returns:
        MonthlyRoadmap: The validated and fixed roadmap
    """
    # Exit early if the roadmap is None or doesn't have weeks
    if not roadmap or not hasattr(roadmap, 'weeks') or not roadmap.weeks:
        return roadmap
        
    try:
        # Ensure all activities in all tasks are properly formatted
        for week in roadmap.weeks:
            if hasattr(week, 'tasks'):
                for i, task in enumerate(week.tasks):
                    if task and hasattr(task, 'practice') and task.practice:
                        try:
                            # Format the practice field to ensure it's a properly formatted numbered list
                            week.tasks[i].practice = format_activity(task.practice)
                        except Exception as e:
                            # If formatting fails, at least make sure it's a valid string
                            print(f"Error formatting task practice: {str(e)}")
                            if not isinstance(task.practice, str):
                                week.tasks[i].practice = str(task.practice)
                            
                            # Remove any control characters that could cause rendering issues
                            week.tasks[i].practice = re.sub(r'[\x00-\x1F\x7F]', '', week.tasks[i].practice)
    except Exception as e:
        print(f"Error in validate_monthly_roadmap: {str(e)}")
        # Don't fail the whole process due to validation issues
    
    return roadmap
