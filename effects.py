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



class Dynamics:

    @staticmethod
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

    @staticmethod
    def eq(rec):
        freqs = np.fft.rfft(rec.arr)
        print(freqs)



def angle_to_pan(a):
    """
    converts radians to pan val
    """
    if a < 0:
        a = -a
    while a > math.pi:
        a = 2 * math.pi - a
        if a < 0:
            a = -a
    a -= math.pi / 2
    p = -a / (math.pi / 2)
    return p


class Reverb1_Node():

    def __init__(self, parent, x, y):
        """
        r: reverb parent
        coord: coordinate
        """
        self.parent = parent
        self.x = x
        self.y = y
        self.other_nodes = [] # [other_node, angle, dist]
        self.purpose = 'node'

    def __eq__(self, other):
        try:
            return (self.__class__ == other.__class__) and (self.x == other.x) and (self.y == other.y)
        except:
            return False
        
    def bounce(self, samp, in_angle, offset):
        """
        samp_data as [sample, offset in samples]
        pass single sample of audio, will return that sample
        """
        samp *= (1 - self.parent.dampening)
        # too quiet now
        if samp < 0.005:
            return
        for n in self.other_nodes:
            # i as [node, angle, dist]
            new_offset = int(offset + (n[2] / 343 * self.parent.rate))
            n[0].bounce(samp, n[1], new_offset)


class Reverb1_Source(Reverb1_Node):

    def __init__(self, parent, arr, x, y):
        super().__init__(parent, x, y)
        self.arr = arr
        self.parent.nodes.append(self)
        self.purpose = 'source'


    def start(self):
        for samp_ind in range(len(self.arr)):
            if samp_ind % self.parent.rate == 0:
                info_line("{0} seconds computed".format(samp_ind / self.parent.rate))
            samp = self.arr[samp_ind]
            for n in self.other_nodes:
                if n[0].purpose != 'listener':
                    # n as [node, angle, dist]
                    pan = angle_to_pan(n[1]) * self.parent.spread
                    samp_val = (samp[0] * (1 - pan)) + (samp[1] * (1 + pan))
                    offset = int(n[2] / 343 * self.parent.rate) + samp_ind
                    n[0].bounce(samp_val, n[1], offset)


    def bounce(self, samp, in_angle, offset):
        pass



class Reverb1_Listener(Reverb1_Node):

    def __init__(self, parent, x, y):
        super().__init__(parent, x, y)
        self.parent.nodes.append(self)
        self.wet_out = [[0, 0] for _ in range(len(self.parent.rec.arr))]
        self.purpose = 'listener'


    def bounce(self, samp, in_angle, offset):
        """
        sets data to self.wet_out
        """
        pan = angle_to_pan(in_angle) * 0.5
        samp_val = [samp * (0.5 - pan), samp * (0.5 + pan)]
        error = True
        while error:
            try:
                self.wet_out[offset][0] += samp_val[0]
                self.wet_out[offset][1] += samp_val[1]
                error = False
            except IndexError:
                self.wet_out += [[0, 0] for _ in range(1 + offset - len(self.wet_out))]





class Reverb1():

    def __init__(self, rec, size, dampening=50, wet=50, dry=80, roughness=50, spread=50):
        """
        args:
            size: radius in meters of room
        """
        section_head("Reverb1")
        self.rec = rec
        self.size = inpt_process(size, 'float', allowed=[1, None])
        self.dampening = inpt_process(dampening, 'pcnt', allowed=[0, None]) * 1/100
        self.wet = inpt_process(wet, 'pcnt', allowed=[0, None])
        self.dry = inpt_process(dry, 'pcnt', allowed=[0, None])
        self.rate = rec.rate
        self.spread = inpt_process(spread, 'pcnt', allowed=[0, 200]) * 1/100

        self.nodes = []
        # self.add_node(0,size)
        self.add_node(size, 0)
        self.add_node(-size, 0)
        # self.add_node(0, -size)

        # source must init before set_other_nodes
        self.listener = Reverb1_Listener(self, 0, 0)
        self.source = Reverb1_Source(self, rec.arr, 0, size/2)

        self.set_other_nodes()

        # do the reverb
        self.source.start()

        # clean up
        self.collect()


    def add_node(self, x, y):
        node = Reverb1_Node(self, x, y)
        self.nodes.append(node)


    def set_other_nodes(self):
        """
        set other_nodes attr for each node, [node, dist]
        """
        for this_node in self.nodes:
            for other_node in self.nodes:
                if other_node != this_node:
                    # get dist and angle from this to other
                    try:
                        slope = (other_node.y - this_node.y) / (other_node.x - this_node.x)
                        angle = math.atan(slope)
                        if str(angle) == "-0.0":
                            angle = math.pi
                    except ZeroDivisionError:
                        angle = math.pi / 2
                    dist = self.node_dist(this_node, other_node)
                    this_node.other_nodes.append([other_node, angle, dist])

    def node_dist(self, a, b):
        return math.sqrt((b.y - a.y)**2 + (b.x - a.x)**2)


    def collect(self):
        # handle slight lag at beginning
        pre_offset = int(self.node_dist(self.listener, self.source) / 343 * self.rate)
        wet_arr = self.listener.wet_out[pre_offset:]
        wet = Recording(
            array=wet_arr,
            name='reverb_wet_out'
        )
        wet.amplify(self.wet * 1/100)
        self.rec.amplify(self.dry * 1/100)
        self.rec.arr = mix(self.rec, wet, name='temp_mix').arr




def get_effects():
    # TODO: do this
    pass



def effects_main():
    """
    """

    obj = Distortion

    a = Rel_Object_Data(obj)

    a.display()



if __name__ == "__main__":
    effects_main()