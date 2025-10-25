# Quick Start Guide

## Installation

```bash
cd obsidianwork-sync-cli
pip install -r requirements.txt
```

## Usage

### Preview Changes (Recommended First)
```bash
python sync.py --peoplework /path/to/peoplework --obsidian /path/to/obsidian --dry-run
```

### Run Sync
```bash
python sync.py --peoplework /path/to/peoplework --obsidian /path/to/obsidian
```

### With Custom Workspace
```bash
python sync.py --peoplework <path> --obsidian <path> --workspace MyWorkspace
```

## What It Does

✅ **Obsidian → People Work**: Creates `.wrk` files from markdown bullet points  
✅ **People Work → Obsidian**: Adds DSL content to markdown files  
✅ **Conflict Resolution**: Preserves both sources with markers  

## Key Features

- Automatic name format conversion
- Preserves all data (no overwrites)
- Dry-run mode for safe testing
- Clear progress and summary output

## Directory Structure

### Obsidian
```
/path/to/obsidian/
└── Leadership/
    └── 1-1s/
        └── Firstname Lastname.md
```

### People Work
```
/path/to/peoplework/
└── MyWorkspace/
    └── work/
        └── firstname_lastname/
            └── events/
                └── YYYY-MM-DD_1_1.wrk
```

## Example

**Before sync:**

Obsidian (`Leadership/1-1s/John Doe.md`):
```markdown
2025-09-26
- Discussed project goals
- Team alignment improving
```

**After sync:**

People Work (`work/john_doe/events/2025-09-26_1_1.wrk`):
```
event: {
  name: "1:1"
  date: "2025-09-26"
  recurrence: {
    starting: "2025-09-26"
    repeats: "weekly"
  }
}
observations: "Discussed project goals
Team alignment improving"
sentiment: neutral
```

## Tips

💡 Always run with `--dry-run` first  
💡 Backup your data before first sync  
💡 Review conflict resolutions manually  
💡 Run regularly to keep systems in sync  

## Help

```bash
python sync.py --help
```

For detailed documentation, see:
- `USAGE.md` - Comprehensive usage guide
- `IMPLEMENTATION.md` - Technical details
- `README.md` - Project overview

