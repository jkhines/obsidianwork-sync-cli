# Usage Guide

## Quick Start

1. **Install dependencies**:
```bash
cd obsidianwork-sync-cli
pip install -r requirements.txt
```

2. **Run a dry-run first** (recommended):
```bash
python sync.py --peoplework /path/to/peoplework --obsidian /path/to/obsidian --dry-run
```

3. **Perform actual sync**:
```bash
python sync.py --peoplework /path/to/peoplework --obsidian /path/to/obsidian
```

## Command Line Options

```
python sync.py --peoplework <path> --obsidian <path> [OPTIONS]
```

### Required Arguments
- `--peoplework`: Path to the People Work root directory (e.g., `/path/to/peoplework`)
- `--obsidian`: Path to the Obsidian vault (e.g., `/path/to/obsidian`)

### Optional Arguments
- `--workspace WORKSPACE`: Name of the People Work workspace (default: `MyWorkspace`)
- `--dry-run`: Preview changes without making any modifications

## What Gets Synced

### From Obsidian to People Work
Files in `{obsidian_vault}/Leadership/1-1s/` are parsed for meeting dates and bullet points.

**Example Obsidian content** (`Leadership/1-1s/Jane Smith.md`):
```markdown
2025-09-26
- We are making progress on project deliverables.
- It is unclear if the order of the sprint ceremonies matters.
```

**Creates People Work file** (`work/jane_smith/events/2025-09-26_1_1.wrk`):
```
event: {
  name: "1:1"
  date: "2025-09-26"
  recurrence: {
    starting: "2025-09-26"
    repeats: "weekly"
  }
}
observations: "We are making progress on project deliverables.
It is unclear if the order of the sprint ceremonies matters."
sentiment: neutral
```

### From People Work to Obsidian
Files in `{peoplework}/{workspace}/work/{person}/events/` are parsed for meeting data.

**Example People Work file** (`work/john_doe/events/2025-09-05_1_1.wrk`):
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

**Adds to Obsidian file** (at the top of `Leadership/1-1s/John Doe.md`):
```markdown
2025-09-05
- **Observations**: Review Q3 goals
- **Sentiment**: positive
- **Comments**: Good progress this quarter
```

### Conflict Resolution
When both systems have content for the same person and date, both sources are preserved with markers:

- In Obsidian: `[From People Work]` marker
- In People Work: `[From Obsidian]` marker

## Directory Structure Requirements

### Obsidian Vault
```
obsidian/
└── Leadership/
    └── 1-1s/
        ├── Firstname Lastname.md
        └── Another Person.md
```

### People Work
```
peoplework/
└── MyWorkspace/  (workspace name)
    ├── core.ppl
    ├── people.ppl
    └── work/
        ├── firstname_lastname/
        │   └── events/
        │       ├── 2025-09-02_1_1.wrk
        │       └── 2025-09-09_1_1.wrk
        └── another_person/
            └── events/
                └── 2025-09-05_1_1.wrk
```

## Name Mapping

The tool automatically handles name format conversion:
- **Obsidian format**: `Firstname Lastname.md`
- **People Work format**: `firstname_lastname`

Examples:
- `John Doe.md` ↔ `john_doe`
- `Jane Smith.md` ↔ `jane_smith`

## Tips

1. **Always run dry-run first**: Use `--dry-run` to preview what changes will be made
2. **Backup your data**: Make backups before running the sync for the first time
3. **Check conflicts**: Review any conflict resolutions to ensure both sources are preserved correctly
4. **Regular syncs**: Run the sync regularly to keep both systems up to date

## Troubleshooting

### "Workspace not found" error
- Verify the workspace name matches the directory under your People Work path
- Use `--workspace` flag if using a different workspace name

### No meetings found
- Check that Obsidian files are in `Leadership/1-1s/` directory
- Check that People Work files are in `{workspace}/work/{person}/events/` directory
- Ensure date format is `YYYY-MM-DD` (e.g., `2025-09-26`)

### Parsing errors
- Ensure Obsidian files use proper date headers (just the date on its own line)
- Ensure bullet points use `-`, `*`, or numbered format
- Ensure People Work `.wrk` files follow the DSL syntax

