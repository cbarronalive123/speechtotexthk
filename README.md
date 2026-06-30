# Speech to Text

A lightweight Windows utility that opens the built-in Windows speech-to-text (Win+H) using a mouse gesture or keyboard shortcut.

## How it works

The app runs in the system tray and listens for a global input event. When triggered, it:

1. Captures the current mouse position.
2. Sends a quick Escape keystroke to dismiss any context menu that may have appeared.
3. Left-clicks at the original position to restore focus in the text field.
4. Sends the Windows `Win+H` keyboard shortcut to open Windows Voice Typing.

A low-level mouse hook is used to detect the mouse gesture, while the `keyboard` library handles the keyboard hotkeys.

## Triggering speech-to-text

- **Mouse gesture:** hold the **left mouse button** and press the **right mouse button**.
- **Keyboard fallback:** press `Ctrl+H`.
- **Toggle on/off:** press `Ctrl+Alt+F9` to enable or disable the trigger without closing the app.

## System tray

The app shows a microphone icon in the Windows system tray:

- **Dark icon** — idle / ready.
- **Green icon** — listening / just triggered.
- **Gray icon** — disabled.

Right-click the tray icon and select **Quit** to close the application.

## Running the app

### Pre-built executable

A compiled EXE is included in the `dist/` folder:

```
dist\SpeechToText.exe
```

Double-click it to run. No console window appears.

### Run from source

1. Create and activate a virtual environment:

```powershell
python -m venv venv
venv\Scripts\activate
```

2. Install the dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the script:

```powershell
python speech_to_text.py
```

Or use one of the included batch files:

- `start_stt.bat` — silent launch (no console window).
- `start_stt_debug.bat` — launch with a console window for debugging.

## Optional Windows integration

- `install_startup.py` — creates a shortcut in the Windows Startup folder so the app launches automatically on login.
- `install_context_menu.py` — adds a "Speech to Text" item to the Windows right-click context menu.

Run these once as Administrator if you want them.

## Building the executable

The project uses PyInstaller. To rebuild `dist\SpeechToText.exe`:

```powershell
python -m PyInstaller SpeechToText.spec
```

The `.spec` file includes the generated icon (`stt.ico`). If you ever need to regenerate the icon:

```powershell
python make_icon.py
```

## Requirements

- Windows 10 or 11
- Python 3.10+ (only needed when running from source or rebuilding)

The app uses Windows' built-in voice typing, so make sure Windows Voice Typing (`Win+H`) is enabled on your system.
