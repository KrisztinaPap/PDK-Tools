import os
import re
from datetime import datetime

GENERIC_MP4_PATTERN = re.compile(r".+\.mp4$", re.IGNORECASE)
GENERIC_JPEG_PATTERN = re.compile(r".+\.jpeg$", re.IGNORECASE)
TITLE_LINE_PATTERN = re.compile(r"^title:\s*(.+)$", re.IGNORECASE)
EPISODE_NUMBER_PATTERN = re.compile(r"(\d+)\.(mp4|jpeg)$", re.IGNORECASE)
THUMBNAIL_NUMBER_PATTERN = re.compile(r".*\((\d+)\)\.jpeg$", re.IGNORECASE)
DATETIME_PATTERN = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2})")


def _numeric_sort_key(filename):

# This function is now only used for MP4s, not JPEGs
    match = DATETIME_PATTERN.search(filename)
    if match:
        try:
            dt = datetime.strptime(match.group(1), "%Y-%m-%d %H-%M-%S")
            return (0, dt, filename)
        except ValueError:
            pass
    return (1, filename)

# JPEG sorting helpers
def jpeg_sort_key_bracket(files):
    # Sort by base name (without bracketed number), then by bracketed number (no number first)
    def extract(file):
        m = re.match(r"^(.*?)(?: \((\d+)\))?\.jpeg$", file, re.IGNORECASE)
        if m:
            base = m.group(1).strip().lower()
            num = int(m.group(2)) if m.group(2) is not None else -1
            return (base, num)
        return (file.lower(), float('inf'))
    return sorted(files, key=extract)

def jpeg_sort_key_number(files):
    # Sort by the last number in the filename (before .jpeg)
    def extract(file):
        m = re.findall(r"(\d+)(?=\D*\.jpeg$)", file, re.IGNORECASE)
        num = int(m[-1]) if m else float('inf')
        return num
    return sorted(files, key=extract)

def get_series_title(series_path):
    index_file = os.path.join(series_path, "index.txt")
    if not os.path.exists(index_file):
        raise ValueError(f"Missing index.txt in {series_path}")

    with open(index_file, "r", encoding="utf-8") as f:
        for line in f:
            match = TITLE_LINE_PATTERN.match(line.strip())
            if match:
                title = match.group(1)
                if not title.strip():
                    break
                return title
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

def find_files_to_process(series_path):
    print(f"DEBUG: Entering find_files_to_process for path: {series_path}")
    mp4_files = []
    jpeg_files = []

    for filename in os.listdir(series_path):
        full_path = os.path.join(series_path, filename)
        if os.path.isfile(full_path):
            if GENERIC_MP4_PATTERN.match(filename):
                mp4_files.append(filename)
                print(f"DEBUG: Found MP4 file to process: {filename}")
            elif GENERIC_JPEG_PATTERN.match(filename):
                jpeg_files.append(filename)
                print(f"DEBUG: Found JPEG file to process: {filename}")

    print(f"DEBUG: Found {len(mp4_files)} MP4 files and {len(jpeg_files)} JPEG files.")
    return mp4_files, jpeg_files

def create_processed_folder(series_path):
    print(f"DEBUG: Entering create_processed_folder for path: {series_path}")
    processed_folder_path = os.path.join(series_path, "Processed")
    if not os.path.exists(processed_folder_path):
        print(f"DEBUG: Processed folder does not exist. Attempting to create: {processed_folder_path}")
        try:
            os.makedirs(processed_folder_path)
            print(f"DEBUG: Successfully created processed folder: {processed_folder_path}")
        except OSError as e:
            print(f"DEBUG: Failed to create processed folder {processed_folder_path}: {e}.")
            return False
    else:
        print(f"DEBUG: Processed folder already exists: {processed_folder_path}")
    return True

def rename_file_pair(mp4_filename, jpeg_filename, base_title, next_episode, processed_folder_path):
    print(f"DEBUG: Renaming file pair: {mp4_filename}, {jpeg_filename} with base title '{base_title}' and episode number {next_episode}")
    new_mp4_name = f"{base_title} {next_episode}.mp4"
    new_jpeg_name = f"{base_title} {next_episode}.jpeg"
    
    new_mp4_path = os.path.join(processed_folder_path, new_mp4_name)
    new_jpeg_path = os.path.join(processed_folder_path, new_jpeg_name)

    print(f"DEBUG: New MP4 path: {new_mp4_path}, New jpeg path: {new_jpeg_path}")
    return new_mp4_path, new_jpeg_path

def rename_files_in_series(series_path):
    print(f"DEBUG: Entering rename_files_in_series for path: {series_path}")
    try:
        base_title = get_series_title(series_path)
        print(f"DEBUG: Successfully retrieved base title: '{base_title}'")
    except ValueError as e:
        print(f"DEBUG: Failed to get series title for {series_path}: {e}. Skipping series.")
        return
    
    mp4_files, jpeg_files = find_files_to_process(series_path)

    if not mp4_files and not jpeg_files:
        print(f"DEBUG: No MP4 or jpeg files found to process in {series_path}. Skipping.")
        return
    elif len(mp4_files) != len(jpeg_files):
        print(f"DEBUG: Mismatch in number of MP4 ({len(mp4_files)}) and jpeg ({len(jpeg_files)}) files. Skipping series {series_path}.")
        return

    processed_folder = os.path.join(series_path, "Processed")
    create_processed_folder(series_path)

    # Sort MP4s as before
    mp4_files.sort(key=_numeric_sort_key)

    # Detect bracketed JPEGs in this series
    has_bracketed = any(re.match(r".*\(\d+\)\.jpeg$", f, re.IGNORECASE) for f in jpeg_files)
    print(f"DEBUG: JPEG bracketed detection: {has_bracketed}")
    if has_bracketed:
        jpeg_files = jpeg_sort_key_bracket(jpeg_files)
        print(f"DEBUG: JPEG files sorted using bracketed logic: {jpeg_files}")
    else:
        jpeg_files = jpeg_sort_key_number(jpeg_files)
        print(f"DEBUG: JPEG files sorted using number-at-end logic: {jpeg_files}")

    print("DEBUG: Files sorted using custom logic for correct sequence.")

    next_episode = get_next_episode_number(series_path)
    print(f"DEBUG: Starting episode numbering from: {next_episode}")

    for i in range(len(mp4_files)):
        mp4_filename = mp4_files[i]
        jpeg_filename = jpeg_files[i]

        new_mp4_path, new_jpeg_path = rename_file_pair(mp4_filename, jpeg_filename, base_title, next_episode, processed_folder)

        try:
            os.rename(os.path.join(series_path, mp4_filename), new_mp4_path)
            print(f"DEBUG: Successfully renamed MP4 file: {mp4_filename} to {new_mp4_path}")
            os.rename(os.path.join(series_path, jpeg_filename), new_jpeg_path)
            print(f"DEBUG: Successfully renamed jpeg file: {jpeg_filename} to {new_jpeg_path}")
        except OSError as e:
            print(f"DEBUG: Failed to rename files {mp4_filename} or {jpeg_filename} in {series_path}: {e}. Skipping this pair.")
            continue

        next_episode += 1

def loop_over_directories(series_path):
    print(f"DEBUG: Entering loop_over_directories for path: {series_path}")
    if not os.path.isdir(series_path):
        print(f"DEBUG: '{series_path}' is not a directory. Skipping.")
        return

    for item in os.listdir(series_path):
        if item == "Processed":
            print(f"DEBUG: Skipping 'Processed' folder at {os.path.join(series_path, item)}")
            continue
        item_path = os.path.join(series_path, item)
        print(f"DEBUG: Checking item: {item_path}")
        if os.path.isdir(item_path):
            subdirs = [d for d in os.listdir(item_path) if os.path.isdir(os.path.join(item_path, d)) and d != "Processed"]
            if subdirs:
                loop_over_directories(item_path)
            else:
                print(f"DEBUG: '{item_path}' is a series directory. Calling rename_files_in_series.")
                rename_files_in_series(item_path)
        else:
            print(f"DEBUG: '{item_path}' is not a directory. Skipping.")

def main():
    print("DEBUG: Starting main function.")
    root_path = os.path.dirname(os.path.abspath(__file__))
    print(f"DEBUG: Root path set to: {root_path}")

    loop_over_directories(root_path)
    
    print("DEBUG: Main function finished.")

if __name__ == "__main__":
    main()