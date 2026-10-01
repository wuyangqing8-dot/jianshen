@echo off
cd /d "%~dp0"
where powershell >nul 2>nul
if errorlevel 1 (
  echo Windows PowerShell is unavailable. Install Python 3 and run: py -m http.server 8000 --bind 127.0.0.1
  pause
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_web.ps1"
if errorlevel 1 pause
