@echo off
REM Email MCP Server - Quick Start
REM Starts Email MCP Server for sending emails

echo ============================================
echo Email MCP Server - Starting...
echo ============================================
echo.

cd /d "%~dp0..\.qwen\skills\email-mcp\scripts"

echo Checking authentication...
if not exist "..\..\..\..\AI_Employee_Vault\Scripts\token.json" (
    echo.
    echo WARNING: Token not found!
    echo Please run authentication first:
    echo   python email_auth.py --vault ../../../../AI_Employee_Vault
    echo.
    pause
    exit /b 1
)

echo Token found!
echo.
echo Starting Email MCP Server on port 8809...
echo.
echo Server will run in this window.
echo Press Ctrl+C to stop.
echo.
echo ============================================
echo.

python email_mcp_server.py --vault ../../../../AI_Employee_Vault --port 8809

pause
