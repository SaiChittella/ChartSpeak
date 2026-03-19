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

    # Create a richer timbre by combining sine waves
    wave = (
        0.6 * np.sin(2 * np.pi * freq * t) +  # Fundamental frequency
        0.3 * np.sin(2 * np.pi * (freq * 2) * t) +  # First harmonic
        0.1 * np.sin(2 * np.pi * (freq * 3) * t)    # Second harmonic
    )

    # Apply an ADSR envelope
    attack = int(0.1 * len(t))  # 10% of the duration
    release = int(0.1 * len(t))  # 10% of the duration
    sustain = len(t) - attack - release
    envelope = np.concatenate([
        np.linspace(0, 1, attack),  # Attack
        np.ones(sustain),           # Sustain
        np.linspace(1, 0, release)  # Release
    ])

    wave *= envelope[:len(t)]  # Apply envelope

    # Normalize to avoid clipping
    wave *= amplitude

    sd.play(wave, fs)
    sd.wait()

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
        tone = (
            0.6 * np.sin(2 * np.pi * freq * t) +  # Fundamental frequency
            0.3 * np.sin(2 * np.pi * (freq * 2) * t) +  # First harmonic
            0.1 * np.sin(2 * np.pi * (freq * 3) * t)    # Second harmonic
        )

        # Apply an ADSR envelope
        attack = int(0.1 * len(t))  # 10% of the duration
        release = int(0.1 * len(t))  # 10% of the duration
        sustain = len(t) - attack - release
        envelope = np.concatenate([
            np.linspace(0, 1, attack),  # Attack
            np.ones(sustain),           # Sustain
            np.linspace(1, 0, release)  # Release
        ])

        tone *= envelope[:len(t)]  # Apply envelope
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