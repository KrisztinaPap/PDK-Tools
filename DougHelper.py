import os
import re

DATETIME_FILENAME_PATTERN = re.compile(r".+\.mp4$", re.IGNORECASE)
GENERIC_JPG_PATTERN = re.compile(r".+\.jpg$", re.IGNORECASE)
TITLE_LINE_PATTERN = re.compile(r"^title:\s*(.+)$", re.IGNORECASE)
EPISODE_NUMBER_PATTERN = re.compile(r"(\d+)\.(mp4|jpg)$", re.IGNORECASE)
THUMBNAIL_NUMBER_PATTERN = re.compile(r".*\((\d+)\)\.jpg$", re.IGNORECASE)


def _numeric_sort_key(filename):
    """
    Custom key for sorting filenames with parenthetical numbers (e.g., 'file (1).jpg', 'file (10).jpg').
    Files without a number in parentheses are treated as '0' for sorting.
    """
    match = THUMBNAIL_NUMBER_PATTERN.match(filename)
    if match:
        return int(match.group(1))
    # If no number in parentheses, treat it as the "first" in sequence (value 0)
    return 0

def get_series_title(series_path):
    print(f"DEBUG: Entering get_series_title for path: {series_path}")
    index_file = os.path.join(series_path, "index.txt")
    if not os.path.exists(index_file):
        print(f"DEBUG: Missing index.txt in {series_path}. Raising ValueError.")
        raise ValueError(f"Missing index.txt in {series_path}")

    with open(index_file, "r", encoding="utf-8") as f:
        for line in f:
            match = TITLE_LINE_PATTERN.match(line.strip())
            if match:
                title = match.group(1)
                print(f"DEBUG: Found series title: '{title}' in {index_file}")
                return title

    print(f"DEBUG: No valid 'title: ...' line found in {index_file}. Raising ValueError.")
    raise ValueError(f"No valid 'title: ...' line in {index_file}")

def get_next_episode_number(series_path):
    print(f"DEBUG: Entering get_next_episode_number for path: {series_path}")
    processed_path = os.path.join(series_path, "Processed")
    max_episode = 0

    if os.path.exists(processed_path):
        print(f"DEBUG: 'Processed' folder exists at {processed_path}. Checking for existing episodes.")
        for filename in os.listdir(processed_path):
            match = re.search(r"(\d+)\.(mp4|jpg)$", filename, re.IGNORECASE)
            if match:
                episode = int(match.group(1))
                max_episode = max(max_episode, episode)
                print(f"DEBUG: Found episode number {episode} from file: {filename}. Current max_episode: {max_episode}")
    else:
        print(f"DEBUG: 'Processed' folder does not exist at {processed_path}.")

    print(f"DEBUG: Next episode number will be: {max_episode + 1}")
    return max_episode + 1

def rename_files_in_series(series_path):
    print(f"DEBUG: Entering rename_files_in_series for path: {series_path}")
    try:
        base_title = get_series_title(series_path)
        print(f"DEBUG: Successfully retrieved base title: '{base_title}'")
    except ValueError as e:
        print(f"DEBUG: Failed to get series title for {series_path}: {e}. Skipping series.")
        return

    processed_folder_path = os.path.join(series_path, "Processed")
    print(f"DEBUG: Processed folder path set to: {processed_folder_path}")

    if not os.path.exists(processed_folder_path):
        print(f"DEBUG: Processed folder does not exist. Attempting to create: {processed_folder_path}")
        try:
            os.makedirs(processed_folder_path)
            print(f"DEBUG: Successfully created processed folder: {processed_folder_path}")
        except OSError as e:
            print(f"DEBUG: Failed to create processed folder {processed_folder_path}: {e}. Skipping series.")
            return
    else:
        print(f"DEBUG: Processed folder already exists: {processed_folder_path}")

    mp4_files_to_process = []
    jpg_files_to_process = []
    print(f"DEBUG: Scanning files in {series_path} for MP4 and JPG files.")
    for filename in os.listdir(series_path):
        full_path = os.path.join(series_path, filename)

        if os.path.isfile(full_path):
            if DATETIME_FILENAME_PATTERN.match(filename):
                mp4_files_to_process.append(filename)
                print(f"DEBUG: Found MP4 file to process: {filename}")
            elif GENERIC_JPG_PATTERN.match(filename):
                jpg_files_to_process.append(filename)
                print(f"DEBUG: Found JPG file to process: {filename}")

    print(f"DEBUG: Found {len(mp4_files_to_process)} MP4 files and {len(jpg_files_to_process)} JPG files.")

    if not mp4_files_to_process and not jpg_files_to_process:
        print(f"DEBUG: No MP4 or JPG files found to process in {series_path}. Skipping.")
        return
    elif len(mp4_files_to_process) != len(jpg_files_to_process):
        print(f"DEBUG: Mismatch in number of MP4 ({len(mp4_files_to_process)}) and JPG ({len(jpg_files_to_process)}) files. Skipping series {series_path}.")
        return

    # Apply custom sorting for both MP4 and JPG files
    mp4_files_to_process.sort(key=_numeric_sort_key)
    jpg_files_to_process.sort(key=_numeric_sort_key)
    print("DEBUG: Files sorted using custom numeric key for correct sequence.")

    next_episode = get_next_episode_number(series_path)
    print(f"DEBUG: Starting episode numbering from: {next_episode}")


    for i in range(len(mp4_files_to_process)):
        mp4_filename = mp4_files_to_process[i]
        jpg_filename = jpg_files_to_process[i]

        old_mp4_path = os.path.join(series_path, mp4_filename)
        old_jpg_path = os.path.join(series_path, jpg_filename)

        new_mp4_name = f"{base_title} {next_episode}.mp4"
        new_mp4_path_in_processed = os.path.join(processed_folder_path, new_mp4_name)

        new_jpg_name = f"{base_title} {next_episode}.jpg"
        new_jpg_path_in_processed = os.path.join(processed_folder_path, new_jpg_name)

        print(f"DEBUG: Processing pair {i+1}/{len(mp4_files_to_process)}:")
        print(f"DEBUG: Renaming '{mp4_filename}' to '{new_mp4_name}'")
        try:
            os.rename(old_mp4_path, new_mp4_path_in_processed)
            print(f"DEBUG: Successfully renamed MP4: '{old_mp4_path}' to '{new_mp4_path_in_processed}'")
        except OSError as e:
            print(f"DEBUG: Failed to rename MP4 '{old_mp4_path}' to '{new_mp4_path_in_processed}': {e}. Skipping this pair.")
            continue

        print(f"DEBUG: Renaming '{jpg_filename}' to '{new_jpg_name}'")
        try:
            os.rename(old_jpg_path, new_jpg_path_in_processed)
            print(f"DEBUG: Successfully renamed JPG: '{old_jpg_path}' to '{new_jpg_path_in_processed}'")
        except OSError as e:
            print(f"DEBUG: Failed to rename JPG '{old_jpg_path}' to '{new_jpg_path_in_processed}': {e}. Skipping this pair.")
            continue

        next_episode += 1
    print(f"DEBUG: Finished processing files for series: {series_path}")

def main():
    print("DEBUG: Starting main function.")
    root_path = os.path.dirname(os.path.abspath(__file__))
    print(f"DEBUG: Root path set to: {root_path}")

    for game_name in os.listdir(root_path):
        game_path = os.path.join(root_path, game_name)
        print(f"DEBUG: Checking item in root_path: {game_path}")
        if not os.path.isdir(game_path):
            print(f"DEBUG: '{game_path}' is not a directory. Skipping.")
            continue
        print(f"DEBUG: '{game_path}' is a directory. Iterating its contents.")
        for series_name in os.listdir(game_path):
            series_path = os.path.join(game_path, series_name)
            print(f"DEBUG: Checking item in game_path: {series_path}")
            if os.path.isdir(series_path):
                print(f"DEBUG: '{series_path}' is a directory. Calling rename_files_in_series.")
                rename_files_in_series(series_path)
            else:
                print(f"DEBUG: '{series_path}' is not a directory. Skipping.")
    print("DEBUG: Main function finished.")

if __name__ == "__main__":
    main()