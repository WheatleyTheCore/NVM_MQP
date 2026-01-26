from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from impulseest import impulseest


classical1 = wavfile.read('guitar_sounds/Classical_1.wav')[1][:, 0]
print(classical1)
steel1 = wavfile.read('guitar_sounds/Steel_1.wav')[1][:, 0]



recovered, remainder = signal.deconvolve(classical1, steel1)
ir_est = impulseest(classical1,steel1,n=100,RegularizationKernel='DC')

modeled_classical = signal.convolve(steel1, recovered)

fig, (ax_orig, ax_win, ax_filt, ax_rec) = plt.subplots(4, 1, sharex=True)
ax_orig.plot(classical1)
ax_orig.set_title('classical guitar')
ax_orig.margins(0, 0.1)
ax_win.plot(steel1)
ax_win.set_title('steel string guitar')
ax_win.margins(0, 0.1)
ax_filt.plot(ir_est)
ax_filt.set_title('IR')
ax_filt.margins(0, 0.1)
ax_rec.plot(modeled_classical)
ax_rec.set_title('Recovered classical')
ax_rec.margins(0, 0.1)
fig.tight_layout()
fig.savefig('output.png')