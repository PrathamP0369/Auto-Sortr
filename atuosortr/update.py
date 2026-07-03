
import os
import sys
import hashlib
import threading
import time
import requests
import subprocess
from pathlib import Path
from datetime import datetime
from utils import create_log, get_app_base_dir


class Updater:
    def __init__(self, gui_instance=None):
        self.gui = gui_instance
        self.base_dir = get_app_base_dir()
        self.current_version = self._get_current_version()
        self.last_check_file = self.base_dir / "last_update_check.txt"
        self.github_username = "PrathamP0369"  # Replace with your actual GitHub username
        self.github_repo = "Auto-Sortr"     # Replace with your actual GitHub repo name
        self.download_folder = self.base_dir / "updates"
        self.backup_folder = self.base_dir / "backup"
        self.download_folder.mkdir(exist_ok=True)
        self.backup_folder.mkdir(exist_ok=True)
        self.is_downloading = False
        self.is_updating = False

    def _get_current_version(self):
        """Read current version from version.txt"""
        version_file = self.base_dir / "version.txt"
        if not version_file.exists():
            with open(version_file, "w", encoding="utf-8") as f:
                f.write("v1.0.0")
        with open(version_file, "r", encoding="utf-8") as f:
            return f.read().strip()

    def _should_check_for_updates(self):
        """Only check once per day"""
        if not self.last_check_file.exists():
            return True
        
        with open(self.last_check_file, "r", encoding="utf-8") as f:
            last_check_str = f.read().strip()
        
        try:
            last_check = datetime.fromisoformat(last_check_str)
            now = datetime.now()
            delta = now - last_check
            return delta.days >= 1
        except:
            return True

    def _save_last_check_time(self):
        """Save the current time as last update check"""
        with open(self.last_check_file, "w", encoding="utf-8") as f:
            f.write(datetime.now().isoformat())

    def _parse_version(self, version_str):
        """Convert vX.Y.Z to tuple for comparison"""
        try:
            version = version_str.lstrip("v").split(".")
            return tuple(map(int, version))
        except:
            return (0, 0, 0)

    def check_for_updates(self, manual_check=False):
        """Check GitHub for latest release"""
        if not manual_check and not self._should_check_for_updates():
            return None, None

        api_url = f"https://api.github.com/repos/{self.github_username}/{self.github_repo}/releases/latest"
        
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            release = response.json()
            
            latest_version = release.get("tag_name", "v0.0.0")
            changelog = release.get("body", "")
            assets = release.get("assets", [])
            
            current = self._parse_version(self.current_version)
            latest = self._parse_version(latest_version)
            
            if not manual_check:
                self._save_last_check_time()
                
            if latest > current:
                create_log(f"Update available: {latest_version}")
                return latest_version, changelog, assets
            
            return None, None, None
            
        except Exception as e:
            create_log(f"Update check failed: {e}")
            return None, None, None

    def _calculate_sha256(self, file_path):
        """Calculate SHA256 checksum"""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def download_update(self, download_url, progress_callback=None):
        """Download update file from GitHub with progress"""
        file_name = Path(download_url).name
        local_path = self.download_folder / file_name
        
        try:
            self.is_downloading = True
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0
            start_time = time.time()
            
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if not self.is_downloading:  # Allow cancellation
                        f.close()
                        local_path.unlink()
                        return None
                        
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            elapsed = time.time() - start_time
                            if elapsed > 0:
                                speed_mb_s = (downloaded / (1024 * 1024)) / elapsed
                                eta = ((total_size - downloaded) / (downloaded / elapsed)) if downloaded > 0 else 0
                                percent = int((downloaded / total_size) * 100)
                                progress_callback(percent, speed_mb_s, eta)
            
            create_log(f"Downloaded update to: {local_path}")
            return local_path
            
        except Exception as e:
            create_log(f"Download failed: {e}")
            if local_path.exists():
                local_path.unlink()
            return None
        finally:
            self.is_downloading = False

    def backup_current_version(self):
        """Backup current executable/files"""
        try:
            if getattr(sys, 'frozen', False):  # If running as EXE
                exe_path = Path(sys.executable)
                backup_path = self.backup_folder / f"AutoSortr_backup_{self.current_version}.exe"
                import shutil
                shutil.copy2(exe_path, backup_path)
                create_log(f"Backed up current version to: {backup_path}")
                return backup_path
            return None
        except Exception as e:
            create_log(f"Backup failed: {e}")
            return None

    def apply_update(self, update_path):
        """Replace current version with new one"""
        try:
            self.is_updating = True
            
            if getattr(sys, 'frozen', False):  # If running as EXE
                exe_path = Path(sys.executable)
                backup = self.backup_current_version()
                
                # Create a simple batch script to replace exe after closing
                batch_content = f'''@echo off
chcp 65001 >nul
timeout /t 2 /nobreak >nul
copy /Y "{update_path}" "{exe_path}"
if %errorlevel% equ 0 (
    echo Update successful!
    del "{update_path}"
    start "" "{exe_path}"
) else (
    echo Update failed! Rolling back...
    if exist "{backup}" (
        copy /Y "{backup}" "{exe_path}"
    )
)
'''
                batch_path = self.download_folder / "update.bat"
                with open(batch_path, "w", encoding="utf-8") as f:
                    f.write(batch_content)
                
                create_log("Starting update process...")
                subprocess.Popen([str(batch_path)], shell=True)
                return True
            
            return False
        except Exception as e:
            create_log(f"Update failed: {e}")
            self.is_updating = False
            return False
