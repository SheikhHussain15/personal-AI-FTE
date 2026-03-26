@echo off
REM AI Employee - Silver Tier Full Automation
REM Fully automated LinkedIn posting with no manual steps

echo ============================================================
echo AI Employee - Silver Tier Full Automation
echo ============================================================
echo.

cd /d "%~dp0.."

REM Check if vault exists
if not exist "AI_Employee_Vault" (
    echo ERROR: AI_Employee_Vault not found!
    pause
    exit /b 1
)

echo This script will:
echo   1. Create LinkedIn post (auto-approved)
echo   2. Start LinkedIn Watcher
echo   3. Auto-post to LinkedIn
echo   4. Move completed post to Done/
echo.

REM Get post content from user
set /p POST_CONTENT="Enter your LinkedIn post content: "

if "%POST_CONTENT%"=="" (
    echo ERROR: Post content is required!
    pause
    exit /b 1
)

echo.
echo Starting automation...
echo.

REM Run auto script
python AI_Employee_Vault\Scripts\auto_run.py --vault AI_Employee_Vault --content "%POST_CONTENT%"

echo.
echo ============================================================
echo Automation complete!
echo ============================================================
echo.
echo Check AI_Employee_Vault\Done\LinkedIn\ for posted content
echo Check AI_Employee_Vault\Logs\ for activity logs
echo.
pause
