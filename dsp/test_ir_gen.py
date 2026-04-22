from scipy.io import wavfile
import noisereduce as nr 
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
from scipy import signal
import pandas as pd
import sys
from lib.ip import *
from lib.optimize import *

from fastdtw import fastdtw

from lib.load_audio_files import *

import warnings
warnings.filterwarnings("ignore") # overkill to ignore the warnings from lib


if __name__ == "__main__":

    data_conf = {
        'excitation_types': ['rpms', 'sweep'],
        'excitation_lengths': ['3s_excitation', '5s_excitation', '10s_excitation'],
        'volumes': ['loud', 'med', 'soft'],
        'variants': ['ring', 'no_ring']
    }

    guitar_data = get_audio_files()
    # TODO: fix, this is bad and hard-coded.
    guitars = ['Bird_Aspen_DH37', 'good_takamine_EG523SC', 'AJ_JJasmine_JF37CD', 'Classical_Unknown', 'bad_takamine_EG440SC', 'Vi_Yamaha_F335']

    conf = {
        'source': guitars[1],
        'target': guitars[5]
    }



    x_rate, x_signal = wavfile.read("./" + str(guitar_data[conf['source']]['10s_excitation']['sweep']['no_ring']['loud']['piezo']))
    y_rate, y_signal = wavfile.read("./" + str(guitar_data[conf['target']]['10s_excitation']['sweep']['no_ring']['loud']['piezo']))

    


    source_melody_rate_piezo, source_melody_piezo  = wavfile.read(guitar_data[conf['source']]['played_melody']['piezo'])
    source_melody_rate_mic, source_melody_mic  = wavfile.read(guitar_data[conf['source']]['played_melody']['mic'])
    source_chords_rate_piezo, source_chords_piezo  = wavfile.read(guitar_data[conf['source']]['played_chords']['piezo'])
    source_chords_rate_mic, source_chords_mic  = wavfile.read(guitar_data[conf['source']]['played_chords']['mic'])
    
    target_melody_rate_piezo, target_melody_piezo  = wavfile.read(guitar_data[conf['target']]['played_melody']['piezo'])
    target_melody_rate_mic, target_melody_mic  = wavfile.read(guitar_data[conf['target']]['played_melody']['mic'])
    target_chords_rate_piezo, target_chords_piezo  = wavfile.read(guitar_data[conf['target']]['played_chords']['piezo'])
    target_chords_rate_mic, target_chords_mic  = wavfile.read(guitar_data[conf['target']]['played_chords']['mic'])

    src_all_frets_rate_piezo, src_all_frets_piezo  = wavfile.read(guitar_data[conf['source']]['all_frets_finger']['piezo'])
    src_all_frets_rate_mic, src_all_frets_mic  = wavfile.read(guitar_data[conf['source']]['all_frets_finger']['mic'])
    target_all_frets_rate_piezo, target_all_frets_piezo  = wavfile.read(guitar_data[conf['target']]['all_frets_finger']['piezo'])
    target_all_frets_rate_mic, target_all_frets_mic  = wavfile.read(guitar_data[conf['target']]['all_frets_finger']['mic'])



    


    print('starting dtw')
    starting_similiarity = compute_MFCC_similarity_dtw(src_all_frets_piezo, target_all_frets_mic)
    print(f'starting sim: {starting_similiarity}')

    top_cut_window_values = np.arange(0, 400, 100)
    ir_len_values = lambda length: [length//x for x in np.arange(1, 7, 2)] # length//x for x in [1...10]
    SNR_values = np.arange(2, 40, 10)
    acdw_window_end = np.arange(400, 200, -100)

    src_rate_melody, src_audio_melody = wavfile.read("./" + str(guitar_data[conf['source']]['played_melody']['piezo']))
    target_rate_melody, target_audio_melody = wavfile.read("./" + str(guitar_data[conf['target']]['played_melody']['piezo']))
    src_rate_chords, src_audio_chords = wavfile.read("./" + str(guitar_data[conf['source']]['played_chords']['piezo']))
    target_rate_chords, target_audio_chords = wavfile.read("./" + str(guitar_data[conf['target']]['played_chords']['piezo']))


    ir_inverse_filtering = inverse_filter(nr.reduce_noise(y=x_signal, sr=x_rate), nr.reduce_noise(y=y_signal, sr=y_rate))
    ir_weiner, _, _ = get_best_weiner(nr.reduce_noise(y=x_signal, sr=x_rate), nr.reduce_noise(y=y_signal, sr=y_rate), snr_vals=SNR_values, window_cut_vals=top_cut_window_values, audition_sig=src_audio_melody, reference_sig=target_audio_melody)
    ir_mel_acdw, _, _ = get_best_acdw(nr.reduce_noise(y=x_signal, sr=x_rate), nr.reduce_noise(y=y_signal, sr=y_rate), audition_sig=src_audio_melody, reference_sig=target_audio_melody)

    

    generated_melody_if = signal.convolve(src_audio_melody, ir_inverse_filtering)
    generated_chords_if = signal.convolve(src_audio_chords, ir_inverse_filtering)
    generated_melody_weiner = signal.convolve(src_audio_melody, ir_weiner)
    generated_chords_weiner = signal.convolve(src_audio_chords, ir_weiner)
    generated_melody_acdw = signal.convolve(src_audio_melody, ir_mel_acdw)
    generated_chords_acdw = signal.convolve(src_audio_chords, ir_mel_acdw)

    generated_melody_if = generated_melody_if / np.max(np.abs(generated_melody_if))
    generated_chords_if = generated_chords_if / np.max(np.abs(generated_chords_if))
    generated_melody_weiner = generated_melody_weiner / np.max(np.abs(generated_melody_weiner))
    generated_chords_weiner = generated_chords_weiner / np.max(np.abs(generated_chords_weiner))
    generated_melody_acdw = generated_melody_acdw / np.max(np.abs(generated_melody_acdw))
    generated_chords_acdw = generated_chords_acdw / np.max(np.abs(generated_chords_acdw))
    sim_if = compute_MFCC_similarity_dtw(generated_melody_if, target_melody_mic) # TODO: maybe make it be like... using an average of stuff?
    sim_weiner = compute_MFCC_similarity_dtw(generated_melody_weiner, target_melody_mic)
    sim_acdw_mel = compute_MFCC_similarity_dtw(generated_melody_acdw, target_melody_mic)

    print(f'if sim: {sim_if}, weiner: {sim_weiner}, acdw_mel: {sim_acdw_mel}')


    wavfile.write('output_optim/if/unprocessed_input_melody.wav', 44100, src_audio_melody)
    wavfile.write('output_optim/if/reference_output_melody.wav', 44100, target_audio_melody)
    wavfile.write('output_optim/if/generated_output_melody.wav', 44100, generated_melody_if)
    wavfile.write('output_optim/if/unprocessed_input_melody.wav', 44100, src_audio_melody)
    wavfile.write('output_optim/if/reference_output_melody.wav', 44100, target_audio_melody)
    wavfile.write('output_optim/if/generated_output_melody.wav', 44100, generated_melody_if)
    wavfile.write('output_optim/weiner/unprocessed_input_chords.wav', 44100, src_audio_melody)
    wavfile.write('output_optim/weiner/reference_output_melody.wav', 44100, target_audio_melody)
    wavfile.write('output_optim/weiner/generated_output_melody.wav', 44100, generated_melody_weiner)
    wavfile.write('output_optim/acdw/unprocessed_input_chords.wav', 44100, src_audio_melody)
    wavfile.write('output_optim/acdw/reference_output_melody.wav', 44100, target_audio_melody)
    wavfile.write('output_optim/acdw/generated_output_melody.wav', 44100, generated_melody_acdw)

    wavfile.write('output_optim/if/unprocessed_input_chords.wav', 44100, src_audio_chords)
    wavfile.write('output_optim/if/reference_output_chords.wav', 44100, target_audio_chords)
    wavfile.write('output_optim/if/generated_output_chords.wav', 44100, generated_chords_if)
    wavfile.write('output_optim/if/unprocessed_input_chords.wav', 44100, src_audio_chords)
    wavfile.write('output_optim/if/reference_output_chords.wav', 44100, target_audio_chords)
    wavfile.write('output_optim/if/generated_output_chords.wav', 44100, generated_chords_if)
    wavfile.write('output_optim/weiner/unprocessed_input_chords.wav', 44100, src_audio_chords)
    wavfile.write('output_optim/weiner/reference_output_chords.wav', 44100, target_audio_chords)
    wavfile.write('output_optim/weiner/generated_output_chords.wav', 44100, generated_chords_weiner)
    wavfile.write('output_optim/acdw/unprocessed_input_chords.wav', 44100, src_audio_chords)
    wavfile.write('output_optim/acdw/reference_output_chords.wav', 44100, target_audio_chords)
    wavfile.write('output_optim/acdw/generated_output_chords.wav', 44100, generated_chords_acdw)
