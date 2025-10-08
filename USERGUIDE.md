## SQLite Note CLI — User Guide

This small CLI note-taking app stores notes in a local SQLite database. It provides commands to add, view, search, update, delete, tag, export notes, and view basic statistics.

Files of interest
- `app.py` — CLI entrypoint. Parses arguments and calls the database layer.
- `note_db.py` — SQLite-backed data access layer (creates tables automatically).

Requirements
- Python 3.8+ (the code uses `sqlite3`, `argparse`, `typing`, and `datetime`).
- No external packages required.

Quick start

1. Open a terminal (Windows PowerShell in this repository):

```powershell
cd c:\Users\wunsi\Desktop\sql\sqlite-note
python app.py --help
```

2. Add a note:

```powershell
python app.py add --title "My First Note" --content "This is the body" --tags "work,important"
```

3. List notes:

```powershell
python app.py list
```

4. Get a note by ID:

```powershell
python app.py get 1
```

Database file
- By default the app uses `notes.db` in the current working directory.
- To use a different file, pass `--db <path>` to any command. Example:

```powershell
python app.py --db C:\path\to\mydb.sqlite list
```

CLI commands (reference)

All commands are subcommands of `app.py`. Run `python app.py <command> --help` for argument-specific help.

- add
  - Usage: `python app.py add --title <title> [--content <text>] [--tags "tag1,tag2"]`
  - Creates a new note. Tags are comma-separated and trimmed. Passing no `--content` creates an empty body.
  - Example:

    ```powershell
    python app.py add --title "Meeting notes" --content "Discussed milestone X." --tags "meetings,team"
    ```

- get
  - Usage: `python app.py get <id>`
  - Prints a formatted view of the note with the given numeric ID.

- list
  - Usage: `python app.py list [--sort created_at|updated_at|title] [--order ASC|DESC]`
  - Lists all notes. Default sort is `created_at` descending.
  - Example: `python app.py list --sort title --order ASC`

- search
  - Usage: `python app.py search [--title <partial>] [--tags "t1,t2"] [--start-date <ISO>] [--end-date <ISO>] [--keyword <text>]`
  - Behavior:
    - `--title` performs a SQL LIKE match on the title (partial match).
    - `--tags` matches notes that have any of the provided tags.
    - `--start-date` / `--end-date` filter by the note `created_at` timestamp (ISO format, e.g. `2023-05-01T00:00:00`).
    - `--keyword` performs a LIKE search on title OR content.
  - Example: search notes with keyword "urgent":

    ```powershell
    python app.py search --keyword urgent
    ```

- update
  - Usage: `python app.py update <id> [--title <new>] [--content <new>] [--tags "t1,t2"]`
  - Updates fields provided. Passing `--tags ""` will clear all tags for the note (empty list). If `--tags` is omitted, existing tags are preserved.
  - Example: replace tags and update content:

    ```powershell
    python app.py update 2 --content "Updated text" --tags "idea,personal"
    ```

- delete
  - Usage: `python app.py delete <id> [-y|--yes]`
  - Prompts for confirmation unless `-y` is provided. Permanently removes the note.

- tags
  - Usage: `python app.py tags <name>`
  - Shows all notes that contain the specified tag.

- stats
  - Usage: `python app.py stats`
  - Shows summary statistics: total notes, total tags, and counts per tag.

- export
  - Usage: `python app.py export [-o|--output <file>]`
  - Exports all notes as a human-readable plain text dump. If `--output` is omitted the content is printed to stdout.

Database schema (for reference)

- notes
  - id INTEGER PRIMARY KEY AUTOINCREMENT
  - title TEXT NOT NULL
  - content TEXT
  - created_at TEXT NOT NULL (ISO timestamp)
  - updated_at TEXT NOT NULL (ISO timestamp)

- tags
  - id INTEGER PRIMARY KEY AUTOINCREMENT
  - name TEXT UNIQUE NOT NULL

- note_tags
  - note_id INTEGER
  - tag_id INTEGER
  - PRIMARY KEY (note_id, tag_id)

Notes on behavior and implementation

- Tag matching: when searching with multiple tags the code returns notes that have any of the tags (logical OR), not only those that have all tags.
- Date filtering uses the stored `created_at` ISO strings. Provide ISO-like strings (e.g. `2023-05-01` or `2023-05-01T00:00:00`) when using `--start-date`/`--end-date`.
- The `keyword` search is a simple SQL LIKE on both title and content — it is not a full-text search index.
- The application opens a direct SQLite connection and commits after every write.

Tips, limitations and troubleshooting

- Concurrent writes: SQLite is file-based. Concurrent multi-process writes can cause busy errors; for light personal use this is fine. If you need multi-user concurrent access, consider moving to a client-server DB or adding retry/backoff.
- Timezones: timestamps are generated with `datetime.now().isoformat()` (local time). If you need UTC or timezone-aware timestamps, change `note_db.py` accordingly.
- Windows path notes: when passing `--db` or `--output` use proper escaping or double quotes for paths with spaces.
- Encoding: the export and file write operations use UTF-8.

Development notes (for contributors)

- The CLI implementation is in `app.py`. The command map dispatches to functions defined in the same file.
- Data logic is in `NoteDB` within `note_db.py`. All DDL is created automatically when `NoteDB` is instantiated.

Suggested small improvements

- Add unit tests that exercise `note_db.py` methods (happy path + edge cases such as empty tags, non-existent IDs).
- Add a `requirements.txt` or small `pyproject.toml` if you extend the project with dependencies.
- Add concurrency-safe retries or a simple connection pool wrapper if multi-process use increases.
- Consider using SQLite FTS (full-text search) for better `--keyword` performance and features.

Contact and credits
- Author: project files in this repository (see `app.py` and `note_db.py`).

This guide describes the current behavior implemented in `app.py` and `note_db.py` as of this repository snapshot.
