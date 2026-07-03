from pathlib import Path
import hashlib
import os
from collections import defaultdict
from datetime import datetime
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading

class DuplicateFinder:
    def __init__(self, gui_instance):
        self.gui = gui_instance
        self.is_scanning = False
        self.pause_event = threading.Event()

    def scan_folder(self, folder_path, include_subfolders=True, method="content"):
        """Main scanning function"""
        self.is_scanning = True
        self.pause_event.clear()
        duplicates = defaultdict(list)
        scanned_count = 0

        self.gui.log_message("🔍 Starting duplicate scan...", "info")

        try:
            root = Path(folder_path)
            files = root.rglob("*") if include_subfolders else root.glob("*")

            for file_path in files:
                if not self.is_scanning:
                    break
                if file_path.is_file():
                    scanned_count += 1

                    # Real-time log
                    if scanned_count % 50 == 0:
                        self.gui.log_message(f"Scanned: {scanned_count} files...", "info")

                    # Pause check
                    if self.pause_event.is_set():
                        self.gui.log_message("⏸️ Scan Paused", "warning")
                        while self.pause_event.is_set() and self.is_scanning:
                            time.sleep(0.5)

                    key = self._generate_key(file_path, method)
                    if key:
                        duplicates[key].append(str(file_path))

        except Exception as e:
            self.gui.log_message(f"Error during scan: {e}", "error")

        # Filter real duplicates
        real_duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}

        self.is_scanning = False
        self.gui.log_message(f"✅ Scan Completed! Found {len(real_duplicates)} duplicate sets", "success")
        
        return real_duplicates, scanned_count

    def _generate_key(self, file_path: Path, method: str):
        """Generate key based on selected method"""
        try:
            if method == "name":
                return file_path.name.lower()

            elif method == "size":
                return file_path.stat().st_size

            elif method == "content":
                return self._get_file_hash(file_path)

            elif method == "name_size":
                return (file_path.name.lower(), file_path.stat().st_size)

            elif method == "fuzzy_name":
                return file_path.stem.lower().replace(" ", "").replace("_", "")

            elif method == "date":
                return (file_path.name.lower(), file_path.stat().st_mtime)

        except:
            return None

    def _get_file_hash(self, file_path: Path, block_size=65536):
        """MD5 hash for content comparison"""
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(block_size), b""):
                hasher.update(block)
        return hasher.hexdigest()

    def delete_duplicates(self, duplicates_dict, keep_first=True):
        """Safe deletion with logging"""
        deleted_count = 0
        for key, file_list in duplicates_dict.items():
            if keep_first:
                to_delete = file_list[1:]
            else:
                to_delete = file_list

            for file in to_delete:
                try:
                    os.remove(file)
                    deleted_count += 1
                    self.gui.log_message(f"🗑️ Deleted: {Path(file).name}", "warning")
                except Exception as e:
                    self.gui.log_message(f"Failed to delete {file}: {e}", "error")
        return deleted_count


def find_and_delete_duplicates(folder_path):
    """Standalone function to find and delete duplicates (used by organizer.py)"""
    from pathlib import Path
    import hashlib
    import os
    from collections import defaultdict

    def get_file_hash(file_path: Path, block_size=65536):
        """MD5 hash for content comparison"""
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(block_size), b""):
                hasher.update(block)
        return hasher.hexdigest()

    duplicates = defaultdict(list)
    root = Path(folder_path)
    files = [f for f in root.iterdir() if f.is_file()]

    for file_path in files:
        try:
            key = get_file_hash(file_path)
            duplicates[key].append(str(file_path))
        except:
            pass

    deleted_count = 0
    for key, file_list in duplicates.items():
        if len(file_list) > 1:
            to_delete = file_list[1:]
            for file in to_delete:
                try:
                    os.remove(file)
                    deleted_count += 1
                except Exception as e:
                    pass

    return deleted_count

    