# Automatic People Addition Feature

## Overview

The sync tool now automatically adds people from Obsidian to the People Work system if they don't already exist. This ensures all meeting notes are properly associated with individuals in the People Work application.

## What Was Implemented

### 1. New Parser (`parsers/people_dsl.py`)
Parses `people.ppl` to extract the list of valid contacts in the workspace.

### 2. New Writer (`writers/people_dsl.py`)
Provides functions to:
- Parse existing members from `core.ppl`
- Add new members to `core.ppl`
- Add new contacts to `people.ppl`
- Ensure a person exists in both files

### 3. Updated Sync Engine
The sync engine now:
1. **Before syncing events**: Automatically adds missing people from Obsidian to People Work
2. **Extracts name parts**: Splits Obsidian names (e.g., "John Doe") into first and last names
3. **Creates member entries**: Adds to `core.ppl` with first name, last name
4. **Creates contact entries**: Adds to `people.ppl` with default group `network`
5. **Tracks additions**: Reports how many people were added in the summary

### 4. Removed Skip Logic
Previously, the tool would skip people not in the system. Now it automatically adds them, so all events get synced.

## How It Works

When you run the sync:

1. **Parsing Phase**: 
   - Reads `people.ppl` to get existing contacts
   - Parses Obsidian vault for all people with meetings

2. **Auto-Addition Phase**:
   - For each person in Obsidian not in People Work:
     - Extracts first/last name from "Firstname Lastname" format
     - Adds member definition to `core.ppl`
     - Adds contact definition to `people.ppl` (group: network)
     - Adds to valid contacts set

3. **Sync Phase**:
   - Syncs all events as before
   - All people are now valid, so no events are skipped

## Example Output

```
Synchronizing...
  + Added Alice Johnson to People Work system
  + Added Bob Martinez to People Work system
  + Added Charlie Wilson to People Work system
  + Added Diana Chen to People Work system
  + Added Emma Garcia to People Work system
  + Added Frank Anderson to People Work system
  + Added Grace Lee to People Work system
  -> Synced alice_johnson 2025-09-10 from Obsidian to People Work
  ...

Sync Summary
==================================================
People added to system:  7
Obsidian -> People Work: 103
People Work -> Obsidian: 130
Conflicts resolved:      10
```

## Files Modified

### Core Logic
- `sync_engine.py`: Added auto-addition logic before sync
- `sync.py`: Updated summary to show people_added count

### New Files
- `parsers/people_dsl.py`: Parse people.ppl
- `writers/people_dsl.py`: Write to core.ppl and people.ppl

## Default Settings

When people are automatically added:
- **Group**: `network` (most appropriate for unclassified relationships)
- **Email**: Not set (only first/last name required)
- **Job**: Not set (not required for contacts)

You can manually change the group later in `people.ppl` to:
- `align` - stakeholders
- `partner` - peers
- `guide` - direct reports/mentees
- `network` - broader professional network

## Result

All people from Obsidian are now in People Work, and all their historical events are visible in the People Work application. The sync process is fully automated - you don't need to manually add anyone to the system.

