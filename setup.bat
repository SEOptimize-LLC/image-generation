@echo off
REM Fast AI Image Generator - Windows Setup Script
REM This script helps you set up the project quickly on Windows

echo.
echo ===================================================
echo    Fast AI Image Generator - Windows Setup Script
echo ===================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [OK] Python found: 
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Create .streamlit directory if it doesn't exist
if not exist ".streamlit" (
    echo Creating .streamlit directory...
    mkdir .streamlit
)

REM Copy example secrets file if secrets.toml doesn't exist
if not exist ".streamlit\secrets.toml" (
    if exist ".streamlit\secrets.toml.example" (
        echo Copying example secrets file...
        copy ".streamlit\secrets.toml.example" ".streamlit\secrets.toml"
        echo.
        echo IMPORTANT: Edit .streamlit\secrets.toml and add your OpenAI API key!
        echo.
    )
)

echo.
echo ===================================================
echo    Setup Complete!
echo ===================================================
echo.
echo Next steps:
echo 1. Edit .streamlit\secrets.toml and add your OpenAI API key
echo 2. Run the app with: streamlit run app.py
echo.
echo For Streamlit Cloud deployment:
echo 1. Push your code to GitHub (excluding secrets.toml)
echo 2. Deploy on share.streamlit.io
echo 3. Add OPENAI_API_KEY in the Streamlit Cloud Secrets tab
echo.
echo Happy generating! 
echo.
pause
