from recording_obj import *
from integraters import *



"""

synth sounds

"""



def simple_sine_wave(freq, dur, amp=0.1, rate=44100, name=None):
    """
    sine wave generator
        freqency (Hz)
        duration (secs)
        amplitude (0-1) 0.1 default
    returns Recording obj
    """
    print("\nGenerating simple sine wave ...")
    freq = f(freq)
    period = int(rate / freq)
    pi2 = 2 * math.pi
    arr = [amp * math.sin( (i * pi2) / period ) for i in range(int(rate * dur))]
    arr =  [[i, i] for i in arr]
    source_block = ["generator", sys._getframe().f_code.co_name, 
                    "frequency", freq,
                    "duration", dur,
                    "amplitude", amp]
    return Recording(array=arr, source=source_block, rate=rate, name=name)


def simple_square_wave(freq, dur, amp=0.05, rate=44100, name=None):
    """
        freqency (Hz)
        duration (secs)
        amplitude (0-1) 0.05 default
        rate (sps) 44100 
    """
    print("\nGenerating simple square wave ...")
    freq = f(freq)
    period = int(rate / freq)
    period_arr = [amp] * (period // 2) + [-amp] * ((period + 1) // 2)
    arr = period_arr * int(freq * dur)
    arr = arr[:int(rate * dur)]
    arr =  [[i, i] for i in arr]
    source_block = ["generator", sys._getframe().f_code.co_name, 
                    "frequency", freq,
                    "duration", dur,
                    "amplitude", amp]
    return Recording(array=arr, source=source_block, rate=rate, name=name)



def simple_triangle_wave(freq, dur, amp=0.1, rate=44100, name=None):
    """
        freqency (Hz)
        duration (secs)
        amplitude (0-1) 0.05 default
        rate (sps) 44100 
    """
    print("\nGenerating simple triangle wave ...")
    freq = f(freq)
    period = int(rate / freq)
    period_arr = []
    delta = amp / period # amount change per sample
    val = 0 # value of sample
    for _ in range(period):
        period_arr.append(val)
        val += delta
        if val > (amp + 0.001):
            delta *= -1
    arr = period_arr * int(freq * dur)
    arr = arr[:int(rate * dur)]
    arr =  [[i, i] for i in arr]
    source_block = ["generator", sys._getframe().f_code.co_name, 
                    "frequency", freq,
                    "duration", dur,
                    "amplitude", amp]
    return Recording(array=arr, source=source_block, rate=rate, name=name)


def square_synth_1(freq, dur, amp=0.1, rate=44100, name=None):
    """
    simple synth from square waves
        freqency, duration, amplitude
    returns Recording obj
    """
    print("\nGenerating square synth 1...")
    freq = f(freq)
    a = []
    note = freq / (2 ** 4)
    for i in range(1, 5):
        a.append(simple_square_wave(note * (2 ** i), dur, amp=amp, name="synth tone"))
    rec = mix_multiple(*a)
    source_block = ["generator", sys._getframe().f_code.co_name, 
                    "frequency", freq,
                    "duration", dur,
                    "amplitude", amp]
    rec.source = source_block
    return rec








def main_generators():
    """
    """
    freq = 99
    rec1 = square_synth_1(freq, 4)
    rec1.playback()
    rec2 = simple_triangle_wave(freq, 4)
    rec4 = simple_sine_wave(freq, 4)
    rec3 = mix_multiple(rec1, rec2, rec4)
    rec3.playback()



if __name__ == "__main__":
    main_generators()