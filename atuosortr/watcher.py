import time 
from watchdog.observers import Observer 
from watchdog.events import FileSystemEventHandler, FileMovedEvent, FileCreatedEvent 
from pathlib import Path 
from organizer import FileOrganizer 
from utils import create_log 
import threading 

class SortingHandler(FileSystemEventHandler): 
    def __init__(self, organizer): 
        self.organizer = organizer 
        self.processing_files = {} 
        self.lock = threading.Lock() 

    def should_ignore(self, file_path: str) -> bool: 
        """Ignore temporary & system files""" 
        ignore_ext = {'.tmp', '.crdownload', '.part', '.download', 
                     '.swp', '.swo', '~', '.temp'} 
        name = Path(file_path).name.lower() 
        
        if any(name.endswith(ext) for ext in ignore_ext): 
            return True 
        if name.startswith('.'): 
            return True 
        if name.startswith('~$'): 
            return True 
        return False 

    def debounce(self, file_path: str, delay=1.5): 
        """Prevent processing the same file multiple times""" 
        with self.lock: 
            current_time = time.time() 
            if file_path in self.processing_files: 
                if current_time - self.processing_files[file_path] < delay: 
                    return False 
            self.processing_files[file_path] = current_time 
            return True 

    def on_created(self, event): 
        if event.is_directory or self.should_ignore(event.src_path): 
            return 
        if self.debounce(event.src_path): 
            self.process_file(event.src_path, "Created") 

    def on_moved(self, event): 
        if event.is_directory or self.should_ignore(event.dest_path): 
            return 
        if self.debounce(event.dest_path): 
            self.process_file(event.dest_path, "Moved") 

    def process_file(self, file_path, event_type): 
        try: 
            print(f"[{event_type}] New file: {Path(file_path).name}") 
            create_log(f"Real-time {event_type}: {file_path}") 
            
            time.sleep(1.0) 
            
            self.organizer.sort_single_file(file_path) 
            
        except Exception as e: 
            create_log(f"Error processing {file_path}: {e}") 
            print(f"Error: {e}") 


class FolderWatcher: 
    def __init__(self): 
        self.organizer = FileOrganizer() 
        self.observer = None 
        self.is_monitoring = False 

    def start(self, recursive=True): 
        if self.is_monitoring: 
            print("Already monitoring!") 
            return 

        source = self.organizer.config['source_folder'] 
        
        if not Path(source).exists(): 
            print("Source folder does not exist!") 
            return 

        event_handler = SortingHandler(self.organizer) 
        self.observer = Observer() 
        self.observer.schedule(event_handler, source, recursive=recursive) 
        
        self.observer.start() 
        self.is_monitoring = True 
        
        print(f"Real-time monitoring STARTED on: {source}") 
        create_log(f"Monitoring started (recursive={recursive})") 

    def stop(self): 
        if self.observer: 
            self.observer.stop() 
            self.observer.join(timeout=5) 
            self.is_monitoring = False 
            print("Real-time monitoring STOPPED") 
            create_log("Monitoring STOPPED")

    def start_multiple(self, folders_list):
        for folder in folders_list:
            self.observer.schedule(SortingHandler(self.organizer), folder, recursive=True)
