#include <AudioFile.h>
#include <FFTConvolver.h>

int main()
{
    AudioFile<double> src_wav;
    bool src_loaded = src_wav.load("c2.wav");
    src_wav.printSummary();

    AudioFile<double> ir_wav;
    bool ir_loaded = ir_wav.load("ir.wav");
    ir_wav.printSummary();

    assert(src_loaded && ir_loaded);

    // set same sample rate
    src_wav.setSampleRate(44100);
    ir_wav.setSampleRate(44100);

    // set same bit depth
    src_wav.setBitDepth(24);
    ir_wav.setBitDepth(24);

    printf("ir data type size: %ld", sizeof(ir_wav.samples[0][0]));
    printf("note data type size: %ld", sizeof(src_wav.samples[0][0]));

    fftconvolver::FFTConvolver convolver;
    // need to convert to samples
    convolver.init(512, &ir_wav.samples[0][0], ir_wav.getNumSamplesPerChannel());


    // for (int i = 0; i < a.getNumSamplesPerChannel(); i++)
    // {
    //     for (int channel = 0; channel < a.getNumChannels(); channel++)
    //     {
    //         a.samples[channel][i] = a.samples[channel][i] * gain;
    //     }
    // }
    return 0;
}