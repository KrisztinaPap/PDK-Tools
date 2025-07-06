import unittest
import os
import shutil
from unittest.mock import patch, mock_open

# Import functions from your main script
# Assuming your main script is named 'rename_files.py'
from rename_files import (
    _numeric_sort_key,
    get_series_title,
    get_next_episode_number,
    rename_files_in_series,
    main,
    DATETIME_FILENAME_PATTERN,
    GENERIC_jpeg_PATTERN,
    TITLE_LINE_PATTERN,
    EPISODE_NUMBER_PATTERN,
    THUMBNAIL_NUMBER_PATTERN
)

class TestRenamingScript(unittest.TestCase):

    def setUp(self):
        """
        Set up a temporary directory structure for each test.
        """
        self.test_root = "test_root"
        os.makedirs(self.test_root, exist_ok=True)
        # Suppress print statements during tests for cleaner output
        # You can comment this out if you want to see the DEBUG prints during testing
        self.patcher_print = patch('builtins.print')
        self.mock_print = self.patcher_print.start()

    def tearDown(self):
        """
        Clean up the temporary directory structure after each test.
        """
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)
        self.patcher_print.stop()

    # --- Test Cases for Helper Functions ---

    def test_numeric_sort_key(self):
        """Test the custom numeric sorting key."""
        self.assertEqual(_numeric_sort_key("file.jpeg"), 0)
        self.assertEqual(_numeric_sort_key("file (1).jpeg"), 1)
        self.assertEqual(_numeric_sort_key("file (9).jpeg"), 9)
        self.assertEqual(_numeric_sort_key("file (10).jpeg"), 10)
        self.assertEqual(_numeric_sort_key("another file (100).jpeg"), 100)
        self.assertEqual(_numeric_sort_key("video.mp4"), 0) # Should not match jpeg pattern, so default to 0

    # --- Test Cases for get_series_title ---

    def test_get_series_title_success(self):
        """Test getting a series title from a valid index.txt."""
        series_path = os.path.join(self.test_root, "Game A", "Series X")
        os.makedirs(series_path, exist_ok=True)
        with open(os.path.join(series_path, "index.txt"), "w") as f:
            f.write("title: My Awesome Series\n")
            f.write("other_info: Some data")
        self.assertEqual(get_series_title(series_path), "My Awesome Series")

    def test_get_series_title_no_index_file(self):
        """Test getting series title when index.txt is missing."""
        series_path = os.path.join(self.test_root, "Game B", "Series Y")
        os.makedirs(series_path, exist_ok=True)
        with self.assertRaises(ValueError) as cm:
            get_series_title(series_path)
        self.assertIn("Missing index.txt", str(cm.exception))

    def test_get_series_title_no_title_line(self):
        """Test getting series title when index.txt exists but lacks 'title:' line."""
        series_path = os.path.join(self.test_root, "Game C", "Series Z")
        os.makedirs(series_path, exist_ok=True)
        with open(os.path.join(series_path, "index.txt"), "w") as f:
            f.write("description: This is a series.\n")
        with self.assertRaises(ValueError) as cm:
            get_series_title(series_path)
        self.assertIn("No valid 'title: ...' line", str(cm.exception))

    def test_get_series_title_empty_title(self):
        """Test getting series title with an empty title value (should raise error)."""
        series_path = os.path.join(self.test_root, "Game D", "Series Empty")
        os.makedirs(series_path, exist_ok=True)
        with open(os.path.join(series_path, "index.txt"), "w") as f:
            f.write("title: \n")
        with self.assertRaises(ValueError) as cm: # <--- CHANGE THIS
            get_series_title(series_path)
        self.assertIn("No valid 'title: ...' line", str(cm.exception))

    # --- Test Cases for get_next_episode_number ---

    def test_get_next_episode_number_no_processed_folder(self):
        """Test when no 'Processed' folder exists."""
        series_path = os.path.join(self.test_root, "Game A", "Series 1")
        os.makedirs(series_path, exist_ok=True)
        self.assertEqual(get_next_episode_number(series_path), 1)

    def test_get_next_episode_number_empty_processed_folder(self):
        """Test when 'Processed' folder exists but is empty."""
        series_path = os.path.join(self.test_root, "Game B", "Series 2")
        processed_path = os.path.join(series_path, "Processed")
        os.makedirs(processed_path, exist_ok=True)
        self.assertEqual(get_next_episode_number(series_path), 1)

    def test_get_next_episode_number_existing_episodes(self):
        """Test with existing episodes in 'Processed' folder."""
        series_path = os.path.join(self.test_root, "Game C", "Series 3")
        processed_path = os.path.join(series_path, "Processed")
        os.makedirs(processed_path, exist_ok=True)
        # Create some dummy processed files
        open(os.path.join(processed_path, "My Series 1.mp4"), 'a').close()
        open(os.path.join(processed_path, "My Series 5.jpeg"), 'a').close() # Max episode is 5
        open(os.path.join(processed_path, "My Series 3.mp4"), 'a').close()
        self.assertEqual(get_next_episode_number(series_path), 6)

    def test_get_next_episode_number_non_episode_files(self):
        """Test that non-episode files don't affect numbering."""
        series_path = os.path.join(self.test_root, "Game D", "Series 4")
        processed_path = os.path.join(series_path, "Processed")
        os.makedirs(processed_path, exist_ok=True)
        open(os.path.join(processed_path, "My Series 1.mp4"), 'a').close()
        open(os.path.join(processed_path, "log.txt"), 'a').close()
        open(os.path.join(processed_path, "temp_file.tmp"), 'a').close()
        self.assertEqual(get_next_episode_number(series_path), 2)

    # --- Test Cases for rename_files_in_series ---

    def test_rename_files_in_series_success_new_series(self):
        """Test renaming a new series (no Processed folder initially)."""
        series_path = os.path.join(self.test_root, "Game X", "New Series")
        os.makedirs(series_path, exist_ok=True)
        with open(os.path.join(series_path, "index.txt"), "w") as f:
            f.write("title: New Adventure\n")

        # Create dummy files
        open(os.path.join(series_path, "2025-01-01 10-00-00.mp4"), 'a').close()
        open(os.path.join(series_path, "Screenshot.jpeg"), 'a').close()
        open(os.path.join(series_path, "2025-01-01 10-30-00.mp4"), 'a').close()
        open(os.path.join(series_path, "Screenshot (1).jpeg"), 'a').close()
        open(os.path.join(series_path, "2025-01-01 11-00-00.mp4"), 'a').close()
        open(os.path.join(series_path, "Screenshot (2).jpeg"), 'a').close()

        rename_files_in_series(series_path)

        processed_path = os.path.join(series_path, "Processed")
        self.assertTrue(os.path.exists(processed_path))
        self.assertTrue(os.path.exists(os.path.join(processed_path, "New Adventure 1.mp4")))
        self.assertTrue(os.path.exists(os.path.join(processed_path, "New Adventure 1.jpeg")))
        self.assertTrue(os.path.exists(os.path.join(processed_path, "New Adventure 2.mp4")))
        self.assertTrue(os.path.exists(os.path.join(processed_path, "New Adventure 2.jpeg")))
        self.assertTrue(os.path.exists(os.path.join(processed_path, "New Adventure 3.mp4")))
        self.assertTrue(os.path.exists(os.path.join(processed_path, "New Adventure 3.jpeg")))

        # Check original files are gone
        self.assertFalse(os.path.exists(os.path.join(series_path, "2025-01-01 10-00-00.mp4")))
        self.assertFalse(os.path.exists(os.path.join(series_path, "Screenshot.jpeg")))

    def test_rename_files_in_series_existing_processed_files(self):
        """Test renaming when episodes already exist in Processed."""
        series_path = os.path.join(self.test_root, "Game Y", "Existing Series")
        os.makedirs(series_path, exist_ok=True)
        processed_path = os.path.join(series_path, "Processed")
        os.makedirs(processed_path, exist_ok=True)

        with open(os.path.join(series_path, "index.txt"), "w") as f:
            f.write("title: Old Journey\n")

        # Existing processed files
        open(os.path.join(processed_path, "Old Journey 1.mp4"), 'a').close()
        open(os.path.join(processed_path, "Old Journey 1.jpeg"), 'a').close()
        open(os.path.join(processed_path, "Old Journey 2.mp4"), 'a').close()
        open(os.path.join(processed_path, "Old Journey 2.jpeg"), 'a').close()

        # New files to process
        open(os.path.join(series_path, "2025-02-01 09-00-00.mp4"), 'a').close()
        open(os.path.join(series_path, "Thumb (0).jpeg"), 'a').close() # Treat as 0 for sorting
        open(os.path.join(series_path, "2025-02-01 09-30-00.mp4"), 'a').close()
        open(os.path.join(series_path, "Thumb (1).jpeg"), 'a').close()

        rename_files_in_series(series_path)

        self.assertTrue(os.path.exists(os.path.join(processed_path, "Old Journey 3.mp4")))
        self.assertTrue(os.path.exists(os.path.join(processed_path, "Old Journey 3.jpeg")))
        self.assertTrue(os.path.exists(os.path.join(processed_path, "Old Journey 4.mp4")))
        self.assertTrue(os.path.exists(os.path.join(processed_path, "Old Journey 4.jpeg")))
        self.assertEqual(len(os.listdir(processed_path)), 8) # 4 mp4s, 4 jpegs

    def test_rename_files_in_series_mismatched_file_counts(self):
        """Test when MP4 and jpeg file counts don't match."""
        series_path = os.path.join(self.test_root, "Game Z", "Mismatch")
        os.makedirs(series_path, exist_ok=True)
        with open(os.path.join(series_path, "index.txt"), "w") as f:
            f.write("title: Mismatched\n")

        open(os.path.join(series_path, "2025-03-01 10-00-00.mp4"), 'a').close()
        open(os.path.join(series_path, "Screenshot (1).jpeg"), 'a').close()
        open(os.path.join(series_path, "2025-03-01 10-30-00.mp4"), 'a').close() # One more MP4

        rename_files_in_series(series_path)

        # No files should be processed or moved
        self.assertFalse(os.path.exists(os.path.join(series_path, "Processed")))
        self.assertTrue(os.path.exists(os.path.join(series_path, "2025-03-01 10-00-00.mp4")))
        self.assertTrue(os.path.exists(os.path.join(series_path, "2025-03-01 10-30-00.mp4")))
        self.assertTrue(os.path.exists(os.path.join(series_path, "Screenshot (1).jpeg")))

    def test_rename_files_in_series_no_files_to_process(self):
        """Test when no MP4 or jpeg files are found."""
        series_path = os.path.join(self.test_root, "Game A", "Empty Series")
        os.makedirs(series_path, exist_ok=True)
        with open(os.path.join(series_path, "index.txt"), "w") as f:
            f.write("title: Empty Series\n")

        # No video or image files created
        rename_files_in_series(series_path)

        # No Processed folder should be created if no files need processing
        self.assertFalse(os.path.exists(os.path.join(series_path, "Processed")))

    def test_rename_files_in_series_missing_index_txt(self):
        """Test the behavior when index.txt is missing."""
        series_path = os.path.join(self.test_root, "Game B", "No Index")
        os.makedirs(series_path, exist_ok=True)
        # Don't create index.txt

        open(os.path.join(series_path, "2025-04-01 10-00-00.mp4"), 'a').close()
        open(os.path.join(series_path, "Screenshot (1).jpeg"), 'a').close()

        rename_files_in_series(series_path)

        # No files should be processed or moved
        self.assertFalse(os.path.exists(os.path.join(series_path, "Processed")))
        self.assertTrue(os.path.exists(os.path.join(series_path, "2025-04-01 10-00-00.mp4")))

    def test_rename_files_in_series_thumbnail_order(self):
        """Test that thumbnails are renamed in correct numerical order."""
        series_path = os.path.join(self.test_root, "Game Thumb", "Ordered Thumbnails")
        os.makedirs(series_path, exist_ok=True)
        with open(os.path.join(series_path, "index.txt"), "w") as f:
            f.write("title: My Thumb Test\n")

        # Create files in a challenging order for alphabetical sort
        open(os.path.join(series_path, "2025-05-01 10-00-00.mp4"), 'a').close()
        open(os.path.join(series_path, "2025-05-01 10-30-00.mp4"), 'a').close()
        open(os.path.join(series_path, "2025-05-01 11-00-00.mp4"), 'a').close()
        open(os.path.join(series_path, "2025-05-01 11-30-00.mp4"), 'a').close()
        open(os.path.join(series_path, "2025-05-01 12-00-00.mp4"), 'a').close()

        open(os.path.join(series_path, "Screenshot (10).jpeg"), 'a').close() # This comes before (2) alphabetically
        open(os.path.join(series_path, "Screenshot (2).jpeg"), 'a').close()
        open(os.path.join(series_path, "Screenshot (1).jpeg"), 'a').close()
        open(os.path.join(series_path, "Screenshot (3).jpeg"), 'a').close()
        open(os.path.join(series_path, "Screenshot.jpeg"), 'a').close() # This comes first (0)

        rename_files_in_series(series_path)

        processed_path = os.path.join(series_path, "Processed")
        self.assertTrue(os.path.exists(processed_path))

        # Check that files were renamed in the correct episode order
        self.assertTrue(os.path.exists(os.path.join(processed_path, "My Thumb Test 1.mp4")))
        self.assertTrue(os.path.exists(os.path.join(processed_path, "My Thumb Test 1.jpeg")))
        self.assertTrue(os.path.exists(os.path.join(processed_path, "My Thumb Test 2.mp4")))
        self.assertTrue(os.path.exists(os.path.join(processed_path, "My Thumb Test 2.jpeg")))
        self.assertTrue(os.path.exists(os.path.join(processed_path, "My Thumb Test 3.mp4")))
        self.assertTrue(os.path.exists(os.path.join(processed_path, "My Thumb Test 3.jpeg")))
        self.assertTrue(os.path.exists(os.path.join(processed_path, "My Thumb Test 4.mp4")))
        self.assertTrue(os.path.exists(os.path.join(processed_path, "My Thumb Test 4.jpeg")))
        self.assertTrue(os.path.exists(os.path.join(processed_path, "My Thumb Test 5.mp4")))
        self.assertTrue(os.path.exists(os.path.join(processed_path, "My Thumb Test 5.jpeg")))


    # --- Test Cases for main function ---

    @patch('rename_files.rename_files_in_series')
    def test_main_function_calls_rename(self, mock_rename):
        """Test that main iterates directories and calls rename_files_in_series."""
        # Create a mock directory structure
        game_a_path = os.path.join(self.test_root, "Game A")
        series_1_path = os.path.join(game_a_path, "Series 1")
        series_2_path = os.path.join(game_a_path, "Series 2")
        game_b_path = os.path.join(self.test_root, "Game B")
        series_3_path = os.path.join(game_b_path, "Series 3")

        os.makedirs(series_1_path, exist_ok=True)
        os.makedirs(series_2_path, exist_ok=True)
        os.makedirs(series_3_path, exist_ok=True)
        open(os.path.join(game_a_path, "not_a_dir.txt"), 'a').close() # Should be skipped

        # Patch os.path.dirname and os.path.abspath to point to our test_root
        with patch('os.path.dirname', return_value=self.test_root), \
             patch('os.path.abspath', return_value=os.path.join(self.test_root, "rename_files.py")):
            main()

            # Verify rename_files_in_series was called for each series directory
            expected_calls = sorted([
                (series_1_path,),
                (series_2_path,),
                (series_3_path,),
            ])
            actual_calls = sorted([call.args for call in mock_rename.call_args_list])

            self.assertEqual(len(actual_calls), 3) # Ensure it was called 3 times
            self.assertListEqual(actual_calls, expected_calls) # Ensure with correct paths

    @patch('rename_files.rename_files_in_series')
    def test_main_function_skips_non_directories(self, mock_rename):
        """Test that main skips non-directory items."""
        game_path = os.path.join(self.test_root, "SingleGame")
        os.makedirs(game_path, exist_ok=True)
        open(os.path.join(game_path, "config.txt"), 'a').close() # This should be skipped
        series_path = os.path.join(game_path, "ActualSeries")
        os.makedirs(series_path, exist_ok=True)


        with patch('os.path.dirname', return_value=self.test_root), \
             patch('os.path.abspath', return_value=os.path.join(self.test_root, "rename_files.py")):
            main()
            mock_rename.assert_called_once_with(series_path)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)