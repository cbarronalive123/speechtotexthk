r"""
install_context_menu.py
-----------------------
Adds / removes "Speech to Text" to the Windows right-click context menu
for all file types and text fields (edit controls).

Run ONCE as Administrator:
    venv\Scripts\python install_context_menu.py install
    venv\Scripts\python install_context_menu.py uninstall
"""

import sys
import os
import winreg

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXE = os.path.join(SCRIPT_DIR, "venv", "Scripts", "pythonw.exe")
MAIN_SCRIPT = os.path.join(SCRIPT_DIR, "speech_to_text.py")

MENU_LABEL = "Speech to Text \U0001f3a4"
REG_KEY    = r"Software\Classes\*\shell\SpeechToText"
CMD_KEY    = REG_KEY + r"\command"

COMMAND = f'"{PYTHON_EXE}" "{MAIN_SCRIPT}"'  # noqa: E501


def install():
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_KEY)
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, MENU_LABEL)
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, PYTHON_EXE)
        winreg.CloseKey(key)

        cmd_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, CMD_KEY)
        winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, COMMAND)
        winreg.CloseKey(cmd_key)

        print("[OK] Right-click 'Speech to Text' added to context menu.")
        print("     Right-click any file or text area to use it.")
    except PermissionError:
        print("[ERROR] Permission denied. Try running as Administrator.")
        sys.exit(1)


def uninstall():
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, CMD_KEY)
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, REG_KEY)
        print("[OK] 'Speech to Text' removed from context menu.")
    except FileNotFoundError:
        print("[INFO] Key not found — already uninstalled.")
    except PermissionError:
        print("[ERROR] Permission denied. Try running as Administrator.")
        sys.exit(1)


if __name__ == "__main__":
    action = sys.argv[1].lower() if len(sys.argv) > 1 else "install"
    if action == "install":
        install()
    elif action == "uninstall":
        uninstall()
    else:
        print("Usage: python install_context_menu.py [install|uninstall]")
