@echo off
REM Setup Script for AI Employee (Bronze Tier)
REM Windows batch script to set up the Obsidian vault and verify installation

echo ============================================
echo AI Employee - Bronze Tier Setup
echo ============================================
echo.

REM Check Python installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.13+
    echo Download from: https://www.python.org/downloads/
    exit /b 1
)
python --version
echo.

REM Check Node.js installation
echo [2/5] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Node.js not found. Some features may not work.
    echo Download from: https://nodejs.org/
) else (
    node --version
)
echo.

REM Check Qwen Code
echo [3/5] Checking Qwen Code installation...
qwen --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Qwen Code not found or not in PATH.
    echo Install from: https://code.qwen.ai/
) else (
    qwen --version
)
echo.

REM Create vault directory structure
echo [4/5] Creating vault directory structure...
set VAULT_DIR=AI_Employee_Vault

if not exist "%VAULT_DIR%" (
    echo Creating vault directory...
    mkdir "%VAULT_DIR%"
)

mkdir "%VAULT_DIR%\Inbox" 2>nul
mkdir "%VAULT_DIR%\Needs_Action" 2>nul
mkdir "%VAULT_DIR%\Done" 2>nul
mkdir "%VAULT_DIR%\Plans" 2>nul
mkdir "%VAULT_DIR%\Pending_Approval" 2>nul
mkdir "%VAULT_DIR%\Approved" 2>nul
mkdir "%VAULT_DIR%\Briefings" 2>nul
mkdir "%VAULT_DIR%\Accounting" 2>nul
mkdir "%VAULT_DIR%\Logs" 2>nul
mkdir "%VAULT_DIR%\Scripts" 2>nul
echo Vault structure created.
echo.

REM Install Python dependencies
echo [5/5] Installing Python dependencies...
pip install watchdog >nul 2>&1
if errorlevel 1 (
    echo WARNING: Could not install watchdog. Trying with --user...
    pip install watchdog --user
)
echo Dependencies installed.
echo.

REM Verify vault files
echo ============================================
echo Verifying vault files...
echo ============================================

if exist "%VAULT_DIR%\Dashboard.md" (
    echo [OK] Dashboard.md
) else (
    echo [MISSING] Dashboard.md
)

if exist "%VAULT_DIR%\Company_Handbook.md" (
    echo [OK] Company_Handbook.md
) else (
    echo [MISSING] Company_Handbook.md
)

if exist "%VAULT_DIR%\Business_Goals.md" (
    echo [OK] Business_Goals.md
) else (
    echo [MISSING] Business_Goals.md
)

if exist "%VAULT_DIR%\Scripts\base_watcher.py" (
    echo [OK] base_watcher.py
) else (
    echo [MISSING] base_watcher.py
)

if exist "%VAULT_DIR%\Scripts\filesystem_watcher.py" (
    echo [OK] filesystem_watcher.py
) else (
    echo [MISSING] filesystem_watcher.py
)

if exist "%VAULT_DIR%\Scripts\orchestrator.py" (
    echo [OK] orchestrator.py
) else (
    echo [MISSING] orchestrator.py
)

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Open the AI_Employee_Vault folder in Obsidian
echo 2. Review Company_Handbook.md for rules
echo 3. Update Business_Goals.md with your targets
echo 4. Drop a test file in AI_Employee_Vault\Inbox
echo 5. Run: python AI_Employee_Vault\Scripts\orchestrator.py
echo.
echo For more information, see VAULT_SKILL.md
echo.

pause
