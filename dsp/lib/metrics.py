import librosa
from dtw import dtw
from fastdtw import fastdtw
import numpy as np
from scipy.fft import fft

def compute_MFCC_similarity(signal_1, signal_2, sr_1=44100, sr_2=44100):
    """
    Basically does the MFCC, computes the DTW, and then gets the euclidian distance between the two.

    Similarity is done by just calculating 1 / (1 + distance), so that signals with 0 distance have
    a similarity of 1 while signals with lots of distance tend to have a closer to 0. 
    """
    
    # normalize signals
    signal_1 = signal_1 / np.linalg.norm(signal_1)
    signal_2 = signal_2 / np.linalg.norm(signal_2)

    # first generate MFCC
    mfcc_1 = librosa.feature.mfcc(y=signal_1, sr=sr_1)[2:13]
    mfcc_2 = librosa.feature.mfcc(y=signal_2, sr=sr_2)[2:13]


    # alginment = dtw(mfcc_1.T, mfcc_2.T)

    min_length = min(len(mfcc_1), len(mfcc_2))
    similarity = np.abs(np.corrcoef(signal_1[:min_length], signal_2[:min_length]))[0, 1]
    return similarity 


def compute_MFCC_similarity_dtw(signal_1, signal_2, sr_1=44100, sr_2=44100):
    """
    Basically does the MFCC, computes the DTW, and then gets the euclidian distance between the two.

    Similarity is done by just calculating 1 / (1 + distance), so that signals with 0 distance have
    a similarity of 1 while signals with lots of distance tend to have a closer to 0. 
    """

    # TODO: ideally do dtw on the input signals

    try:
    # normalize signals
        signal_1 = signal_1 / np.linalg.norm(signal_1)
        signal_2 = signal_2 / np.linalg.norm(signal_2)

        length = min(len(signal_1), len(signal_2))

        # first generate MFCC
        mfcc_1 = librosa.feature.mfcc(y=signal_1, sr=sr_1)[2:13]
        mfcc_2 = librosa.feature.mfcc(y=signal_2, sr=sr_2)[2:13] # TODO: cut to like [2:13 or something? idk which correlate to timbre]


        dist, path = fastdtw(mfcc_1.T, mfcc_2.T)

        # min_length = min(len(mfcc_1), len(mfcc_2))
        # similarity = np.abs(np.corrcoef(signal_1[:min_length], signal_2[:min_length]))[0, 1]
        # return similarity
        return 1 / (1 + abs(dist))

    except:
        return 100 # really hacky solution..... probably not a great move. 


def compute_FFT_similarity(signal_1, signal_2, sample_end=44100):
    """
    Compute the spectral magnitude difference
    """

    length = min(len(signal_1), len(signal_2))

    signal_1 = signal_1[:length]
    signal_2 = signal_2[:length]

    signal_1 = signal_1 / np.linalg.norm(signal_1)
    signal_2 = signal_2 / np.linalg.norm(signal_2)

    fft_1 = fft(signal_1[:sample_end])
    fft_2 = fft(signal_2[:sample_end])
    

    # abs to get a single number for the strength of each frequency, not the phase
    abs_1 = np.abs(fft_1)
    abs_2 = np.abs(fft_2)

    distance = np.linalg.norm(abs_1 - abs_2)
    similarity = 1 / (1 + distance)
    return similarity

def basic_correlation(signal_1, signal_2, sample_end=44100):

    return np.abs(np.corrcoef(signal_1[:sample_end], signal_2[:sample_end])[0, 1])
