# sweeps as per https://www.researchgate.net/publication/252775034_THE_COMPARISON_OF_ROOM_IMPULSE_RESPONSE_MEASURING_SYSTEMS

from scipy.signal import chirp
from scipy.io.wavfile import write
import numpy as np

def generate_log_sweep(duration, sr=44100, filename="log_sweep.wav"):
    """
    Generates a log sweep of length <duration> and saves it to a file.
    """

    t = np.linspace(0, duration, sr * duration)
    signal = chirp(t, f0=20, f1=20000, t1=duration, method='logarithmic')
    write(filename, sr, signal)
    return signal
    


def generate_pink_RPMS(duration, sr=44100, filename="pink_rpms.wav"):

    # Generate white noise
    white_noise = np.random.randn(duration * sr)
    
    # Compute FFT of white noise
    white_fft = np.fft.rfft(white_noise)
    
    # Compute frequency bins
    freqs = np.fft.rfftfreq(duration * sr, d=1/sr)
    
    # Compute scaling factors for each frequency bin to create pink noise
    scale = np.zeros_like(freqs)
    scale[1:] = 1 / np.sqrt(freqs[1:])  # Exclude DC component
    
    # Apply scaling to FFT of white noise
    pink_fft = white_fft * scale
    
    # Inverse FFT to obtain pink noise
    pink_noise = np.fft.irfft(pink_fft)
    
    # Normalize to 16-bit range
    pink_noise *= 32767 / np.max(np.abs(pink_noise))

    pink_noise = pink_noise.astype(np.int16)

    print(pink_noise.dtype)

    write(filename, sr, pink_noise)
    
    return pink_noise

def generate_pink_noise(n_samples, sample_rate):
    # Generate white noise
    white_noise = np.random.randn(n_samples)
    
    # Compute FFT of white noise
    white_fft = np.fft.rfft(white_noise)
    
    # Compute frequency bins
    freqs = np.fft.rfftfreq(n_samples, d=1/sample_rate)
    
    # Compute scaling factors for each frequency bin to create pink noise
    scale = np.zeros_like(freqs)
    scale[1:] = 1 / np.sqrt(freqs[1:])  # Exclude DC component
    
    # Apply scaling to FFT of white noise
    pink_fft = white_fft * scale
    
    # Inverse FFT to obtain pink noise
    pink_noise = np.fft.irfft(pink_fft)
    
    # Normalize to 16-bit range
    pink_noise *= 32767 / np.max(np.abs(pink_noise))
    
    return pink_noise.astype(np.int16)