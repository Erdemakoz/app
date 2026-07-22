@echo off
setlocal
title StreamScout Installatie
cd /d "%~dp0"

echo ============================================
echo          STREAMSCOUT INSTALLATIE
echo ============================================
echo.

where py >nul 2>nul
if errorlevel 1 (
  echo Python is nog niet geinstalleerd.
  echo De officiele Python-installer wordt nu geopend.
  echo.
  start "" "https://www.python.org/downloads/windows/"
  echo BELANGRIJK: vink "Add python.exe to PATH" aan.
  echo Sluit dit venster na installatie en start INSTALLEREN.bat opnieuw.
  pause
  exit /b 1
)

echo Python gevonden.
py -3 -m venv .venv
if errorlevel 1 goto error

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto error

python -m pip install -r requirements.txt
if errorlevel 1 goto error

where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo.
  echo FFmpeg ontbreekt. Ik probeer het via winget te installeren...
  where winget >nul 2>nul
  if errorlevel 1 (
    echo Winget is niet beschikbaar.
    echo Installeer FFmpeg handmatig en voer INSTALLEREN.bat opnieuw uit.
    start "" "https://ffmpeg.org/download.html"
    pause
    exit /b 1
  )
  winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements
)

echo.
echo ============================================
echo Installatie geslaagd.
echo Start voortaan START_APP.bat
echo ============================================
pause
exit /b 0

:error
echo.
echo Installatie is mislukt. Maak een foto van deze foutmelding.
pause
exit /b 1
