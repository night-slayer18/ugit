"""
Display commit history.
"""

import json
from typing import Optional
from ..core.repository import Repository
from ..core.objects import get_object
from ..utils.helpers import format_timestamp, ensure_repository


def log(max_commits: Optional[int] = None) -> None:
    """
    Display commit history.
    
    Args:
        max_commits: Maximum number of commits to show (None for all)
    """
    repo = ensure_repository()
        
    current = repo.get_head_ref()
    if not current:
        print("No commits yet")
        return
        
    count = 0
    while current and (max_commits is None or count < max_commits):
        try:
            type_, data = get_object(current)
            if type_ != "commit":
                print(f"Error: Expected commit object, got {type_}")
                break
                
            commit = json.loads(data.decode())
            
            # Format and display commit information
            print(f"commit {current}")
            print(f"Author: {commit['author']}")
            
            # Try to format timestamp nicely
            timestamp = commit.get('timestamp', '')
            formatted_time = format_timestamp(timestamp)
            print(f"Date:   {formatted_time}")
            
            # Display commit message with proper indentation
            message_lines = commit['message'].strip().split('\n')
            print()
            for line in message_lines:
                print(f"    {line}")
            print()
            
            current = commit.get("parent")
            count += 1
            
        except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
            print(f"Error reading commit {current}: {e}")
            break