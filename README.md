
# AutoSortr - Smart File Organizer

A desktop application to automatically organize your files with duplicate detection, smart renaming, and auto-updating features.

## Features
- Auto-organize files into categories (images, videos, docs, etc.)
- Duplicate file detection and removal
- Smart file renaming using metadata
- Real-time folder monitoring
- Built-in auto-update system using GitHub releases

---

## 📚 Guides
- [How to Build AutoSortr.exe (BUILD_GUIDE.md)](BUILD_GUIDE.md)
- [How the Auto-Update System Works (UPDATE_SYSTEM_GUIDE.md)](UPDATE_SYSTEM_GUIDE.md)

---

## Building EXE
To build a standalone executable, see [BUILD_GUIDE.md](BUILD_GUIDE.md) for step-by-step instructions!

---

## Auto-Update System Setup
For detailed setup, see [UPDATE_SYSTEM_GUIDE.md](UPDATE_SYSTEM_GUIDE.md)!

Quick steps:
1. Create a public GitHub repo for AutoSortr
2. Edit `atuosortr/update.py` to use your GitHub username/repo name
3. Release versions on GitHub with tags matching `version.txt` and attach your EXE!

---

## Usage
- **Sort Now**: Manually sort files from the source folder
- **Start Monitoring**: Watch for new files and auto-sort them
- **Check for Updates**: Check GitHub for latest version

---

## License
MIT
