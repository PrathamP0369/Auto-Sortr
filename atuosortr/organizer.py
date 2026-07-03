import shutil
import json
import sys
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

from utils import get_file_type, get_date_folder, create_log, get_file_hash, get_app_base_dir
from duplicate_finder import find_and_delete_duplicates
from smart_renamer import SmartRenamer

def has_console():
    return hasattr(sys.stdout, 'write')

DEFAULT_CONFIG = {
    "source_folder": str(Path.home() / "Downloads"),
    "target_folder": str(Path.home() / "Sorted_Files"),
    "backup_enabled": False,
    "backup_folder": str(Path.home() / "AutoSortr_Backups"),
    "delete_duplicates": True,
    "sort_by_date": True,
    "watch_recursive": True,
    "debounce_delay": 1.5,
    "ignore_patterns": [".tmp", ".crdownload"],
    "file_types": {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"],
        "Videos": [".mp4", ".mkv", ".mov", ".avi", ".webm"],
        "Documents": [".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".txt"],
        "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".go"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "Audio": [".mp3", ".wav", ".ogg", ".m4a"]
    }
}

class FileOrganizer:
    def __init__(self):
        base_dir = get_app_base_dir()
        config_path = base_dir / "config.json"
        
        if not config_path.exists():
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        
        with open(config_path, encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.renamer = SmartRenamer()
        self.smart_rename = True               # Toggle for smart renaming

    def organize(self):
        source = Path(self.config['source_folder'])
        target = Path(self.config['target_folder'])
        
        if not source.exists():
            if has_console():
                print("❌ Source folder not found!")
            return
        
        target.mkdir(parents=True, exist_ok=True)
        create_log("=== AutoSortr Started ===")
        
        # Step 1: Delete Duplicates
        if self.config.get('delete_duplicates'):
            if has_console():
                print("🔍 Finding duplicates...")
            dups = find_and_delete_duplicates(source)
            create_log(f"Found {dups} duplicates")
            if has_console():
                print(f"✅ {dups} duplicates removed")
        
        # Step 2: Sort Files
        files = [f for f in source.iterdir() if f.is_file()]
        moved = 0
        
        if has_console():
            print("📁 Sorting files...")
        
        for file in tqdm(files, desc="Organizing", disable=not has_console()):
            try:
                category = get_file_type(file.name, self.config['file_types'])
                date_folder = get_date_folder(str(file)) if self.config.get('sort_by_date') else ""
                
                dest_folder = target / category
                if date_folder:
                    dest_folder = dest_folder / date_folder
                
                dest_folder.mkdir(parents=True, exist_ok=True)
                
                # Smart Renaming
                if self.smart_rename:
                    new_name = self.renamer.generate_smart_name(str(file), category)
                    destination = dest_folder / new_name
                else:
                    destination = dest_folder / file.name

                # Handle same name conflict
                if destination.exists():
                    new_name = f"{destination.stem}_{datetime.now().strftime('%H%M%S')}{destination.suffix}"
                    destination = dest_folder / new_name
                
                shutil.move(str(file), str(destination))
                moved += 1
                create_log(f"Moved: {file.name} → {category}")
                
            except Exception as e:
                create_log(f"Error moving {file.name}: {e}")
        
        if has_console():
            print(f"\n🎉 Sorting Completed!")
            print(f"✅ {moved} files organized")
        create_log(f"Sorting Completed - {moved} files moved")

    def sort_single_file(self, file_path):
        """Sort only one file (used by real-time watcher)"""
        try:
            file = Path(file_path)
            if not file.exists() or not file.is_file():
                return

            category = get_file_type(file.name, self.config['file_types'])
            date_folder = get_date_folder(str(file)) if self.config.get('sort_by_date') else ""

            dest_folder = Path(self.config['target_folder']) / category
            if date_folder:
                dest_folder = dest_folder / date_folder
            dest_folder.mkdir(parents=True, exist_ok=True)

            # Smart Rename
            if self.smart_rename:
                new_name = self.renamer.generate_smart_name(str(file), category)
            else:
                new_name = file.name

            destination = dest_folder / new_name

            # Handle name conflict
            counter = 1
            original_stem = Path(new_name).stem
            while destination.exists():
                new_name = f"{original_stem}_{counter}{destination.suffix}"
                destination = dest_folder / new_name
                counter += 1

            shutil.move(str(file), str(destination))
            create_log(f"Real-time Moved: {file.name} → {category}")
            if has_console():
                print(f"✅ Moved: {file.name}")

        except Exception as e:
            create_log(f"Error sorting single file {file_path}: {e}")
            if has_console():
                print(f"❌ Error: {e}")