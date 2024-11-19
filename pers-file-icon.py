import os
import fnmatch
import tkinter as tk
from tkinter import filedialog
import sys
import subprocess
from colorama import Fore, Back, Style, init

# Initialize colorama for cross-platform compatibility
init(autoreset=True)

# Hardcoded ignore list
IGNORE_FOLDERS = ["*/Temp/*", "*.git*", "*/Theme/*", "*_*"]  # Wildcard patterns for folders to ignore
IGNORE_FILES = []  # Wildcard patterns for files to ignore
FOLDER_DEPTH = 5  # Maximum depth for processing folders

def print_colored(text, color_code):
    """Utility function to print colored text"""
    print(f"{color_code}{text}{Style.RESET_ALL}")

def hide_file(file_path):
    """Hide the specified file using the 'attrib' command"""
    try:
        subprocess.run(['attrib', '+h', file_path], check=True)
        return 1  # Return 1 for hidden file
    except subprocess.CalledProcessError:
        return 0  # Return 0 if error hiding file

def unhide_file(file_path):
    """Unhide the specified file using the 'attrib' command"""
    try:
        subprocess.run(['attrib', '-h', file_path], check=True)
        return 1  # Return 1 for unhidden file
    except subprocess.CalledProcessError:
        return 0  # Return 0 if error unhiding file

def process_folder(directory, depth, ignore_folders, ignore_files, folder_depth):
    """Process the directory tree and create .ini files for icons"""
    if depth > folder_depth:
        return 0, [], 0  # Skip processing beyond the specified depth
    
    total_created = 0
    folder_structure = []  # To store folder structure for final output
    total_hidden_files = 0
    
    for root, dirs, files in os.walk(directory):
        current_depth = root[len(directory):].count(os.sep)
        
        # Skip folders based on the ignore list using fnmatch for matching folder patterns
        relative_folder = os.path.relpath(root, directory)
        if any(fnmatch.fnmatch(relative_folder, pattern) for pattern in ignore_folders):
            dirs[:] = []  # Prevent walking into this folder
            continue
        
        # Remove ignored folders and files
        dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(os.path.join(root, d), pattern) for pattern in ignore_folders)]
        files = [f for f in files if not any(fnmatch.fnmatch(os.path.join(root, f), pattern) for pattern in ignore_files)]

        # Only process directories within the allowed depth
        if current_depth <= folder_depth:
            # Check for any icon matching *_icon.ico
            matching_icons = [f for f in files if fnmatch.fnmatch(f, "*_icon.ico")]
            if matching_icons:
                indent = " " * (2 * current_depth)  # Indentation based on folder depth
                for icon in matching_icons:
                    folder_structure.append(f"{indent}{current_depth} {os.path.basename(root)} - {Fore.GREEN}{icon}")
                    # Create .ini file for each found icon
                    ini_path = os.path.join(root, "desktop.ini")
                    if not os.path.exists(ini_path):
                        total_created += 1
                        try:
                            with open(ini_path, 'w', encoding='utf-8') as ini_file:
                                ini_file.write(f"[.ShellClassInfo]\n")
                                ini_file.write(f"IconResource=.{os.sep}{icon},0\n")
                                ini_file.write(f"[ViewState]\nMode=\nVid=\nFolderType=Generic\n")
                        except PermissionError:
                            print_colored(f"Error creating desktop.ini for {root}: Permission denied", Fore.RED)  # Red
                        # After creating the .ini file, hide it
                        hide_file(ini_path)

            # Hide existing _icon.ico files
            for icon in matching_icons:
                icon_path = os.path.join(root, icon)
                total_hidden_files += hide_file(icon_path)

    return total_created, folder_structure, total_hidden_files

def main():
    # Set directory to process
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory(title="Select Folder")
    
    if not directory:
        print_colored("No directory selected, exiting...", Fore.RED)
        sys.exit(1)
    
    # Author info and initial empty line
    print("\n" + Fore.CYAN + "Author: @AlesRFK - Custom Icon Folders Script")
    print("\n----------------------------------------")

    print(f"Selected folder: {directory}")
    print(f"Using hardcoded ignore settings:")
    print(f"  Ignore folders: {IGNORE_FOLDERS}")
    print(f"  Ignore files: {IGNORE_FILES}")
    print(f"  Folder depth: {FOLDER_DEPTH}")

    # Horizontal line before the tree
    print("\n----------------------------------------")

    # Unhide existing .ini and _icon.ico files before starting
    total_unhidden_files = 0
    print_colored("Unhiding .ini and _icon.ico files...", Fore.GREEN)
    for root, dirs, files in os.walk(directory):
        current_depth = root[len(directory):].count(os.sep)
        # Unhide only if within the allowed folder depth
        if current_depth <= FOLDER_DEPTH:
            for file in files:
                if file.endswith(".ini") or file.endswith("_icon.ico"):
                    total_unhidden_files += unhide_file(os.path.join(root, file))

    # Process the folder tree
    total_created, folder_structure, total_hidden_files = process_folder(directory, 0, IGNORE_FOLDERS, IGNORE_FILES, FOLDER_DEPTH)

    # Print processed folder structure
    for folder in folder_structure:
        print(folder)

    # Footer section with total statistics
    print("\n----------------------------------------")
    print_colored(f"Total folders processed: {total_created}", Fore.BLUE)  # Blue
    print_colored(f"Total desktop.ini created: {total_created}", Fore.BLUE)  # Blue
    print_colored(f"Total hidden files processed: {total_hidden_files}", Fore.BLUE)  # Blue
    print_colored(f"Total unhidden files: {total_unhidden_files}", Fore.GREEN)  # Green

    # Hide created .ini and _icon.ico files at the end
    total_hidden_at_end = 0
    print_colored("Hiding created .ini and _icon.ico files...", Fore.RED)
    for root, dirs, files in os.walk(directory):
        current_depth = root[len(directory):].count(os.sep)
        # Hide only if within the allowed folder depth
        if current_depth <= FOLDER_DEPTH:
            for file in files:
                if file.endswith(".ini") or file.endswith("_icon.ico"):
                    total_hidden_at_end += hide_file(os.path.join(root, file))

    # Clearing Icon Cache: Remove iconcache files from the user profile
    icon_cache_dir = os.path.join(os.getenv('USERPROFILE'), 'AppData', 'Local', 'Microsoft', 'Windows', 'Explorer')
    deleted_files = 0
    try:
        for file in os.listdir(icon_cache_dir):
            if 'iconcache' in file.lower():
                file_path = os.path.join(icon_cache_dir, file)
                os.remove(file_path)
                deleted_files += 1
        print_colored(f"Deleted {deleted_files} icon cache files.", Fore.GREEN)  # Green
    except Exception as e:
        print_colored(f"Error clearing icon cache: {e}", Fore.RED)  # Red

    # Footer with hiding notification
    print_colored(f"Total hidden files after process: {total_hidden_at_end}", Fore.RED)

if __name__ == "__main__":
    main()
