"""
chartNavigator.py
==================
Handles hotkey-driven navigation between detected bar charts.

Hotkeys:
    N — next chart
    P — previous chart
    R — replay current chart
    Q — quit
"""

import os
from pathlib import Path

from pynput import keyboard

from gemini import extract_bar_data, normalize_bars, setup_gemini
from Sound import playNormalizedValues
from state import app


client     = setup_gemini()
current    = 0
is_playing = False


# ── TTS ───────────────────────────────────────────────────────────────

def _announce(text: str):
    os.system(f'say "{text}"')


# ── Playback ──────────────────────────────────────────────────────────

def _play_chart(index: int):
    """Extract (or use cache) and play the chart at the given index."""
    global is_playing

    if is_playing:
        return

    is_playing = True
    image_path = app.cropped_image_paths[index]
    total      = len(app.cropped_image_paths)

    try:
        _announce(f"Chart {index + 1} of {total}.")

        if index in app.cache:
            normalized = app.cache[index]
            print(f"\n[Chart {index + 1}/{total}] Using cached data")
        else:
            print(f"\n[Chart {index + 1}/{total}] Extracting: {Path(image_path).name}")
            raw_data = extract_bar_data(image_path, client)

            if not raw_data:
                _announce("Could not extract this chart. Press N to skip.")
                return

            normalized        = normalize_bars(raw_data)
            app.cache[index]  = normalized

            title     = raw_data.get("chart_title") or "Untitled chart"
            low       = raw_data["y_axis_min"]
            high      = raw_data["y_axis_max"]
            bar_count = len(normalized)

            _announce(
                f"{title}. {bar_count} bars. "
                f"Low is {low}, high is {high}. Playing now."
            )

        values = [r["normalized_value"] for r in normalized]
        print(f"  Normalized values: {values}")
        playNormalizedValues(values)

    finally:
        is_playing = False


# ── Hotkey actions ─────────────────────────────────────────────────────

def _go_next():
    global current, is_playing

    if is_playing:
        return

    if current < len(app.cropped_image_paths) - 1:
        current += 1
        _play_chart(current)
    else:
        _announce("This is the last chart.")


def _go_prev():
    global current, is_playing

    if is_playing:
        return

    if current > 0:
        current -= 1
        _play_chart(current)
    else:
        _announce("This is the first chart.")


def _replay():
    global is_playing

    is_playing = False
    _play_chart(current)


def _quit():
    _announce("Closing ChartSpeak.")
    return False


# ── Keyboard listener ──────────────────────────────────────────────────

def _on_press(key):
    try:
        k = key.char.lower() if hasattr(key, 'char') and key.char else None
    except AttributeError:
        k = None

    if k == 'n':
        _go_next()
    elif k == 'p':
        _go_prev()
    elif k == 'r':
        _replay()


# ── Entry point ────────────────────────────────────────────────────────

def read():
    """
    Plays the first chart, then blocks on the keyboard listener
    until Q is pressed. Listener runs on main thread (required on macOS).
    """
    total = len(app.cropped_image_paths)



    print(f"\n{'─' * 50}")
    print(f"  ChartSpeak — {total} chart(s) detected")
    print(f"  N = next  |  P = previous  |  A = replay  ")
    print(f"{'─' * 50}\n")

    _announce(
        f"Found {total} bar chart{'s' if total != 1 else ''}. "
        f"Press N for next, P for previous, R to replay, Q to quit."
    )

    _play_chart(0)