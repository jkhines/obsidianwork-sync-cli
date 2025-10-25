# Implementation Documentation

## Overview

This tool provides bidirectional synchronization between Obsidian markdown files and People Work DSL (.wrk) files for 1:1 meeting notes.

## Architecture

The implementation follows a modular design with clear separation of concerns:

```
sync.py (CLI entry point)
    ↓
parsers/ (Extract data)
    ├── obsidian.py     - Parse markdown files
    └── peoplework.py   - Parse .wrk DSL files
    ↓
sync_engine.py (Compare and sync)
    ↓
writers/ (Generate output)
    ├── obsidian.py     - Write markdown
    └── peoplework.py   - Write .wrk DSL
```

## Component Details

### 1. Parsers

#### Obsidian Parser (`parsers/obsidian.py`)
- **Purpose**: Extract meeting notes from Obsidian markdown files
- **Input**: `{vault}/Leadership/1-1s/*.md` files
- **Output**: `{person_name: {date: [bullet_points]}}`
- **Logic**:
  - Scans markdown files for date headers matching `YYYY-MM-DD`
  - Extracts all bullet points (using `-`, `*`, or numbered lists) under each date
  - Groups by person name (from filename)

#### People Work Parser (`parsers/peoplework.py`)
- **Purpose**: Extract meeting data from People Work DSL files
- **Input**: `{workspace}/work/{person}/events/*.wrk` files
- **Output**: `{person_name: {date: {observations, sentiment, comments}}}`
- **Logic**:
  - Extracts date from filename pattern `YYYY-MM-DD_*.wrk`
  - Parses DSL fields using regex patterns
  - Handles both simple strings and triple-quoted multiline strings

### 2. Sync Engine (`sync_engine.py`)

Core synchronization logic with three scenarios:

#### Scenario 1: Obsidian Only
- **Condition**: Meeting exists in Obsidian but not in People Work
- **Action**: Create new `.wrk` file in People Work
- **Mapping**:
  - Bullet points → `observations` field
  - `sentiment` = `neutral`
  - `comments` = empty string

#### Scenario 2: People Work Only
- **Condition**: Meeting exists in People Work but not in Obsidian
- **Action**: Add entry to Obsidian markdown file
- **Formatting**:
  ```markdown
  YYYY-MM-DD
  - **Observations**: {observations}
  - **Sentiment**: {sentiment}
  - **Comments**: {comments}
  ```

#### Scenario 3: Conflict (Both Exist)
- **Condition**: Meeting exists in both systems with different content
- **Action**: Append both sources with markers
- **People Work**:
  ```
  observations: "{original observations}

  [From Obsidian]
  {obsidian bullet points}"
  ```
- **Obsidian**:
  ```markdown
  YYYY-MM-DD
  - {existing bullets}
  - [From People Work] **Observations**: {observations}
  - [From People Work] **Sentiment**: {sentiment}
  - [From People Work] **Comments**: {comments}
  ```

### 3. Writers

#### People Work Writer (`writers/peoplework.py`)
- **Purpose**: Generate People Work DSL files
- **DSL Format**:
  ```
  event: {
    name: "1:1"
    date: "YYYY-MM-DD"
    recurrence: {
      starting: "YYYY-MM-DD"
      repeats: "weekly"
    }
  }
  observations: "..."
  sentiment: neutral|positive|negative
  comments: "..."
  ```
- **Features**:
  - Auto-detects multiline content and uses triple quotes
  - Creates directory structure if missing
  - Always includes recurrence block (per requirements)

#### Obsidian Writer (`writers/obsidian.py`)
- **Purpose**: Update Obsidian markdown files
- **Features**:
  - Inserts new date sections at top of file
  - Appends to existing date sections for conflicts
  - Creates directory structure if missing
  - Formats with bullet points and bold labels

### 4. Name Mapping (`utils/names.py`)

Handles conversion between naming conventions:

| System | Format | Example |
|--------|--------|---------|
| Obsidian | `Firstname Lastname.md` | `John Doe.md` |
| People Work | `firstname_lastname` | `john_doe` |

Functions:
- `obsidian_to_peoplework()`: Converts `"John Doe.md"` → `"john_doe"`
- `peoplework_to_obsidian()`: Converts `"john_doe"` → `"John Doe.md"`

## CLI Interface

### Arguments
- **Required**:
  - `--peoplework`: Path to People Work root
  - `--obsidian`: Path to Obsidian vault
- **Optional**:
  - `--workspace NAME`: Workspace name (default: "MyWorkspace")
  - `--dry-run`: Preview changes without applying

### Output
- Progress messages during parsing and sync
- Summary statistics:
  - Count of syncs from Obsidian → People Work
  - Count of syncs from People Work → Obsidian
  - Count of conflicts resolved

## Design Decisions

### 1. Why Python?
- Excellent string parsing capabilities (regex, multiline)
- Simple file I/O
- Cross-platform compatibility
- Rich ecosystem for text processing

### 2. Why Modular Structure?
- Easy to test individual components
- Clear separation of concerns
- Easy to extend or modify specific parts
- Reusable parsers/writers

### 3. Recurrence Handling
- **Decision**: Always include recurrence block in People Work files
- **Rationale**: Per DSL specification, 1:1 meetings typically recur weekly
- **Note**: Does not parse or modify existing recurrence settings

### 4. Conflict Strategy
- **Decision**: Append both sources with markers
- **Rationale**: Preserves all data, allows manual review
- **Alternative considered**: Last-write-wins (rejected as data loss risk)

### 5. Sentiment Mapping
- **Decision**: Default to `neutral` for Obsidian → People Work
- **Rationale**: Obsidian doesn't encode sentiment, assuming neutral is safest
- **Note**: Could be enhanced with sentiment analysis in future

## Testing Approach

### Manual Testing Performed
1. **Parser validation**:
   - Tested with sample `.wrk` files
   - Tested with sample markdown files
   - Verified correct extraction of all fields

2. **Name conversion**:
   - Tested bidirectional conversion
   - Verified capitalization handling

3. **CLI interface**:
   - Help text generation
   - Argument parsing
   - Dry-run mode

4. **Integration test**:
   - Dry-run with real directory structures
   - Found 17 people with 112 meetings in Obsidian
   - Found 13 people with 19 meetings in People Work

### Test Cases to Run
Before first production use, recommend testing:
1. **Empty directories**: Both systems empty
2. **One-way sync**: Only Obsidian has data
3. **One-way sync**: Only People Work has data
4. **Conflict resolution**: Same person, same date, different content
5. **Special characters**: Names with apostrophes, quotes
6. **Multiline content**: Observations/comments spanning multiple lines

## Known Limitations

1. **Recurrence**: Always set to weekly, doesn't parse existing recurrence
2. **Event names**: Always "1:1", doesn't support custom event names
3. **Date-only parsing**: Obsidian parser only looks for date headers, ignores non-bullet text
4. **File format assumptions**: Expects specific directory structures

## Future Enhancements

1. **Incremental sync**: Track last sync time, only process changes
2. **Conflict UI**: Interactive conflict resolution
3. **Sentiment analysis**: Auto-detect sentiment from Obsidian text
4. **Custom event types**: Support for different meeting types
5. **Validation**: Pre-sync validation of file formats
6. **Backup**: Auto-backup before sync
7. **Logging**: Detailed log file for troubleshooting

## Dependencies

- **python-dateutil** (^2.8.0): Date parsing utilities (reserved for future use)
- **Python Standard Library**:
  - `argparse`: CLI argument parsing
  - `os`: File system operations
  - `re`: Regular expression parsing
  - `collections.defaultdict`: Data structure for grouping

## File Locations

### Input Files
- Obsidian: `{vault}/Leadership/1-1s/*.md`
- People Work: `{peoplework}/{workspace}/work/{person}/events/*.wrk`

### Output Files
- Creates new `.wrk` files when syncing from Obsidian
- Updates existing `.md` files when syncing from People Work
- Creates directories as needed

## Error Handling

- Path validation before processing
- Graceful handling of missing directories
- File encoding: UTF-8 for all read/write operations
- Exit codes:
  - 0: Success
  - 1: Validation error (missing paths)

