@echo off
REM Gmail Watcher - Quick Start
REM Starts Gmail monitoring for AI Employee

echo ============================================
echo Gmail Watcher - Starting...
echo ============================================
echo.

cd /d "%~dp0AI_Employee_Vault\Scripts"

REM Check if vault exists
if not exist "AI_Employee_Vault" (
    echo ERROR: AI_Employee_Vault not found!
    pause
    exit /b 1
)

echo Starting Gmail Watcher...
echo Monitoring: Gmail Inbox
echo Check Interval: 120 seconds (2 minutes)
echo Looking for: Unread, Important emails
echo.
echo Press Ctrl+C to stop
echo ============================================
echo.

python gmail_watcher.py --vault .. --interval 120

pause
