# Inverse Proble Methods. 
from scipy import signal
from scipy.fft import fft, ifft
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile


def inverse_filter(x, y, ir_len=44100//2):
    """
    Naiive inverse filtering. has tunable parameter ir_len, 
    which should be optimized for best performance.

    returns IR that should solve x*IR=y

    note: works best when noise from x and y have been removed as 
    much as possible
    """

    assert len(x) == len(y), "x and y must be the same length"

    x_fft = fft(x)
    y_fft = fft(y)

    H = (y_fft / x_fft).real

    ir = ifft(H).real[:ir_len]

    return ir

def wiener_deconv(x, y, ir_len=44100//2, window_cut=0, snr=20):
    """
    wiener filtering as per https://stanford.edu/class/ee367/reading/lecture6_notes.pdf.
    
    SNR is the tunable parameter here, tbh probably we should
    try to figure out a way to calculate it per-frequency
    """

    assert len(x) == len(y), "x and y must be the same length"

    y_fft = fft(y)  #b as per https://stanford.edu/class/ee367/reading/lecture6_notes.pdf
    x_fft = fft(x)   # c as per https://stanford.edu/class/ee367/reading/lecture6_notes.pdf

    noise_fft = (np.abs(x_fft)**2)/((np.abs(x_fft)**2) + (1/(snr + 1e-10)))
    ir = y_fft/x_fft 
    ir = ir
    
    H = noise_fft * ir
    H = H[:len(H) - window_cut - 10]
    ir = ifft(H).real
    if len(ir) > ir_len:
        ir = ir[:ir_len]
    return ir


def ACDW(x, y, ir_len=44100//2, window_end=None, window_start=0):
    """
    adaptive_cepstral_domain_windowing as per
    https://link.springer.com/chapter/10.1007/978-981-13-1165-9_5

    note: mfcc might be another angle for this
    """

    assert len(x) == len(y), "x and y must be the same length"

    if window_end is None:
        window_end = len(x)

    fft_x = fft(x)
    fft_y = fft(y)

    log_fft_x = np.log10(np.abs(fft_x) + 1e-10)
    log_fft_y = np.log10(np.abs(fft_y) + 1e-10)

    c_x = ifft(log_fft_x).real
    c_y = ifft(log_fft_y).real

    c_ir = c_y - c_x
    c_ir_windowed = c_ir[window_start:window_end]

    ir_FFT = fft(c_ir_windowed)
    ir = ifft(np.power(10, ir_FFT)).real[:ir_len]

    return ir / np.max(np.abs(ir))