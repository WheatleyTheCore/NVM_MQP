#include "tinywav.h"
#include "conv.h"

#define NUM_CHANNELS 1
#define SAMPLE_RATE 32000
#define BLOCK_SIZE 480

#define C2_FRAMES 21887 // magic number found by printing number of frames
#define IR_FRAMES 47839 // ^^

int main()
{
  TinyWav tw;
  tinywav_open_read(&tw,
                    "./ir.wav",
                    TW_SPLIT // the samples will be delivered by the read function in split format
  );

  int ir_frames = tw.numFramesInHeader;

  int *ir_buffer = malloc(ir_frames * sizeof(float));

  for (int i = 0; i < ir_frames / BLOCK_SIZE; i++)
  {
    // samples are always provided in float32 format,
    // regardless of file sample format
    float samples[NUM_CHANNELS * BLOCK_SIZE];

    tinywav_read_f(&tw, samples&, BLOCK_SIZE);

    for (int j = 0; j < BLOCK_SIZE; j++)
    {
      ir_buffer[i * BLOCK_SIZE + j] = samples[j];
    }
  }

  tinywav_close_read(&tw);

  tinywav_open_write(&tw,
                     NUM_CHANNELS,
                     SAMPLE_RATE,
                     TW_FLOAT32,        // the output samples will be 32-bit floats. TW_INT16 is also supported
                     TW_INLINE,         // the samples to be written will be assumed to be inlined in a single buffer.
                                        // Other options include TW_INTERLEAVED and TW_SPLIT
                     "./test_write.wav" // the output path
  );

  tinywav_write_f(&tw, ir_buffer, ir_frames);
  free(ir_buffer);
}
