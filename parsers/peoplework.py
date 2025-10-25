"""Parser for People Work DSL (.wrk) event files."""

import os
import re
from collections import defaultdict


def parse_peoplework_workspace(peoplework_path, workspace_name):
    """Parse all 1:1 events from People Work workspace.
    
    Args:
        peoplework_path: Path to the People Work root directory
        workspace_name: Name of the workspace to parse
        
    Returns:
        Dict mapping person names to dates to event data:
        {person_name: {date: {observations, sentiment, comments}}}
    """
    meetings = defaultdict(dict)
    
    # Path to work directory
    work_path = os.path.join(peoplework_path, workspace_name, 'work')
    
    if not os.path.exists(work_path):
        return meetings
    
    # Iterate through person directories
    for person_name in os.listdir(work_path):
        person_path = os.path.join(work_path, person_name)
        
        if not os.path.isdir(person_path):
            continue
        
        events_path = os.path.join(person_path, 'events')
        
        if not os.path.exists(events_path):
            continue
        
        # Parse all .wrk files in events directory
        for filename in os.listdir(events_path):
            if not filename.endswith('.wrk'):
                continue
            
            # Extract date from filename (YYYY-MM-DD_*.wrk)
            date_match = re.match(r'^(\d{4}-\d{2}-\d{2})_', filename)
            if not date_match:
                continue
            
            date = date_match.group(1)
            filepath = os.path.join(events_path, filename)
            
            # Parse the .wrk file
            event_data = parse_wrk_file(filepath)
            
            if event_data:
                meetings[person_name][date] = event_data
    
    return dict(meetings)


def parse_wrk_file(filepath):
    """Parse a single .wrk file to extract event data.
    
    Args:
        filepath: Path to the .wrk file
        
    Returns:
        Dict with keys: observations, sentiment, comments
        Returns None if file doesn't contain required data
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    event_data = {
        'observations': '',
        'sentiment': 'neutral',
        'comments': ''
    }
    
    # Parse observations (multiline string between triple quotes or simple string)
    observations_match = re.search(r'observations:\s*"""(.*?)"""', content, re.DOTALL)
    if observations_match:
        event_data['observations'] = observations_match.group(1).strip()
    else:
        observations_match = re.search(r'observations:\s*"([^"]*)"', content)
        if observations_match:
            event_data['observations'] = observations_match.group(1).strip()
    
    # Parse sentiment
    sentiment_match = re.search(r'sentiment:\s*(\w+)', content)
    if sentiment_match:
        event_data['sentiment'] = sentiment_match.group(1).strip()
    
    # Parse comments (multiline string between triple quotes or simple string)
    comments_match = re.search(r'comments:\s*"""(.*?)"""', content, re.DOTALL)
    if comments_match:
        event_data['comments'] = comments_match.group(1).strip()
    else:
        comments_match = re.search(r'comments:\s*"([^"]*)"', content)
        if comments_match:
            event_data['comments'] = comments_match.group(1).strip()
    
    return event_data

