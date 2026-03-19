import numpy as np
import sounddevice as sd
from state import app

SEMITONE_RATIO = 2 ** (1/12)


def increase_high_note():
    app.high_note_freq *= SEMITONE_RATIO
    play_frequency(app.high_note_freq)

def decrease_high_note():
    app.high_note_freq /= SEMITONE_RATIO
    play_frequency(app.high_note_freq)

def increase_low_note():
    app.low_note_freq *= SEMITONE_RATIO
    play_frequency(app.low_note_freq)

def decrease_low_note():
    app.low_note_freq /= SEMITONE_RATIO
    play_frequency(app.low_note_freq)


def play_frequency(freq, fs=44100, amplitude=0.5):
    
    duration = app.duration 
    
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)

    wave = (
        0.6 * np.sin(2 * np.pi * freq * t) +
        0.3 * np.sin(2 * np.pi * (freq * 2) * t) +
        0.1 * np.sin(2 * np.pi * (freq * 3) * t)
    )

    attack = int(0.1 * len(t))
    release = int(0.1 * len(t))
    sustain = len(t) - attack - release
    envelope = np.concatenate([
        np.linspace(0, 1, attack),
        np.ones(sustain),
        np.linspace(1, 0, release)
    ])

    wave *= envelope[:len(t)]

    wave *= amplitude

    sd.play(wave, fs)
    sd.wait()

def playNormalizedValues(values):

    data = np.array(values)

    duration = app.duration
    fs = 44100

    def value_to_freq(value):
        return app.low_note_freq + value * (app.high_note_freq - app.low_note_freq)

    def generate_tone(freq, duration, fs):
        t = np.linspace(0, duration, int(fs * duration), False)
        tone = (
            0.6 * np.sin(2 * np.pi * freq * t) +
            0.3 * np.sin(2 * np.pi * (freq * 2) * t) +
            0.1 * np.sin(2 * np.pi * (freq * 3) * t)
        )

        attack = int(0.1 * len(t))
        release = int(0.1 * len(t))
        sustain = len(t) - attack - release
        envelope = np.concatenate([
            np.linspace(0, 1, attack),
            np.ones(sustain),
            np.linspace(1, 0, release)
        ])

        tone *= envelope[:len(t)]
        return tone

    audio = np.array([])

    for v in data:
        freq = value_to_freq(v)
        tone = generate_tone(freq, duration, fs)
        audio = np.concatenate((audio, tone))

    audio *= 0.3

    sd.play(audio, fs)
    sd.wait()