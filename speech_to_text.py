"""
Speech to Text - Left + Right Mouse Button Hotkey
--------------------------------------------------
Press LEFT and RIGHT mouse buttons simultaneously to trigger
Windows built-in speech recognition (Win+H).

Also works with Ctrl+H as a keyboard fallback.
Shows an STT icon in the system tray so you know it's running.
"""

import ctypes
import ctypes.wintypes as wt
import threading
import time
import sys

import keyboard
import pystray
from PIL import Image, ImageDraw, ImageFont

# ── Configuration ──────────────────────────────────────────────────────────────
KEYBOARD_FALLBACK = "ctrl+h"

# ── ctypes setup ──────────────────────────────────────────────────────────────
user32 = ctypes.WinDLL("user32", use_last_error=True)

user32.CallNextHookEx.restype  = ctypes.c_long
user32.CallNextHookEx.argtypes = [wt.HHOOK, ctypes.c_int, wt.WPARAM, ctypes.c_void_p]

user32.SetWindowsHookExW.restype  = wt.HHOOK
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, ctypes.c_void_p, wt.HINSTANCE, wt.DWORD]

user32.UnhookWindowsHookEx.restype  = wt.BOOL
user32.UnhookWindowsHookEx.argtypes = [wt.HHOOK]

user32.keybd_event.restype  = None
user32.keybd_event.argtypes = [ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ulong, ctypes.c_ulong]

# ── Globals ────────────────────────────────────────────────────────────────────
_hook_handle  = None
_left_down    = False
_right_down   = False
_triggered    = False
_last_pt      = None
_trigger_lock = threading.Lock()
_tray_icon    = None
_enabled      = True          # toggle with TOGGLE_HOTKEY

TOGGLE_HOTKEY = "ctrl+alt+F9"

WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP   = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP   = 0x0205

VK_LWIN         = 0x5B
KEYEVENTF_KEYUP = 0x0002

# ── Tray icon images ───────────────────────────────────────────────────────────

def _make_tray_image(state="idle"):
    """
    state: 'idle'    — dark bg, white mic + STT
           'active'  — green bg, white mic + STT
    """
    size  = 64
    img   = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d     = ImageDraw.Draw(img)

    bg    = (30, 30, 30, 255)   if state == "idle" else (30, 160, 60, 255) if state == "active" else (120, 40, 40, 255)
    fg    = (255, 255, 255, 255) if state != "disabled" else (150, 150, 150, 255)
    pad   = size * 0.06

    # Background rounded square
    d.rounded_rectangle([pad, pad, size - pad, size - pad],
                        radius=size * 0.18, fill=bg)

    # Mic body
    d.rounded_rectangle([size*0.35, size*0.10, size*0.65, size*0.54],
                        radius=size*0.13, fill=fg)

    # Arc (stand)
    lw = max(2, int(size * 0.06))
    d.arc([size*0.27, size*0.36, size*0.73, size*0.66],
          start=0, end=180, fill=fg, width=lw)

    # Pole
    cx = size * 0.5 - lw / 2
    d.rectangle([cx, size*0.64, cx + lw, size*0.74], fill=fg)

    # Base bar
    bh = max(2, int(size * 0.06))
    d.rounded_rectangle([size*0.28, size*0.74, size*0.72, size*0.74 + bh],
                        radius=bh // 2, fill=fg)

    # "STT" text
    try:
        font = ImageFont.truetype("arial.ttf", 10)
    except Exception:
        font = ImageFont.load_default()
    bbox = d.textbbox((0, 0), "STT", font=font)
    tw   = bbox[2] - bbox[0]
    d.text(((size - tw) / 2, size * 0.82), "STT", fill=fg, font=font)

    return img


_img_idle   = _make_tray_image("idle")
_img_active = _make_tray_image("active")
_img_disabled = _make_tray_image("disabled")


def _set_tray_active(active: bool):
    """Flash the tray icon green when triggered, back to dark when done."""
    if _tray_icon:
        if active:
            _tray_icon.icon  = _img_active
            _tray_icon.title = "STT — Listening..."
        else:
            if _enabled:
                _tray_icon.icon  = _img_idle
                _tray_icon.title = "Speech to Text  |  Left+Right click or Ctrl+H"
            else:
                _tray_icon.icon  = _img_disabled
                _tray_icon.title = "Speech to Text  |  DISABLED  (Ctrl+Alt+F9 to enable)"


def _toggle_enabled():
    """Toggle enabled/disabled state."""
    global _enabled
    _enabled = not _enabled
    _set_tray_active(False)  # update icon to reflect new state


# ── Speech trigger ─────────────────────────────────────────────────────────────

def _dismiss_and_fire():
    global _last_pt

    if not _enabled:
        return

    _set_tray_active(True)

    # Escape closes any context menu that slipped through
    time.sleep(0.04)
    user32.keybd_event(0x1B, 0, 0, 0)
    user32.keybd_event(0x1B, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.04)

    # Left-click at the original spot to restore focus in the text field
    if _last_pt:
        x, y = _last_pt
        user32.SetCursorPos(x, y)
        time.sleep(0.03)
        user32.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
        time.sleep(0.03)
        user32.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
        time.sleep(0.05)

    # Fire Win+H
    user32.keybd_event(VK_LWIN, 0, 0, 0)
    user32.keybd_event(0x48, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(0x48, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0)

    # Keep icon green for 1 second so you can see it fired, then go back to idle
    time.sleep(1.0)
    _set_tray_active(False)


# ── Low-level mouse hook ───────────────────────────────────────────────────────

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt",          wt.POINT),
        ("mouseData",   wt.DWORD),
        ("flags",       wt.DWORD),
        ("time",        wt.DWORD),
        ("dwExtraInfo", ctypes.c_ulong),
    ]

HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, wt.WPARAM, ctypes.c_void_p)


def _mouse_hook_proc(nCode, wParam, lParam):
    global _left_down, _right_down, _triggered, _last_pt

    if nCode >= 0:
        if wParam == WM_LBUTTONDOWN:
            _left_down = True

        elif wParam == WM_LBUTTONUP:
            _left_down = False
            with _trigger_lock:
                _triggered = False

        elif wParam == WM_RBUTTONDOWN:
            if _left_down and _enabled:
                _right_down = True
                with _trigger_lock:
                    already = _triggered
                    if not already:
                        _triggered = True
                if not already:
                    info     = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
                    _last_pt = (info.pt.x, info.pt.y)
                    threading.Thread(target=_dismiss_and_fire, daemon=True).start()
                return 1  # suppress right-click when left is held
            else:
                _right_down = True

        elif wParam == WM_RBUTTONUP:
            _right_down = False
            if not _left_down:
                with _trigger_lock:
                    _triggered = False

    return user32.CallNextHookEx(_hook_handle, nCode, wParam, lParam)


_hook_proc_ref = HOOKPROC(_mouse_hook_proc)


def _install_hook():
    global _hook_handle
    _hook_handle = user32.SetWindowsHookExW(14, _hook_proc_ref, None, 0)
    if not _hook_handle:
        err = ctypes.get_last_error()
        raise RuntimeError(f"SetWindowsHookExW failed, error={err}")


def _message_loop():
    _install_hook()
    msg = wt.MSG()
    while True:
        ret = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
        if ret == 0 or ret == -1:
            break
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))


# ── Tray setup ─────────────────────────────────────────────────────────────────

def _build_tray():
    global _tray_icon

    def on_quit(icon, item):
        icon.stop()

    menu = pystray.Menu(
        pystray.MenuItem("Speech to Text", None, enabled=False),
        pystray.MenuItem("Left+Right click  or  Ctrl+H", None, enabled=False),
        pystray.MenuItem("Toggle: Ctrl+Alt+F9", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", on_quit),
    )

    _tray_icon = pystray.Icon(
        name="SpeechToText",
        icon=_img_idle,
        title="Speech to Text  |  Left+Right click or Ctrl+H",
        menu=menu,
    )
    return _tray_icon


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    # Keyboard fallback
    keyboard.add_hotkey(
        KEYBOARD_FALLBACK,
        lambda: threading.Thread(target=_dismiss_and_fire, daemon=True).start(),
        suppress=True,
    )

    # Toggle enable/disable
    keyboard.add_hotkey(TOGGLE_HOTKEY, _toggle_enabled, suppress=True)

    # Start the mouse hook on a background thread
    hook_thread = threading.Thread(target=_message_loop, daemon=True)
    hook_thread.start()

    # Give hook a moment to install
    time.sleep(0.3)

    # Run the tray icon on the main thread (required by pystray on Windows)
    tray = _build_tray()
    tray.run()

    # Tray was quit — clean up
    if _hook_handle:
        user32.UnhookWindowsHookEx(_hook_handle)
    keyboard.unhook_all()


if __name__ == "__main__":
    main()
