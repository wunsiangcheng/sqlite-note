# sqlite-note

A small command-line note-taking application backed by SQLite.

Written in Python and packaged as a simple CLI in `app.py`. Notes, tags, and associations are stored in a local SQLite database (default: `notes.db`).

## Features

- Create, read, update, and delete notes
- Tag notes (many-to-many relationship)
- Search by title, tag, date range, or keyword (title/content)
- List and export notes as plain text
- Simple statistics (total notes, tag counts)

## Requirements

- Linux (examples below use bash)
- Python 3.8+ (works on 3.8, 3.9, 3.10, 3.11+)
- No external Python packages required (uses the standard library `sqlite3`).

## Quick start (Linux)

Open a terminal in the project directory and follow these commands.

1. (Optional) Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Run the CLI (the default database file is `notes.db`)

- Show help

```bash
python3 app.py -h
```

- Add a note

```bash
python3 app.py add --title "My First Note" --content "This is the content." --tags "work,important"
```

- List notes

```bash
python3 app.py list
```

- Get a note by ID

```bash
python3 app.py get 1
```

- Search notes (keyword/title/tag/date range)

```bash
# Search by keyword in title or content
python3 app.py search --keyword "important"

# Search by title (partial match)
python3 app.py search --title "First"

# Search by tag(s)
python3 app.py search --tags "work,personal"

# Date range (ISO format: YYYY-MM-DD or full ISO)
python3 app.py search --start-date "2025-01-01" --end-date "2025-12-31"
```

- Update a note (replace tags if provided)

```bash
python3 app.py update 1 --title "Updated title" --content "New content" --tags "urgent,work"
```

- Delete a note (with confirmation)

```bash
python3 app.py delete 1
# or skip confirmation
python3 app.py delete 1 -y
```

- View notes by tag

```bash
python3 app.py tags work
```

- Export notes to a file

```bash
python3 app.py export -o notes.txt
```

- Show statistics

```bash
python3 app.py stats
```

## Using a custom database file

By default the app uses `notes.db` in the current directory. To use a different file, pass `--db` before the subcommand:

```bash
python3 app.py --db mynotes.db list
```

## Inspecting or resetting the database (Linux)

- Check that the database file exists

```bash
ls -lh notes.db
```

- Remove the database (reset all notes)

```bash
rm notes.db
```

- Inspect the SQLite schema interactively

```bash
sqlite3 notes.db ".schema"
```

## Development notes

- The code is intentionally minimal and uses only the Python standard library (`sqlite3`, `argparse`, `datetime`).
- The database tables are created automatically on first run.
- Tags are stored in a separate `tags` table with a `note_tags` join table.

## Help and troubleshooting

- If you see errors about Python versions, ensure you're running a supported Python binary (python3). Use `python3 --version` to check.
- For usage details for any command, run:

```bash
python3 app.py <command> -h
```

## Files

- `app.py` — CLI entrypoint and argument parsing
- `note_db.py` — SQLite data access layer


## License

No license specified. Copy or reuse as you like, or add a LICENSE file if you want to clarify terms.
