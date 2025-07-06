# rename_files.py - Content Series Renamer

## Overview

This Python script is designed to automate the tedious process of renaming video recordings (.mp4) and their corresponding thumbnail images (.jpeg) for content series. It was specifically developed for a content creator who faced the daily challenge of manually renaming a dozen or more files, a time-consuming task that significantly impacted their workflow.

**This script marks the crucial first step in automating the content creator's entire post-recording workflow.** Due to limited free time, this project is being developed in manageable chunks, focusing initially on solving the most pressing bottleneck: file organization and consistent naming.

By leveraging a structured folder system and an `index.txt` file, this script intelligently renames and organizes files into a "Processed" subdirectory, ensuring consistent naming conventions and correct sequential numbering for each episode in a series.

## The Problem It Solves

Imagine recording 8 hour streams, as 30-minute clips, 5 days a week. That's 8 x 2 x 5 = 80 clips per week. Each file comes with a generic, date-based filename (e.g., `2025-07-05 18-00-00.mp4`, `Screenshot (1).jpeg`). You also generate a thumbnail with the unique episode number for each clip. Updating the one number is fairly quick, but you still need to rename each thumbnail file either when saving, or afterwards. Manually renaming all these files to `[Series Title] [Episode Number].mp4` and `[Series Title] [Episode Number].jpeg` is incredibly repetitive and prone to errors. This script eliminates that manual effort, freeing up valuable time for content creation.

## Features

* **Automated Renaming:** Renames `.mp4` video files and `.jpeg` thumbnail files based on a series title and sequential episode numbers.
* **Intelligent Episode Numbering:** Automatically determines the next available episode number by scanning already processed files.
* **Thumbnail Sequence Correction:** Handles common naming patterns for thumbnails (e.g., `Screenshot.jpeg`, `Screenshot (1).jpeg`, `Screenshot (10).jpeg`) to ensure they are processed and renamed in the correct numerical order.
* **Structured Folder Management:** Creates a `Processed` subdirectory within each series folder to move and store the newly renamed files, keeping your original recording directory clean.
* **Hierarchical Scanning:** Scans through a root directory, then game-specific subdirectories, and finally series-specific subdirectories to find content to process.
* **`index.txt` Driven:** Uses a simple `index.txt` file within each series folder to retrieve the series title.

## How It Works

The script operates by looking for a specific directory structure:

```
/Your_Root_Content_Folder/
├── Game_Title_1/
│   ├── Series_Name_A/
│   │   ├── index.txt
│   │   ├── Your_Video_File_1.mp4
│   │   ├── Your_Thumbnail_1.jpeg
│   │   └── Your_Video_File_2.mp4
│   │   └── Your_Thumbnail_2.jpeg
│   └── Series_Name_B/
│       ├── index.txt
│       └── ...
├── Game_Title_2/
│   └── Series_Name_C/
│       ├── index.txt
│       └── ...
└── rename_script.py (this script)
```

For each `Series_Name` folder, the script performs the following steps:

1.  **Reads Series Title:** It looks for an `index.txt` file inside the series folder. This file must contain a line like `title: Your Series Title`.
2.  **Determines Next Episode Number:** It checks for a `Processed` subfolder. If found, it scans existing `.mp4` and `.jpeg` files within `Processed` to find the highest episode number used, then increments it for the new files.
3.  **Identifies Files to Process:** It scans the current series folder for `.mp4` video files (matching a typical datetime pattern) and `.jpeg` thumbnail files (matching a generic pattern, including those with `(number)` suffixes).
4.  **Sorts Files Correctly:** Crucially, it uses a custom sorting logic to ensure that thumbnails like `Screenshot.jpeg`, `Screenshot (1).jpeg`, `Screenshot (2).jpeg`, and `Screenshot (10).jpeg` are sorted numerically (0, 1, 2, 10) rather than alphabetically.
5.  **Renames and Moves:** For each matching pair of `.mp4` and `.jpeg` files, it renames them to `[Series Title] [Next Episode Number].mp4` and `[Series Title] [Next Episode Number].jpeg` respectively, and then moves them into the `Processed` folder.

## Setup and Usage

1.  **Clone the Repository:**

    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
    ```

2.  **Place the Script:** Place `rename_script.py` (or whatever you name your Python file) in the root directory of your content structure. This is the parent folder that contains your `Game_Title` folders.

    ```
    /My Content/
    ├── Game A/
    │   └── Series 1/
    ├── Game B/
    │   └── Series 2/
    └── rename_script.py  <-- Place it here
    ```

3.  **Create `index.txt` Files:** In each series folder (e.g., `Game A/Series 1/`), create an `index.txt` file with the series title.

    Example `index.txt`:

    ```
    title: My Awesome Game Series
    # You can add other notes here if you like, but only the 'title:' line is used.
    ```

4.  **Run the Script:**

    Navigate to the root content folder in your terminal and run the script:

    ```bash
    python rename_script.py
    ```


### Example Folder Structure Before Running

```
/MyContent/
├── Elder Scrolls Online/
│   ├── Dungeon Runs/
│   │   ├── index.txt (content: title: ESO Dungeon Runs)
│   │   ├── 2025-07-05 10-30-00.mp4
│   │   ├── eso_thumbnail (1).jpeg
│   │   ├── 2025-07-05 11-00-00.mp4
│   │   ├── eso_thumbnail (2).jpeg
│   │   ├── 2025-07-05 11-30-00.mp4
│   │   └── eso_thumbnail (3).jpeg
│   └── Quests/
│       ├── index.txt (content: title: ESO Quests)
│       └── ...
└── rename_script.py
```


### Example Folder Structure After Running (for `Dungeon Runs`)

```
/MyContent/
├── Elder Scrolls Online/
│   ├── Dungeon Runs/
│   │   ├── index.txt
│   │   └── Processed/
│   │       ├── ESO Dungeon Runs 1.mp4
│   │       ├── ESO Dungeon Runs 1.jpeg
│   │       ├── ESO Dungeon Runs 2.mp4
│   │       ├── ESO Dungeon Runs 2.jpeg
│   │       ├── ESO Dungeon Runs 3.mp4
│   │       └── ESO Dungeon Runs 3.jpeg
│   └── Quests/
│       ├── index.txt
│       └── ...
└── rename_script.py
```

## Test Coverage

This project includes a robust test suite using Python's `unittest` framework to ensure reliability and prevent regressions. It covers:

- **Core Functions:** Validating series title extraction and next episode number generation.

- **File Handling:** Ensuring correct renaming, movement to the "Processed" folder, and proper handling of file counts (e.g., mismatched pairs, no files).

- **Edge Cases:** Verifying behavior with missing `index.txt` files, empty processed folders, and challenging thumbnail naming patterns (e.g., numeric sorting).


## Debugging

The script includes extensive `DEBUG` print statements that will output to your terminal as it runs. These messages provide real-time feedback on what the script is doing, which files it's finding, and any issues it encounters (like missing `index.txt` files or mismatched file counts). This is invaluable for understanding its behavior and troubleshooting problems.


## Contributions

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request.


## License

This project is open-source and available under the [MIT License](LICENSE).