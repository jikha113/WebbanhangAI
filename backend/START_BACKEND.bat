@echo off
cd /d "%~dp0"
echo ==========================================
echo   WEBBANHANG - START BACKEND (DJANGO)
echo ==========================================
echo.

if not exist "venv" (
  echo [INFO] Tao virtual environment...
  python -m venv venv
)

echo [INFO] Kich hoat virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Cai dat dependencies...
pip install -r requirements.txt

echo [INFO] Migrate database...
python manage.py migrate

echo [INFO] Khoi dong server tai http://localhost:8000 ...
python manage.py runserver
