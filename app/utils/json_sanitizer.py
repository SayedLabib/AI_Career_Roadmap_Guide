"""Utilities for sanitizing JSON responses"""

import re
import json
from typing import Dict, Any

def sanitize_json_string(json_str: str) -> str:
    """
    Cleans up a JSON string to fix common issues that might cause parsing errors:
    - Normalizes line endings
    - Removes control characters
    - Properly escapes quotes and backslashes in string values
    - Handles special cases for activity fields
    
    Args:
        json_str: The raw JSON string to clean
        
    Returns:
        A sanitized JSON string that should parse correctly
    """
    # Normalize line endings
    json_str = json_str.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove problematic control characters
    json_str = re.sub(r'[\x00-\x09\x0B\x0C\x0E-\x1F\x7F]', '', json_str)
    
    # Fix activity fields with special handling
    pattern = r'"activity":\s*"(.*?)(?=",|"\s*})'
    
    def fix_activity(match):
        activity = match.group(1)
        # Escape backslashes, newlines and double quotes
        activity = activity.replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"')
        return f'"activity": "{activity}'
    
    json_str = re.sub(pattern, fix_activity, json_str, flags=re.DOTALL)
    
    return json_str

def safe_parse_json(json_str: str) -> Dict[str, Any]:
    """
    Safely parse a JSON string with multiple fallback methods
    
    Args:
        json_str: The JSON string to parse
        
    Returns:
        The parsed JSON object
        
    Raises:
        ValueError: If all parsing attempts fail
    """
    # First attempt: Standard JSON parsing
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Second attempt: Try with sanitization
        try:
            sanitized = sanitize_json_string(json_str)
            return json.loads(sanitized)
        except json.JSONDecodeError:
            # Third attempt: Use a line-by-line approach
            try:
                sanitized = sanitize_line_by_line(json_str)
                return json.loads(sanitized)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON after multiple attempts: {str(e)}")

def sanitize_line_by_line(json_str: str) -> str:
    """
    Process a JSON string line by line to handle specific formatting issues
    
    Args:
        json_str: The JSON string to sanitize
        
    Returns:
        A sanitized JSON string
    """
    lines = json_str.split('\n')
    result = []
    
    activity_content = False
    activity_buffer = ""
    
    for line in lines:
        stripped = line.strip()
        
        # Check if we're entering an activity field
        if '"activity":' in stripped:
            activity_content = True
            
            # Extract everything before the value starts
            prefix = stripped.split('"activity":', 1)[0] + '"activity": "'
            
            # Handle if there's content after the activity field starts
            if '"activity":' in stripped and stripped.endswith('"') and stripped.count('"') > 3:
                # Activity starts and ends on this line
                content = stripped.split('"activity":', 1)[1].strip()
                if content.startswith('"') and content.endswith('"'):
                    content = content[1:-1]  # Remove quotes
                    content = content.replace('"', '\\"')  # Escape quotes
                    activity_content = False
                    result.append(f'{prefix}{content}"')
                else:
                    # Start collecting multi-line activity
                    activity_buffer = content
            else:
                # Activity continues to next lines
                content = stripped.split('"activity":', 1)[1].strip()
                if content.startswith('"'):
                    content = content[1:]  # Remove opening quote
                activity_buffer = content
        
        # If we're inside an activity field
        elif activity_content:
            if stripped.endswith('"') and not stripped.endswith('\\"'):
                # This is the end of the activity
                activity_content = False
                activity_buffer += " " + stripped[:-1]  # Exclude closing quote
                activity_buffer = activity_buffer.replace('"', '\\"').replace('\n', '\\n')
                result.append(f'{activity_buffer}"')
                activity_buffer = ""
            else:
                # Continue collecting activity content
                activity_buffer += " " + stripped
        
        # Regular line (not part of activity)
        else:
            result.append(stripped)
    
    # Join everything back together
    return '\n'.join(result)
