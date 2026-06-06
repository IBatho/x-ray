@echo off
REM One-click demo: REAL Bluetooth-LE sensing via the built-in radio, no extra
REM hardware. Detects nearby earbuds/watches/bands/beacons and tracks movement
REM by signal strength. Open http://127.0.0.1:8000 in your browser.
REM
REM Make sure Bluetooth is turned ON in Windows Settings first.

cd /d "%~dp0"

if not exist ".venv\" (
  echo Creating virtual environment...
  python -m venv .venv
)
call .venv\Scripts\activate.bat

echo Installing dependencies (first run only)...
pip install -q fastapi "uvicorn[standard]" bleak

set FOOTFALL_MODE=btscan
echo.
echo ============================================================
echo  WiFi X-Ray running in REAL Bluetooth scan mode (no hardware).
echo  Bluetooth must be ON in Windows Settings.
echo  Open this on THIS computer:  http://127.0.0.1:8000
echo  Tip: walk a BLE device (earbuds/watch) around and watch it move.
echo ============================================================
echo.
python -m uvicorn footfall.server:app --host 0.0.0.0 --port 8000
