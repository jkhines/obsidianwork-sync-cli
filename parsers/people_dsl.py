"""Parser for People Work DSL people.ppl file to extract valid contacts."""

import os
import re


def parse_people_file(peoplework_path, workspace_name):
    """Parse people.ppl to get list of valid contacts.
    
    Args:
        peoplework_path: Path to the People Work root directory
        workspace_name: Name of the workspace
        
    Returns:
        Set of contact IDs (person names in People Work format)
    """
    people_file = os.path.join(peoplework_path, workspace_name, 'people.ppl')
    
    if not os.path.exists(people_file):
        return set()
    
    contacts = set()
    
    with open(people_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all contact definitions: contact identifier {
    # Also include the user
    contact_pattern = re.compile(r'^(?:contact|user)\s+(\w+)\s*\{', re.MULTILINE)
    
    for match in contact_pattern.finditer(content):
        contact_id = match.group(1)
        contacts.add(contact_id)
    
    return contacts

