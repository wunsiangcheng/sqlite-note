# SQLite CLI Note-Taking Application

A command-line interface (CLI) note-taking application built with SQLite, supporting note management, tag categorization, and full-text search.

## Features

### Note Content Management
- ✅ Add notes: Enter title, content, tags, with automatic timestamp
- ✅ Query notes: Search by title, tags, or date range
- ✅ Edit notes: Modify content or title of existing notes
- ✅ Delete notes: Remove unwanted notes

### Categorization and Tagging System
- ✅ Create tag classification hierarchy
- ✅ Assign multiple tags to notes
- ✅ Query all notes under a specific tag

### Time Management
- ✅ Record note creation and modification times
- ✅ Support time-based sorting (newest/oldest first)
- ✅ Support date range queries

### Additional Features
- ✅ Statistics (by tags, by time)
- ✅ Full-text search in titles and content
- ✅ Import/Export notes (plain text format)

## File Structure

```
sqlite-note/
├── app.py              # CLI entry point, parses arguments and calls database layer
├── note_db.py          # SQLite data access layer
├── test_app.py         # Unit tests for CLI application
├── test_note_db.py     # Unit tests for database layer
└── README.md           # Documentation
```

## Installation and Usage

### Prerequisites
- Python 3.7+
- SQLite3 (built into Python)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd sqlite-note

# No additional packages required - uses Python standard library
```

### Running Tests
```bash
# Test database layer
python test_note_db.py

# Test CLI application
python test_app.py

# Run all tests
python -m unittest discover
```

## Usage Guide

### Basic Command Format
```bash
python app.py [--db DATABASE] COMMAND [OPTIONS]
```

### Command List

#### 1. Add Note (`add`)
```bash
python app.py add --title "My First Note" --content "This is the note content" --tags "work,important"
```

#### 2. List All Notes (`list`)
```bash
# List all notes (default: descending by creation time)
python app.py list

# Sort by update time
python app.py list --sort updated_at --order ASC

# Sort by title
python app.py list --sort title --order ASC
```

#### 3. View Single Note (`get`)
```bash
python app.py get 1
```

#### 4. Search Notes (`search`)
```bash
# Search by title
python app.py search --title "Python"

# Search by tags
python app.py search --tags "work,important"

# Search by keyword (in title or content)
python app.py search --keyword "important"

# Search by date range
python app.py search --start-date "2025-01-01" --end-date "2025-12-31"

# Combined search
python app.py search --title "Python" --tags "programming" --keyword "tutorial"
```

#### 5. Update Note (`update`)
```bash
# Update title
python app.py update 1 --title "New Title"

# Update content
python app.py update 1 --content "New Content"

# Update tags (replaces existing tags)
python app.py update 1 --tags "new_tag1,new_tag2"

# Update multiple fields at once
python app.py update 1 --title "New Title" --content "New Content" --tags "tag1,tag2"
```

#### 6. Delete Note (`delete`)
```bash
# Delete note (will prompt for confirmation)
python app.py delete 1

# Delete without confirmation
python app.py delete 1 -y
```

#### 7. View Notes by Tag (`tags`)
```bash
python app.py tags work
```

#### 8. Statistics (`stats`)
```bash
python app.py stats
```

#### 9. Export Notes (`export`)
```bash
# Export to console
python app.py export

# Export to file
python app.py export -o notes_backup.txt
```

### Usage Examples

#### Scenario 1: Work Notes
```bash
# Add work-related note
python app.py add --title "Project Progress Report" --content "Completed features A and B this week" --tags "work,project"

# View all work-tagged notes
python app.py tags work
```

#### Scenario 2: Study Notes Management
```bash
# Add study note
python app.py add --title "Python Decorators" --content "Decorators are a design pattern..." --tags "programming,Python,learning"

# Search all Python-related notes
python app.py search --tags "Python"

# Search for notes containing "design pattern"
python app.py search --keyword "design pattern"
```

#### Scenario 3: Note Backup
```bash
# View statistics
python app.py stats

# Export all notes
python app.py export -o backup_2025_10_08.txt
```

## Database Structure

### Tables

#### `notes` - Notes table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| title | TEXT | Note title |
| content | TEXT | Note content |
| created_at | TEXT | Creation time (ISO format) |
| updated_at | TEXT | Update time (ISO format) |

#### `tags` - Tags table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| name | TEXT | Tag name (unique) |

#### `note_tags` - Note-Tag association table
| Column | Type | Description |
|--------|------|-------------|
| note_id | INTEGER | Note ID (foreign key) |
| tag_id | INTEGER | Tag ID (foreign key) |

## Development Guide

### Extending Features

#### Adding New Commands
1. Add database operation method in `note_db.py`
2. Add sub-parser in `main()` function in `app.py`
3. Implement command handler function (e.g., `cmd_xxx()`)
4. Register new command in `command_map`
5. Write corresponding unit tests

#### Modifying Database Structure
1. Modify `_create_tables()` method in `note_db.py`
2. Update related query and operation methods
3. Update test cases

### Testing Guide

All features should have corresponding unit tests:
- `test_note_db.py`: Tests all methods in the database layer
- `test_app.py`: Tests CLI command input/output

```bash
# Run specific test class
python -m unittest test_note_db.TestNoteDB

# Run specific test method
python -m unittest test_note_db.TestNoteDB.test_add_note

# Verbose output
python -m unittest -v
```

## Notes

1. **Database file**: Default is `notes.db`, can be specified via `--db` parameter
2. **Time format**: Uses ISO 8601 format (`YYYY-MM-DDTHH:MM:SS`)
3. **Tag separator**: Multiple tags separated by comma `,`
4. **Encoding**: All files use UTF-8 encoding
5. **Delete operation**: Deleting a note automatically cleans up related tag associations

## FAQ

### Q: How to backup notes?
A: You can directly copy the `notes.db` file, or use the `export` command to export as text.

### Q: How to restore notes?
A: Copy the backed-up `notes.db` file back to the directory.

### Q: Can I search with multiple criteria simultaneously?
A: Yes, all search criteria use AND logic. For example:
```bash
python app.py search --tags "work" --keyword "important" --start-date "2025-01-01"
```

### Q: How to view complete help information?
A: Use `-h` or `--help` parameter:
```bash
python app.py -h
python app.py add -h
python app.py search -h
```

## License

MIT License

## Contributing

Issues and Pull Requests are welcome!
