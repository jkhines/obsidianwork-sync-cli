"""Name conversion utilities for mapping between Obsidian and People Work formats."""

import re


def obsidian_to_peoplework(obsidian_name):
    """Convert 'Firstname Lastname.md' to 'firstname_lastname'.
    
    Args:
        obsidian_name: Filename in Obsidian format (e.g., 'John Doe.md')
        
    Returns:
        String in People Work format (e.g., 'john_doe')
    """
    # Remove .md extension
    name = obsidian_name.replace('.md', '')
    # Convert to lowercase and replace spaces with underscores
    return name.lower().replace(' ', '_')


def peoplework_to_obsidian(peoplework_name):
    """Convert 'firstname_lastname' to 'Firstname Lastname.md'.
    
    Args:
        peoplework_name: Name in People Work format (e.g., 'john_doe')
        
    Returns:
        Filename in Obsidian format (e.g., 'John Doe.md')
    """
    # Split by underscore and capitalize each word
    parts = peoplework_name.split('_')
    capitalized = ' '.join(word.capitalize() for word in parts)
    return f"{capitalized}.md"

