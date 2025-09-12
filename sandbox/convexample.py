import torchaudio
import torchaudio.functional as F
import torch

# Load the impulse response and normalise
rir, rir_sample_rate = torchaudio.load('assets/room-impulse-responses/irs/MIT_Survey/h047_Hallway_MIT_4txts.wav')

note, note_sample_rate = torchaudio.load('assets/pianoNotes/wav/e1.wav') # this is the incorrect note name.....

if note_sample_rate != rir_sample_rate:
    resampler = torchaudio.transforms.Resample(orig_freq=rir_sample_rate, new_freq=note_sample_rate)
    rir = resampler(rir)
    
    
# normalize so we don't get volume/distortion issues (otherwise it will be loud)
rir = rir / torch.linalg.vector_norm(rir, ord=2)

# Convolve note with room impulse response
note_with_reverb = F.fftconvolve(note, rir)

torchaudio.save('assets/note_with_reverb.wav', note_with_reverb, note_sample_rate)