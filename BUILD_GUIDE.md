
# AutoSortr EXE Build Guide

Follow these simple steps to build AutoSortr.exe:

---

## Step 1: Open Command Prompt in the Right Folder
1. Open **File Explorer** and go to: `c:\Users\Pratham\OneDrive\Desktop\AutoSortr\atuosortr`
2. Click in the **address bar** at the top, type `cmd`, and press Enter
   (This opens Command Prompt directly in the correct folder!)

---

## Step 2: Install Dependencies
In the Command Prompt window, type (or copy-paste) this line and press Enter:
```cmd
python -m pip install --user Pillow mutagen watchdog requests tqdm pyinstaller
```
Wait for it to finish installing everything!

---

## Step 3: Build the EXE!
Now type this line and press Enter:
```cmd
python -m PyInstaller --clean AutoSortr.spec
```

---

## Step 4: Get Your EXE!
When it finishes, you'll find `AutoSortr.exe` in the `dist` folder:
```
c:\Users\Pratham\OneDrive\Desktop\AutoSortr\atuosortr\dist\AutoSortr.exe
```

🎉 That's it! Now you can run AutoSortr.exe!
