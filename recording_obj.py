import math
import os
import random as rd
import re
import sys
import time
import tkinter as tk
from tkinter import filedialog
import numpy as np

import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment as pd

from data_save import *
from errors import *
from freq_and_time import *
from name_and_path import *
from process import *
from utility import *
from input_processing import *
from output_and_prompting import *


"""

add start/end capability

undo capability

tremelo
reverb
distortion

change pitch without tempo
change tempo without pitch
fade effect in/out

markers

add_to_project
add_to_sampler

"""






class Recording:
    """
    Attributes:
        type (str): 'Recording'
        arr (list or None): wav array, if none is set will be read from file
        source (list): source information for where this recording came from
        name (str or None): name of this object, will be prompted if None
        rate (int): samples per second of this recording
        pan_val (float): number -1 (L) to 1 (R)
        parent: pointer to parent Proj or Sample, if exists
        recents: array of up to 5 recent arrays
    """


    # Initialization #
    def __init__(self, array=None, source=None, name=None, rate=44100, \
            parent=None, hidden=False, type_='Recording'):
        self.type = type_ # for inheritance
        self.name = name
        if name is None:
            self.rename()
        if not hidden:
            section_head("Initializing {0} '{1}'...".format(self.type, self.name))
        self.rate = rate
        self.source = source
        self.arr = array
        self.parent = parent
        if array is None:
            self.init_mode__()
        self.pan_val = 0
        self.recents = None # for undoing
        if not hidden:
            self.save(silent=True)


    def init_mode__(self):
        """
        fill in initialization via input
        get recording by mode
        call get_help/playback if asked
        returns rec array
        """
        valid_modes = ("live Record (R)", "read from File (F)", "Help (H)")
        info_title("Available modes:")
        info_list(valid_modes)
        p("Select mode")
        mode = inpt('letter', allowed='rfh')

        # Record Mode
        if mode == "r":
            self.record_live__()

        # File Mode
        elif mode == "f":
            self.read_file__()

        # Help
        elif mode == "h":
            raise NotImplementedError
        

    def record_live__(self):
        """
        record -- but get this -- live!
        """
        section_head("Record mode")
        device_ind, device_name = sd_select_device()
        p("Enter recording duration (in seconds)")
        record_time = inpt('float', allowed=[0, None])
        p('Choose sample rate to record at, in samples per second. Hit enter to use default 44100')
        rate = inpt('int', required=False)
        if rate == '':
            rate = 44100
        self.rate = rate
        print("  Enter 'R' to begin recording, or anything else to cancel: ", end="")
        cont = inpt('name')
        if cont != "r":
            raise Cancel
        time.sleep(0.05)
        section_head("Recording at input {0} ({1}) for {2} seconds".format(device_ind, \
            device_name, record_time))
        sd.default.channels = 2
        recording = sd.rec(int(record_time * rate), rate, device=device_name)
        sd.wait()
        info_block("Finished recording")
        self.arr = recording
        if not isinstance(self.arr[0], list):
            self.arr = [[i, i] for i in self.arr]
        self.source = [
            'live recording', "input '{0}'".format(device_name)
        ]


    def read_file__(self):
        """
        reads files for recording object init
        takes multiple formats (via PyDub and Soundfile)
        updates self.source, self.arr, self.rate
        """
        section_head("Reading file")
        source = self.source
        if source is None:
            print("  Choose an input sound file...")
            time.sleep(1)
            root = tk.Tk()
            root.withdraw()
            source = filedialog.askopenfilename(initialdir = os.getcwd(), title = "Choose a sample")
            if source == "":
                raise Cancel
        # Handling file types
        if source[-3:] == "wav":
            file = source
        else:
            try:
                not_wav = pd.from_file(source, source[-3:])
                not_wav.export(".temp_soundfile.wav", format="wav")
                file = ".temp_soundfile.wav"
            except FileNotFoundError:
                print("  > unable to find file '{0}'".format(source))
                print("  > make sure to include .wav/.mp3/etc extension")
                self.source = None
                return self.read_file__()
        self.source = ["file", file]
        # Reading and Processing File
        try:
            recording, rate = sf.read(file)
        except RuntimeError:
            print("  > unable to find or read '{0}'. Is that the correct extension?".format(source))
            self.source = None
            return self.read_file__()
        try:
            os.remove(".temp_soundfile.wav")
        except FileNotFoundError:
            pass
        self.arr = recording.tolist()
        if not isinstance(self.arr[0], list):
            self.arr = [[i, i] for i in self.arr]
        self.rate = rate
        info_block("  sound file '{0}' read successfully".format(source), indent=2)


    # Representation #
    def __repr__(self):
        string = "'{0}'. {1} object from".format(self.name, self.type)
        for ind in range(len(self.source) // 2):
            string += " {0}: {1};".format(self.source[2 * ind], self.source[2 * ind + 1])
        return string


    def info(self):
        section_head("Info for {0} '{1}'".format(self.type, self.name))
        print("  sourced from {0}: {1}".format(self.source[0], self.source[1]))
        for ind in range(2, len(self.source) // 2):
            print("    {0}: {1}".format(self.source[2 * ind], self.source[2 * ind + 1]))
        print("  parent: {0}".format(self.parent))
        print("  rate: {0} samples per second".format(self.rate))
        print("  size: {0:.4f} seconds, {1:,} samples".format(self.size_secs(), self.size_samps()))
        print("  pan: {0}".format(self.pan_val))


    def get_name(self):
        return self.name


    # Metadata #

    def rename(self, name=None):
        if name is None:
            print("  Give this {0} a name: ".format(self.type), end="")
            name = inpt("obj")
            print("  named '{0}'".format(name))
        else:
            name = inpt_process(name, 'obj')
        self.name = name
        try:
            self.parent.validate_child_name(self)
        except AttributeError:
            pass


    def playback(self, duration=5, start=0, first_time=True):
        duration = t(Relativism.TEST_BPM, inpt_process(start, 'beat'))
        start = t(Relativism.TEST_BPM, inpt_process(start, 'beat'))
        section_head(" Playback")

        print("  preparing...")
        start_ind = int(start * self.rate)
        if duration <= 0:
            end_ind = self.size_samps()
        else:
            end_ind = start_ind + int(duration * self.rate)
        arr = self.arr[start_ind : end_ind]
        if self.pan_val > 0:
            arr = [
                [i * self.pan_val, j + (self.pan_val * i)] for i, j in arr
            ]
        elif self.pan_val < 0:
            arr = [
                [i - (self.pan_val * j), -j * self.pan_val] for i, j in arr
            ]

        print("  playing...")
        try:
            sd.play(arr, self.rate)
            sd.wait()
        except TypeError as e:
            if first_time:
                retry = True
                err_mess("Error playing back. Trying again")
                self.arr = [[float(i), float(j)] for i,j in self.arr]
                self.playback(duration, start, False)
            else:
                raise e
        print("  finished playback")


    def write_to_wav(self, outfile=None):
        section_head("Writing to file")
        if outfile is None:
            print("  select output file name: ", end="")
            outfile = inpt("file")
        outfile = re.sub(r"\..*", ".wav", outfile)
        if ".wav" not in outfile:
            outfile += ".wav"
        try:
            sf.write(outfile, self.arr, self.rate)
            print("  written successfully\n")
        except TypeError as e:
            print("  > Failed to write to file '{0}': {1}".format(outfile, e))


    def size_samps(self):
        return len(self.arr)
    

    def size_secs(self):
        return len(self.arr) / self.rate


    # Simple edit processes #
    def stretch(self, factor):
        """
        0.2, 5
        stretch by factor
            factor (float): >0
        """
        factor = inpt_process(factor, 'float', allowed=[0, None])
        print("  stretching by a factor of {0}...".format(factor))
        new_rec = []
        factor_count = 0
        for i in self.arr:
            factor_count += factor
            for _ in range(int(factor_count)):
                new_rec.append(i)
            factor_count = factor_count - int(factor_count)
        self.arr = new_rec


    def sliding_stretch(self, i_factor, f_factor, start=0, end=None):
        """
        0.2, 5; 0.2, 5;
        stretch by factor
            i_factor, f_factor (float): >0
            (optional) start, end: start and end of sliding stretch in 
        """
        i_factor = inpt_process(i_factor, "flt", allowed=[0, None])
        f_factor = inpt_process(f_factor, "flt", allowed=[0, None])
        start = t(Relativism.TEST_BPM, inpt_process(start, "beat"))
        if end is None:
            end = len(self.arr)
        else:
            end = t(Relativism.TEST_BPM, inpt_process(end, 'beat'))
            end = int(end * self.rate)
        print("  sliding stretch, from factor {0}x to {1}x...".format(i_factor, f_factor))
        start = int(start * self.rate)
        new_rec = self.arr[:start]
        factor_count = 0
        factor = i_factor
        delta_factor = (f_factor - i_factor) / (end - start)
        for i in self.arr[start:end]:
            factor_count += factor
            for _ in range(int(factor_count)):
                new_rec.append(i)
            factor_count = factor_count - int(factor_count)
            factor += delta_factor
        new_rec += self.arr[end:]
        self.arr = new_rec


    def reverse(self):
        """
        simple reverse of self.arr
        updates self.arr
        """
        print("  reversing...")
        self.arr = self.arr[::-1]


    def scramble(self, amount):
        """
        1, 10;
        move chunk of between 1/2 and 1/8th of a second to a new random
        index in the array
        amount is number of scrambles
            amount (int): >=1
        """
        amount = inpt_process(amount, "int", allowed=[1, None])
        while amount >= 1:
            print("  scrambling, {0} to go...".format(amount))
            chunk = self.rate // rd.randint(2, 8)
            start = rd.randint(0, len(self.arr) - chunk)
            new = rd.randint(0, len(self.arr) - chunk)
            chunk_arr = self.arr[start:start+chunk]
            self.arr = self.arr[:start] + self.arr[start+chunk:]
            self.arr = self.arr[:new] + chunk_arr + self.arr[new:]
            amount -= 1


    def amplify(self, factor):
        """
        0.5, 1.5;
        multiply amplitude by factor
            factor (float): 0 to >1
        """
        factor = inpt_process(factor, 'float', allowed=[0, None])
        print("  amplifying by {0}x...".format(factor))
        for i in range(len(self.arr)):
            self.arr[i][0] *= factor
            self.arr[i][1] *= factor


    def repeat(self, times):
        """
        1, 10;
        repeat a number of times
            times (int): >=1
        """
        times = inpt_process(times, 'int', allowed=[1, None])
        print("  repeating {0} times...".format(times))
        self.arr = self.arr * times


    def ir_repeat(self, times, percent):
        """
        1, 10; 1, 100;
        repeat number of times, skipping percent of repeats (replaced with silence)
            times (int): >=1
            percent: 0 to 100
        """
        times = inpt_process(times, 'int', allowed=[1, None])
        percent = inpt_process(percent, 'pcnt', allowed=[0, 100])
        print("  irregular repeat {0} times at {1}%...".format(times, percent))
        orig_size = self.size_samps()
        orig_arr = self.arr
        for _ in range(int(times)):
            if rd.randint(0, 100) <= percent:
                self.arr += [[0, 0] for _ in range(orig_size)]
            else:
                self.arr += orig_arr


    def extend(self, length, placement="a"):
        """
        0, 1;
        extend with silence by a number of seconds
            (optional) placement: "a"=after, "b"=before
        """
        length = t(Relativism.TEST_BPM, inpt_process(length, 'beat'))
        if placement == "b":
            before = " before"
        else:
            before = ""
        print("  extending by {0} seconds{1}...".format(length, before))
        silence = [[0, 0] for _ in range(int(self.rate * length))]
        if placement == "b":
            self.arr = silence + self.arr
        else:
            self.arr += silence


    def swap_channels(self):
        """
        swap stereo channels
        """
        print("  swapping stereo channels...")
        self.arr = [[j, i] for i, j in self.arr]
    

    def pan(self, amount):
        """
        -1, 1;
            amount (float): -1 to 1 (left to right)
        """
        amount = inpt_process(amount, 'float', allowed=[-1, 1])
        print("  Setting pan to {0}...".format(amount))
        self.pan_val = amount


    def trim(self, left, right=None):
        """
        0, 2;
        trim from left secs to right secs
        """
        if right is None:
            print("  trimming first {0} seconds".format(left))
            right = self.size_samps()
        else:
            print("  trimming everything outside {0} to {1} seconds".format(left, right))
        if left * self.rate > self.size_samps():
            print("  > this will empty the recording, confirm? [y/n]: ", end="")
            if not inpt("y-n"):
                return
            self.arr = []
        else:
            self.arr = self.arr[int(left * self.rate):int(right * self.rate)]  


    def fade_in(self, seconds, start=0):
        """
        0, 5; 
        fade in
        """
        print("  Fading in {0} seconds starting at {1} seconds...".format(seconds, start))
        length = int(self.rate * seconds)
        for i in range(length):
            try:
                self.arr[i + start][0] *= i / length
                self.arr[i + start][1] *= i / length
            except IndexError:
                pass


    def fade_out(self, seconds, end=None):
        """
        0, 5;
        fade out
        """
        if end is None:
            end == self.size_samps()
        else:
            end *= self.rate
        print("  Fading out {0} seconds ending at {1} seconds...".format(seconds, end))
        length = int(self.rate * seconds)
        for i in range(int(end) - length, int(end)):
            try:
                self.arr[i][0] *= (length - i) / length
                self.arr[i][1] *= (length - i) / length
            except IndexError:
                pass


    # Meta-functions #
    def random_method(self):
        """
        implement random sound-editing on recording, with radnom args
        """
        non_edit_methods = ["size_secs", "size_samps", "change_savefile", "rename", 
        "options", "process", "random_method", "info", "read_file__", "write_to_file",
        "playback"]
        methods = [func for func in dir(self.__class__) if callable(getattr(self.__class__, \
            func)) and "__" not in func and func not in non_edit_methods]
        func = rd.choice(methods)
        doc = eval(self.__class__ + "." + func + ".__doc__").split("\n")[1]
        doc = re.sub(r"\s+", "", doc)
        args = doc.split(";")
        if len(args) == 1:
            args = []
        else:
            print(args)
            if args[-1] == "":
                del args[-1]
            for i in range(len(args)):
                min_arg, max_arg = args[i].split(",")
                args[i] = rd.uniform(float(min_arg), float(max_arg))
            print(args)
        try:
            func = eval("self." + func)
            func(*args)
        except TypeError as e:
            print("  > Wrong number of arguments: {0}".format(e))


    def processes(self):
        print("\n    {process}\n\t{arguments in order, with optional args in [brackets]}\n")
        print("  - Amplify\n\tfactor: 0-1 makes quieter, >1 makes louder")
        print("  - Bitcrusher_1: swaps adjacent bits\n\tamount: 0-100+ (percentage)")
        print("  - Bitcrusher_2: shrink and stretch bitcrushing\n\tamount: 0-100+ (percentage)")
        print("  - Change_Savefile")
        print("  - Distortion_1: simple white noise injection\n\tamount: 0-100+")
        print("  - Extend: add silence to beginning or end\n\t" + \
            "seconds of silence\n\t['b' to extend before]")
        print("  - Fade_in\n\tseconds: length of fade in\n\t[start: seconds to " + \
            "start at, default 0. Negative creates\n\t  partial fade-in]")
        print("  - Fade_out\n\tseconds: length of fade out\n\t[end: seconds to " + \
            "end fade-out at, default end of recording.\n\t  Number greater than " + \
            "length of rec gives partial fade in]")
        print("  - Info: get info of this {0} object".format(self.type))
        print("  - Ir_repeat: irregular repeat\n\ttimes\n\tpercent of skips")
        print("  - Muffler: smoothes high frequencies, makes things sound muffled\n\t" + \
            "amount: integer, number of passes through the waveform")
        print("  - Pan\n\tamount: -1 (L) to 1 (R)")
        print("  - Playback\n\tduration: seconds. defaults to 5, enter 0 to play whole recording\n\t" + \
            "[start: time in seconds to start at, defaults to 0]" )
        print("  - Rename")
        print("  - Repeat\n\ttimes: integer >=1")
        print("  - Reverse")
        print("  - Scramble\n\tnumber of scrambles: integer >=1")
        print("  - Stretch\n\tfactor: number, 0-1 shrinks, >1 stretches")
        print("  - Swap_channels: swap stereo channels")
        print("  - Trim: trim all audio before <left> and after <right> seconds\n\t" + \
            "left: seconds\n\t[right: seconds, no right trim if blank]")
        print("  - Write_to_wav\n\tfilename to write to (wav files only)")


    def process__(self):
        process(self)


    def pre_process__(self, process):
        """
        actions to run before process: save current rec to 
        """
        if process != 'undo':
            self.update_recents__()
    
    
    def post_process__(self, process):
        """
        """
        self.save()


    def update_recents__(self):
        if len(self.recents) == 0 or (self.recents[0] == self.arr):
            self.recents.insert(0, self.arr)
            if len(self.recents) > 5:
                self.recents.pop()


    def undo(self):
        """
        arr pulled from most recent
        """
        section_head("Undoing ...")
        self.arr = self.recents.pop(0)


    def save(self, silent=False):
        """
        returns bool: true on success
        """
        # TODO: determine whether save should happen
        if not isinstance(silent, bool):
            silent = False
        if (self.parent is None):
            if not silent:
                err_mess("{0} {1} has no parent to save under!".format(self.type, self.name))
            return False
        else:
            # duplicate with no recents
            dup = Recording(array=self.arr, source=self.source, name=self.name,
                rate=self.rate, parent=self.parent, hidden=True)
            try:
                self.parent.save_child__(dup)
                return True
            except (AttributeError, NotImplementedError):
                    err_mess("Parent {0} '{1}' has not implemented save feature".format(
                        self.parent.type, self.parent.get_name()))


def initialize():
    """
    set infile, outfile
    """
    infile, outfile = None, None

    for i in sys.argv[1:]:
        if re.fullmatch(r"^infile=.+", i) or re.fullmatch(r"^f=.+", i):
            infile = re.sub(r".+=", "", i)
        elif re.fullmatch(r"^outfile=.+", i) or re.fullmatch(r"^o=.+", i):
            outfile = re.sub(r".+=", "", i)
        else:
            print("  > Unrecognized command line flag: '" + i +"'. Ignoring...")

    return infile, outfile



def sd_select_device(dev_type='in'):
    """
    type: in or out
    returns [index, name] of device
    """
    info_title("Devices by index ({0} found):".format(len(sd.query_devices())))
    for i in str(sd.query_devices()).split('\n'):
        info_line(i)
    while True:
        p("Enter desired device index")
        device_ind = inpt('int')
        try:
            device = sd.query_devices()[device_ind]
        except IndexError:
            err_mess("No device with index {0}".format(device_ind))
            continue
        if dev_type in ('in', 'input'):
            if device['max_input_channels'] < 1:
                err_mess("Device cannot be used as an input")
                continue
        elif dev_type in ('out', 'output'):
            if device['max_output_channels'] < 1:
                err_mess("Device cannot be used as an output")
        device_name = device['name']
        info_block("'{0}' selected".format(device_name))
        return [device_ind, device_name]


def main_rec_obj():

    infile, outfile = initialize()
    
    a = Recording(source=infile)

    process(a)


if __name__ == "__main__":
    main_rec_obj()
