from scipy.io import wavfile
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks
import numpy as np
import math
import sys

"""
input: audio file name
* default: samples/note_c4.wav
output:
* info about audio file
* most prevalent frequencies (above 55th percentile amplitude) with their amplitudes and notes,
sorted in descending order

todo:
* fix imprecise octave issue
* look into norm=forward vs other norms vs rfft and if that affects octaves/output frequencies
* figure out how to determine how many frequencies to take instead of hard-coded p55
* figure out what to do with multiple audio channels
* make sure discarding negative frequencies is ok
* understand why we're taking absolute value of output of FT
* learn what makes FFT fast
* scroll through song (short-time FT) instead of using entire audio file
* visualize notes

notes:
* sample = amplitude value at that moment in time
    * volume in the range noise floor to 0 dbFS
    * number of possible amplitude values depends on bit depth
        * bit depth = num bits/bytes used for a single sample
        * for example, 8-bit music in the past, now 16-bit (2 bytes) is standard
    * u can't take infinite samples so u just take as many data points as the sampling rate
    * each sample is like a dot on a graph that should look like a sine wave
    * the amplitude doesn't affect pitch, of course, only frequency based on the "outlined" wave

* fourier transform
    * input = array of amplitudes that "outline" a wave of an audio snippet
    * (for example, 1 second of a chord)
    * output = graph of "magnitudes" of frequencies
    * (how prevalent a frequency is in the original audio snippet)
    * short-time fourier transform (stft) = take most recent samples as u scroll over audio file
        * https://www.chciken.com/digital/signal/processing/2020/05/13/guitar-tuner.html
    * get peaks of output of FT to get the most pravalent frequencies
"""

# https://stackoverflow.com/questions/64555524/turning-a-frequency-into-a-note-in-pytho
def freq_to_note(freq):
    notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

    # formula taken from https://en.wikipedia.org/wiki/Piano_key_frequencies
    note_number = 12 * math.log2(freq / 440) + 49
    note_number = round(note_number)

    note = (note_number - 1 ) % len(notes)
    note = notes[note]

    octave = (note_number + 8 ) // len(notes)

    return note + str(octave)

# get audio file from command line input
audiofile = "samples/note_c4.wav" if len(sys.argv) < 2 else sys.argv[1]
sampling_rate, data = wavfile.read(audiofile)

num_samples = len(data)
num_channels = len(data[0])
length_in_seconds = num_samples / sampling_rate

print("sampling rate: " + str(sampling_rate))   # also called sampling frequency
print("num samples: " + str(num_samples))
print("num channels: " + str(num_channels))
print("length in seconds: " + str(length_in_seconds))

# fast fourier transform on just 1 channel for now
signal = data[:, 0]
freq = fftfreq(signal.size, d=1./sampling_rate) # frequency scale. signal.size is also num_samples

# version 1 based on second response to this stackoverflow:
# https://stackoverflow.com/questions/69888553/how-to-find-peaks-of-fft-graph-using-python
p55_amplitude = np.percentile(signal, 55)
print("p55 amplitude: " + str(p55_amplitude))

amplitudes = fft(signal, norm="forward")    # forward gets back the amplitude as "y value" (magnitude)
amplitudes_abs = np.abs(amplitudes)

peak_indices, properties = find_peaks(amplitudes_abs, height=p55_amplitude)
peak_heights = properties["peak_heights"]

# version 2 based on this tutorial: https://klyshko.github.io/teaching/2019-02-22-teaching
# magnitudes = np.fft.rfft(signal)    # r means real
# magnitudes_abs = np.abs(magnitudes)
# top_p_magnitude = np.percentile(magnitudes_abs, 99.97)
# peak_indices, properties = find_peaks(magnitudes_abs, height=top_p_magnitude)
# peak_heights = properties["peak_heights"]

# only get positive frequencies (idk if this makes sense but i was getting repeats with negatives)
peak_freqs = [(freq[peak_indices[i]], peak_heights[i], freq_to_note(freq[peak_indices[i]]))
                for i in range(len(peak_indices))
                if freq[peak_indices[i]] >= 0]
peak_freqs.sort(key=lambda tup: tup[1], reverse=True)

print("\nfrequency    \t amplitude       \t note")
[print("%4.2f    \t %10.3f       \t %s" % peak_freqs[i]) for i in range(len(peak_freqs))]
