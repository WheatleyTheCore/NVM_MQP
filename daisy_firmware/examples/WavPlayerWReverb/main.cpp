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
#include "daisy_seed.h"

#include "FFTConvolver/FFTConvolver.h"
#include "FFTConvolver/TwoStageFFTConvolver.h"
#include "FFTConvolver/Utilities.h"

using namespace daisy;

static constexpr const size_t kTransferSize = 16384;

static DaisySeed                hw;
static SdmmcHandler             sdmmc;
static FatFSInterface           fsi;
static WavPlayer<kTransferSize> player;
static WavPlayer<kTransferSize> ir_player;
static FIL                      file;

void AudioCallback(AudioHandle::InputBuffer  in,
                   AudioHandle::OutputBuffer out,
                   size_t                    size)
{
    for(size_t i = 0; i < size; i++)
    {
        // Fill two channels of data per sample
        float samps[2];
        player.Stream(samps, 2);
        out[0][i] = samps[0];
        out[1][i] = samps[1];
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
    const uint32_t ir_num_samples = ir_player.GetDurationInSamples();
    int16_t ir_samples[ir_num_samples];


    if (f_open(&file, "ir.wav", FA_READ) == FR_OK) {
        UINT bytes_read = 0;
        f_read(&file, ir_samples,  ir_num_samples * sizeof(ir_samples[0]), &bytes_read);
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
