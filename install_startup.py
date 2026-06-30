"""
install_startup.py
------------------
Creates a shortcut in the Windows Startup folder so Speech to Text
launches automatically when you log in.

Run once:
    venv\Scripts\python install_startup.py
"""

import os
import sys

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
STARTUP_DIR = os.path.join(
    os.environ["APPDATA"],
    r"Microsoft\Windows\Start Menu\Programs\Startup",
)
SHORTCUT_PATH = os.path.join(STARTUP_DIR, "SpeechToText.lnk")
BAT_FILE      = os.path.join(SCRIPT_DIR, "start_stt.bat")


def create_shortcut():
    try:
        import win32com.client  # part of pywin32
    except ImportError:
        # Fallback: just copy the .bat to startup folder
        import shutil
        dst = os.path.join(STARTUP_DIR, "SpeechToText.bat")
        shutil.copy2(BAT_FILE, dst)
        print(f"[OK] Copied start_stt.bat to Startup folder:\n     {dst}")
        return

    shell    = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(SHORTCUT_PATH)
    shortcut.TargetPath       = BAT_FILE
    shortcut.WorkingDirectory = SCRIPT_DIR
    shortcut.WindowStyle      = 7   # minimized / silent
    shortcut.Description      = "Speech to Text tray app"
    shortcut.save()
    print(f"[OK] Startup shortcut created:\n     {SHORTCUT_PATH}")


if __name__ == "__main__":
    create_shortcut()
