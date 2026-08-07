@echo off
setlocal
cd /d "%~dp0"
echo Starting OPOlogy COMPLETE Subject Notebook
echo Build: 2026-08-07 V8
echo Address: http://127.0.0.1:9012
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 opology_server.py --port 9012 --open
) else (
  python opology_server.py --port 9012 --open
)
if errorlevel 1 (
  echo.
  echo Python 3 is required. Install it from https://www.python.org/downloads/
  pause
)
endlocal
