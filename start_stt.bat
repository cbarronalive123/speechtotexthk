@echo off
REM Silent launcher (no console window) - use for normal everyday use
cd /d "%~dp0"
start "" "venv\Scripts\pythonw.exe" "speech_to_text.py"
echo Speech to Text started silently.
