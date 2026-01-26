from scipy import signal
import numpy as np
import matplotlib.pyplot as plt


t = np.linspace(0, 20, 500)


sig1 = signal.square(t)
sig2 = signal.gausspulse(t[:20], fc=5)

conv_sig = signal.convolve(sig1, sig2)


recovered, remainder = signal.deconvolve(conv_sig, sig1)

fig, (ax_orig, ax_win, ax_filt, ax_rec) = plt.subplots(4, 1, sharex=True)
ax_orig.plot(sig1)
ax_orig.set_title('Original pulse')
ax_orig.margins(0, 0.1)
ax_win.plot(np.append(sig2, np.zeros(500-20)))
ax_win.set_title('Filter impulse response')
ax_win.margins(0, 0.1)
ax_filt.plot(conv_sig)
ax_filt.set_title('Convolution signal')
ax_filt.margins(0, 0.1)
ax_rec.plot(np.append(recovered, np.zeros(500-len(recovered))))
ax_rec.set_title('Recovered IR')
ax_rec.margins(0, 0.1)
fig.tight_layout()
fig.savefig('output.png')