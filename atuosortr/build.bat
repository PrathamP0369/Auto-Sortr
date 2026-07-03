
@echo off
echo ========================================
echo Building AutoSortr Executable...
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install required dependencies
echo Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

REM Build the executable
echo.
echo Building executable...
python -m PyInstaller --clean AutoSortr.spec
if errorlevel 1 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build complete!
echo Executable is in: dist\AutoSortr.exe
echo ========================================
pause
