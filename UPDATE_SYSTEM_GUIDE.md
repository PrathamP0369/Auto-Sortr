
# AutoSortr Auto-Update System Guide

## Part 1: One-Time Setup (Before First Release)

---

### 1. Configure `update.py`
Open `atuosortr/update.py` and change these lines to match your GitHub info:

```python
self.github_username = "YOUR_GITHUB_USERNAME"  # Replace this!
self.github_repo = "YOUR_REPO_NAME"           # Replace this!
```

Example:
```python
self.github_username = "pratham123"
self.github_repo = "AutoSortr"
```

---

### 2. Create Your GitHub Repository
1. Go to https://github.com/new
2. Name your repo (must match what you put in `update.py`)
3. Make it **Public** (required for the API to work without auth)
4. Click "Create repository"

---

## Part 2: Publish Your First Version (v1.0.0)

---

### 1. Build AutoSortr.exe
Follow the steps in `BUILD_GUIDE.md` to build your EXE!

---

### 2. Create a GitHub Release
1. Go to your repo on GitHub
2. Click on **"Releases"** (right-hand side)
3. Click **"Draft a new release"**
4. Fill in the details:
   - **Choose a tag**: Type `v1.0.0` (must match version.txt)
   - **Release title**: `AutoSortr v1.0.0`
   - **Description**: Write something like "First release!"
5. Attach your EXE file (`AutoSortr.exe`) by dragging-and-dropping it into the "Attach binaries" section
6. Click **"Publish release"**

---

## Part 3: How to Publish an Update

---

### Step 1: Update Your App Code
Make whatever changes/fixes/additions you want to your code!

---

### Step 2: Update `version.txt`
Open `atuosortr/version.txt` and change the version number!

Examples of version updates:
- Bug fix: `v1.0.0` → `v1.0.1`
- New feature: `v1.0.1` → `v1.1.0`
- Major rewrite: `v1.1.0` → `v2.0.0`

---

### Step 3: Build the New EXE
Use the build guide to make a new `AutoSortr.exe`!

---

### Step 4: Create a New GitHub Release
1. Go back to your repo's **Releases** page
2. Click **"Draft a new release"** again
3. Fill in the new tag (like `v1.0.1`)
4. Write a changelog in the release description (tell users what changed!)
5. Attach your **new** `AutoSortr.exe`
6. Click **"Publish release"**

---

## Part 4: How Users Get Updates

---

### Automatic Check
The app automatically checks for updates **once per day** when it starts!

### Manual Check
Users can click the **"Check for Updates"** button in the app to check anytime!

### Update Process
1. App shows a notification when an update is available
2. User clicks **"Update Now"**
3. App downloads the new EXE (shows progress bar!)
4. App backs up old version
5. App closes and replaces itself with new version
6. App restarts automatically!
