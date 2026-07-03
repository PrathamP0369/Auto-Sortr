
@echo off
echo ================================
echo Building AutoSortr EXE...
echo ================================
echo.

REM Step 1: Install dependencies (using --user to avoid permissions
echo [1/3] Installing dependencies...
python -m pip install --user Pillow mutagen watchdog requests tqdm pyinstaller
echo Dependencies installed (or already present)!
echo.

REM Step 2: Build using the spec file
echo [2/3] Running PyInstaller...
python -m PyInstaller --clean AutoSortr.spec
if errorlevel 1 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)
echo PyInstaller finished!
echo.

REM Step 3: Check if the EXE exists
echo [3/3] Checking for AutoSortr.exe...
if exist "dist\AutoSortr.exe" (
    echo ================================
    echo SUCCESS! AutoSortr.exe created!
    echo Location: %cd%\dist\AutoSortr.exe
    echo ================================
) else (
    echo ERROR: AutoSortr.exe not found in dist folder!
)

pause
