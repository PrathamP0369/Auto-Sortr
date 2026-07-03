import sys
import io

# Fix stdout encoding if possible (only if stdout is not None)
if sys.stdout is not None and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from organizer import FileOrganizer
from gui import AutoSortrGUI

if __name__ == "__main__":
    print("="*50)
    print("AutoSortr - Smart File Organizer".center(50))
    print("="*50)
    
    organizer = FileOrganizer()
    organizer.organize()
    
    print("\nThank you for using AutoSortr!")

    app = AutoSortrGUI()
    app.root.mainloop()
