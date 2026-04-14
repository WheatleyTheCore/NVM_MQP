from pathlib import Path
import warnings

def get_audio_files(data_dir='./Guitar_Data_REAL'):
    """
    Populate dict with excitations files of guitar data stored at `MQP_Data/<guitar>
    Structure is:
    /3s_excitation
        /sweep
            /no_ring
                /loud
                    piezo: filename
                    mic: filname
                /med
                    piezo: filename
                    mic:   filename
                ...
        /rpms
            /no_ring
                /loud
                    piezo: filename
                    mic: filname
                /med
                    piezo: filename
                    mic:   filename
                ...
    ...

    """
    guitar_data = dict()
    guitars = [str(x).split('/')[-1] for x in Path(data_dir).glob("*") if x.is_dir()]
    if 'excitation_signals' in guitars:
        guitars.remove('excitation_signals') # hard-coded value here is bad.
    excitation_lengths = ['3s_excitation', '5s_excitation', '10s_excitation']
    excitation_variants = ['rpms', 'sweep']
    ring_variants = ['ring', 'no_ring']
    volume_variants = ['loud', 'med', 'soft']
    recording_variants = ['piezo', 'mic']

    for guitar_subdir in guitars:
        guitar_data[guitar_subdir] = dict()
        for excitation_length in excitation_lengths:
            excitation_files = list(Path(f'{data_dir}/{guitar_subdir}/{excitation_length}').glob("*.wav"))
            
            # TODO: this is kinda incomprehensible. this needs to be broken out more cleanly. :(
            if (excitation_length not in guitar_data[guitar_subdir].keys()):
                guitar_data[guitar_subdir][excitation_length] = dict()
            for excitation_variant in excitation_variants:
                if (excitation_variant not in guitar_data[guitar_subdir][excitation_length].keys()):
                    guitar_data[guitar_subdir][excitation_length][excitation_variant] = dict()
                for ring_variant in ring_variants:
                    if ring_variant not in guitar_data[guitar_subdir][excitation_length][excitation_variant].keys():
                        guitar_data[guitar_subdir][excitation_length][excitation_variant][ring_variant] = dict() 
                    for volume in volume_variants:
                        if volume not in guitar_data[guitar_subdir][excitation_length][excitation_variant][ring_variant].keys():
                            guitar_data[guitar_subdir][excitation_length][excitation_variant][ring_variant][volume] = dict()
                        for recording_variant in recording_variants:
                            file_search_properties = [excitation_variant, ring_variant, volume, recording_variant]
                            matching_files = [x for x in excitation_files if all(prop in str(x) for prop in file_search_properties)]
                            if ring_variant == 'ring':
                                matching_files = [x for x in matching_files if 'no_ring' not in str(x)] # TODO: need to not match 'no_ring' values with ring when running first. def bad for performance.
                            if len(matching_files) == 0:
                                warnings.warn(f"{guitar_subdir} {excitation_length} {excitation_variant} {ring_variant} {volume} {recording_variant} not found!")
                            guitar_data[guitar_subdir][excitation_length][excitation_variant][ring_variant][volume][recording_variant] = matching_files[0] # TODO: handle multiple matches
                            

        non_excitation_files = list(Path(f'./{data_dir}/{guitar_subdir}').glob("*.wav"))
        non_excitation_data = ['all_frets_finger', 'excerpt', 'open_strings', 'played_chords', 'played_melody']
        for data_type in non_excitation_data:
            mic_file = [x for x in non_excitation_files if all(prop in str(x) for prop in [data_type, 'mic'])]
            piezo_file = [x for x in non_excitation_files if all(prop in str(x) for prop in [data_type, 'piezo'])]

            if len(mic_file) == 0:
                warnings.warn(f'{guitar_subdir} {data_type} mic file not found!')
            if len(piezo_file) == 0:
                warnings.warn(f'{guitar_subdir} {data_type} piezo file not found!')

            if data_type not in guitar_data[guitar_subdir].keys():
                guitar_data[guitar_subdir][data_type] = dict()
            guitar_data[guitar_subdir][data_type]['mic'] = mic_file[0]
            guitar_data[guitar_subdir][data_type]['piezo'] = piezo_file[0]

    return guitar_data