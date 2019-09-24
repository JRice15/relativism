from recording_obj import *
from integraters import *



class BaseGenerator:

    @staticmethod
    def wave(period, dur, shift=0, amp=1):
        factor = 2 * np.pi * period
        return amp * np.sin(
            (np.arange(int(dur)) - shift) * factor
        )


class Generator:
    """
    class with subcategories for generating tones, clicks, synths, etc
    """

    class SimpleWave:

        @staticmethod
        def sine(freq, dur, amp=0.1, rate=44100, name=None):
            """
            sine wave generator
                freqency (Hz)
                duration (secs)
                amplitude (0-1) 0.1 default
            returns Recording obj
            """
            print("\nGenerating simple sine wave ...")
            freq = f(freq)
            dur = samps(dur)
            amp = inpt_process(amp, 'flt', allowed=[0, 2])
            period = rate / freq
            arr = BaseGenerator.wave(period, dur, shift=0, amp=amp)
            source_block = ["generator", sys._getframe().f_code.co_name, 
                            "frequency", freq,
                            "duration", dur,
                            "amplitude", amp]
            return Recording(array=arr, source=source_block, rate=rate, name=name)


        @staticmethod
        def square(freq, dur, amp=0.05, rate=44100, name=None):
            """
                freqency (Hz)
                duration (secs)
                amplitude (0-1) 0.05 default
                rate (sps) 44100 
            """
            print("\nGenerating simple square wave ...")
            freq = f(freq)
            dur = secs(dur)
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


        @staticmethod
        def triangle(freq, dur, amp=0.1, rate=44100, name=None):
            """
                freqency (Hz)
                duration (secs)
                amplitude (0-1) 0.05 default
                rate (sps) 44100 
            """
            print("\nGenerating simple triangle wave ...")
            freq = f(freq)
            dur = secs(dur)
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
            source_block = ["generator", sys._getframe().f_code.co_name, 
                            "frequency", freq,
                            "duration", dur,
                            "amplitude", amp]
            return Recording(array=arr, source=source_block, rate=rate, name=name)

        @staticmethod
        def triangle_2(freq, dur, amp=0.1, rate=44100, name=None):
            """
                freqency (Hz)
                duration (secs)
                amplitude (0-1) 0.05 default
                rate (sps) 44100 
            """
            print("\nGenerating simple triangle wave ...")
            freq = f(freq)
            dur = secs(dur)
            period = int(rate / freq)
            arr = []
            delta = 4 * amp / period # amount change per sample
            val = 0 # value of sample
            for _ in range(int(dur * rate)):
                arr.append([val, val])
                val += delta
                if abs(val) > (amp + 0.001):
                    delta *= -1
            source_block = ["generator", sys._getframe().f_code.co_name, 
                            "frequency", freq,
                            "duration", dur,
                            "amplitude", amp]
            return Recording(array=arr, source=source_block, rate=rate, name=name)


    class Synth:

        @staticmethod
        def square_synth_1(freq, dur, amp=0.1, rate=44100, name=None):
            """
            simple synth from square waves
                freqency, duration, amplitude
            returns Recording obj
            """
            print("\nGenerating square synth 1...")
            freq = f(freq)
            dur = secs(dur)
            a = []
            note = freq / (2 ** 4)
            for i in range(1, 5):
                a.append(Generator.SimpleWave.square(note * (2 ** i), dur, amp=amp, name="synth tone"))
            rec = mix_multiple(*a)
            source_block = ["generator", sys._getframe().f_code.co_name, 
                            "frequency", freq,
                            "duration", dur,
                            "amplitude", amp]
            rec.source = source_block
            return rec


    class Click:

        @staticmethod
        def clip_click(amp=0.5):
            array = [
                [amp, amp]
            ]
            source_block = ["generator", sys._getframe().f_code.co_name, 
                        "amplitude", amp]
            return Recording(
                array=array,
                source=source_block
            )

        @staticmethod
        def clip_click2(amp=0.5):
            array = []
            for _ in range(300):
                a = rd.random() * amp
                array.append([a, a])
            source_block = ["generator", sys._getframe().f_code.co_name, 
                        "amplitude", amp]
            return Recording(
                array=array,
                source=source_block
            )



def main_generators():
    """
    """
    a = Generator.SimpleWave.sine(400, 20)



if __name__ == "__main__":
    main_generators()