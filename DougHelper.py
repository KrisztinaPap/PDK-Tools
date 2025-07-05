import os
import re

DATETIME_FILENAME_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.mp4$", re.IGNORECASE)
GENERIC_JPG_PATTERN = re.compile(r".+\.jpg$", re.IGNORECASE)
TITLE_LINE_PATTERN = re.compile(r"^title:\s*(.+)$", re.IGNORECASE)
EPISODE_NUMBER_PATTERN = re.compile(r"(\d+)\.(mp4|jpg)$", re.IGNORECASE)

def get_series_title(series_path):
    index_file = os.path.join(series_path, "index.txt")
    if not os.path.exists(index_file):
        raise ValueError(f"Missing index.txt in {series_path}")

    with open(index_file, "r", encoding="utf-8") as f:
        for line in f:
            match = TITLE_LINE_PATTERN.match(line.strip())
            if match:
                return match.group(1)

    raise ValueError(f"No valid 'title: ...' line in {index_file}")

def get_next_episode_number(series_path):
    processed_path = os.path.join(series_path, "Processed")
    max_episode = 0

    if os.path.exists(processed_path):
        for filename in os.listdir(processed_path):
            match = re.search(r"(\d+)\.(mp4|jpg)$", filename, re.IGNORECASE)
            if match:
                episode = int(match.group(1))
                max_episode = max(max_episode, episode)

    return max_episode + 1

def rename_files_in_series(series_path):
    try:
        base_title = get_series_title(series_path)
    except ValueError as e:
        return

    processed_folder_path = os.path.join(series_path, "Processed")

    if not os.path.exists(processed_folder_path):
        try:
            os.makedirs(processed_folder_path)
        except OSError as e:
            return

    mp4_files_to_process = []
    jpg_files_to_process = []

    for filename in os.listdir(series_path):
        full_path = os.path.join(series_path, filename)

        if os.path.isfile(full_path):
            if DATETIME_FILENAME_PATTERN.match(filename):
                mp4_files_to_process.append(filename)
            elif GENERIC_JPG_PATTERN.match(filename):
                jpg_files_to_process.append(filename)

    if not mp4_files_to_process and not jpg_files_to_process:
        return
    elif len(mp4_files_to_process) != len(jpg_files_to_process):
        return

    mp4_files_to_process.sort()
    jpg_files_to_process.sort()

    next_episode = get_next_episode_number(series_path)


    for i in range(len(mp4_files_to_process)):
        mp4_filename = mp4_files_to_process[i]
        jpg_filename = jpg_files_to_process[i]

        old_mp4_path = os.path.join(series_path, mp4_filename)
        old_jpg_path = os.path.join(series_path, jpg_filename)

        new_mp4_name = f"{base_title} - Episode {next_episode}.mp4"
        new_mp4_path_in_processed = os.path.join(processed_folder_path, new_mp4_name)

        new_jpg_name = f"{base_title} - Episode {next_episode}.jpg"
        new_jpg_path_in_processed = os.path.join(processed_folder_path, new_jpg_name)

        try:
            os.rename(old_mp4_path, new_mp4_path_in_processed)
        except OSError as e:
            continue

        try:
            os.rename(old_jpg_path, new_jpg_path_in_processed)
        except OSError as e:
            continue

        next_episode += 1

def main():
    root_path = os.path.dirname(os.path.abspath(__file__))

    for game_name in os.listdir(root_path):
        game_path = os.path.join(root_path, game_name)
        if not os.path.isdir(game_path):
            continue
        for series_name in os.listdir(game_path):
            series_path = os.path.join(game_path, series_name)
            if os.path.isdir(series_path):
                rename_files_in_series(series_path)

if __name__ == "__main__":
    main()