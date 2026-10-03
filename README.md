# 🔍 -AI-GENERATED-DuplicateDestroyer

A GUI-based desktop application designed to find duplicate files across two different locations. The system detects exact matches based on byte size and a hashing algorithm (MD5) applied to the file content. Equipped with a filter to skip hidden files and the ability to dynamically read .gitignore rules, it ensures an efficient scanning process.

# ✨ Features

- Accurate Matching (MD5 Hashing): Compares files based solely on their content, ignoring differences in filenames or creation/modification timestamps.
- Grouping: Groups findings based on file paths (folder structures).
- Developer-Friendly (Gitignore Parser): Includes built-in options to skip hidden files/folders (such as .git or .env) and automatically adheres to .gitignore rules (like node_modules) without relying on third-party libraries.
- Bulk Actions: Allows you to select multiple files at once and permanently delete them from their locations directly within the application.
- No Complex Installation: Relies entirely on the Python Standard Library; no `pip install` commands are required.

# 🛠️ Prerequisites

- Operating System: Windows, macOS, or Linux.
- Python is installed on your system. (Can be downloaded from python.org).

# 🚀 How to Run the Program

- Download or copy the [`DuplicateDestroyer.py`](DuplicateDestroyer.py) program code to your computer.
- Open Terminal (Linux/macOS) or Command Prompt / PowerShell (Windows).
- Navigate to the folder where you saved the program code (e.g., C:\Users\Name\Downloads).

```bash
cd C:\Users\Name\Downloads
```

- Run the following command:

```bash
python DuplicateDestroyer.py

# Note: If you are using macOS/Linux, you might need to type python3
python3 DuplicateDestroyer.py
```

- The application interface window (GUI) will open immediately.

# 📖 How to Use the Application

1. Select Locations to Compare:

- Click "Select Location A" and specify the first source directory/folder.
- Click "Select Location B" and specify the second source directory/folder.

2. Configure Filter Options (Optional but recommended):
   Below the folder selection buttons, there are two checkboxes enabled by default:

- Skip hidden folders/files: Ignores all files/folders with names starting with a dot (e.g., .git, .vscode).
- Skip folders/files in .gitignore: Reads any .gitignore file found during the scan and ignores heavy folders (such as node_modules or build/) based on the rules defined within them.

3. Start Search:

- Click the "Start Search" button.
- Monitor the Status indicator on the right. The program first scans file sizes, then matches the hashes (content) of files that share the same size.

4. Review Results:

- If duplicates are found, the files will appear sequentially in the main table.
- The table displays Size, Original Name, Exact Location A, Exact Location B, and the dates for both files.
- If a series of consecutive files originates from the same folder, that folder is likely a duplicate project.

5. Perform Actions (Delete/Keep):

- View Original Location: Click a file in the table, then click "Open Location A" or "Open Location B" to open the original folder in File Explorer or Finder.
- Delete Files: Select one or more files (hold the Ctrl key while clicking), then choose "Delete File at Location A" or "Delete File at Location B". The files will be immediately deleted from your storage.
- Ignore: If you decide to keep the duplicates, click "Keep Both" to clear them from the list without deleting the original files.

# ⚠️ Security Warning

The deletion feature will permanently remove files from your storage (they will not go to the Recycle Bin/Trash). Please double-check the file location and details before confirming the deletion!
