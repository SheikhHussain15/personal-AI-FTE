@echo off
REM Silver Tier - Start All Watchers
REM Starts Filesystem, Gmail, LinkedIn Watchers, and Orchestrator

echo ============================================
echo AI Employee - Silver Tier Watchers
echo ============================================
echo.

cd /d "%~dp0.."

REM Check if vault exists
if not exist "AI_Employee_Vault" (
    echo ERROR: AI_Employee_Vault not found!
    exit /b 1
)

echo Starting watchers...
echo.

REM Terminal 1: Filesystem Watcher
echo [1/4] Starting Filesystem Watcher...
start cmd /k "cd AI_Employee_Vault\Scripts && python filesystem_watcher.py --vault .. --interval 30"

REM Terminal 2: Gmail Watcher
echo [2/4] Starting Gmail Watcher...
start cmd /k "python .qwen/skills/gmail-watcher/scripts/gmail_watcher.py --vault AI_Employee_Vault --interval 120"

REM Terminal 3: LinkedIn Watcher
echo [3/4] Starting LinkedIn Watcher...
start cmd /k "cd AI_Employee_Vault\Scripts && python linkedin_watcher.py --vault .. --interval 60"

REM Terminal 4: Orchestrator
echo [4/4] Starting Orchestrator...
start cmd /k "cd AI_Employee_Vault\Scripts && python orchestrator.py --vault .. --watch --interval 60"

echo.
echo ============================================
echo All watchers started!
echo ============================================
echo.
echo Running in 4 separate terminal windows:
echo   1. Filesystem Watcher (30s interval)
echo   2. Gmail Watcher (120s interval)
echo   3. LinkedIn Watcher (60s interval) - AUTO POSTING
echo   4. Orchestrator (60s interval)
echo.
echo To stop: Close each terminal window or press Ctrl+C
echo.
echo Check AI_Employee_Vault\Logs for activity logs.
echo ============================================
echo.
pause
