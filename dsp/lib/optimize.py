"""
!! Important! This is really bad code! It should probably use actual stochastic gradient descent 
so that local minima aren't as much of a problem, and gradient influencing the hop size 
would make this so much more performant. Also, multiple outputs references should be used 
to make the judgement, and the MFCC similarity as a metric is probably not the best metric 
that could be used.
"""

from .ip import *
from .metrics import *

import numpy as np

top_cut_window_values = np.arange(0, 400, 10)
ir_len_values = lambda length: [length//x for x in np.arange(1, 10, 1)] # length//x for x in [1...10]
gen_window_end_vals = lambda length: [length//x for x in np.arange(10, 1, -3)] # length//x for x in [1...10]
SNR_values = np.arange(0, 40, 2)
acdw_window_end = np.arange(0, 400, 50)

def get_best_inverse_filter(x, y, audition_sig, reference_sig, max_strikes=3):
    assert len(x) == len(y), "both signals need to have the same length"
    best_performance = 0
    best_ir = None
    best_length = None
    strikes = 0
    for length in ir_len_values(len(x)):
        ir = inverse_filter(x, y, ir_len=length)
        similarity = compute_MFCC_similarity_dtw(reference_sig, signal.fftconvolve(audition_sig, ir))
        if similarity > best_performance:
            best_ir = ir
            best_performance = similarity
            best_length = length
        elif similarity <= best_performance:
            strikes = strikes + 1
            if strikes >= max_strikes:
                break
    return (best_ir, best_performance, {'ir_length': best_length})

def get_best_weiner(x, y, snr_vals, window_cut_vals, audition_sig, reference_sig, max_strikes=3):
    """
    This assumes that IR length and window_cut/snr are independent. This is based on vibes, and 
    probably shouldn't be assumed, but I need this to run in a reasonable time or I will explode 
    into flames.
    """
    assert len(x) == len(y), "both signals need to have the same length"
    best_performance = 0
    best_ir = None
    strikes = 0
    best_ir_length = 44100//2
    best_snr = snr_vals[0]
    best_window_cut = window_cut_vals[0]

    ir_lengths = ir_len_values(len(x))

    for snr in snr_vals:
        for window_cut in window_cut_vals:
            ir = wiener_deconv(x, y, window_cut=window_cut, snr=snr)
            similarity = compute_MFCC_similarity_dtw(reference_sig, signal.fftconvolve(audition_sig, ir))
            best_ir = ir
            if similarity > best_performance:
                # print('better performance in weiner!!')

                best_ir = ir
                best_snr = snr
                best_window_cut = window_cut
                best_performance = similarity 
            elif similarity <= best_performance:
                strikes = strikes + 1
                if strikes >= max_strikes:
                    break

    
    

    return (best_ir, best_performance, {'ir_length': best_ir_length, 'snr': best_snr, 'window_cut': best_window_cut})

def get_best_acdw(x, y, audition_sig, reference_sig, max_strikes=3):
    assert len(x) == len(y), "both signals need to have the same length"
    window_end_vals = gen_window_end_vals(len(x))


    best_performance = 0
    best_ir = None
    strikes = 0
    best_ir_length = None
    best_window_end = window_end_vals[0]


    # for length in ir_lengths:
    #     # print(length)
    #     ir = ACDW(x, y, ir_len=length)
    #     similarity = compute_MFCC_similarity_dtw(reference_sig, signal.fftconvolve(audition_sig, ir))
    #     if similarity > best_performance:
    #         best_ir = ir
    #         best_ir_length = length
    #         best_performance = similarity 
    #     elif similarity <= best_performance:
    #         strikes = strikes + 1
    #         if strikes >= max_strikes:
    #             break

    for window_end in window_end_vals:
        ir = ACDW(x, y, window_end=window_end)
        similarity = compute_MFCC_similarity_dtw(reference_sig, signal.fftconvolve(audition_sig, ir))
        best_ir = ir
        if similarity > best_performance:
            best_ir = ir
            best_window_end = window_end
            best_performance = similarity 
        elif similarity <= best_performance:
            strikes = strikes + 1
            if strikes >= max_strikes:
                break
    

    return (best_ir, best_performance, {'ir_length': best_ir_length, 'window_end': best_window_end})