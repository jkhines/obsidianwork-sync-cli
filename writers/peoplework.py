"""Writer for People Work DSL (.wrk) event files."""

import os


def write_peoplework_event(peoplework_path, workspace_name, person_name, date, observations, sentiment='neutral', comments=''):
    """Write a People Work event file in DSL format.
    
    Args:
        peoplework_path: Path to the People Work root directory
        workspace_name: Name of the workspace
        person_name: Person name in People Work format (e.g., 'john_doe')
        date: Date in YYYY-MM-DD format
        observations: Observations text
        sentiment: Sentiment value (positive, neutral, negative)
        comments: Comments text
    """
    # Create directory structure if it doesn't exist
    events_path = os.path.join(peoplework_path, workspace_name, 'work', person_name, 'events')
    os.makedirs(events_path, exist_ok=True)
    
    # Generate filename
    filename = f"{date}_1_1.wrk"
    filepath = os.path.join(events_path, filename)
    
    # Generate DSL content
    content = generate_wrk_content(date, observations, sentiment, comments)
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def generate_wrk_content(date, observations, sentiment, comments):
    """Generate People Work DSL content for an event.
    
    Args:
        date: Date in YYYY-MM-DD format
        observations: Observations text
        sentiment: Sentiment value
        comments: Comments text
        
    Returns:
        String containing properly formatted DSL content
    """
    content = f'''event: {{
  name: "1:1"
  date: "{date}"
  recurrence: {{
    starting: "{date}"
    repeats: "weekly"
  }}
}}
'''
    
    # Add observations (always include, even if empty)
    if observations:
        # Always use triple quotes but format with newlines for better parsing
        # Place content on separate lines from the quotes
        content += 'observations: """\n' + observations + '\n"""\n'
    else:
        content += 'observations: "None"\n'
    
    # Add sentiment
    content += f'sentiment: {sentiment}\n'
    
    # Add comments (always include - appears to be required by parser)
    if comments:
        # Always use triple quotes but format with newlines for better parsing
        content += 'comments: """\n' + comments + '\n"""\n'
    else:
        content += 'comments: "None"\n'
    
    return content

