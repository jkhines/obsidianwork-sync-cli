"""Parser for Obsidian markdown files containing 1:1 meeting notes."""

import os
import re
from collections import defaultdict


def parse_obsidian_vault(vault_path):
    """Parse all 1:1 meeting notes from Obsidian vault.
    
    Args:
        vault_path: Path to the Obsidian vault root directory
        
    Returns:
        Dict mapping person names to dates to bullet points:
        {person_name: {date: [bullet_points]}}
    """
    meetings = defaultdict(lambda: defaultdict(list))
    
    # Path to 1:1 notes
    oneonone_path = os.path.join(vault_path, 'Leadership', '1-1s')
    
    if not os.path.exists(oneonone_path):
        return meetings
    
    # Iterate through all markdown files
    for filename in os.listdir(oneonone_path):
        if not filename.endswith('.md'):
            continue
            
        person_name = filename[:-3]  # Remove .md extension
        filepath = os.path.join(oneonone_path, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the content
        person_meetings = parse_markdown_content(content)
        
        if person_meetings:
            meetings[person_name] = person_meetings
    
    return dict(meetings)


def parse_markdown_content(content):
    """Parse markdown content to extract meetings by date.
    
    Args:
        content: Markdown file content
        
    Returns:
        Dict mapping dates to bullet points: {date: [bullet_points]}
    """
    meetings = defaultdict(list)
    
    lines = content.split('\n')
    current_date = None
    current_bullet = None
    
    # Date pattern: YYYY-MM-DD
    date_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2})$')
    bullet_pattern = re.compile(r'^[-*+]\s+|\d+\.\s+')
    
    for line in lines:
        # Check if line is a date header
        date_match = date_pattern.match(line.strip())
        
        if date_match:
            # Save any pending bullet before switching dates
            if current_bullet and current_date:
                meetings[current_date].append(current_bullet.strip())
                current_bullet = None
            current_date = date_match.group(1)
        elif current_date:
            # Check if this is a new bullet point
            if line.strip().startswith(('- ', '* ', '+ ', '1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ')):
                # Save previous bullet if exists
                if current_bullet:
                    meetings[current_date].append(current_bullet.strip())
                
                # Start new bullet
                # Extract bullet point content (remove bullet/number prefix)
                bullet_content = re.sub(r'^(?:[-*+]\s+|\d+\.\s+)', '', line).strip()
                
                # Skip lines that have the "[From People Work]" marker - these are already synced
                if bullet_content.startswith('[From People Work]'):
                    current_bullet = None
                else:
                    # Remove label prefixes like "**Observations**:", "**Sentiment**:", "**Comments**:"
                    bullet_content = re.sub(r'^\*\*(Observations|Sentiment|Comments)\*\*:\s*', '', bullet_content)
                    current_bullet = bullet_content if bullet_content else None
            elif line.strip() and current_bullet is not None:
                # Continuation line - append to current bullet
                current_bullet += '\n' + line.strip()
            elif not line.strip() and current_bullet:
                # Empty line - save current bullet
                meetings[current_date].append(current_bullet.strip())
                current_bullet = None
    
    # Save any remaining bullet
    if current_bullet and current_date:
        meetings[current_date].append(current_bullet.strip())
    
    return dict(meetings)

