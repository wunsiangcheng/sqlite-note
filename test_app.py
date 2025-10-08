"""
Unit tests for the CLI application.
"""
import unittest
import os
import tempfile
import sys
from io import StringIO
from unittest.mock import patch
from note_db import NoteDB
import app


class TestApp(unittest.TestCase):
    """Test CLI application"""
    
    def setUp(self):
        """Create temporary database before each test"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = NoteDB(self.temp_db.name)
    
    def tearDown(self):
        """Clean up temporary database after each test"""
        self.db.close()
        os.unlink(self.temp_db.name)
    
    def test_format_note(self):
        """Test formatting a single note"""
        note = {
            'id': 1,
            'title': 'Test Title',
            'content': 'Test Content',
            'tags': ['tag1', 'tag2'],
            'created_at': '2025-01-01T00:00:00',
            'updated_at': '2025-01-01T00:00:00'
        }
        
        output = app.format_note(note)
        
        self.assertIn('Test Title', output)
        self.assertIn('Test Content', output)
        self.assertIn('tag1', output)
        self.assertIn('tag2', output)
    
    def test_format_note_list(self):
        """Test formatting a list of notes"""
        notes = [
            {
                'id': 1,
                'title': 'Note 1',
                'content': 'Content 1',
                'tags': ['tag1'],
                'created_at': '2025-01-01T00:00:00',
                'updated_at': '2025-01-01T00:00:00'
            },
            {
                'id': 2,
                'title': 'Note 2',
                'content': 'Content 2',
                'tags': [],
                'created_at': '2025-01-02T00:00:00',
                'updated_at': '2025-01-02T00:00:00'
            }
        ]
        
        output = app.format_note_list(notes)
        
        self.assertIn('Found 2 note', output)
        self.assertIn('Note 1', output)
        self.assertIn('Note 2', output)
    
    def test_format_empty_note_list(self):
        """Test formatting an empty list of notes"""
        output = app.format_note_list([])
        self.assertIn('No notes found', output)
    
    def test_cmd_add(self):
        """Test add note command"""
        args = type('Args', (), {
            'title': 'Test Title',
            'content': 'Test Content',
            'tags': 'tag1,tag2'
        })()
        
        app.cmd_add(args, self.db)
        
        notes = self.db.get_all_notes()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]['title'], 'Test Title')
        self.assertEqual(len(notes[0]['tags']), 2)
    
    def test_cmd_add_without_tags(self):
        """Test adding a note without tags"""
        args = type('Args', (), {
            'title': 'Test Title',
            'content': 'Test Content',
            'tags': None
        })()
        
        app.cmd_add(args, self.db)
        
        notes = self.db.get_all_notes()
        self.assertEqual(len(notes), 1)
        self.assertEqual(len(notes[0]['tags']), 0)
    
    def test_cmd_get(self):
        """Test get note command"""
        note_id = self.db.add_note("Test Title", "Test Content")
        
        args = type('Args', (), {'id': note_id})()
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            app.cmd_get(args, self.db)
            output = fake_out.getvalue()
            self.assertIn('Test Title', output)
            self.assertIn('Test Content', output)
    
    def test_cmd_get_nonexistent(self):
        """Test getting a non-existent note"""
        args = type('Args', (), {'id': 9999})()
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            app.cmd_get(args, self.db)
            output = fake_out.getvalue()
            self.assertIn('not found', output)
    
    def test_cmd_list(self):
        """Test list notes command"""
        self.db.add_note("Note 1", "Content 1")
        self.db.add_note("Note 2", "Content 2")
        
        args = type('Args', (), {
            'sort': 'created_at',
            'order': 'DESC'
        })()
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            app.cmd_list(args, self.db)
            output = fake_out.getvalue()
            self.assertIn('Found 2 note', output)
    
    def test_cmd_search(self):
        """Test search notes command"""
        self.db.add_note("Python Tutorial", "Content", tags=["programming"])
        self.db.add_note("Java Tutorial", "Content", tags=["programming"])
        
        args = type('Args', (), {
            'title': 'Python',
            'tags': None,
            'start_date': None,
            'end_date': None,
            'keyword': None
        })()
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            app.cmd_search(args, self.db)
            output = fake_out.getvalue()
            self.assertIn('Found 1 note', output)
    
    def test_cmd_update(self):
        """Test update note command"""
        note_id = self.db.add_note("Old Title", "Old Content")
        
        args = type('Args', (), {
            'id': note_id,
            'title': 'New Title',
            'content': None,
            'tags': None
        })()
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            app.cmd_update(args, self.db)
            output = fake_out.getvalue()
            self.assertIn('updated successfully', output)
        
        note = self.db.get_note(note_id)
        self.assertEqual(note['title'], 'New Title')
    
    def test_cmd_delete_with_confirmation(self):
        """Test deleting a note (with confirmation)"""
        note_id = self.db.add_note("Test Title", "Test Content")
        
        args = type('Args', (), {
            'id': note_id,
            'yes': True
        })()
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            app.cmd_delete(args, self.db)
            output = fake_out.getvalue()
            self.assertIn('deleted successfully', output)
        
        note = self.db.get_note(note_id)
        self.assertIsNone(note)
    
    def test_cmd_tags(self):
        """Test view notes by tag command"""
        self.db.add_note("Note 1", "Content", tags=["work"])
        self.db.add_note("Note 2", "Content", tags=["work"])
        self.db.add_note("Note 3", "Content", tags=["personal"])
        
        args = type('Args', (), {'name': 'work'})()
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            app.cmd_tags(args, self.db)
            output = fake_out.getvalue()
            self.assertIn('Found 2 note', output)
    
    def test_cmd_stats(self):
        """Test statistics command"""
        self.db.add_note("Note 1", "Content", tags=["work"])
        self.db.add_note("Note 2", "Content", tags=["work"])
        self.db.add_note("Note 3", "Content", tags=["personal"])
        
        args = type('Args', (), {})()
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            app.cmd_stats(args, self.db)
            output = fake_out.getvalue()
            self.assertIn('Total notes: 3', output)
            self.assertIn('Total tags: 2', output)
            self.assertIn('work: 2', output)
    
    def test_cmd_export(self):
        """Test export command"""
        self.db.add_note("Test Title", "Test Content", tags=["test"])
        
        args = type('Args', (), {'output': None})()
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            app.cmd_export(args, self.db)
            output = fake_out.getvalue()
            self.assertIn('Test Title', output)
            self.assertIn('Test Content', output)
    
    def test_cmd_export_to_file(self):
        """Test exporting to file"""
        self.db.add_note("Test Title", "Test Content")
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt')
        temp_file.close()
        
        try:
            args = type('Args', (), {'output': temp_file.name})()
            
            with patch('sys.stdout', new=StringIO()) as fake_out:
                app.cmd_export(args, self.db)
                output = fake_out.getvalue()
                self.assertIn('exported successfully', output)
            
            with open(temp_file.name, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('Test Title', content)
        
        finally:
            os.unlink(temp_file.name)
    
    def test_tag_parsing(self):
        """Test tag parsing"""
        args = type('Args', (), {
            'title': 'Test',
            'content': 'Content',
            'tags': ' tag1 , tag2 , , tag3 '
        })()
        
        app.cmd_add(args, self.db)
        
        notes = self.db.get_all_notes()
        self.assertEqual(len(notes[0]['tags']), 3)
        self.assertIn('tag1', notes[0]['tags'])
        self.assertIn('tag2', notes[0]['tags'])
        self.assertIn('tag3', notes[0]['tags'])


if __name__ == '__main__':
    unittest.main()
