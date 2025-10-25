"""Writer for People Work DSL people.ppl and core.ppl files."""

import os
import re


def parse_existing_members(core_file_path):
    """Parse existing members from core.ppl.
    
    Args:
        core_file_path: Path to core.ppl file
        
    Returns:
        Set of member IDs that already exist
    """
    if not os.path.exists(core_file_path):
        return set()
    
    members = set()
    
    with open(core_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all member definitions
    member_pattern = re.compile(r'^member\s+(\w+)\s*\{', re.MULTILINE)
    
    for match in member_pattern.finditer(content):
        member_id = match.group(1)
        members.add(member_id)
    
    return members


def add_member_to_core(peoplework_path, workspace_name, member_id, first_name, last_name, email=None):
    """Add a new member definition to core.ppl.
    
    Args:
        peoplework_path: Path to People Work root directory
        workspace_name: Name of the workspace
        member_id: Member identifier (e.g., 'john_doe')
        first_name: First name of the person
        last_name: Last name of the person
        email: Email address (optional, generates placeholder if not provided)
    """
    core_file = os.path.join(peoplework_path, workspace_name, 'core.ppl')
    
    # Generate placeholder email if not provided (appears to be required by app)
    if not email:
        email = f"{member_id}@placeholder.com"
    
    # Create member definition
    member_def = f'''member {member_id} {{
  first_name: "{first_name}"
  last_name: "{last_name}"
  email: "{email}"
}}
'''
    
    # Append to core.ppl
    with open(core_file, 'a', encoding='utf-8') as f:
        f.write(member_def)


def add_contact_to_people(peoplework_path, workspace_name, contact_id, group='network'):
    """Add a new contact definition to people.ppl.
    
    Args:
        peoplework_path: Path to People Work root directory
        workspace_name: Name of the workspace
        contact_id: Contact identifier (e.g., 'john_doe')
        group: Relationship group (default: 'network')
    """
    people_file = os.path.join(peoplework_path, workspace_name, 'people.ppl')
    
    # Create contact definition
    contact_def = f'''contact {contact_id} {{
  group: {group}
}}
'''
    
    # Append to people.ppl
    with open(people_file, 'a', encoding='utf-8') as f:
        f.write(contact_def)


def ensure_person_exists(peoplework_path, workspace_name, peoplework_name, first_name, last_name, group='network', email=None):
    """Ensure a person exists in both core.ppl and people.ppl.
    
    Args:
        peoplework_path: Path to People Work root directory
        workspace_name: Name of the workspace
        peoplework_name: Person name in People Work format
        first_name: First name of the person
        last_name: Last name of the person
        group: Relationship group (default: 'network')
        email: Email address (optional, generates placeholder if not provided)
        
    Returns:
        Tuple of (member_added, contact_added) booleans
    """
    core_file = os.path.join(peoplework_path, workspace_name, 'core.ppl')
    people_file = os.path.join(peoplework_path, workspace_name, 'people.ppl')
    
    member_added = False
    contact_added = False
    
    # Check if member exists in core.ppl
    existing_members = parse_existing_members(core_file)
    if peoplework_name not in existing_members:
        add_member_to_core(peoplework_path, workspace_name, peoplework_name, first_name, last_name, email)
        member_added = True
    
    # Check if contact exists in people.ppl
    with open(people_file, 'r', encoding='utf-8') as f:
        people_content = f.read()
    
    contact_pattern = re.compile(rf'^contact\s+{re.escape(peoplework_name)}\s*\{{', re.MULTILINE)
    if not contact_pattern.search(people_content):
        add_contact_to_people(peoplework_path, workspace_name, peoplework_name, group)
        contact_added = True
    
    return member_added, contact_added

