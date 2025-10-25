"""Core synchronization logic for bidirectional sync between Obsidian and People Work."""

from utils.names import obsidian_to_peoplework, peoplework_to_obsidian
from writers.obsidian import write_obsidian_meeting
from writers.peoplework import write_peoplework_event
from parsers.people_dsl import parse_people_file
from writers.people_dsl import ensure_person_exists


class SyncEngine:
    """Handles bidirectional synchronization between Obsidian and People Work."""
    
    def __init__(self, peoplework_path, obsidian_path, workspace_name):
        """Initialize the sync engine.
        
        Args:
            peoplework_path: Path to People Work root directory
            obsidian_path: Path to Obsidian vault
            workspace_name: Name of the People Work workspace
        """
        self.peoplework_path = peoplework_path
        self.obsidian_path = obsidian_path
        self.workspace_name = workspace_name
        self.valid_contacts = parse_people_file(peoplework_path, workspace_name)
        self.skipped_people = set()
        self.changes = {
            'obsidian_to_peoplework': 0,
            'peoplework_to_obsidian': 0,
            'conflicts': 0,
            'people_added': 0
        }
    
    def sync(self, obsidian_data, peoplework_data):
        """Perform bidirectional synchronization.
        
        Args:
            obsidian_data: Dict from Obsidian parser
            peoplework_data: Dict from People Work parser
        """
        # First, add any people from Obsidian who don't exist in People Work
        for obsidian_name in obsidian_data.keys():
            peoplework_name = obsidian_to_peoplework(obsidian_name)
            
            if peoplework_name not in self.valid_contacts:
                # Extract first and last name from Obsidian format
                name_parts = obsidian_name.replace('.md', '').split()
                if len(name_parts) >= 2:
                    first_name = name_parts[0]
                    last_name = ' '.join(name_parts[1:])
                else:
                    first_name = obsidian_name.replace('.md', '')
                    last_name = ''
                
                # Add to People Work
                member_added, contact_added = ensure_person_exists(
                    self.peoplework_path,
                    self.workspace_name,
                    peoplework_name,
                    first_name,
                    last_name,
                    group='network'
                )
                
                if member_added or contact_added:
                    self.valid_contacts.add(peoplework_name)
                    self.changes['people_added'] += 1
                    print(f"  + Added {obsidian_name} to People Work system", flush=True)
        
        # Get all unique person names from both sources
        all_people = set()
        
        # Add Obsidian people (convert to People Work format for comparison)
        for obsidian_name in obsidian_data.keys():
            peoplework_name = obsidian_to_peoplework(obsidian_name)
            all_people.add((obsidian_name, peoplework_name))
        
        # Add People Work people (convert to Obsidian format for comparison)
        for peoplework_name in peoplework_data.keys():
            obsidian_name = peoplework_to_obsidian(peoplework_name)
            all_people.add((obsidian_name, peoplework_name))
        
        # Process each person
        for obsidian_name, peoplework_name in all_people:
            self._sync_person(obsidian_name, peoplework_name, obsidian_data.get(obsidian_name, {}), peoplework_data.get(peoplework_name, {}))
        
        return self.changes
    
    def _sync_person(self, obsidian_name, peoplework_name, obsidian_meetings, peoplework_meetings):
        """Sync meetings for a single person.
        
        Args:
            obsidian_name: Person name in Obsidian format
            peoplework_name: Person name in People Work format
            obsidian_meetings: Dict of {date: [bullet_points]}
            peoplework_meetings: Dict of {date: {observations, sentiment, comments}}
        """
        # Get all unique dates
        all_dates = set(obsidian_meetings.keys()) | set(peoplework_meetings.keys())
        
        for date in all_dates:
            obsidian_entry = obsidian_meetings.get(date)
            peoplework_entry = peoplework_meetings.get(date)
            
            if obsidian_entry and peoplework_entry:
                # Both exist - potential conflict
                self._handle_conflict(obsidian_name, peoplework_name, date, obsidian_entry, peoplework_entry)
            elif obsidian_entry and not peoplework_entry:
                # Only in Obsidian - sync to People Work
                self._sync_to_peoplework(peoplework_name, date, obsidian_entry)
            elif peoplework_entry and not obsidian_entry:
                # Only in People Work - sync to Obsidian
                self._sync_to_obsidian(obsidian_name, date, peoplework_entry)
    
    def _sync_to_peoplework(self, peoplework_name, date, bullet_points):
        """Sync Obsidian entry to People Work.
        
        Args:
            peoplework_name: Person name in People Work format
            date: Date in YYYY-MM-DD format
            bullet_points: List of bullet point strings
        """
        # Convert bullet points to observations
        observations = '\n'.join(bullet_points)
        
        # Write to People Work with neutral sentiment and empty comments
        write_peoplework_event(self.peoplework_path, self.workspace_name, peoplework_name, date, observations, sentiment='neutral', comments='')
        
        self.changes['obsidian_to_peoplework'] += 1
        print(f"  -> Synced {peoplework_name} {date} from Obsidian to People Work", flush=True)
    
    def _sync_to_obsidian(self, obsidian_name, date, peoplework_entry):
        """Sync People Work entry to Obsidian.
        
        Args:
            obsidian_name: Person name in Obsidian format
            date: Date in YYYY-MM-DD format
            peoplework_entry: Dict with observations, sentiment, comments
        """
        # Write to Obsidian with labels
        write_obsidian_meeting(self.obsidian_path, obsidian_name, date, peoplework_entry['observations'], peoplework_entry['sentiment'], peoplework_entry['comments'])
        
        self.changes['peoplework_to_obsidian'] += 1
        print(f"  -> Synced {obsidian_name} {date} from People Work to Obsidian", flush=True)
    
    def _handle_conflict(self, obsidian_name, peoplework_name, date, obsidian_entry, peoplework_entry):
        """Handle conflicting entries that exist in both systems.
        
        Args:
            obsidian_name: Person name in Obsidian format
            peoplework_name: Person name in People Work format
            date: Date in YYYY-MM-DD format
            obsidian_entry: List of bullet points from Obsidian
            peoplework_entry: Dict with observations, sentiment, comments from People Work
        """
        # Convert Obsidian bullets to comparable text
        obsidian_text = '\n'.join(obsidian_entry).strip()
        # Build a combined text for People Work to compare fairly against Obsidian bullets
        combined_pw_parts = [peoplework_entry['observations'].strip()]
        if peoplework_entry.get('sentiment') and peoplework_entry['sentiment'] != 'neutral':
            combined_pw_parts.append(peoplework_entry['sentiment'].strip())
        if peoplework_entry.get('comments'):
            combined_pw_parts.append(peoplework_entry['comments'].strip())
        peoplework_text = '\n'.join([p for p in combined_pw_parts if p])
        
        # Check if the combined content is identical
        if obsidian_text == peoplework_text:
            # Content is identical, no conflict - skip
            return
        
        # Real conflict - different content in both systems
        # Append People Work content to Obsidian with marker
        write_obsidian_meeting(self.obsidian_path, obsidian_name, date, peoplework_entry['observations'], peoplework_entry['sentiment'], peoplework_entry['comments'])
        
        # Append Obsidian content to People Work observations with marker
        combined_observations = peoplework_entry['observations'] + '\n\n[From Obsidian]\n' + obsidian_text
        write_peoplework_event(self.peoplework_path, self.workspace_name, peoplework_name, date, combined_observations, peoplework_entry['sentiment'], peoplework_entry['comments'])
        
        self.changes['conflicts'] += 1
        print(f"  ! Conflict resolved for {obsidian_name} {date} - appended both sources", flush=True)

