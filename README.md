# Obsidian People Work Sync CLI

Bidirectional synchronization tool for 1:1 meeting notes between Obsidian and People Work.

## Overview

This tool synchronizes meeting notes between:
- **Obsidian**: Markdown files in `Leadership/1-1s/` organized by date within each person's file
- **People Work**: `.wrk` DSL files in the workspace's `work/{person}/events/` directory

## Installation

```bash
cd obsidianwork-sync-cli
pip install -r requirements.txt
```

## Usage

Basic usage:
```bash
python sync.py --peoplework /path/to/peoplework --obsidian /path/to/obsidian
```

With custom workspace:
```bash
python sync.py --peoplework /path/to/peoplework --obsidian /path/to/obsidian --workspace MyCompany
```

Dry run (preview changes without applying):
```bash
python sync.py --peoplework /path/to/peoplework --obsidian /path/to/obsidian --dry-run
```

## Synchronization Logic

### Automatic People Addition
- **NEW**: People from Obsidian who don't exist in People Work are automatically added
- Added to `core.ppl` as members with first/last name
- Added to `people.ppl` as contacts in the `network` group
- All historical events are then synced to People Work

### Obsidian → People Work
- Bullet points from Obsidian are converted to `observations`
- `sentiment` is set to `neutral`
- `comments` field is left empty

### People Work → Obsidian
- `observations`, `sentiment`, and `comments` are formatted as labeled bullet points
- Content is added to the top of the person's markdown file

### Conflict Resolution
When both systems have content for the same date:
- Both sources are preserved
- Content is appended with markers: `[From Obsidian]` and `[From People Work]`

## File Structure

```
obsidianwork-sync-cli/
├── sync.py              # Main CLI entry point
├── sync_engine.py       # Core synchronization logic
├── requirements.txt     # Python dependencies
├── parsers/
│   ├── obsidian.py     # Obsidian markdown parser
│   ├── peoplework.py   # People Work DSL parser
│   └── people_dsl.py   # People Work people.ppl parser
├── writers/
│   ├── obsidian.py     # Obsidian markdown writer
│   ├── peoplework.py   # People Work DSL writer
│   └── people_dsl.py   # People Work core.ppl/people.ppl writer
└── utils/
    └── names.py        # Name format conversion utilities
```

## Name Mapping

The tool automatically converts between naming conventions:
- **Obsidian**: `Firstname Lastname.md`
- **People Work**: `firstname_lastname`

## Example

Given this Obsidian file (`Leadership/1-1s/John Doe.md`):
```markdown
2025-09-02
- Discussed project timeline
- Team alignment is improving
```

And this People Work file (`work/john_doe/events/2025-09-05_1_1.wrk`):
```
event: {
  name: "1:1"
  date: "2025-09-05"
  recurrence: {
    starting: "2025-09-05"
    repeats: "weekly"
  }
}
observations: "Review Q3 goals"
sentiment: positive
comments: "Good progress this quarter"
```

After sync:
- A new file `work/john_doe/events/2025-09-02_1_1.wrk` is created with Obsidian content
- The Obsidian file gets the 2025-09-05 meeting content added at the top

## Requirements

- Python 3.7+
- python-dateutil

## License

See parent project for license information.
