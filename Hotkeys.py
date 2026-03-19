from FindCharts import detect_crop_save
from pynput import keyboard
from sound import *
from ChartNavigator import _go_next, _go_prev, _replay, read

# Hotkeys.py
exit_callback = None

def set_exit_callback(callback):
    global exit_callback
    exit_callback = callback

def exit_app():
    if exit_callback is not None:
        exit_callback()

pressed = set()

HOTKEYS = {
    frozenset([keyboard.Key.cmd, keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('c')]): detect_crop_save,
    frozenset([keyboard.Key.ctrl, keyboard.Key.alt, keyboard.Key.shift, keyboard.Key.up]): increase_low_note,
    frozenset([keyboard.Key.ctrl, keyboard.Key.alt, keyboard.Key.shift, keyboard.Key.down]): decrease_low_note,
    frozenset([keyboard.Key.ctrl, keyboard.Key.alt, keyboard.Key.up]): increase_high_note,
    frozenset([keyboard.Key.ctrl, keyboard.Key.alt, keyboard.Key.down]): decrease_high_note,
    frozenset([keyboard.Key.cmd, keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('r')]): read,
    frozenset([keyboard.Key.cmd, keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('n')]): _go_next,
    frozenset([keyboard.Key.cmd, keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('p')]): _go_prev,
    frozenset([keyboard.Key.cmd, keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('a')]): _replay,
    frozenset([keyboard.Key.cmd, keyboard.Key.ctrl, keyboard.Key.alt, keyboard.KeyCode.from_char('q')]): exit_app,
}

def on_press(key):
    pressed.add(key)
    current = frozenset(pressed)

    # Find the most specific match (most keys required)
    best_match = None
    best_len = 0
    for combo, action in HOTKEYS.items():
        if combo.issubset(current) and len(combo) > best_len:
            best_match = action
            best_len = len(combo)

    if best_match:
        best_match()

def on_release(key):
    pressed.discard(key)

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
