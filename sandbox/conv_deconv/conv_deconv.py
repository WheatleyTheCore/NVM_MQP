from scipy import signal
from scipy.fft import fft, ifft
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
# from impulseest import impulseest


rate_guitar, guitar_raw = wavfile.read('test_sounds/guitar.wav')
rate_trombone, trombone_raw = wavfile.read('test_sounds/tronmone.wav')
rate_lick, lick_raw = wavfile.read('test_sounds/guitarlick.wav')

guitar_note = guitar_raw[:, 0]
trombone_note = trombone_raw[:, 0]
lick = lick_raw[:, 0]

number_samples = len(guitar_note)
assert len(trombone_note) == number_samples, 'input files need to have the same number of samples'
print(rate_guitar)
assert rate_guitar == rate_trombone, 'audio file sample rates must match'

# get rid of preceeding zeros 
shortened_guitar = np.trim_zeros(guitar_note, 'f')
shortened_trombone = np.trim_zeros(trombone_note, 'f')

# make sure the two are the same length
shorter_sample_length = min(len(shortened_trombone), len(shortened_guitar))
shortened_guitar = shortened_guitar[:shorter_sample_length]
shortened_trombone = shortened_trombone[:shorter_sample_length]

print('preprocessing done')

assert len(shortened_trombone) == len(shortened_guitar), f'processed note lengths don\'t match, guitar is {len(shortened_guitar)} samples, trombone is {len(shortened_trombone)} samples'

guitar_fft = fft(shortened_guitar)
trombone_fft = fft(shortened_trombone)

print('fft done')

H = trombone_fft / guitar_fft

ir = ifft(H).real[:number_samples]

trombone_lick = signal.convolve(shortened_guitar, ir)[:len(shortened_guitar)]

print('convolution done')

fig, (ax_orig, ax_win, ax_filt, ax_rec) = plt.subplots(4, 1, sharex=True)
ax_orig.plot(shortened_trombone)
ax_orig.set_title('trombone')
ax_orig.margins(0, 0.1)
ax_win.plot(shortened_guitar)
ax_win.set_title('guitar')
ax_win.margins(0, 0.1)
ax_filt.plot(ir)
ax_filt.set_title('IR')
ax_filt.margins(0, 0.1)
ax_rec.plot(trombone_lick)
ax_rec.set_title('modeled trombone output')
ax_rec.margins(0, 0.1)
fig.tight_layout()
fig.savefig('figure.png')

wavfile.write('trombonelick.wav', 44100, trombone_lick)

# display(Audio(shortened_trombone, rate=44100, autoplay=False))
# display(Audio(shortened_guitar, rate=44100, autoplay=False))
# display(Audio(trombone_lick, rate=44100, autoplay=False))