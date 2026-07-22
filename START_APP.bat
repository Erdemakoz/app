@echo off
setlocal
title StreamScout
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo StreamScout is nog niet geinstalleerd.
  echo Start eerst INSTALLEREN.bat
  pause
  exit /b 1
)

where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo FFmpeg is niet gevonden.
  echo Start INSTALLEREN.bat opnieuw.
  pause
  exit /b 1
)

echo StreamScout wordt gestart...
echo Laat dit zwarte venster open zolang je de app gebruikt.
echo.
start "" cmd /c "timeout /t 4 >nul & start http://localhost:8000"
call .venv\Scripts\activate.bat
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
