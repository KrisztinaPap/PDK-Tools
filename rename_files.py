import os
import re

DATETIME_FILENAME_PATTERN = re.compile(r".+\.mp4$", re.IGNORECASE)
GENERIC_jpeg_PATTERN = re.compile(r".+\.jpeg$", re.IGNORECASE)
TITLE_LINE_PATTERN = re.compile(r"^title:\s*(.+)$", re.IGNORECASE)
EPISODE_NUMBER_PATTERN = re.compile(r"(\d+)\.(mp4|jpeg)$", re.IGNORECASE)
THUMBNAIL_NUMBER_PATTERN = re.compile(r".*\((\d+)\)\.jpeg$", re.IGNORECASE)


def _numeric_sort_key(filename):
    """
    Custom key for sorting filenames with parenthetical numbers (e.g., 'file (1).jpeg', 'file (10).jpeg').
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
            match = re.search(r"(\d+)\.(mp4|jpeg)$", filename, re.IGNORECASE)
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

    # --- THIS BLOCK WAS MOVED FROM HERE ---
    # processed_folder_path = os.path.join(series_path, "Processed")
    # print(f"DEBUG: Processed folder path set to: {processed_folder_path}")
    # if not os.path.exists(processed_folder_path):
    #     print(f"DEBUG: Processed folder does not exist. Attempting to create: {processed_folder_path}")
    #     try:
    #         os.makedirs(processed_folder_path)
    #         print(f"DEBUG: Successfully created processed folder: {processed_folder_path}")
    #     except OSError as e:
    #         print(f"DEBUG: Failed to create processed folder {processed_folder_path}: {e}. Skipping series.")
    #         return
    # else:
    #     print(f"DEBUG: Processed folder already exists: {processed_folder_path}")
    # --- END OF MOVED BLOCK COMMENT ---

    mp4_files_to_process = []
    jpeg_files_to_process = []
    print(f"DEBUG: Scanning files in {series_path} for MP4 and jpeg files.")
    for filename in os.listdir(series_path):
        full_path = os.path.join(series_path, filename)

        if os.path.isfile(full_path):
            if DATETIME_FILENAME_PATTERN.match(filename):
                mp4_files_to_process.append(filename)
                print(f"DEBUG: Found MP4 file to process: {filename}")
            elif GENERIC_jpeg_PATTERN.match(filename):
                jpeg_files_to_process.append(filename)
                print(f"DEBUG: Found jpeg file to process: {filename}")

    print(f"DEBUG: Found {len(mp4_files_to_process)} MP4 files and {len(jpeg_files_to_process)} jpeg files.")

    if not mp4_files_to_process and not jpeg_files_to_process:
        print(f"DEBUG: No MP4 or jpeg files found to process in {series_path}. Skipping.")
        return
    elif len(mp4_files_to_process) != len(jpeg_files_to_process):
        print(f"DEBUG: Mismatch in number of MP4 ({len(mp4_files_to_process)}) and jpeg ({len(jpeg_files_to_process)}) files. Skipping series {series_path}.")
        return

    # --- NEW, CORRECT LOCATION FOR PROCESSED FOLDER CREATION ---
    # The 'Processed' folder should only be created if we have files to process
    # and they match in count.
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
    # --- END NEW LOCATION ---

    # Apply custom sorting for both MP4 and jpeg files
    mp4_files_to_process.sort(key=_numeric_sort_key)
    jpeg_files_to_process.sort(key=_numeric_sort_key)
    print("DEBUG: Files sorted using custom numeric key for correct sequence.")

    next_episode = get_next_episode_number(series_path)
    print(f"DEBUG: Starting episode numbering from: {next_episode}")


    for i in range(len(mp4_files_to_process)):
        mp4_filename = mp4_files_to_process[i]
        jpeg_filename = jpeg_files_to_process[i]

        old_mp4_path = os.path.join(series_path, mp4_filename)
        old_jpeg_path = os.path.join(series_path, jpeg_filename)

        new_mp4_name = f"{base_title} {next_episode}.mp4"
        new_mp4_path_in_processed = os.path.join(processed_folder_path, new_mp4_name)

        new_jpeg_name = f"{base_title} {next_episode}.jpeg"
        new_jpeg_path_in_processed = os.path.join(processed_folder_path, new_jpeg_name)

        print(f"DEBUG: Processing pair {i+1}/{len(mp4_files_to_process)}:")
        print(f"DEBUG: Renaming '{mp4_filename}' to '{new_mp4_name}'")
        try:
            os.rename(old_mp4_path, new_mp4_path_in_processed)
            print(f"DEBUG: Successfully renamed MP4: '{old_mp4_path}' to '{new_mp4_path_in_processed}'")
        except OSError as e:
            print(f"DEBUG: Failed to rename MP4 '{old_mp4_path}' to '{new_mp4_path_in_processed}': {e}. Skipping this pair.")
            continue

        print(f"DEBUG: Renaming '{jpeg_filename}' to '{new_jpeg_name}'")
        try:
            os.rename(old_jpeg_path, new_jpeg_path_in_processed)
            print(f"DEBUG: Successfully renamed jpeg: '{old_jpeg_path}' to '{new_jpeg_path_in_processed}'")
        except OSError as e:
            print(f"DEBUG: Failed to rename jpeg '{old_jpeg_path}' to '{new_jpeg_path_in_processed}': {e}. Skipping this pair.")
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