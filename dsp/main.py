from scipy.io import wavfile
import noisereduce as nr 
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
from scipy import signal
import pandas as pd
import time

from multiprocessing import Pool
from tqdm import tqdm

from lib.ip import *
from lib.load_audio_files import get_audio_files
from lib.metrics import *
from lib.optimize import *

import warnings
warnings.filterwarnings("ignore") # overkill to ignore the warnings from lib

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inverse problem solving for inside-out guitars")
    parser.add_argument('-s', '--source', help='Source guitar for IR calculation (the one we\'ll be playing)', default=None)
    parser.add_argument('-t', '--target', help='Target guitar for IR calculation (the one we want to model)', default=None)
    parser.add_argument('-v', '--volume', help='Volume to use for IR calc (of recording data)', default="loud")
    parser.add_argument('-r', '--ring', help='use data with ring?', action='store_true', default=False)
    parser.add_argument('-d', '--data', help='data directory', default='./Guitar_Data_REAL')
    args = parser.parse_args()

    guitar_data = get_audio_files()

    data_conf = {
        'excitation_types': ['sweep', 'rpms'], 
        'excitation_lengths': ['3s_excitation', '5s_excitation', '10s_excitation'],
        'volumes': ['loud', 'med', 'soft'], 
        'variants': ['no_ring', 'ring']
    }

    guitars = list(guitar_data.keys())
    print(guitars)
    # for i in ['bad_takamine_EG440SC', "Vi_Yamaha_F335", "Classical_Unknown"]:
    #     print(i)
    #     guitars.remove(i) # bc of time crunch for poster, to be removed.
    # # guitars.remove('bad_takamine_EG440SC')

    print(guitars)

    df = pd.DataFrame(columns=['IR', "guitar_mapping", "mic_mapping", "excitation_type", "excitation_length", "has_ring", "volume", "if_params", "weiner_params", "acdw_params", "Inverse_Filtering_Similarity_Melody", "Weiner_Similarity_Melody", "ACDW_Similarity_Melody", "Inverse_Filtering_Similarity_Chords", "Weiner_Similarity_Chords", "ACDW_Similarity_Chords"])
    df_i = 0 # to keep track of what row to add our stuff to

    for source_guitar in tqdm(guitars):
        source_melody_rate_piezo, source_melody_piezo  = wavfile.read(guitar_data[source_guitar]['played_melody']['piezo'])
        source_melody_rate_mic, source_melody_mic  = wavfile.read(guitar_data[source_guitar]['played_melody']['mic'])
        source_chords_rate_piezo, source_chords_piezo  = wavfile.read(guitar_data[source_guitar]['played_chords']['piezo'])
        source_chords_rate_mic, source_chords_mic  = wavfile.read(guitar_data[source_guitar]['played_chords']['mic'])

        source_melodies = {'mic': source_melody_mic, 'piezo': source_melody_piezo}
        source_chords = {'mic': source_chords_mic, 'piezo': source_chords_piezo}

        targets = [guitar for guitar in guitars if guitar is not source_guitar]

        def compute_ir_to_target(target_guitar):
        #for target_guitar in targets:
            print(f'----------------data for {source_guitar} to {target_guitar}')

            target_melody_rate_piezo, target_melody_piezo = wavfile.read(guitar_data[target_guitar]['played_melody']['piezo'])
            target_melody_rate_mic, target_melody_mic = wavfile.read(guitar_data[target_guitar]['played_melody']['mic'])
            target_chords_rate_piezo, target_chords_piezo = wavfile.read(guitar_data[target_guitar]['played_chords']['piezo'])
            target_chords_rate_mic, target_chords_mic = wavfile.read(guitar_data[target_guitar]['played_chords']['mic'])

            target_melodies = {'mic': target_melody_mic, 'piezo': target_melody_piezo}
            target_chords = {'mic': target_chords_mic, 'piezo': target_chords_piezo}

            jobs = [['mic', 'mic'], ['piezo', 'mic']]


            # TODO: test piezo-mic, piezo-piezo, mic-mic, and also all_frets to all_frets, open_strings to open_strings
            # correlation shoul be done for melody and chords? idk 
            ir_data = []

            for excitation_len in tqdm(data_conf['excitation_lengths'], desc=f"Excitations"):
                for excitation_type in data_conf['excitation_types']:
                    for variant in data_conf['variants']:
                        for volume in data_conf['volumes']:
                            ir_dir = Path(f'./irs/{source_guitar}_to_{target_guitar}/{excitation_len}/{excitation_type}/{variant}/{volume}')
                            ir_dir.mkdir(parents=True, exist_ok=True) 

                            # load data
                            source_rate_mic, source_signal_mic  = wavfile.read("./" + str(guitar_data[source_guitar][excitation_len][excitation_type][variant][volume]['mic']))
                            source_rate_piezo, source_signal_piezo = wavfile.read(guitar_data[source_guitar][excitation_len][excitation_type][variant][volume]['piezo'])
                            target_rate_mic, target_signal_mic = wavfile.read(guitar_data[target_guitar][excitation_len][excitation_type][variant][volume]['mic'])
                            target_rate_piezo, target_signal_piezo = wavfile.read(guitar_data[target_guitar][excitation_len][excitation_type][variant][volume]['piezo'])

                            assert len(source_signal_mic) != 0, "didn't read file"
                            assert len(source_signal_piezo) != 0, "didn't read file"
                            assert len(target_signal_mic) != 0, "didn't read file"
                            assert len(target_signal_piezo) != 0, "didn't read file"
                            # reduce noise
                            source_signal_mic = nr.reduce_noise(y=source_signal_mic, sr=source_rate_mic)
                            source_signal_piezo = nr.reduce_noise(y=source_signal_piezo, sr=source_rate_piezo)
                            target_signal_mic = nr.reduce_noise(y=target_signal_mic, sr=target_rate_mic)
                            target_signal_piezo = nr.reduce_noise(y=target_signal_piezo, sr=target_rate_piezo)
                            

                            source_types = {'mic': source_signal_mic, 'piezo': source_signal_piezo}
                            target_types = {'mic': target_signal_mic, 'piezo': target_signal_piezo}

                            top_cut_window_values = np.arange(0, 600, 100)
                            ir_len_values = lambda length: [length//x for x in np.arange(1, 7, 2)] # length//x for x in [1...10]
                            SNR_values = np.arange(2, 40, 10)
                            acdw_window_end = np.arange(700, 200, -100)

                            def compute_ir_with_data(mapping):

                                source_type = mapping[0]
                                target_type = mapping[1]

                                # ir_inverse_filtering, _, params_if = get_best_inverse_filter(source_types[source_type], target_types[target_type], source_melodies[source_type], target_melodies[target_type])
                                ir_weiner, _, params_weiner = get_best_weiner(source_types[source_type], target_types[target_type], SNR_values, top_cut_window_values, source_melodies[source_type], target_melodies[target_type])
                                ir_acdw, _, params_acdw = get_best_acdw(source_types[source_type], target_types[target_type], source_melodies[source_type], target_melodies[target_type])

                                ir_inverse_filtering = inverse_filter(source_types[source_type], target_types[target_type])
                                # ir_weiner = wiener_deconv(source_types[source_type], target_types[target_type])
                                # ir_acdw = ACDW(source_types[source_type], target_types[target_type])

                                ir_inverse_filtering = ir_inverse_filtering / np.max(np.abs(ir_inverse_filtering))
                                ir_weiner = ir_weiner / np.max(np.abs(ir_weiner))
                                ir_acdw = ir_acdw / np.max(np.abs(ir_acdw))


                                params_if = None
                                params_weiner = None


                                wavfile.write(str(ir_dir) + f"/{source_type}_to_{target_type}_inverse_ir.wav", 44100, ir_inverse_filtering.astype('float32'))
                                wavfile.write(str(ir_dir) + f"/{source_type}_to_{target_type}_weiner_ir.wav", 44100, ir_weiner.astype('float32'))
                                wavfile.write(str(ir_dir) + f"/{source_type}_to_{target_type}_acdw_ir.wav", 44100, ir_acdw.astype('float32'))


                                generated_chord_inverse_filtering = signal.fftconvolve(source_chords[source_type], ir_inverse_filtering)
                                generated_chord_weiner = signal.fftconvolve(source_chords[source_type], ir_weiner)
                                generated_chord_acdw = signal.fftconvolve(source_chords[source_type], ir_acdw)

                                generated_chord_inverse_filtering = generated_chord_inverse_filtering / np.max(np.abs(generated_chord_inverse_filtering))
                                generated_chord_weiner = generated_chord_weiner / np.max(np.abs(generated_chord_weiner))
                                generated_chord_acdw = generated_chord_acdw / np.max(np.abs(generated_chord_acdw))

                                chord_similarity_inverse_filtering = compute_MFCC_similarity(generated_chord_inverse_filtering, target_chords[target_type])
                                chord_similarity_weiner = compute_MFCC_similarity(generated_chord_weiner, target_chords[target_type])
                                chord_similarity_acdw = compute_MFCC_similarity(generated_chord_acdw, target_chords[target_type])
                                # chord_correlation_inverse_filtering = basic_correlation(generated_chord_inverse_filtering[:44100*2], target_chords[target_type[:44100*2]])
                                # chord_correlation_weiner = basic_correlation(generated_chord_weiner[:44100*2], target_chords[target_type[:44100*2]])
                                # chord_correlation_acdw = basic_correlation(generated_chord_acdw[:44100*2], target_chords[target_type[:44100*2]])

                                generated_melody_inverse_filtering = signal.fftconvolve(source_melodies[source_type], ir_inverse_filtering)
                                generated_melody_weiner = signal.fftconvolve(source_melodies[source_type], ir_weiner)
                                generated_melody_acdw = signal.fftconvolve(source_melodies[source_type], ir_acdw)

                                generated_melody_inverse_filtering = generated_melody_inverse_filtering / np.max(np.abs(generated_melody_inverse_filtering))
                                generated_melody_weiner = generated_melody_weiner / np.max(np.abs(generated_melody_weiner))
                                generated_melody_acdw = generated_melody_acdw / np.max(np.abs(generated_melody_acdw))
                                

                                melody_similarity_inverse_filtering = compute_MFCC_similarity(generated_melody_inverse_filtering, target_melodies[target_type])
                                melody_similarity_weiner = compute_MFCC_similarity(generated_melody_weiner, target_melodies[target_type])
                                melody_similarity_acdw = compute_MFCC_similarity(generated_melody_acdw, target_melodies[target_type])
                                # melody_correlation_inverse_filtering = basic_correlation(generated_melody_inverse_filtering[:44100*2], target_melodies[target_type][:44100*2])
                                # melody_correlation_weiner = basic_correlation(generated_melody_weiner[:44100*2], target_melodies[target_type][:44100*2])
                                # melody_correlation_acdw = basic_correlation(generated_melody_acdw[:44100*2], target_melodies[target_type][:44100*2])
                                
                                return [f'{source_guitar}_{source_type}_to_{target_guitar}_{target_type}', f'{source_guitar}_to_{target_guitar}', f'{source_type}_to_{target_type}', excitation_type, excitation_len, variant, volume] + [params_if, params_weiner, params_acdw, melody_similarity_inverse_filtering, melody_similarity_weiner, melody_similarity_acdw, chord_similarity_inverse_filtering, chord_similarity_weiner, chord_similarity_acdw]

                            for job in jobs:
                                results = compute_ir_with_data(job)
                                ir_data.append(results)
                                # df.loc[df_i] = result
                                # df_i = df_i + 1
            return ir_data
        

        with Pool(processes=6) as pool:
            results = pool.map(compute_ir_to_target, targets)
            for result_arr in results:
                for row in result_arr:
                    df.loc[df_i] = row
                    df_i = df_i + 1
            
            
            # TODO: copy/pasted code below, should really be fixed....
            # source_rate_mic, source_signal_mic  = wavfile.read("./" + str(guitar_data[source_guitar]['all_frets_finger']['mic']))
            # source_rate_piezo, source_signal_piezo = wavfile.read(guitar_data[source_guitar]['all_frets_finger']['piezo'])
            # target_rate_mic, target_signal_mic = wavfile.read(guitar_data[target_guitar]['all_frets_finger']['mic'])
            # target_rate_piezo, target_signal_piezo = wavfile.read(guitar_data[target_guitar]['all_frets_finger']['piezo'])
            # source_types = {'mic': source_signal_mic, 'piezo': source_signal_piezo}
            # target_types = {'mic': target_signal_mic, 'piezo': target_signal_piezo}

            # def compute_ir_with_data(mapping):

            #     source_type = mapping[0]
            #     target_type = mapping[1]

            #     ir_inverse_filtering = inverse_filter(source_types[source_type], target_types[target_type])
            #     ir_weiner = wiener_deconv(source_types[source_type], target_types[target_type])
            #     ir_acdw = ACDW(source_types[source_type], target_types[target_type])

            #     wavfile.write(str(ir_dir) + f"/{source_type}_to_{target_type}_inverse_ir.wav", 44100, ir_inverse_filtering)
            #     wavfile.write(str(ir_dir) + f"/{source_type}_to_{target_type}_weiner_ir.wav", 44100, ir_weiner)
            #     wavfile.write(str(ir_dir) + f"/{source_type}_to_{target_type}_acdw_ir.wav", 44100, ir_acdw)


            #     generated_chord_inverse_filtering = signal.fftconvolve(source_chords[source_type], ir_inverse_filtering)
            #     generated_chord_weiner = signal.fftconvolve(source_chords[source_type], ir_weiner)
            #     generated_chord_acdw = signal.fftconvolve(source_chords[source_type], ir_acdw)

            #     chord_similarity_inverse_filtering = compute_MFCC_similarity(generated_chord_inverse_filtering, target_chords[target_type])
            #     chord_similarity_weiner = compute_MFCC_similarity(generated_chord_weiner, target_chords[target_type])
            #     chord_similarity_acdw = compute_MFCC_similarity(generated_chord_acdw, target_chords[target_type])
            #     chord_correlation_inverse_filtering = basic_correlation(generated_chord_inverse_filtering[:44100*2], target_chords[target_type[:44100*2]])
            #     chord_correlation_weiner = basic_correlation(generated_chord_weiner[:44100*2], target_chords[target_type[:44100*2]])
            #     chord_correlation_acdw = basic_correlation(generated_chord_acdw[:44100*2], target_chords[target_type[:44100*2]])

            #     generated_melody_inverse_filtering = signal.fftconvolve(source_melodies[source_type], ir_inverse_filtering)
            #     generated_melody_weiner = signal.fftconvolve(source_melodies[source_type], ir_weiner)
            #     generated_melody_acdw = signal.fftconvolve(source_melodies[source_type], ir_acdw)

            #     melody_similarity_inverse_filtering = compute_MFCC_similarity(generated_melody_inverse_filtering, target_melodies[target_type])
            #     melody_similarity_weiner = compute_MFCC_similarity(generated_melody_weiner, target_melodies[target_type])
            #     melody_similarity_acdw = compute_MFCC_similarity(generated_melody_acdw, target_melodies[target_type])
            #     melody_correlation_inverse_filtering = basic_correlation(generated_melody_inverse_filtering[:44100*2], target_melodies[target_type][:44100*2])
            #     melody_correlation_weiner = basic_correlation(generated_melody_weiner[:44100*2], target_melodies[target_type][:44100*2])
            #     melody_correlation_acdw = basic_correlation(generated_melody_acdw[:44100*2], target_melodies[target_type][:44100*2])
                
            #     chord_correlation_inverse_filtering = chord_correlation_weiner = chord_correlation_acdw = melody_correlation_inverse_filtering = melody_correlation_weiner = melody_correlation_acdw = None
            #     return [f'{source_guitar}_{source_type}_to_{target_guitar}_{target_type}_all_frets', f'{source_guitar}_to_{target_guitar}', f'{source_type}_to_{target_type}', "'all_frets", None, None, None] + [melody_similarity_inverse_filtering, melody_correlation_inverse_filtering, melody_similarity_weiner, melody_correlation_weiner, melody_similarity_acdw, melody_correlation_acdw, chord_similarity_inverse_filtering, chord_correlation_inverse_filtering, chord_similarity_weiner, chord_correlation_weiner, chord_similarity_acdw, chord_correlation_acdw]

            # with Pool(processes=4) as pool:
            #     results = pool.map(compute_ir_with_data, jobs)
            #     for result in results:
            #         df.loc[df_i] = result
            #         df_i = df_i + 1
    df.to_csv(f'results_{int(time.time())}.csv')









    
    