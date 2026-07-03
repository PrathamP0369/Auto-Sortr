import os
import sys
from datetime import datetime
import hashlib
from pathlib import Path

def get_app_base_dir() -> Path:
    """Get the base directory of the app (works for both script and EXE)"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent

def get_file_type(filename: str, file_types: dict) -> str:
    ext = os.path.splitext(filename)[1].lower()
    for folder, extensions in file_types.items():
        if ext in extensions:
            return folder
    return "Others"

def get_date_folder(file_path: str) -> str:
    timestamp = os.path.getmtime(file_path)
    date = datetime.fromtimestamp(timestamp)
    return date.strftime("%Y-%m")

def get_file_hash(file_path: str) -> str:
    """MD5 hash for duplicate detection"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def create_log(message: str):
    base_dir = get_app_base_dir()
    log_dir = base_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"autosortr_{datetime.now().strftime('%Y-%m-%d')}.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")