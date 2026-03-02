/** Simple demonstration of WAV file playback
 *
 *  When the program starts, it will attempt to load, and start looping
 *  the file, "loop.wav".
 *
 *  The "loop.wav" file used here is included in the repo for convenience.
 *  The file is a 48kHz stereo, 16-bit sine wave at 440Hz -6dB
 *
 *  Any 16-bit WAV file can be used with this class, but sample-rate
 *  is not automatically adjusted for.
 *
 *  The included file was created with sox, using the following command:
 *  sox -n -r 48000 -b 16 -c 2 loop.wav synth 1 sine 440 gain -6
 */
#include <vector>

#include "daisy_seed.h"

#include "FFTConvolver/FFTConvolver.h"
#include "FFTConvolver/TwoStageFFTConvolver.h"
#include "FFTConvolver/Utilities.h"

#include <cmath>
#include <cstdio>
#include <cstdlib>

using namespace daisy;

static constexpr const size_t kTransferSize = 16384;

static DaisySeed                hw;
static SdmmcHandler             sdmmc;
static FatFSInterface           fsi;
static WavPlayer<kTransferSize> player;
static WavPlayer<kTransferSize> ir_player;
static FIL                      file;

uint32_t num_ir_samples;
// int16_t ir_samples[900000000]; // this is a bad hack
std::vector<fftconvolver::Sample> ir;


template<typename T>
void SimpleConvolve(const T* input, size_t inLen, const T* ir, size_t irLen, T* output)
{
  if (irLen > inLen)
  {
    SimpleConvolve(ir, irLen, input, inLen, output);
    return;
  }
  
  ::memset(output, 0, (inLen+irLen-1) * sizeof(T));
  
  for (size_t n=0; n<irLen; ++n)
  {
    for (size_t m=0; m<=n; ++m)
    {
      output[n] += ir[m] * input[n-m];
    }
  }
  
  for (size_t n=irLen; n<inLen; ++n)
  {
    for (size_t m=0; m<irLen; ++m)
    {
      output[n] += ir[m] * input[n-m];
    }
  }
  
  for (size_t n=inLen; n<inLen+irLen-1; ++n)
  {
    for (size_t m=n-inLen+1; m<irLen; ++m)
    {
      output[n] += ir[m] * input[n-m];
    }
  }
}


void AudioCallback(AudioHandle::InputBuffer  in,
                   AudioHandle::OutputBuffer out,
                   size_t                    size)
{
    float outL[size];
    float outR[size];
    std::vector<fftconvolver::Sample> signal(size);


    for(size_t i = 0; i < size; i++)
    {
        // Fill two channels of data per sample
        float samps[2];
        player.Stream(samps, 2);


        signal[i] = samps[1];


    }

    SimpleConvolve(&signal[0], signal.size(), &ir[0], ir.size(), &outL[0]);

    for (size_t i = 0; i < size; i++) {
      OUT_L[0] = signal[i];
      OUT_R[1] = signal[i];
    }
        
}

int main(void)
{
    /** Initialize our hardware */
    hw.Init(true);
    hw.StartLog(true);

    /** The SD Card/FatFS Initialization remains unchanged
     *  For multiple WavPlayer objects, or playback at
     *  faster playback speeds or sample rates it is recommended
     *  to use 4-bit I/O, and as fast a speed as the PCB layout permits.
     *
     *  These settings are minimal for demonstration purposes.
     */
    SdmmcHandler::Config sdcfg;
    sdcfg.Defaults();
    sdcfg.speed = SdmmcHandler::Speed::STANDARD;
    sdcfg.width = SdmmcHandler::BusWidth::BITS_1;
    sdmmc.Init(sdcfg);
    fsi.Init(FatFSInterface::Config::Media::MEDIA_SD);
    f_mount(&fsi.GetSDFileSystem(), "/", 1);

    // get IR file info 
    hw.PrintLine("Trying to load IR...");
    auto sta = f_open(
        &file, "ir.wav", (FA_OPEN_EXISTING | FA_READ));
    if(sta != FR_OK)
    {
        hw.PrintLine("Could not open: %s", "ir.wav");
    }
    FileReader reader(&file);
    WavParser  parser;
    if(!parser.parse(reader))
    {
        hw.PrintLine("Error parsing file: %s",
                        "ir.wav");
    }

    const auto& info = parser.info();
    hw.PrintLine("File Information: %s", "ir.wav");
    hw.PrintLine("\tSample Rate:\t%d", info.sampleRate);
    hw.PrintLine("\tChannels:\t%d", info.numChannels);
    hw.PrintLine("\tBit Depth:\t%d", info.bitsPerSample);

     

    

    if (ir_player.Init("ir.wav") != WavPlayer<kTransferSize>::Result::Ok) {
      // Error..
      hw.PrintLine("IR failed to load into player");
    }

    // note: this should *really* load into RAM via DSY_SDRAM_BSS
    num_ir_samples = ir_player.GetDurationInSamples();
    int16_t ir_samples[num_ir_samples];


    if (f_open(&file, "ir.wav", FA_READ) == FR_OK) {
        UINT bytes_read = 0;
        f_read(&file, ir_samples,  ir.size(), &bytes_read);
    }

    for (uint8_t i = 0; i < num_ir_samples; i++) {
      ir.push_back(ir_samples[i]);
    }

    hw.PrintLine("IR Loaded");


    /** Open Loop.WAV
     *  And blink very fast if there's a problem
     */
    if (player.Init("loop.wav") != WavPlayer<kTransferSize>::Result::Ok) {
      // Error..
      while(true) {
        // Blink really fast if there was a problem
        hw.SetLed((System::GetNow() & 127) < 63);
      }
    }

    /** Enable Looping playback of the audio file */
    player.SetLooping(true);
    player.SetPlaying(true);
    player.Restart();

    /** Start the Audio */
    hw.StartAudio(AudioCallback);

    while(1)
    {
        /** Blink Slower in normal operation */
        hw.SetLed((System::GetNow() & 511) < 255);

        /** This does the actual Disk I/O whenever the Audio FIFOs are low */
        player.Prepare();
    }
}
