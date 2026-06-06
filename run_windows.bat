@echo off
REM One-click Windows demo: REAL WiFi sensing, no extra hardware.
REM Reads nearby WiFi access points/hotspots live via netsh and shows the
REM signal-strength heatmap. Open http://127.0.0.1:8000 in your browser.

cd /d "%~dp0"

if not exist ".venv\" (
  echo Creating virtual environment...
  python -m venv .venv
)
call .venv\Scripts\activate.bat

echo Installing dependencies (first run only)...
pip install -q fastapi "uvicorn[standard]"

set FOOTFALL_MODE=winscan
echo.
echo ============================================================
echo  WiFi X-Ray running in REAL Windows scan mode (no hardware).
echo  Open this on THIS computer:  http://127.0.0.1:8000
echo  Tip: walk around the room and watch the heatmap shift.
echo ============================================================
echo.
python -m uvicorn footfall.server:app --host 0.0.0.0 --port 8000
