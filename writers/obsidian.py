"""Writer for Obsidian markdown files."""

import os
import re


def write_obsidian_meeting(vault_path, person_name, date, observations, sentiment, comments):
    """Add a meeting entry to an Obsidian markdown file.
    
    Args:
        vault_path: Path to the Obsidian vault root directory
        person_name: Person name in Obsidian format (e.g., 'John Doe')
        date: Date in YYYY-MM-DD format
        observations: Observations text
        sentiment: Sentiment value
        comments: Comments text
    """
    # Ensure Leadership/1-1s directory exists
    oneonone_path = os.path.join(vault_path, 'Leadership', '1-1s')
    os.makedirs(oneonone_path, exist_ok=True)
    
    # Generate filename (person_name already includes .md extension)
    filename = person_name if person_name.endswith('.md') else f"{person_name}.md"
    filepath = os.path.join(oneonone_path, filename)
    
    # Read existing content if file exists
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    else:
        existing_content = ''
    
    # Generate new meeting entry
    new_entry = generate_meeting_entry(date, observations, sentiment, comments)
    
    # Insert at the top of the file
    if existing_content:
        # Check if the date already exists (allow trailing whitespace)
        date_pattern = re.compile(f'^{re.escape(date)}\\s*$', re.MULTILINE)
        if not date_pattern.search(existing_content):
            new_content = new_entry + '\n' + existing_content
        else:
            # Date exists, append to that section
            new_content = append_to_date_section(existing_content, date, observations, sentiment, comments)
    else:
        new_content = new_entry
    
    # Write back to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)


def generate_meeting_entry(date, observations, sentiment, comments):
    """Generate a markdown entry for a meeting.
    
    Args:
        date: Date in YYYY-MM-DD format
        observations: Observations text
        sentiment: Sentiment value
        comments: Comments text
        
    Returns:
        String containing formatted markdown entry
    """
    entry = f"{date}\n"
    
    # Add observations as bullet points if present
    if observations:
        entry += f"- **Observations**: {observations}\n"
    
    # Add sentiment
    if sentiment and sentiment != 'neutral':
        entry += f"- **Sentiment**: {sentiment}\n"
    
    # Add comments if present
    if comments:
        entry += f"- **Comments**: {comments}\n"
    
    return entry


def append_to_date_section(content, date, observations, sentiment, comments):
    """Append meeting data to an existing date section.
    
    Args:
        content: Existing file content
        date: Date to append to
        observations: Observations text
        sentiment: Sentiment value
        comments: Comments text
        
    Returns:
        Updated content with appended data
    """
    lines = content.split('\n')
    
    # Find the target date line
    date_index = -1
    for i, line in enumerate(lines):
        if line.strip() == date.strip():
            date_index = i
            break
    
    if date_index == -1:
        # Date not found, shouldn't happen but return original
        return content
    
    # Find where this date section ends (next date or EOF)
    section_end = len(lines)
    for i in range(date_index + 1, len(lines)):
        if re.match(r'^\d{4}-\d{2}-\d{2}', lines[i].strip()):
            # Found next date section
            section_end = i
            break
    
    # Check if this content already exists in the date section (to prevent duplicates)
    section_text = '\n'.join(lines[date_index:section_end])
    marker = "[From People Work]"
    if observations and f"{marker} **Observations**: {observations}" in section_text:
        # Content already exists, don't add duplicate
        return content
    
    # Build the new lines to insert
    new_lines = []
    if observations:
        new_lines.append(f"- {marker} **Observations**: {observations}")
    if sentiment and sentiment != 'neutral':
        new_lines.append(f"- {marker} **Sentiment**: {sentiment}")
    if comments:
        new_lines.append(f"- {marker} **Comments**: {comments}")
    
    # Insert before the section_end (which is either the next date or EOF)
    # Also ensure there's a blank line before the next section if needed
    result = lines[:section_end]
    
    # Add blank line before new content if the last line isn't already blank
    if result and result[-1].strip() != '':
        result.append('')
    
    # Add the new content
    result.extend(new_lines)
    
    # Add the rest of the file
    result.extend(lines[section_end:])
    
    return '\n'.join(result)

