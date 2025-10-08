"""
CLI entrypoint for the note-taking application.
Parses arguments and calls the database layer.
"""
import argparse
import sys
from note_db import NoteDB


def format_note(note):
    """Format a single note for output"""
    tags_str = ', '.join(note['tags']) if note['tags'] else 'None'
    return f"""
{'=' * 60}
ID: {note['id']}
Title: {note['title']}
Tags: {tags_str}
Created: {note['created_at']}
Updated: {note['updated_at']}
{'-' * 60}
{note['content']}
{'=' * 60}
"""


def format_note_list(notes):
    """Format a list of notes for output"""
    if not notes:
        return "No notes found."
    
    output = [f"\nFound {len(notes)} note(s):\n"]
    
    for note in notes:
        tags_str = ', '.join(note['tags']) if note['tags'] else 'None'
        output.append(f"[{note['id']}] {note['title']}")
        output.append(f"    Tags: {tags_str}")
        output.append(f"    Date: {note['created_at']}")
        preview = note['content'][:50] + "..." if len(note['content']) > 50 else note['content']
        output.append(f"    Preview: {preview}")
        output.append("")
    
    return "\n".join(output)


def cmd_add(args, db):
    """Add note command"""
    tags = args.tags.split(',') if args.tags else []
    tags = [tag.strip() for tag in tags if tag.strip()]
    
    note_id = db.add_note(args.title, args.content or "", tags)
    print(f"✓ Note added successfully! ID: {note_id}")


def cmd_get(args, db):
    """Get note command"""
    note = db.get_note(args.id)
    
    if note:
        print(format_note(note))
    else:
        print(f"✗ Note with ID {args.id} not found.")


def cmd_list(args, db):
    """List all notes command"""
    notes = db.get_all_notes(sort_by=args.sort, order=args.order)
    print(format_note_list(notes))


def cmd_search(args, db):
    """Search notes command"""
    tags = args.tags.split(',') if args.tags else None
    if tags:
        tags = [tag.strip() for tag in tags if tag.strip()]
    
    notes = db.search_notes(
        title=args.title,
        tags=tags,
        start_date=args.start_date,
        end_date=args.end_date,
        keyword=args.keyword
    )
    
    print(format_note_list(notes))


def cmd_update(args, db):
    """Update note command"""
    tags = None
    if args.tags is not None:
        tags = args.tags.split(',') if args.tags else []
        tags = [tag.strip() for tag in tags if tag.strip()]
    
    success = db.update_note(
        args.id,
        title=args.title,
        content=args.content,
        tags=tags
    )
    
    if success:
        print(f"✓ Note ID {args.id} updated successfully")
    else:
        print(f"✗ Note with ID {args.id} not found.")


def cmd_delete(args, db):
    """Delete note command"""
    if args.yes or input(f"Are you sure you want to delete note ID {args.id}? (y/N): ").lower() == 'y':
        success = db.delete_note(args.id)
        
        if success:
            print(f"✓ Note ID {args.id} deleted successfully")
        else:
            print(f"✗ Note with ID {args.id} not found.")
    else:
        print("Deletion cancelled.")


def cmd_tags(args, db):
    """View notes with specific tag command"""
    notes = db.get_notes_by_tag(args.name)
    print(f"\nNotes with tag '{args.name}':")
    print(format_note_list(notes))


def cmd_stats(args, db):
    """Show statistics command"""
    stats = db.get_statistics()
    
    print("\n=== Note Statistics ===")
    print(f"Total notes: {stats['total_notes']}")
    print(f"Total tags: {stats['total_tags']}")
    
    if stats['tag_counts']:
        print("\nNotes per tag:")
        for tag, count in stats['tag_counts'].items():
            print(f"  {tag}: {count}")
    else:
        print("\nNo tags yet.")


def cmd_export(args, db):
    """Export notes command"""
    content = db.export_notes()
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Notes exported successfully to {args.output}")
    else:
        print(content)


def main():
    """Main program entry point"""
    parser = argparse.ArgumentParser(
        description="SQLite CLI Note-Taking Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add --title "My First Note" --content "This is the content" --tags "work,important"
  %(prog)s list
  %(prog)s search --keyword "important"
  %(prog)s get 1
  %(prog)s update 1 --title "New Title"
  %(prog)s delete 1
        """
    )
    
    parser.add_argument('--db', default='notes.db', help='Database file path (default: notes.db)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add note
    parser_add = subparsers.add_parser('add', help='Add a new note')
    parser_add.add_argument('--title', required=True, help='Note title')
    parser_add.add_argument('--content', help='Note content')
    parser_add.add_argument('--tags', help='Tags (comma-separated)')
    
    # Get note
    parser_get = subparsers.add_parser('get', help='Get a single note')
    parser_get.add_argument('id', type=int, help='Note ID')
    
    # List all notes
    parser_list = subparsers.add_parser('list', help='List all notes')
    parser_list.add_argument('--sort', choices=['created_at', 'updated_at', 'title'], 
                             default='created_at', help='Sort field')
    parser_list.add_argument('--order', choices=['ASC', 'DESC'], 
                             default='DESC', help='Sort direction')
    
    # Search notes
    parser_search = subparsers.add_parser('search', help='Search notes')
    parser_search.add_argument('--title', help='Title search (partial match)')
    parser_search.add_argument('--tags', help='Tag search (comma-separated)')
    parser_search.add_argument('--start-date', help='Start date (ISO format)')
    parser_search.add_argument('--end-date', help='End date (ISO format)')
    parser_search.add_argument('--keyword', help='Full-text search keyword')
    
    # Update note
    parser_update = subparsers.add_parser('update', help='Update a note')
    parser_update.add_argument('id', type=int, help='Note ID')
    parser_update.add_argument('--title', help='New title')
    parser_update.add_argument('--content', help='New content')
    parser_update.add_argument('--tags', help='New tags (comma-separated, replaces existing tags)')
    
    # Delete note
    parser_delete = subparsers.add_parser('delete', help='Delete a note')
    parser_delete.add_argument('id', type=int, help='Note ID')
    parser_delete.add_argument('-y', '--yes', action='store_true', help='Delete without confirmation')
    
    # View notes by tag
    parser_tags = subparsers.add_parser('tags', help='View all notes with a specific tag')
    parser_tags.add_argument('name', help='Tag name')
    
    # Statistics
    parser_stats = subparsers.add_parser('stats', help='Show statistics')
    
    # Export notes
    parser_export = subparsers.add_parser('export', help='Export all notes')
    parser_export.add_argument('-o', '--output', help='Output file path (prints to console if not specified)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Create database connection
    db = NoteDB(args.db)
    
    try:
        # Execute the corresponding command
        command_map = {
            'add': cmd_add,
            'get': cmd_get,
            'list': cmd_list,
            'search': cmd_search,
            'update': cmd_update,
            'delete': cmd_delete,
            'tags': cmd_tags,
            'stats': cmd_stats,
            'export': cmd_export,
        }
        
        if args.command in command_map:
            command_map[args.command](args, db)
        else:
            print(f"Unknown command: {args.command}")
            parser.print_help()
    
    finally:
        db.close()


if __name__ == '__main__':
    main()
