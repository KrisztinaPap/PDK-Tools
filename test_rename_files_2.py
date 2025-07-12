import unittest
import os
import shutil
import tempfile

from rename_files_2 import (
    get_series_title,
    get_next_episode_number,
    find_files_to_process,
    rename_files_in_series,
)

class TestRenameFiles(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def make_series_dir(self, structure):
        for rel_path, content in structure.items():
            abs_path = os.path.join(self.test_dir, rel_path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(content)
        return self.test_dir

    def test_get_series_title(self):
        structure = {'index.txt': 'title: My Series'}
        self.make_series_dir(structure)
        self.assertEqual(get_series_title(self.test_dir), 'My Series')

    def test_get_next_episode_number(self):
        structure = {
            'Processed/Title 1.jpeg': '',
            'Processed/Title 2.jpeg': '',
            'Processed/Title 5.jpeg': '',
        }
        self.make_series_dir(structure)
        self.assertEqual(get_next_episode_number(self.test_dir), 6)

    def test_find_jpeg_files(self):
        structure = {
            'foo 1.jpeg': '',
            'foo 2.jpeg': '',
            'bar.txt': '',
        }
        self.make_series_dir(structure)
        mp4_files, jpeg_files = find_files_to_process(self.test_dir)
        self.assertEqual(sorted(jpeg_files), ['foo 1.jpeg', 'foo 2.jpeg'])

    def test_rename_jpeg_files_in_series(self):
        structure = {
            'index.txt': 'title: TestShow',
            'foo 2.jpeg': '',
            'foo 1.jpeg': '',
            'Processed/TestShow 3.jpeg': '',
        }
        self.make_series_dir(structure)
        # Create dummy mp4 files to match the number of jpeg files
        with open(os.path.join(self.test_dir, 'foo 1.mp4'), 'w') as f:
            f.write('')
        with open(os.path.join(self.test_dir, 'foo 2.mp4'), 'w') as f:
            f.write('')
        rename_files_in_series(self.test_dir)
        processed = os.listdir(os.path.join(self.test_dir, 'Processed'))
        # Should contain the original and two new renamed pairs
        self.assertIn('TestShow 3.jpeg', processed)
        self.assertIn('TestShow 4.jpeg', processed)
        self.assertIn('TestShow 5.jpeg', processed)
        self.assertIn('TestShow 4.mp4', processed)
        self.assertIn('TestShow 5.mp4', processed)

    def test_missing_index_txt(self):
        # Should print error, not raise
        # Create dummy mp4 and jpeg files
        with open(os.path.join(self.test_dir, 'foo 1.mp4'), 'w') as f:
            f.write('')
        with open(os.path.join(self.test_dir, 'foo 1.jpeg'), 'w') as f:
            f.write('')
        # Should not raise, just print error
        rename_files_in_series(self.test_dir)

