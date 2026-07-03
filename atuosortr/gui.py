import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from duplicate_finder import DuplicateFinder
from organizer import FileOrganizer
from watcher import FolderWatcher
from update import Updater

class AutoSortrGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AutoSortr - Smart File Organizer")
        self.root.geometry("750x600")
        self.root.resizable(True, True)
        
        self.organizer = FileOrganizer()
        self.watcher = FolderWatcher()
        self.monitoring = False
        self.updater = Updater(self)
        self.latest_assets = []

        self.create_widgets()
        self.check_updates_on_startup()

    def create_widgets(self):
        # Title and Version
        title_frame = tk.Frame(self.root)
        title_frame.pack(pady=10)
        title = tk.Label(title_frame, text="AutoSortr", font=("Arial", 20, "bold"))
        title.pack()
        self.version_label = tk.Label(title_frame, text=f"Version {self.updater.current_version}", fg="#666666")
        self.version_label.pack()

        # Source Folder
        tk.Label(self.root, text="Source Folder:").pack(anchor="w", padx=20)
        self.source_var = tk.StringVar(value=self.organizer.config['source_folder'])
        tk.Entry(self.root, textvariable=self.source_var, width=60).pack(padx=20, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_source).pack(pady=5)

        # Target Folder
        tk.Label(self.root, text="Target Folder:").pack(anchor="w", padx=20)
        self.target_var = tk.StringVar(value=self.organizer.config['target_folder'])
        tk.Entry(self.root, textvariable=self.target_var, width=60).pack(padx=20, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_target).pack(pady=5)

        # Buttons Frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Sort Now", font=("Arial", 12, "bold"),
                  bg="#4CAF50", fg="white", width=15, height=2,
                  command=self.start_sorting).grid(row=0, column=0, padx=10)

        self.monitor_btn = tk.Button(btn_frame, text="Start Monitoring", 
                                    font=("Arial", 12, "bold"), bg="#2196F3", 
                                    fg="white", width=15, height=2,
                                    command=self.toggle_monitoring)
        self.monitor_btn.grid(row=0, column=1, padx=10)

        tk.Button(btn_frame, text="Save Config", command=self.save_config).grid(row=0, column=2, pady=10, padx=10)
        
        # Update Button
        tk.Button(btn_frame, text="Check for Updates", command=self.check_for_updates_manual, 
                 bg="#FF9800", fg="white", width=15, height=2, font=("Arial", 10, "bold")).grid(row=0, column=3, padx=10)

        # Status
        self.status = tk.Label(self.root, text="Ready", fg="gray", font=("Arial", 10))
        self.status.pack(pady=5)

        # Duplicate Finder Section
        dup_frame = tk.LabelFrame(self.root, text="🔍 Duplicate Finder", padx=10, pady=10)
        dup_frame.pack(pady=10, fill="x", padx=20)

        self.method_var = tk.StringVar(value="content")
        ttk.Combobox(dup_frame, textvariable=self.method_var, 
                    values=["name", "size", "content", "name_size", "fuzzy_name"]).pack()

        tk.Button(dup_frame, text="Start Duplicate Scan", 
                  command=self.start_duplicate_scan).pack(pady=5)

        self.dup_log = tk.Text(dup_frame, height=5, bg="#1e1e1e", fg="#00ff00")
        self.dup_log.pack(fill="x")
        
        # Activity Log Panel
        log_frame = tk.LabelFrame(self.root, text="📜 Activity Log", padx=10, pady=10)
        log_frame.pack(pady=10, fill="both", expand=True, padx=20)
        
        self.activity_log = tk.Text(log_frame, height=8, bg="#f0f0f0", fg="#000000", font=("Consolas", 9))
        self.activity_log.pack(fill="both", expand=True)
        
        # Footer
        tk.Label(self.root, text="Made with love for real-world use", fg="gray").pack(side="bottom", pady=5)

    def browse_source(self):
        path = filedialog.askdirectory()
        if path:
            self.source_var.set(path)

    def browse_target(self):
        path = filedialog.askdirectory()
        if path:
            self.target_var.set(path)

    def save_config(self):
        self.organizer.config['source_folder'] = self.source_var.get()
        self.organizer.config['target_folder'] = self.target_var.get()
        # Save to config.json (optional)
        messagebox.showinfo("Success", "Settings Updated!")

    def start_sorting(self):
        threading.Thread(target=self._run_sorting, daemon=True).start()

    def _run_sorting(self):
        self.status.config(text="Sorting in progress...", fg="orange")
        try:
            self.organizer.organize()
            self.status.config(text="Sorting Completed!", fg="green")
        except Exception as e:
            self.status.config(text="Error occurred", fg="red")

    def toggle_monitoring(self):
        if not self.monitoring:
            threading.Thread(target=self._start_monitoring, daemon=True).start()
        else:
            self.watcher.stop()
            self.monitoring = False
            self.monitor_btn.config(text="Start Monitoring", bg="#2196F3")
            self.status.config(text="Monitoring Stopped", fg="gray")

    def _start_monitoring(self):
        self.monitoring = True
        self.monitor_btn.config(text="Stop Monitoring", bg="#f44336")
        self.status.config(text="Monitoring Active...", fg="blue")
        self.watcher.start()

    def log_message(self, message, level="info"):
        colors = {"info": "#00ff00", "warning": "#ffff00", "error": "#ff0000", "success": "#00ffff"}
        self.dup_log.insert("end", message + "\n", level)
        self.dup_log.see("end")

    def start_duplicate_scan(self):
        folder = filedialog.askdirectory(title="Select Folder to Scan for Duplicates")
        if folder:
            threading.Thread(target=self._scan_duplicates, args=(folder,), daemon=True).start()

    def _scan_duplicates(self, folder):
        self.log_message(f"Starting scan in: {folder}", "info")
        finder = DuplicateFinder(self)
        duplicates, total = finder.scan_folder(folder, method=self.method_var.get())
        
        if duplicates:
            self.log_message(f"Found {len(duplicates)} duplicate sets!", "warning")
            # Show results in a new window or listbox
        else:
            self.log_message("No duplicates found.", "success")
    
    def log_activity(self, message):
        """Add message to activity log"""
        self.activity_log.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.activity_log.see(tk.END)
    
    def check_updates_on_startup(self):
        """Silently check for updates on app startup"""
        def _check():
            latest_ver, changelog, assets = self.updater.check_for_updates(manual_check=False)
            if latest_ver:
                self.latest_assets = assets
                self.root.after(0, lambda: self.show_update_dialog(latest_ver, changelog))
        
        threading.Thread(target=_check, daemon=True).start()
    
    def check_for_updates_manual(self):
        """Manual check for updates from button click"""
        self.log_activity("Checking for updates...")
        
        def _check():
            latest_ver, changelog, assets = self.updater.check_for_updates(manual_check=True)
            if latest_ver:
                self.latest_assets = assets
                self.root.after(0, lambda: self.show_update_dialog(latest_ver, changelog))
                self.log_activity(f"Update {latest_ver} available!")
            else:
                self.log_activity("You are using the latest version!")
                messagebox.showinfo("AutoSortr", "You are using the latest version!")
        
        threading.Thread(target=_check, daemon=True).start()
    
    def show_update_dialog(self, latest_version, changelog):
        """Show update notification dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Available!")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        
        tk.Label(dialog, text=f"Update {latest_version} available!", font=("Arial", 16, "bold")).pack(pady=10)
        
        tk.Label(dialog, text="What's new:", font=("Arial", 12)).pack(anchor="w", padx=20)
        changelog_text = tk.Text(dialog, height=10, width=55, bg="#f0f0f0", wrap=tk.WORD)
        changelog_text.pack(pady=5, padx=20)
        changelog_text.insert(tk.END, changelog if changelog else "No changelog available")
        changelog_text.config(state=tk.DISABLED)
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Update Now", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                 width=15, height=2, command=lambda: self.start_update_process(latest_version, dialog)).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Remind Later", bg="#f0f0f0", font=("Arial", 12),
                 width=15, height=2, command=dialog.destroy).grid(row=0, column=1, padx=10)
    
    def start_update_process(self, latest_version, dialog):
        """Start download and update process"""
        dialog.destroy()
        
        # Find the .exe asset from GitHub
        exe_asset = None
        for asset in self.latest_assets:
            if asset.get("name", "").endswith(".exe"):
                exe_asset = asset
                break
        
        if not exe_asset:
            messagebox.showerror("Update Failed", "Could not find update file!")
            return
        
        self.log_activity(f"Downloading update {latest_version}...")
        
        # Create progress window
        progress_win = tk.Toplevel(self.root)
        progress_win.title("Downloading Update")
        progress_win.geometry("400x200")
        progress_win.resizable(False, False)
        
        tk.Label(progress_win, text=f"Downloading AutoSortr {latest_version}", font=("Arial", 12)).pack(pady=20)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_win, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(pady=10, padx=30, fill="x")
        
        self.speed_label = tk.Label(progress_win, text="0.00 MB/s | ETA: 0s")
        self.speed_label.pack()
        
        def download_callback(percent, speed, eta):
            self.progress_var.set(percent)
            self.speed_label.config(text=f"{speed:.2f} MB/s | ETA: {int(eta)}s")
            self.log_activity(f"Downloading: {percent}% ({speed:.2f} MB/s)")
        
        def download_and_update():
            download_url = exe_asset.get("browser_download_url")
            update_path = self.updater.download_update(download_url, download_callback)
            
            if update_path:
                self.log_activity("Download complete! Applying update...")
                self.log_activity("Closing app to apply update...")
                
                if self.updater.apply_update(update_path):
                    self.root.destroy()
                else:
                    messagebox.showerror("Update Failed", "Failed to apply update!")
            else:
                progress_win.destroy()
                messagebox.showerror("Update Failed", "Download failed!")
        
        threading.Thread(target=download_and_update, daemon=True).start()


from datetime import datetime

if __name__ == "__main__":
    app = AutoSortrGUI()
    app.root.mainloop()
