import numpy as np
import matplotlib.pyplot as plt

# linspace to work from 
domain = np.linspace(0, 10, 10)

input_sound = np.zeros(10)
input_sound[0] = 1

ir_domain = np.linspace(0, 10, 10)
ir = [1, 0.2, 0.10, 0.05, 0, 0, 0, 0, 0, 0]


fig, subplots = plt.subplots(1, 3, figsize=(20, 5))

subplots[0].scatter(domain, input_sound)
subplots[0].set_title("System Input")
subplots[0].set_xlabel("Samples")
subplots[0].set_ylabel("Amplitude")

subplots[1].scatter(ir_domain, ir)
subplots[1].set_title("System Impulse Response")
subplots[1].set_xlabel("Samples")
subplots[1].set_ylabel("Amplitude")

convolution = np.convolve(input_sound, ir)[:10]
conv_domain = np.arange(len(convolution))

subplots[2].scatter(conv_domain, convolution)
subplots[2].set_title("Convolution Output")
subplots[2].set_xlabel("Samples")
subplots[2].set_ylabel("Amplitude")
 
fig.tight_layout(pad=2.0) 

plt.savefig('conv_figures/sample_conv.png')

input_sound = np.zeros(10)
input_sound[0] = 2

ir_domain = np.linspace(0, 10, 10)
ir = [1, 0.2, 0.10, 0.05, 0, 0, 0, 0, 0, 0]


fig, subplots = plt.subplots(1, 3, figsize=(20, 5))

subplots[0].scatter(domain, input_sound)
subplots[0].set_title("System Input")
subplots[0].set_xlabel("Samples")
subplots[0].set_ylabel("Amplitude")

subplots[1].scatter(ir_domain, ir)
subplots[1].set_title("System Impulse Response")
subplots[1].set_xlabel("Samples")
subplots[1].set_ylabel("Amplitude")

convolution = np.convolve(input_sound, ir)[:10]
conv_domain = np.arange(len(convolution))

subplots[2].scatter(conv_domain, convolution)
subplots[2].set_title("Convolution Output")
subplots[2].set_xlabel("Samples")
subplots[2].set_ylabel("Amplitude")
 
fig.tight_layout(pad=2.0) 

plt.savefig('conv_figures/sample_conv2.png')

domain = np.linspace(0, 10, 10)

input_sound = np.zeros(10)
input_sound[2] = 1


fig, subplots = plt.subplots(1, 3, figsize=(20, 5))

subplots[0].scatter(domain, input_sound, c='red')
subplots[0].set_title("System Input")
subplots[0].set_xlabel("Samples")
subplots[0].set_ylabel("Amplitude")

subplots[1].scatter(ir_domain, ir, c='red')
subplots[1].set_title("System Impulse Response")
subplots[1].set_xlabel("Samples")
subplots[1].set_ylabel("Amplitude")

convolution = np.convolve(input_sound, ir)[:10]
conv_domain = np.arange(len(convolution))

subplots[2].scatter(conv_domain, convolution, c='red')
subplots[2].set_title("Convolution Output")
subplots[2].set_xlabel("Samples")
subplots[2].set_ylabel("Amplitude")
 
fig.tight_layout(pad=2.0) 

plt.savefig('conv_figures/sample_conv3.png')

domain = np.linspace(0, 10, 10)

input_sound = np.zeros(10)
input_sound[2] = 1
input_sound[0] = 2


fig, subplots = plt.subplots(1, 3, figsize=(20, 5))

subplots[0].scatter(domain, input_sound, c='purple')
subplots[0].set_title("System Input")
subplots[0].set_xlabel("Samples")
subplots[0].set_ylabel("Amplitude")

subplots[1].scatter(ir_domain, ir, c='purple')
subplots[1].set_title("System Impulse Response")
subplots[1].set_xlabel("Samples")
subplots[1].set_ylabel("Amplitude")

convolution = np.convolve(input_sound, ir)[:10]
conv_domain = np.arange(len(convolution))

subplots[2].scatter(conv_domain, convolution, c='purple')
subplots[2].set_title("Convolution Output")
subplots[2].set_xlabel("Samples")
subplots[2].set_ylabel("Amplitude")
 
fig.tight_layout(pad=2.0) 

plt.savefig('conv_figures/sample_conv4.png')
