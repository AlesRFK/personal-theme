# Icon Folders Automatization

### Overview
This Python script is designed to manage and organize folders tree structure by creating custom `.ini` files for icon customization. It hides and unhides `.ini` and `_icon.ico` files while respecting the folder depth and a predefined ignore list.

### Features
- **Unhide and Hide Files**: The script unhides `.ini` and `_icon.ico` files before processing and hides them back after completing the task.
- **Custom Icons**: Automatically creates a `desktop.ini` file for each folder that contains an `_icon.ico` file.
- **Depth Control**: Processes files and folders up to a specific depth level.
- **Folder and File Exclusion**: Allows excluding specific folders and files based on custom patterns.

### Requirements
- Python 3.x
- `colorama` library (for colored output)
- Access to a Windows machine (since the script uses Windows-specific commands like `attrib`)

### Installation
1. Clone this repository or download the script.
2. Install the required dependencies:
```bash
pip install colorama
```

### Usage
```bash
python custom_icon_folders.py
```

### License
*This project is licensed under the MIT License*
*Yes I do...*