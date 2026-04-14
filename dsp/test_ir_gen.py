from scipy.io import wavfile
import noisereduce as nr 
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
from scipy import signal
import pandas as pd
import sys

from lib.load_audio_files import *

# if __name__ == "__main__":

#     data_conf = {
#         'excitation_types': ['rpms', 'sweep'],
#         'excitation_lengths': ['3s_excitation', '5s_excitation', '10s_excitation'],
#         'volumes': ['loud', 'med', 'soft'],
#         'variants': ['ring', 'no_ring']
#     }

#     guitar_data = get_audio_files()
#     # TODO: fix, this is bad and hard-coded.
#     guitars = ['Bird_Aspen_DH37', 'good_takamine_EG523SC', 'AJ_JJasmine_JF37CD', 'Classical_Unknown', 'bad_takamine_EG440SC', 'Vi_Yamaha_F335']


#     input_rate, input_signal = wavfile.read("./" + guitar_data])
    

#     ir_rate, ir_data = wavfile.read(f'./irs/{args.source}_to_{args.target}/{args.excitation_length}/{args.excitation}/{args.ring}/{args.volume}/{args.convert_from}_to_{args.convert_to}_{args.ir}_ir.wav')
#     generated_signal = signal.convolve(src_audio, ir_data[:44100//2])

#     print(generated_signal.dtype)

#     wavfile.write('output/unprocessed_input.wav', 44100, src_audio)
#     wavfile.write('output/reference_output.wav', 44100, target_audio)
#     wavfile.write('output/generated_output.wav', 44100, generated_signal)

#     p = pyaudio.PyAudio()

#     stream = p.open(format=FORMAT,
#                 channels=CHANNELS,
#                 rate=FS,
#                 output=True)

#     stream.write