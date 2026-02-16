@echo off
echo ========================================
echo RAG Evaluator - Quick Setup
echo ========================================
echo.

echo Step 1: Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo Make sure Python and pip are installed
    pause
    exit /b 1
)

echo.
echo Step 2: Creating data directory...
if not exist "data" mkdir data
echo Created: data\

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit config.py with your API keys
echo 2. Put PDF/DOCX files in data\ folder
echo 3. Run: python main.py
echo.
echo For Google Sheets integration:
echo - Setup service account (see README.md)
echo - Save credentials to: %%APPDATA%%\gspread\service_account.json
echo.
pause