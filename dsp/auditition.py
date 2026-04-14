from scipy.io import wavfile
import noisereduce as nr 
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
from scipy import signal
import pandas as pd
import sys

from lib.load_audio_files import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inverse problem solving for inside-out guitars")
    parser.add_argument('-t', '--target', help='Target guitar (the one we want to model)')
    parser.add_argument('-s', '--source', help='Source Guitar (what would be played)')
    parser.add_argument('-a', '--audition', help='Which kind of audition: chords, melody, excerpt', default='played_chords')
    parser.add_argument('-p', '--convert_from', help='type of conversion. e.g. piezo', default='piezo')
    parser.add_argument('-m', '--convert_to', help='type of conversion. e.g. mic', default='mic')
    parser.add_argument('-l', '--excitation_length', help='excitation length', default='5s_excitation')
    parser.add_argument('-e', '--excitation', help='rpms or sweep excitation', default='sweep')
    parser.add_argument('-v', '--volume', help='volume to use for IR', default='loud')
    parser.add_argument('-r', '--ring', help='whether to use ring or no_ring ir', default='no_ring')
    parser.add_argument('-i', '--ir', help='ir type', default='inverse')
    
    args = parser.parse_args()

    if not args.target and not args.source:
        print("Both source and target guitars required")
        parser.print_help()
        sys.exit(1)


    guitar_data = get_audio_files()

    src_rate, src_audio = wavfile.read("./" + str(guitar_data[args.source][args.audition][args.convert_from]))
    target_rate, target_audio = wavfile.read("./" + str(guitar_data[args.target][args.audition][args.convert_to]))

    ir_rate, ir_data = wavfile.read(f'./irs/{args.source}_to_{args.target}/{args.excitation_length}/{args.excitation}/{args.ring}/{args.volume}/{args.convert_from}_to_{args.convert_to}_{args.ir}_ir.wav')
    generated_signal = signal.convolve(src_audio, ir_data[:44100//2])

    print(generated_signal.dtype)

    wavfile.write('output/unprocessed_input.wav', 44100, src_audio)
    wavfile.write('output/reference_output.wav', 44100, target_audio)
    wavfile.write('output/generated_output.wav', 44100, generated_signal)

    # p = pyaudio.PyAudio()

    # stream = p.open(format=FORMAT,
    #             channels=CHANNELS,
    #             rate=FS,
    #             output=True)

    # stream.write