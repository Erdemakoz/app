@echo off
taskkill /F /IM python.exe >nul 2>nul
echo StreamScout is gestopt.
timeout /t 2 >nul
