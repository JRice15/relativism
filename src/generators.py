import numpy as np
import random as rd

from src.recording_obj import Recording
from src.integraters import mix, mix_multiple, concatenate
from src.data_types import *


class BaseGenerator:

    @staticmethod
    def wave(dur, period, shift=0, amp=1):
        """
        generate sine wave by period and dur, shift and amp.
        dur, period, shift: samples
        """
        factor = 2 * np.pi / period
        return amp * np.sin(
            (np.arange(int(dur)) - shift) * factor
        )
    
    @staticmethod
    def wave_point(index_or_arr, period, shift=0, amp=1):
        """
        pass sample index as single num or as np.array
        """
        factor = 2 * np.pi / period
        return amp * np.sin(
            (index_or_arr - shift) * factor
        )
    



class Generator:
    """
    class with subcategories for generating tones, clicks, synths, etc
    """

    class SimpleWave:

        @staticmethod
        def sine(note, dur, amp=0.1, rate=44100, name=None):
            """
            sine wave generator
                freqency (Hz)
                duration (secs)
                amplitude (0-1) 0.1 default
            returns Recording obj
            """
            print("\nGenerating simple sine wave ...")
            freq = RelPitch.valid_freq(note)
            dur = RelTime.valid_beatsec(dur).samps()
            amp = inpt_validate(amp, 'flt', allowed=[0, 2])
            arr = BaseGenerator.wave(dur, freq.get_period(rate), shift=0, amp=amp)
            source_block = {"type": "generator",
                            "name": sys._getframe().f_code.co_name,
                            "note": freq,
                            "duration": dur,
                            "amplitude": amp}
            return Recording(array=arr, source_block=source_block, rate=rate, name=name)

        @staticmethod
        def square(note, dur, amp=0.05, rate=44100, name=None):
            """
                freqency (Hz)
                duration (secs)
                amplitude (0-1) 0.05 default
                rate (sps) 44100 
            """
            print("\nGenerating simple square wave ...")
            freq = RelPitch.valid_freq(note)
            dur = RelSecs.valid_beatsec(dur)
            period = freq.get_period(rate)
            period_arr = [amp] * (period // 2) + [-amp] * ((period + 1) // 2)
            arr = period_arr * int(freq * dur)
            arr = arr[:int(rate * dur)]
            arr = [[i, i] for i in arr]
            source_block = {"generator": sys._getframe().f_code.co_name,
                            "frequency": note,
                            "duration": dur,
                            "amplitude": amp}
            return Recording(array=arr, source_block=source_block, rate=rate, name=name)

        @staticmethod
        def triangle(freq, dur, amp=0.1, rate=44100, name=None):
            """
                freqency (Hz)
                duration (secs)
                amplitude (0-1) 0.05 default
                rate (sps) 44100 
            """
            print("\nGenerating simple triangle wave ...")
            freq = RelPitch.valid_freq(freq)
            dur = RelSecs.valid_beatsec(dur)
            period = int(rate / freq)
            period_arr = []
            delta = 4 * amp / period # amount change per sample
            val = 0 # value of sample
            for _ in range(period):
                period_arr.append([val, val])
                val += delta
                if abs(val) > (amp + 0.001):
                    delta *= -1
            arr = period_arr * int(freq * dur * 1.1)
            arr = arr[:int(rate * dur)]
            source_block = {"generator": sys._getframe().f_code.co_name, 
                            "frequency": freq,
                            "duration": dur,
                            "amplitude": amp}
            return Recording(array=arr, source_block=source_block, rate=rate, name=name)

        @staticmethod
        def triangle_2(freq, dur, amp=0.1, rate=44100, name=None):
            """
                freqency (Hz)
                duration (secs)
                amplitude (0-1) 0.05 default
                rate (sps) 44100 
            """
            print("\nGenerating simple triangle wave ...")
            freq = RelPitch.valid_freq(freq)
            dur = RelSecs.valid_beatsec(dur)
            period = int(rate / freq)
            arr = []
            delta = 4 * amp / period # amount change per sample
            val = 0 # value of sample
            for _ in range(int(dur * rate)):
                arr.append([val, val])
                val += delta
                if abs(val) > (amp + 0.001):
                    delta *= -1
            source_block = {"generator": sys._getframe().f_code.co_name, 
                            "frequency": freq,
                            "duration": dur,
                            "amplitude": amp}
            return Recording(array=arr, source_block=source_block, rate=rate, name=name)


    class Synth:

        @staticmethod
        def square_synth_1(freq, dur, amp=0.1, rate=44100, name=None):
            """
            simple synth from square waves
                freqency, duration, amplitude
            returns Recording obj
            """
            print("\nGenerating square synth 1...")
            freq = RelPitch.valid_freq(freq)
            dur = RelSecs.valid_beatsec(dur)
            a = []
            note = freq / (2 ** 4)
            for i in range(1, 5):
                a.append(Generator.SimpleWave.square(note * (2 ** i), dur, amp=amp, name="synth tone"))
            rec = mix_multiple(*a)
            source_block = {"generator": sys._getframe().f_code.co_name, 
                            "frequency": freq,
                            "duration": dur,
                            "amplitude": amp}
            rec.source_block = source_block
            return rec


    class Click:

        @staticmethod
        def clip_click(amp=0.5):
            array = [
                [amp, amp]
            ]
            source_block = {"generator": sys._getframe().f_code.co_name, 
                            "amplitude": amp}
            return Recording(
                array=array,
                source_block=source_block
            )

        @staticmethod
        def clip_click2(amp=0.5):
            array = []
            for _ in range(300):
                a = rd.random() * amp
                array.append([a, a])
            source_block = {"generator": sys._getframe().f_code.co_name,
                            "amplitude": amp}
            return Recording(
                array=array,
                source_block=source_block
            )



def main_generators():
    """
    """
    while True:
        p("freq")
        freq = inpt('freq')
        Generator.SimpleWave.sine(freq, 20).playback()



if __name__ == "__main__":
    main_generators()