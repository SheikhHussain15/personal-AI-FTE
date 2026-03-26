@echo off
REM Quick Test - LinkedIn Auto Posting
REM Tests the full automation flow

echo ============================================================
echo LinkedIn Auto-Post Quick Test
echo ============================================================
echo.

cd /d "%~dp0.."

echo This will:
echo   1. Create a test post in Approved/
echo   2. Start LinkedIn Watcher for 2 minutes
echo   3. Check if post was published
echo.

pause

echo.
echo Creating test post...
python .qwen\skills\linkedin-poster\scripts\linkedin_poster.py ^
  --vault AI_Employee_Vault ^
  --content "Test post from AI Employee Silver Tier - Auto generated #[time]"

echo.
echo Starting LinkedIn Watcher (will run for 2 minutes)...
start cmd /k "cd AI_Employee_Vault\Scripts && python linkedin_watcher.py --vault .. --interval 10"

echo.
echo Waiting 2 minutes for auto-post...
timeout /t 120 /nobreak

echo.
echo Checking if post was published...
dir AI_Employee_Vault\Done\LinkedIn\LINKEDIN_POST_*.md

echo.
echo ============================================================
echo Test complete!
echo ============================================================
echo.
echo Check AI_Employee_Vault\Done\LinkedIn\ for posted content
echo Check AI_Employee_Vault\Logs\ for screenshots
echo.
pause
