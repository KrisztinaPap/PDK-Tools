# Content Series Renamer
Automate the renaming and organization of video recordings (.mp4) and their thumbnail images (.jpeg) for your content series. This repo contains two Python applications—`rename_files.py` (original) and `rename_files_2.py` (improved)—plus a test suite for each.

## Features
- Automated Pair Renaming: Pairs `.mp4` and `.jpeg` files, renaming them with the series title and sequential episode numbers.
- Strict Pair Matching: Only processes folders where the number of `.mp4` and `.jpeg` files match.
- Intelligent Sorting: Handles both bracketed (e.g., `Screenshot (1).jpeg`) and number-at-end (e.g., `foo 2.jpeg`) thumbnail naming conventions.
- Episode Numbering: Determines the next episode number by scanning the `Processed` folder for previously renamed files.
- Folder Management: Moves renamed files into a `Processed` subfolder within each series directory.
- Recursive Scanning: Recursively processes all series folders under your content root.
- Title Extraction: Reads the series title from an `index.txt` file (`title: ...` required).

## How It Works
1. Traversal: Recursively scans for series folders (leaf directories).
2. Validation: Checks for `index.txt` and matching counts of `.mp4` and `.jpeg` files.
3. Sorting: Sorts files using custom logic for correct pairing.
4. Renaming: Renames and moves each pair to the `Processed` folder as `[Series Title] [Episode Number].mp4` and `.jpeg`.
5. Error Handling: Skips folders with missing/malformed `index.txt`, mismatched file counts, or file errors, with debug output.

## Folder Structure

```
/Your_Root_Content_Folder/
├── Game_Title/
│   └── Series_Name/
│       ├── index.txt
│       ├── [video and thumbnail files]
│       └── Processed/
├── rename_files.py
├── rename_files_2.py
├── test_rename_files.py
└── test_rename_files_2.py
```

## Setup & Usage
1. Clone the Repository:

```
git clone https://github.com/KrisztinaPap/PDK-Tools.git
cd PDK-Tools
```

2. Organize Your Content:
Place the script in your content root. Each series folder must have an `index.txt` with a line like:
`title: My Awesome Series`

3. Run the Script:

```
python rename_files_2.py
```

(Or use `rename_files.py` for the original version.)

## Example
### Before:

```
/MyContent/
└── Game/
    └── Series/
        ├── index.txt
        ├── 2025-07-05 10-30-00.mp4
        ├── Screenshot (1).jpeg
```

### After:

```
/MyContent/
└── Game/
    └── Series/
        ├── index.txt
        └── Processed/
            ├── My Awesome Series 1.mp4
            ├── My Awesome Series 1.jpeg
```

## Testing
- Full test suites for both versions using Python’s `unittest`.
- Covers sorting, pairing, title extraction, episode numbering, edge cases, and file operations.
- Run all tests with:

```
python -m unittest test_rename_files.py
python -m unittest test_rename_files_2.py
```


## Debugging
- Prints `DEBUG` statements for progress and troubleshooting.
- Skips problematic folders gracefully.

## Contributing
This is a personal project and I am not seeking external contributions at this time. Thanks for your interest!

## License
MIT License