from recording_obj import *
from generators import *


class Distortion:

    @staticmethod
    def white_noise_injection(rec, amount):
        """
        0, 60;
        simple white-noise injection distortion
            amount: 0-100
        """
        print("  White Noise Distortion by {0}%...".format(amount))
        for i in range(len(rec.arr)):
            dist = amount / 1000 * rd.random()
            rec.arr[i][0] += dist
            rec.arr[i][1] += dist

    @staticmethod
    def saw(rec, freq, pct):
        """
        15,10000; 10,90;
        tend wave toward saw of freq
            freq: 
            percent: 0-100%
        """
        print("  Saw Distortion at {0} hz and {1}%".format(freq, pct))
        period = rec.rate / inpt_process(freq, 'freq')
        amount = inpt_process(pct, 'pcnt', allowed=[0, 100]) / 100

        # TODO: amplitude analysis
        amp = 0.5

        delta = amp * 4 / period # amount change per sample
        val = 0 # value to average with
        for i in range(rec.size_samps()):
            rec.arr[i] = [
                ((rec.arr[i][0] * (1 - amount)) + (val * amount)), 
                ((rec.arr[i][1] * (1 - amount)) + (val * amount))
            ]
            val += delta
            if abs(val) > (amp + 0.001):
                delta *= -1



class Bitcrusher:

    @staticmethod
    def bit_swap(rec, amount):
        """
        0, 80;
        swap adjacent bits
            amount: 0-100+: percentage of bits swapped per second
        """
        print("  Bit-Swapping, {0}%...".format(amount))
        end = len(rec.arr) - 2
        for _ in range(int(amount / 100 * rec.size_samps())):
            ind = rd.randint(0, end)
            rec.arr[ind], rec.arr[ind + 1] = \
                rec.arr[ind + 1], rec.arr[ind]


    @staticmethod
    def stretch_and_unstretch(rec, amount):
        """
        1, 60;
        dirtier
        stretch and unstretch
            amount: 1-100+
        """
        print("  Stretch-Unstretch Bitcrusher, {0}%...".format(amount))
        rec.stretch(1/amount)
        rec.stretch(amount)




def scrambler(obj, amount):
    """
    cat: edit
    desc: move chunk of between 1/2 and 1/8th of a second to a new random place
    args:
        amount: number of scrambles to perform, integer >=1; 1, 10;
    """
    amount = inpt_process(amount, "int", allowed=[1, None])

    while amount >= 1:
        print("  scrambling, {0} to go...".format(amount))
        chunk = obj.rate // rd.randint(2, 8)
        start = rd.randint(0, len(obj.arr) - chunk)
        new = rd.randint(0, len(obj.arr) - chunk)
        chunk_arr = obj.arr[start:start+chunk]
        obj.arr = obj.arr[:start] + obj.arr[start+chunk:]
        obj.arr = obj.arr[:new] + chunk_arr + obj.arr[new:]
        amount -= 1



def muffler(rec, amount):
    """
    1, 10;
    average adjacent bits
        amount: int: number of reps
    """
    print("  muffling {0}x...".format(amount))
    for i in range(int(amount)):
        for ind in range(1, rec.size_samps() - 1):
            if (ind + i) % 2 == 0:
                rec.arr[ind][0] = (rec.arr[ind - 1][0] + rec.arr[ind + 1][0]) / 2
            else:
                rec.arr[ind][1] = (rec.arr[ind - 1][1] + rec.arr[ind + 1][1]) / 2


def eq(rec):
    freqs = np.fft.rfft(rec.arr)
    print(freqs)



def get_effects():
    # TODO: do this
    pass



def effects_main():
    """
    """

    obj = Distortion

    a = Object_Data(obj)

    a.display()



if __name__ == "__main__":
    effects_main()