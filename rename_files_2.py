import os
import re

generic_jpeg_pattern = re.compile(r"^(.+?) (\d+)\.jpeg$", re.IGNORECASE)
title_line_pattern = re.compile(r"^title:\s*(.+)$", re.IGNORECASE)
episode_number_pattern = re.compile(r"(\d+)\.(mp4|jpeg)$", re.IGNORECASE)

def get_series_title(series_path):
    index_file = os.path.join(series_path, "index.txt")
    if not os.path.exists(index_file):
        raise ValueError(f"Missing index.txt in {series_path}")
    with open(index_file, "r", encoding="utf-8") as f:
        for line in f:
            match = title_line_pattern.match(line.strip())
            if match:
                title = match.group(1)
                if not title.strip():
                    break
                return title
    raise ValueError(f"No valid 'title: ...' line in {index_file}")

def get_next_episode_number(series_path):
    processed_path = os.path.join(series_path, "Processed")
    max_episode = 0
    if os.path.exists(processed_path):
        for filename in os.listdir(processed_path):
            match = episode_number_pattern.search(filename)
            if match:
                episode = int(match.group(1))
                max_episode = max(max_episode, episode)
    return max_episode + 1

def find_jpeg_files(series_path):
    jpeg_files = []
    for filename in os.listdir(series_path):
        full_path = os.path.join(series_path, filename)
        if os.path.isfile(full_path):
            match = generic_jpeg_pattern.match(filename)
            if match:
                base, number = match.groups()
                jpeg_files.append((filename, int(number)))
    return jpeg_files

def create_processed_folder(series_path):
    processed_folder_path = os.path.join(series_path, "Processed")
    if not os.path.exists(processed_folder_path):
        try:
            os.makedirs(processed_folder_path)
        except OSError as e:
            print(f"Failed to create processed folder {processed_folder_path}: {e}.")
            return False
    return True

def rename_jpeg_files_in_series(series_path):
    try:
        base_title = get_series_title(series_path)
    except ValueError as e:
        print(f"Failed to get series title for {series_path}: {e}. Skipping series.")
        return
    jpeg_files = find_jpeg_files(series_path)
    if not jpeg_files:
        print(f"No JPEG files found to process in {series_path}. Skipping.")
        return
    create_processed_folder(series_path)
    jpeg_files.sort(key=lambda x: x[1])  # sort by the number in the filename
    next_episode = get_next_episode_number(series_path)
    processed_folder = os.path.join(series_path, "Processed")
    for filename, _ in jpeg_files:
        new_jpeg_name = f"{base_title} {next_episode}.jpeg"
        new_jpeg_path = os.path.join(processed_folder, new_jpeg_name)
        try:
            os.rename(os.path.join(series_path, filename), new_jpeg_path)
            print(f"Renamed {filename} to {new_jpeg_name}")
        except OSError as e:
            print(f"Failed to rename file {filename} in {series_path}: {e}. Skipping.")
            continue
        next_episode += 1

def main():
    root_path = os.path.dirname(os.path.abspath(__file__))
    for game in os.listdir(root_path):
        game_path = os.path.join(root_path, game)
        if not os.path.isdir(game_path):
            continue
        for series in os.listdir(game_path):
            series_path = os.path.join(game_path, series)
            if os.path.isdir(series_path):
                rename_jpeg_files_in_series(series_path)

if __name__ == "__main__":
    main()