@echo off
REM Debug launcher - shows console output so you can see what's happening
cd /d "%~dp0"
venv\Scripts\python.exe speech_to_text.py
pause
