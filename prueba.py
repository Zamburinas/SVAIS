import wave
import numpy as np
import matplotlib.pyplot as plt

# Open the .wav file
with wave.open('ais/AIS.wav', 'rb') as wav_file:
    # Read the audio frames as bytes
    audio_frames = wav_file.readframes(wav_file.getnframes())
    
    # Convert the byte data to a numpy array
    audio_data = np.frombuffer(audio_frames, dtype=np.int16)
    
    # Get the frame rate and create a time axis for the audio
    frame_rate = wav_file.getframerate()
    time_axis = np.linspace(0, len(audio_data) / frame_rate, num=len(audio_data))
    
    # Plot the audio waveform
    plt.plot(time_axis, audio_data)
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title('Audio Waveform')
    plt.show()
