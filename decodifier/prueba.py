import wave
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, gaussian

# SDRuno_20200907_184926Z_161985kHz
SEQUENCE_FLAG = "01111110"

# Open the .wav file
with wave.open('ais/AIS.wav', 'rb') as wav_file:
    # Read the audio frames as bytes
    audio_frames = wav_file.readframes(wav_file.getnframes())

    # Convert the byte data to a numpy array
    modulated_signal = np.frombuffer(audio_frames, dtype=np.int16)

# Parameters
symbol_rate = 9600  # Symbol rate in symbols per second
mod_index = 0.5     # Modulation index
sample_rate = 10 * symbol_rate  # Sample rate (must be higher than Nyquist rate)
fc = 161_985_000           # Carrier frequency in Hz

# Gaussian filter
bt = 0.3  # BT product, where B is the bandwidth and T is the symbol period
num_taps = 50
gaussian_filter = gaussian(num_taps, bt / (4 * np.pi))
gaussian_filter /= np.sum(gaussian_filter)

# Apply Gaussian filter
filtered_signal = np.convolve(modulated_signal, gaussian_filter, mode='same')

# Symbol detection
symbols = np.zeros_like(modulated_signal)
for i in range(len(symbols)):
    sample_index = int(i * sample_rate / symbol_rate)
    symbol = np.sign(filtered_signal[sample_index])
    symbols[i] = 0 if symbol < 0 else 1

# Print demodulated bitstream
print("Demodulated bitstream:")
print(symbols.astype(int))
print(len(symbols))

