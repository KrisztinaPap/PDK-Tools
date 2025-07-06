# Content Series Renamer (`rename_files.py`)

## Overview

This Python script automates the renaming and organization of video recordings (`.mp4`) and their thumbnail images (`.jpeg`) for content series. It efficiently processes bulk recordings, ensures consistent naming, and organizes outputs for streamlined content management.

---

## Features

- **Automated Pair Renaming:** Pairs `.mp4` and `.jpeg` files, renaming them with the series title and sequential episode numbers.
- **Strict Pair Matching:** Only processes folders where the number of `.mp4` and `.jpeg` files match exactly. Skips folders otherwise.
- **Intelligent Sorting:** Uses custom sorting to correctly align videos and thumbnails, handling patterns like `Screenshot (1).jpeg` and date-named videos.
- **Episode Numbering:** Determines the next episode number by scanning the `Processed` folder for previously renamed files, incrementing from the highest found.
- **Folder Management:** Moves renamed files into a `Processed` subfolder within each series directory, keeping originals clean.
- **Hierarchical Scanning:** Recursively scans a root directory, traversing through game, then series directories, and processes every series folder found.
- **Title Extraction:** Reads the series title from an `index.txt` file (must include a line: `title: ...`). Skips folders if missing or malformed.

---

## How It Works

1. **Traversal:** Starting from the root directory (where the script is located), the script recursively searches for leaf directories (series folders).
2. **Validation:** In each series folder, checks for an `index.txt` file and matching counts of `.mp4` and `.jpeg` files.
3. **Sorting:** Sorts video and thumbnail files using a custom numeric and datetime-aware order to ensure proper pairing.
4. **Renaming:** Renames and moves each video and its paired thumbnail to the `Processed` folder, using the format:  
   `[Series Title] [Episode Number].mp4` and `[Series Title] [Episode Number].jpeg`
5. **Error Handling:** Provides debug output for missing titles, mismatched file counts, and I/O errors, skipping problematic folders.

---

## Folder Structure

```
/Your_Root_Content_Folder/
├── Game_Title/
│   └── Series_Name/
│       ├── index.txt
│       ├── [video and thumbnail files]
│       └── Processed/
└── rename_files.py
```

---

## Setup & Usage

1. **Clone the Repository**
    ```bash
    git clone https://github.com/KrisztinaPap/PDK-Tools.git
    cd PDK-Tools
    ```
2. **Organize Your Content:**  
   Place `rename_files.py` in the root of your content folder (above all games/series directories).
3. **Prepare `index.txt`:**  
   Each series folder must have an `index.txt` file with a line such as:
    ```
    title: My Awesome Series
    ```
4. **Run the Script**
    ```bash
    python rename_files.py
    ```

---

## Example: Before & After

**Before:**
```
/MyContent/
└── Game/
    └── Series/
        ├── index.txt
        ├── 2025-07-05 10-30-00.mp4
        ├── Screenshot (1).jpeg
```
**After:**
```
/MyContent/
└── Game/
    └── Series/
        ├── index.txt
        └── Processed/
            ├── My Awesome Series 1.mp4
            ├── My Awesome Series 1.jpeg
```

---

## Testing

- A complete test suite (`test_rename_files.py`) is included, using Python’s `unittest` framework.
- The tests cover:
    - Sorting and pairing logic
    - Title extraction and validation
    - Episode number generation
    - Handling of edge cases (e.g. missing files, mismatched pairs, empty or malformed `index.txt`)
    - Actual file renaming and movement in temporary directories
    - Main entrypoint’s recursive directory traversal
- Debug output is suppressed during tests for clarity.

Run all tests with:
```bash
python -m unittest test_rename_files.py
```

---

## Debugging

- The script prints `DEBUG` statements for real-time progress and troubleshooting.
- Skips folders with missing/malformed `index.txt`, mismatched file counts, or file errors.

---

## Contributing

Contributions, issues, and feature requests are welcome. Please open an issue or pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).