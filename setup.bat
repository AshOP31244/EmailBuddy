@echo off
REM Email Buddy Setup Script for Windows
REM This script automates the initial setup process

echo ================================
echo Email Buddy Setup Script
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python 3 is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo [OK] Python 3 is installed
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv myenv

if %errorlevel% equ 0 (
    echo [OK] Virtual environment created successfully
) else (
    echo [FAIL] Failed to create virtual environment
    pause
    exit /b 1
)

echo.

REM Activate virtual environment
echo Activating virtual environment...
call myenv\Scripts\activate.bat

if %errorlevel% equ 0 (
    echo [OK] Virtual environment activated
) else (
    echo [FAIL] Failed to activate virtual environment
    pause
    exit /b 1
)

echo.

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo [OK] Dependencies installed successfully
) else (
    echo [FAIL] Failed to install dependencies
    pause
    exit /b 1
)

echo.

REM Run migrations
echo Running database migrations...
python manage.py makemigrations
python manage.py migrate

if %errorlevel% equ 0 (
    echo [OK] Database migrations completed
) else (
    echo [FAIL] Failed to run migrations
    pause
    exit /b 1
)

echo.

REM Create superuser
echo ================================
echo Create Admin User
echo ================================
echo Please create an admin user to access the application:
echo.
python manage.py createsuperuser

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo To start the development server, run:
echo   python manage.py runserver
echo.
echo Then visit:
echo   - Main app: http://127.0.0.1:8000/
echo   - Admin: http://127.0.0.1:8000/admin/
echo.
echo Happy coding! 🚀
echo.
pause