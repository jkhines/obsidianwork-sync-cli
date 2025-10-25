#!/usr/bin/env python3
"""Bidirectional synchronization tool for Obsidian and People Work 1:1 meeting notes."""

import argparse
import os
import sys

from parsers.obsidian import parse_obsidian_vault
from parsers.peoplework import parse_peoplework_workspace
from sync_engine import SyncEngine


def validate_paths(peoplework_path, obsidian_path, workspace_name):
    """Validate that required paths exist.
    
    Args:
        peoplework_path: Path to People Work root directory
        obsidian_path: Path to Obsidian vault
        workspace_name: Name of the People Work workspace
        
    Returns:
        True if all paths are valid, False otherwise
    """
    errors = []
    
    if not os.path.exists(peoplework_path):
        errors.append(f"People Work path does not exist: {peoplework_path}")
    
    if not os.path.exists(obsidian_path):
        errors.append(f"Obsidian vault path does not exist: {obsidian_path}")
    
    workspace_path = os.path.join(peoplework_path, workspace_name)
    if not os.path.exists(workspace_path):
        errors.append(f"Workspace '{workspace_name}' not found at: {workspace_path}")
    
    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        return False
    
    return True


def main():
    """Main entry point for the sync tool."""
    parser = argparse.ArgumentParser(description='Synchronize 1:1 meeting notes between Obsidian and People Work')
    
    parser.add_argument('--peoplework', required=True, help='Path to the People Work root directory')
    parser.add_argument('--obsidian', required=True, help='Path to the Obsidian vault')
    parser.add_argument('--workspace', default='MyWorkspace', help='Name of the People Work workspace (default: MyWorkspace)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be synced without making changes')
    
    args = parser.parse_args()
    
    # Validate paths
    if not validate_paths(args.peoplework, args.obsidian, args.workspace):
        sys.exit(1)
    
    print("Obsidian <-> People Work Sync Tool")
    print("=" * 50)
    print(f"People Work: {args.peoplework}")
    print(f"Obsidian:    {args.obsidian}")
    print(f"Workspace:   {args.workspace}")
    print()
    
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        print()
    
    # Parse Obsidian data
    print("Parsing Obsidian vault...")
    obsidian_data = parse_obsidian_vault(args.obsidian)
    obsidian_count = sum(len(meetings) for meetings in obsidian_data.values())
    print(f"  Found {len(obsidian_data)} people with {obsidian_count} meetings")
    
    # Parse People Work data
    print("Parsing People Work workspace...")
    peoplework_data = parse_peoplework_workspace(args.peoplework, args.workspace)
    peoplework_count = sum(len(meetings) for meetings in peoplework_data.values())
    print(f"  Found {len(peoplework_data)} people with {peoplework_count} meetings")
    print()
    
    # Perform synchronization
    if not args.dry_run:
        print("Synchronizing...")
        sync_engine = SyncEngine(args.peoplework, args.obsidian, args.workspace)
        changes = sync_engine.sync(obsidian_data, peoplework_data)
        
        print()
        print("Sync Summary")
        print("=" * 50)
        print(f"People added to system:  {changes['people_added']}")
        print(f"Obsidian -> People Work: {changes['obsidian_to_peoplework']}")
        print(f"People Work -> Obsidian: {changes['peoplework_to_obsidian']}")
        print(f"Conflicts resolved:      {changes['conflicts']}")
        print()
        print("Synchronization complete!")
    else:
        print("Dry run complete. Use without --dry-run to perform actual sync.")


if __name__ == '__main__':
    main()

