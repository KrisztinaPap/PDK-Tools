import unittest
import os
import shutil
import tempfile

from rename_files_2 import (
    get_series_title,
    get_next_episode_number,
    find_jpeg_files,
    rename_jpeg_files_in_series,
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
        files = find_jpeg_files(self.test_dir)
        self.assertEqual(sorted(files), [('foo 1.jpeg', 1), ('foo 2.jpeg', 2)])

    def test_rename_jpeg_files_in_series(self):
        structure = {
            'index.txt': 'title: TestShow',
            'foo 2.jpeg': '',
            'foo 1.jpeg': '',
            'Processed/TestShow 3.jpeg': '',
        }
        self.make_series_dir(structure)
        rename_jpeg_files_in_series(self.test_dir)
        processed = os.listdir(os.path.join(self.test_dir, 'Processed'))
        self.assertEqual(set(processed), {'TestShow 3.jpeg', 'TestShow 4.jpeg', 'TestShow 5.jpeg'})

    def test_missing_index_txt(self):
        # Should print error, not raise
        rename_jpeg_files_in_series(self.test_dir)

