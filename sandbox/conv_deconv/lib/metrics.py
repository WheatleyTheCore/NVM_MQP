import librosa
from dtw import dtw
import numpy as np
from scipy.fft import fft

def compute_MFCC_similarity(signal_1, sr_1, signal_2, sr_2):
    """
    Basically does the MFCC, computes the DTW, and then gets the euclidian distance between the two.

    Similarity is done by just calculating 1 / (1 + distance), so that signals with 0 distance have
    a similarity of 1 while signals with lots of distance tend to have a closer to 0. 
    """

    # normalize signals
    signal_1 = signal_1 / np.linalg.norm(signal_1)
    signal_2 = signal_2 / np.linalg.norm(signal_2)

    # first generate MFCC
    mfcc_1 = librosa.feature.mfcc(y=signal_1, sr=sr_1)
    mfcc_2 = librosa.feature.mfcc(y=signal_2, sr=sr_2)


    alginment = dtw(mfcc_1.T, mfcc_2.T)
    similarity = 1/ (1 + alginment.distance)
    return similarity 


def compute_FFT_similarity(signal_1, signal_2):
    """
    Compute the spectral magnitude difference
    """

    signal_1 = signal_1 / np.linalg.norm(signal_1)
    signal_2 = signal_2 / np.linalg.norm(signal_2)

    fft_1 = fft(signal_1)
    fft_2 = fft(signal_2)
    

    # abs to get a single number for the strength of each frequency, not the phase
    abs_1 = np.abs(fft_1)
    abs_2 = np.abs(fft_2)

    distance = np.linalg.norm(abs_1 - abs_2)
    similarity = 1 / (1 + distance)
    return similarity

def compute_dtw_correlation(signal_1, signal_2):
    alignment = dtw(signal_1, signal_2, keep_internals=True)
    aligned_signal_1 = [signal_1[i] for i in alignment.index1]
    aligned_signal_2 = [signal_2[i] for i in alignment.index2]

    return np.corrcoef(aligned_signal_1, aligned_signal_2)[0, 1]
