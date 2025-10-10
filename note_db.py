"""
SQLite-backed data access layer for the note-taking application.
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class NoteDB:
    """Minimal SQLite database layer for managing notes."""
    
    def __init__(self, db_path: str = "notes.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary tables for notes and tags."""
        cursor = self.conn.cursor()
        
        # Notes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        
        # Note-tags association table (many-to-many)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS note_tags (
                note_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (note_id, tag_id),
                FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """)
        
        self.conn.commit()
    
    def add_note(self, title: str, content: str = "", tags: List[str] = None) -> int:
        """
        Add a new note
        
        Args:
            title: Note title
            content: Note content
            tags: List of tags
            
        Returns:
            ID of the newly created note
        """
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO notes (title, content, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, (title, content, now, now))
        
        note_id = cursor.lastrowid
        
        # Handle tags
        if tags:
            for tag in tags:
                tag_id = self._get_or_create_tag(tag)
                cursor.execute("""
                    INSERT INTO note_tags (note_id, tag_id)
                    VALUES (?, ?)
                """, (note_id, tag_id))
        
        self.conn.commit()
        return note_id
    
    def _get_or_create_tag(self, tag_name: str) -> int:
        """Get or create a tag, return tag ID"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        row = cursor.fetchone()
        
        if row:
            return row['id']
        
        cursor.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
        return cursor.lastrowid
    
    def get_note(self, note_id: int) -> Optional[Dict]:
        """
        Get a single note
        
        Args:
            note_id: Note ID
            
        Returns:
            Note data dictionary including list of tags
        """
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        note_row = cursor.fetchone()
        
        if not note_row:
            return None
        
        # Get tags
        cursor.execute("""
            SELECT t.name FROM tags t
            JOIN note_tags nt ON t.id = nt.tag_id
            WHERE nt.note_id = ?
        """, (note_id,))
        
        tags = [row['name'] for row in cursor.fetchall()]
        
        return {
            'id': note_row['id'],
            'title': note_row['title'],
            'content': note_row['content'],
            'created_at': note_row['created_at'],
            'updated_at': note_row['updated_at'],
            'tags': tags
        }
    
    def search_notes(
        self,
        title: Optional[str] = None,
        tags: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        keyword: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for notes
        
        Args:
            title: Title search (partial match)
            tags: List of tags (returns notes with any of the tags)
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            keyword: Full-text search keyword (title or content)
            
        Returns:
            List of notes matching the criteria
        """
        cursor = self.conn.cursor()
        
        query = "SELECT DISTINCT n.* FROM notes n"
        conditions = []
        params = []
        
        # Tag search requires JOIN
        if tags:
            query += """
                JOIN note_tags nt ON n.id = nt.note_id
                JOIN tags t ON nt.tag_id = t.id
            """
            tag_placeholders = ','.join(['?' for _ in tags])
            conditions.append(f"t.name IN ({tag_placeholders})")
            params.extend(tags)
        
        # Title search
        if title:
            conditions.append("n.title LIKE ?")
            params.append(f"%{title}%")
        
        # Date range
        if start_date:
            conditions.append("n.created_at >= ?")
            params.append(start_date)
        
        if end_date:
            conditions.append("n.created_at <= ?")
            params.append(end_date)
        
        # Full-text search
        if keyword:
            conditions.append("(n.title LIKE ? OR n.content LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        # Combine query
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY n.created_at DESC"
        
        cursor.execute(query, params)
        notes = []
        
        for row in cursor.fetchall():
            note = self.get_note(row['id'])
            notes.append(note)
        
        return notes
    
    def update_note(
        self,
        note_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Update a note
        
        Args:
            note_id: Note ID
            title: New title (optional)
            content: New content (optional)
            tags: New list of tags (optional, replaces existing tags)
            
        Returns:
            True if update was successful
        """
        cursor = self.conn.cursor()
        
        # Check if note exists
        cursor.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
        if not cursor.fetchone():
            return False
        
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        
        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(note_id)
            
            query = f"UPDATE notes SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
        
        # Update tags
        if tags is not None:
            # Delete existing tag associations
            cursor.execute("DELETE FROM note_tags WHERE note_id = ?", (note_id,))
            
            # Add new tags
            for tag in tags:
                tag_id = self._get_or_create_tag(tag)
                cursor.execute("""
                    INSERT INTO note_tags (note_id, tag_id)
                    VALUES (?, ?)
                """, (note_id, tag_id))
        
        self.conn.commit()
        return True
    
    def delete_note(self, note_id: int) -> bool:
        """
        Delete a note
        
        Args:
            note_id: Note ID
            
        Returns:
            True if deletion was successful
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        deleted = cursor.rowcount > 0
        self.conn.commit()
        return deleted
    
    def get_all_notes(self, sort_by: str = "created_at", order: str = "DESC") -> List[Dict]:
        """
        Get all notes
        
        Args:
            sort_by: Sort field (created_at or updated_at)
            order: Sort direction (ASC or DESC)
            
        Returns:
            List of all notes
        """
        cursor = self.conn.cursor()
        
        valid_sort = sort_by if sort_by in ["created_at", "updated_at", "title"] else "created_at"
        valid_order = order if order in ["ASC", "DESC"] else "DESC"
        
        query = f"SELECT * FROM notes ORDER BY {valid_sort} {valid_order}"
        cursor.execute(query)
        
        notes = []
        for row in cursor.fetchall():
            note = self.get_note(row['id'])
            notes.append(note)
        
        return notes
    
    def get_notes_by_tag(self, tag_name: str) -> List[Dict]:
        """
        Get all notes with a specific tag
        
        Args:
            tag_name: Tag name
            
        Returns:
            List of notes with the specified tag
        """
        return self.search_notes(tags=[tag_name])
    
    def get_statistics(self) -> Dict:
        """
        Get statistics
        
        Returns:
            Dictionary containing various statistics
        """
        cursor = self.conn.cursor()
        
        # Total number of notes
        cursor.execute("SELECT COUNT(*) as count FROM notes")
        total_notes = cursor.fetchone()['count']
        
        # Total number of tags
        cursor.execute("SELECT COUNT(*) as count FROM tags")
        total_tags = cursor.fetchone()['count']
        
        # Number of notes per tag
        cursor.execute("""
            SELECT t.name, COUNT(nt.note_id) as count
            FROM tags t
            LEFT JOIN note_tags nt ON t.id = nt.tag_id
            GROUP BY t.id
            ORDER BY count DESC
        """)
        
        tag_counts = {row['name']: row['count'] for row in cursor.fetchall()}
        
        return {
            'total_notes': total_notes,
            'total_tags': total_tags,
            'tag_counts': tag_counts
        }
    
    def export_notes(self) -> str:
        """
        Export all notes as plain text
        
        Returns:
            Formatted note text
        """
        notes = self.get_all_notes()
        output = []
        
        for note in notes:
            output.append("=" * 80)
            output.append(f"Title: {note['title']}")
            output.append(f"ID: {note['id']}")
            output.append(f"Tags: {', '.join(note['tags']) if note['tags'] else 'None'}")
            output.append(f"Created: {note['created_at']}")
            output.append(f"Updated: {note['updated_at']}")
            output.append("-" * 80)
            output.append(note['content'])
            output.append("")
        
        return "\n".join(output)
    
    def close(self):
        """Close database connection"""
        self.conn.close()

