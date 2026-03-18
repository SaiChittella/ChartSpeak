import numpy as np
import sounddevice as sd

def playNormalizedValues(values):

    # Example normalized data (0–1)
    data = np.array(values)

    # Parameters
    duration = 2  # seconds per tone
    fs = 44100      # sample rate
    min_freq = 220  # A3
    max_freq = 880  # A5

    def value_to_freq(value):
        """Map normalized value (0–1) to frequency range."""
        return min_freq + value * (max_freq - min_freq)

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