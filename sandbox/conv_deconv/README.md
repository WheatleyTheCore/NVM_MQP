# Marlin notes!

So we have sweeps with a few different attributes:
1. loud, medium, soft volume 
2. with and without sympathetic string vibration (I taped down the strings to dampen them for without)

there's also sample data of played guitar, slides, open string plucks.

The data is organized into two folders, good guitar (from the nice fancy one) and bad guitar (the cheap bad one).
Inside it has folders for each sweep length. Inside each of these, the file names say the loudness, if it's with or without sympathetic string vibration, and if it's mic data or piezo data.

## To generate IRs
I've found that using the *good mic* and the *bad piezo* sweeps have the best results.

For inverse filtering it's just something like "loud_bad_guitar_piezo_w_ring" / "loud_good_guitar_mic_w_ring".

You'll want to use the piezo sweep as the "input sweep" in the software, and the mic'd good guitar one as the output.