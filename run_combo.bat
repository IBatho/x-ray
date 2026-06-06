@echo off
REM One-click demo: REAL WiFi access points + REAL Bluetooth devices on one
REM radar, no extra hardware. Open http://127.0.0.1:8000 in your browser.
REM Turn Bluetooth ON in Windows Settings for the BT half.

cd /d "%~dp0"

if not exist ".venv\" (
  echo Creating virtual environment...
  python -m venv .venv
)
call .venv\Scripts\activate.bat

echo Installing dependencies (first run only)...
pip install -q fastapi "uvicorn[standard]" bleak

set FOOTFALL_MODE=combo
echo.
echo ============================================================
echo  WiFi X-Ray running in COMBINED WiFi + Bluetooth mode.
echo  Bluetooth must be ON in Windows Settings.
echo  Open this on THIS computer:  http://127.0.0.1:8000
echo ============================================================
echo.
python -m uvicorn footfall.server:app --host 0.0.0.0 --port 8000
