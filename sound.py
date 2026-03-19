import numpy as np
import sounddevice as sd
from state import app


semitone_ratio = 2 ** (1/12)


def increase_high_note():
    app.high_note_freq *= semitone_ratio
    play_frequency(app.high_note_freq)

def decrease_high_note():
    app.high_note_freq /= semitone_ratio
    play_frequency(app.high_note_freq)

def increase_low_note():
    app.low_note_freq *= semitone_ratio
    play_frequency(app.low_note_freq)

def decrease_low_note():
    app.low_note_freq /= semitone_ratio
    play_frequency(app.low_note_freq)


def play_frequency(freq, fs=44100, amplitude=0.5):
    
    duration = app.duration 
    
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    
    wave = amplitude * np.sin(2 * np.pi * freq * t)
    
    sd.play(wave, fs)
    sd.wait()

import numpy as np
import sounddevice as sd
from state import app

def playNormalizedValues(values):

    # Example normalized data (0–1)
    data = np.array(values)

    # Parameters
    duration = app.duration  # seconds per tone
    fs = 44100      # sample rate

    def value_to_freq(value):
        """Map normalized value (0–1) to frequency range."""
        return app.low_note_freq + value * (app.high_note_freq - app.low_note_freq)

    def generate_tone(freq, duration, fs):
        t = np.linspace(0, duration, int(fs * duration), False)
        tone = np.sin(2 * np.pi * freq * t)
        return tone

    # Build full audio signal
    audio = np.array([])

    for v in data:
        freq = value_to_freq(v)
        tone = generate_tone(freq, duration, fs)
        audio = np.concatenate((audio, tone))

    # Normalize to avoid clipping
    audio *= 0.3

    # Play sound
    sd.play(audio, fs)
    sd.wait()