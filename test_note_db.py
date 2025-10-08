"""
Unit tests for the database layer.
"""
import unittest
import os
import tempfile
from note_db import NoteDB


class TestNoteDB(unittest.TestCase):
    """Test NoteDB database layer"""
    
    def setUp(self):
        """Create temporary database before each test"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = NoteDB(self.temp_db.name)
    
    def tearDown(self):
        """Clean up temporary database after each test"""
        self.db.close()
        os.unlink(self.temp_db.name)
    
    def test_add_note(self):
        """Test adding a note"""
        note_id = self.db.add_note("Test Title", "Test Content")
        self.assertIsInstance(note_id, int)
        self.assertGreater(note_id, 0)
    
    def test_add_note_with_tags(self):
        """Test adding a note with tags"""
        note_id = self.db.add_note("Test Title", "Test Content", tags=["work", "important"])
        note = self.db.get_note(note_id)
        
        self.assertIsNotNone(note)
        self.assertEqual(len(note['tags']), 2)
        self.assertIn("work", note['tags'])
        self.assertIn("important", note['tags'])
    
    def test_get_note(self):
        """Test getting a note"""
        note_id = self.db.add_note("Test Title", "Test Content")
        note = self.db.get_note(note_id)
        
        self.assertIsNotNone(note)
        self.assertEqual(note['title'], "Test Title")
        self.assertEqual(note['content'], "Test Content")
        self.assertIn('created_at', note)
        self.assertIn('updated_at', note)
    
    def test_get_nonexistent_note(self):
        """Test getting a non-existent note"""
        note = self.db.get_note(9999)
        self.assertIsNone(note)
    
    def test_update_note_title(self):
        """Test updating note title"""
        note_id = self.db.add_note("Old Title", "Content")
        success = self.db.update_note(note_id, title="New Title")
        
        self.assertTrue(success)
        note = self.db.get_note(note_id)
        self.assertEqual(note['title'], "New Title")
        self.assertEqual(note['content'], "Content")
    
    def test_update_note_content(self):
        """Test updating note content"""
        note_id = self.db.add_note("Title", "Old Content")
        success = self.db.update_note(note_id, content="New Content")
        
        self.assertTrue(success)
        note = self.db.get_note(note_id)
        self.assertEqual(note['content'], "New Content")
    
    def test_update_note_tags(self):
        """Test updating note tags"""
        note_id = self.db.add_note("Title", "Content", tags=["old_tag"])
        success = self.db.update_note(note_id, tags=["new_tag1", "new_tag2"])
        
        self.assertTrue(success)
        note = self.db.get_note(note_id)
        self.assertEqual(len(note['tags']), 2)
        self.assertIn("new_tag1", note['tags'])
        self.assertIn("new_tag2", note['tags'])
        self.assertNotIn("old_tag", note['tags'])
    
    def test_update_nonexistent_note(self):
        """Test updating a non-existent note"""
        success = self.db.update_note(9999, title="New Title")
        self.assertFalse(success)
    
    def test_delete_note(self):
        """Test deleting a note"""
        note_id = self.db.add_note("Test Title", "Test Content")
        success = self.db.delete_note(note_id)
        
        self.assertTrue(success)
        note = self.db.get_note(note_id)
        self.assertIsNone(note)
    
    def test_delete_nonexistent_note(self):
        """Test deleting a non-existent note"""
        success = self.db.delete_note(9999)
        self.assertFalse(success)
    
    def test_get_all_notes(self):
        """Test getting all notes"""
        self.db.add_note("Note 1", "Content 1")
        self.db.add_note("Note 2", "Content 2")
        self.db.add_note("Note 3", "Content 3")
        
        notes = self.db.get_all_notes()
        self.assertEqual(len(notes), 3)
    
    def test_get_all_notes_sorted(self):
        """Test getting sorted notes"""
        id1 = self.db.add_note("Note A", "Content")
        id2 = self.db.add_note("Note B", "Content")
        id3 = self.db.add_note("Note C", "Content")
        
        # Default: descending by creation time
        notes = self.db.get_all_notes()
        self.assertEqual(notes[0]['id'], id3)
        
        # Ascending by creation time
        notes = self.db.get_all_notes(order='ASC')
        self.assertEqual(notes[0]['id'], id1)
    
    def test_search_by_title(self):
        """Test searching by title"""
        self.db.add_note("Python Tutorial", "Content")
        self.db.add_note("JavaScript Tutorial", "Content")
        self.db.add_note("Python Advanced", "Content")
        
        notes = self.db.search_notes(title="Python")
        self.assertEqual(len(notes), 2)
    
    def test_search_by_tags(self):
        """Test searching by tags"""
        self.db.add_note("Note 1", "Content", tags=["work"])
        self.db.add_note("Note 2", "Content", tags=["personal"])
        self.db.add_note("Note 3", "Content", tags=["work", "important"])
        
        notes = self.db.search_notes(tags=["work"])
        self.assertEqual(len(notes), 2)
    
    def test_search_by_keyword(self):
        """Test full-text search"""
        self.db.add_note("Title 1", "This is Python content")
        self.db.add_note("Title 2", "This is Java content")
        self.db.add_note("Python Tutorial", "This is content")
        
        notes = self.db.search_notes(keyword="Python")
        self.assertEqual(len(notes), 2)
    
    def test_search_combined(self):
        """Test combined search"""
        self.db.add_note("Python Note", "Learning content", tags=["programming"])
        self.db.add_note("Python Advanced", "Advanced content", tags=["programming"])
        self.db.add_note("Java Note", "Learning content", tags=["programming"])
        
        notes = self.db.search_notes(title="Python", tags=["programming"])
        self.assertEqual(len(notes), 2)
    
    def test_get_notes_by_tag(self):
        """Test getting notes by specific tag"""
        self.db.add_note("Note 1", "Content", tags=["work"])
        self.db.add_note("Note 2", "Content", tags=["work", "important"])
        self.db.add_note("Note 3", "Content", tags=["personal"])
        
        notes = self.db.get_notes_by_tag("work")
        self.assertEqual(len(notes), 2)
    
    def test_statistics(self):
        """Test statistics function"""
        self.db.add_note("Note 1", "Content", tags=["work"])
        self.db.add_note("Note 2", "Content", tags=["work"])
        self.db.add_note("Note 3", "Content", tags=["personal"])
        
        stats = self.db.get_statistics()
        
        self.assertEqual(stats['total_notes'], 3)
        self.assertEqual(stats['total_tags'], 2)
        self.assertEqual(stats['tag_counts']['work'], 2)
        self.assertEqual(stats['tag_counts']['personal'], 1)
    
    def test_export_notes(self):
        """Test exporting notes"""
        self.db.add_note("Test Title", "Test Content", tags=["test"])
        
        export = self.db.export_notes()
        
        self.assertIn("Test Title", export)
        self.assertIn("Test Content", export)
        self.assertIn("test", export)
    
    def test_tag_reuse(self):
        """Test tag reuse"""
        self.db.add_note("Note 1", "Content", tags=["shared_tag"])
        self.db.add_note("Note 2", "Content", tags=["shared_tag"])
        
        stats = self.db.get_statistics()
        self.assertEqual(stats['total_tags'], 1)
        self.assertEqual(stats['tag_counts']['shared_tag'], 2)
    
    def test_empty_database(self):
        """Test empty database"""
        notes = self.db.get_all_notes()
        self.assertEqual(len(notes), 0)
        
        stats = self.db.get_statistics()
        self.assertEqual(stats['total_notes'], 0)
        self.assertEqual(stats['total_tags'], 0)


if __name__ == '__main__':
    unittest.main()
