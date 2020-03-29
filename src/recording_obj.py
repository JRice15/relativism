"""
Recording Object


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

import math
import os
import random as rd
import re
import sys
import time
import numpy as np

import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment as pd

from src.errors import *
from src.utility import *

from src.data_types import *
from src.object_data import (public_process, is_public_process, 
    RelativismObject, RelativismPublicObject)
from src.process import process
from src.input_processing import inpt, inpt_validate, input_dir, input_file
from src.output_and_prompting import (p, info_title, info_list, info_line, 
    section_head, info_block, nl, err_mess, critical_err_mess, show_error)
from src.analysis import Analysis
from src.path import join_path, split_path


class Recording(RelativismPublicObject):
    """
    Args:
        mode: "read", "record", or leave as None to use data passed in array
        arr: np.array for arr data, if mode is None
        file: file to read from, for readfile mode
        source_block: info dict if rec is generated
        name: name of array (will prompt if not given)
        rate: defaults to 44100
        parent:
        hidden:
        reltype:
        pan_val:

    Attributes:
        type (str): 'Recording'
        arr (list or None): wav array, if none is set will be read from file
        source_block (dict): source_block information for where this recording came from
        name (str or None): name of this object, will be prompted if None
        rate (int): samples per second of this recording
        pan_val (float): number -1 (L) to 1 (R)
        parent: pointer to parent Proj or Sampler, if exists
        recents: array of up to 5 recent arrs
    """

    # Initialization #
    def __init__(self,
            mode="load",
            arr=None, 
            file=None,
            source_block=None,
            name=None, 
            rate=44100,
            parent=None, 
            hidden=False, 
            reltype='Recording', 
            pan_val=0,
            path=None,
            rel_id=None,
        ):

        super().__init__(rel_id=rel_id, reltype=reltype, name=name, path=path, parent=parent)

        if name is None:
            self.rename()

        # path
        if self.path is None:
            if self.parent is not None:
                self.path = join_path(self.parent.path, self.get_data_filename(), is_dir=True)
            else:
                self.path = join_path(".", self.get_data_filename(), is_dir=True)
        os.makedirs(self.path, exist_ok=True)
        os.makedirs(join_path(self.path, "recents", is_dir=True), exist_ok=True)

        # audio data
        if not hidden:
            section_head("Initializing {0} '{1}'...".format(self.reltype, self.name))
        self.rate = Units.rate(rate)
        self.source_block = {} if source_block is None else source_block
        self.arr = np.asarray(arr)
        self.pan_val = pan_val

        # mode
        if mode in ('read', 'file', 'read_file'):
            self.read_file(file)
        elif mode in ('record', 'record_live'):
            self.record_live()
        elif mode is "load":
            if arr is None:
                self.init_mode()
        else:
            raise UnexpectedIssue("Unknown mode {0}".format(mode))




    def init_mode(self):
        """
        fill in initialization via input
        get recording by mode
        call get_help/playback if asked
        returns rec array
        """
        valid_modes = ("live Record (R)", "read from File (F)", 
            "relativism project or sampler Object (O)", "Help (H)")
        info_title("Available modes:")
        info_list(valid_modes)
        p("Select mode")
        mode = inpt('letter', allowed='rfh')

        # Record Mode
        if mode == "r":
            self.record_live()
        # File Mode
        elif mode == "f":
            self.read_file()
        elif mode == "o":
            raise NotImplementedError
        # Help
        elif mode == "h":
            raise NotImplementedError


    def record_live(self):
        """
        record -- but get this -- live!
        """
        section_head("Record mode")
        device_ind, device_name = sd_select_device()
        p("Enter recording duration (in seconds)")
        record_time = inpt('beatsec')
        p('Choose sample rate to record at, in samples per second. Hit enter to use default 44100')
        rate = inpt('int', required=False)
        if rate == '':
            rate = 44100
        self.rate = Units.rate(rate)
        print("  Press Enter to begin recording, or 'q' to quit: ", end="")
        inpt("none", required=False)
        time.sleep(0.05)
        section_head("Recording at input {0} ({1}) for {2}".format(device_ind, \
            device_name, record_time))
        sd.default.channels = 2
        recording = sd.rec(
            ind(record_time * self.rate), 
            self.rate.magnitude, 
            device=device_name)
        sd.wait()
        info_block("Finished recording")
        self.arr = recording
        if len(self.arr.shape) < 2:
            transpose = self.arr.reshape(-1, 1)
            self.arr = np.hstack((transpose, transpose))
        self.source_block = {
            'live recording': "input '{0}'".format(device_name)
        }


    def read_file(self, file_path=None):
        """
        reads files for recording object init
        takes multiple formats (via PyDub and Soundfile)
        updates self.source, self.arr, self.rate
        """
        section_head("Reading file")
        if file_path is None:
            print("  Choose an input sound file...")
            time.sleep(1)
            file_path = input_file()

        info_block("reading...")
        t1 = time.time()

        # Handling file types
        _,_,ext = split_path(file_path)
        if ext != "wav":
            try:
                not_wav = pd.from_file(file_path, file_path.ext)
                not_wav.export(".temp_soundfile.wav", format="wav")
                file_path = ".temp_soundfile.wav"
            except FileNotFoundError:
                print("  > unable to find file '{0}'".format(file_path))
                print("  > make sure to include .wav/.mp3/etc extension")
                return self.read_file()
                
        self.source_block["file"] = file_path
        # Reading and Processing File
        try:
            self.arr, rate = sf.read(file_path)
            self.rate = Units.rate(rate)
        except RuntimeError:
            print("  > unable to find or read '{0}'. Is that the correct extension?".format(file_path))
            return self.read_file()
        try:
            os.remove(".temp_soundfile.wav")
        except FileNotFoundError:
            pass
        if len(self.arr.shape) < 2:
            self.arr = NpOps.stereoify(self.arr)
        t2 = time.time()
        info_line("sound file '{0}' read successfully in {1:.4f} seconds".format(
            file_path, t2-t1))


    # Saving #
    def pre_process(self, process):
        """
        actions to run before process: save current rec to 
        """
        if self.get_method(process).is_edit_rec():
            self.update_recents()


    def post_process(self, process):
        """
        called after process calls method.
        """


    def update_recents(self):
        """
        update recents arr to include last arr
        """
        recents_dir = join_path(self.path, "recents")
        os.rename(
            join_path(self.path, self.get_data_filename() + ".wav"),
            join_path(recents_dir, str(time.time_ns()) + ".wav")
        )


    def parse_write_meta(self, attrs):
        """
        for parsing attribute data for writing
        """
        del attrs['arr']
        attrs["mode"] = "file"
        attrs["file"] = self.get_audiofile_fullpath()
        return attrs


    @public_process
    def undo(self):
        """
        cat: save
        desc: reverts to previous state (maximum of 5 times)
        """
        section_head("Undoing...")
        if len(self.recents) != 0:
            self.arr = self.recents.pop(0)
        else:
            err_mess("No history to revert to!")


    @public_process
    def save(self):
        """
        cat: save
        desc: save data
        """
        self.save_audio()
        self.save_metadata()


    @public_process
    def export_to_wav(self, outfile=None):
        """
        cat: save
        desc: save recording to wav file
        args:
            outfile: filename to save to. do not include '.wav' or any other extention
        """
        section_head("Writing to file")
        if outfile is None:
            print("  Enter output file name: ", end="")
            outfile = inpt("file")
        try:
            info_line("writing...")
            t1 = time.time()
            self.write_audio(outfile)
            t2 = time.time()
            info_line("written successfully in {0:.4f} seconds".format(t2 - t1))
        except TypeError as e:
            print("  > Failed to write to file '{0}': {1}".format(outfile, e))


    # Info #
    @public_process
    def info(self):
        """
        desc: display this objects data
        cat: info
        dev: essentially just an expanded repr. repr is also defined in super()
        """
        section_head("{0} '{1}'".format(self.reltype, self.name))
        info_line("sourced from {0}: {1}".format(self.source_block[0], self.source_block[1]))
        for ind in range(1, len(self.source_block) // 2):
            print("    {0}: {1}".format(self.source_block[2 * ind], self.source_block[2 * ind + 1]))
        info_line("parent: {0}".format(self.parent))
        info_line("rate: {0}".format(self.rate))
        info_line("size: {0:.4f}, {1:,}".format(self.size_secs(), self.size_samps()))
        info_line("pan: {0}".format(self.pan_val))


    def size_samps(self):
        """
        length of arr in samples
        """
        return Units.samps(self.arr.shape[0])


    def size_secs(self):
        """
        length of arr in secs
        """
        return (self.size_samps() / self.rate).to_secs()


    @public_process
    def playback(self, duration=5, start=0, first_time=True):
        """
        cat: info
        desc:
        args:
            [duration: beats/seconds. default 5]
            [start: beat/seconds to start at. defualts to beginning]
        """
        duration = inpt_validate(duration, 'beatsec')
        start = inpt_validate(start, 'beatsec')
        section_head("Playback of '{0}'".format(self.name))

        print("  preparing...")
        start_ind = ind(start * self.rate)
        if duration <= 0:
            end_ind = self.size_samps()
        else:
            end_ind = start_ind + ind(duration * self.rate)
        arr = self.arr[start_ind : end_ind]
        arr = self.get_panned_rec(arr)

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


    @public_process
    def view_waveform(self, start=0, end=None, precision=50):
        """
        cat: info
        desc: show the waveform of this audio
        args:
            [start: seconds/beats to begin view window. default beginning]
            [end: seconds/beats to end view window. -1 selects end. default end]
            [precision: percent of how detailed the plot should be. default 50]
        """
        start = inpt_validate(start, 'beatsec')
        if (end is None) or (end == "-1"):
            end = self.size_samps()
        else:
            end = inpt_validate(end, 'beatsec')
            if end.samples_value >= self.size_samps():
                end = self.size_samps()
        if end <= start:
            err_mess("End cannot be before or equal to start")
            raise Cancel
        precision = inpt_validate(precision, 'pcnt', allowed=[5, 10000])

        info_block("Generating waveform at {0}%...".format(precision))

        anlsys = Analysis(self, start=start, end=end)
        frame_len = (end - start) / (precision * 2)
        anlsys.set_frame_lengths(frame_len)

        left = anlsys.arr[:, 0]
        right = anlsys.arr[:, 1]

        anlsys.plot(left, right, fill=True)


    # Metadata #
    @public_process
    def rename(self, name=None):
        """
        cat: meta
        desc: rename (and resave) this object
        args:
            name: name for this object
        """
        old_name = self.name

        super().rename(name)

        # rename files
        if old_name is not None:
            try:
                os.rename(self.get_path(old_name), self.get_path())
                os.rename(self.get_path(old_name, extension="wav"),
                    self.get_path(extension="wav")
                )
            except OSError:
                pass


    # Simple edit processes #
    @public_process
    def stretch(self, factor):
        """
        cat: edit
        desc: stretch by a factor
        args:
            factor: number >0; 0.2, 3
        """
        factor = inpt_validate(factor, 'float', allowed=[0, None])
        print("  stretching by a factor of {0:.4f}...".format(factor))
        new_rec = []
        factor_count = 0
        for i in self.arr:
            factor_count += factor
            for _ in range(int(factor_count)):
                new_rec.append(i)
            factor_count -= int(factor_count)
        self.arr = np.asarray(new_rec)


    @public_process
    def sliding_stretch(self, i_factor, f_factor, start=0, end=None):
        """
        cat: edit
        desc: stretch by sliding amount
        args:
            i_factor: initial factor, num >0; 0.2, 3;
            f_factor: final, num >0; 0.2, 3;
            [start: beat/second to begin. defaults beginning]
            [end: beat/second to end. defaults to end of rec]
        """
        i_factor = inpt_validate(i_factor, "flt", allowed=[0, None])
        f_factor = inpt_validate(f_factor, "flt", allowed=[0, None])
        start = inpt_validate(start, 'beatsec').to_samps()
        if end is None:
            end = self.size_samps()
        else:
            end = inpt_validate(end, 'beatsec').to_samps()
        print("  sliding stretch, from factor {0:.4f}x to {1:.4f}x...".format(i_factor, f_factor))
        beginning = self.arr[:start]

        middle = []
        factor_count = 0
        factor = i_factor
        delta_factor = (f_factor - i_factor) / ind(end - start)
        for i in self.arr[start:end]:
            factor_count += factor
            for _ in range(int(factor_count)):
                middle.append(i)
            factor_count = factor_count - int(factor_count)
            factor += delta_factor
        
        end = self.arr[end:]
        self.arr = np.vstack((beginning, middle, end))


    @public_process
    def reverse(self):
        """
        cat: edit
        desc: simple reverse
        """
        print("  reversing...")
        self.arr = self.arr[::-1]


    @public_process
    def amplify(self, factor):
        """
        cat: edit
        desc: multiply amplitude by factor. 0-1 to reduce, >1 to amplify
        args:
            factor: num >0; 0.5, 1.5;
        """
        factor = inpt_validate(factor, 'float', allowed=[0, 10])
        print("  amplifying by {0}x...".format(factor))
        self.arr *= factor


    @public_process
    def repeat(self, times):
        """
        cat: edit
        args:
            times: integer number of times to repeat, >=1; 1, 10;
        """
        times = inpt_validate(times, 'int', allowed=[1, None])
        print("  repeating {0} times...".format(times))
        self.arr = np.vstack([self.arr] * times)


    @public_process
    def extend(self, length, placement="a"):
        """
        cat: edit
        desc: extend with silence by a number of seconds/beats
        args:
            length: beats/seconds to extend; 0, 1;
            [placement: "a"=after, "b"=before. default after]
        """
        length = inpt_validate(length, 'beatsec')
        placement = inpt_validate(placement, "letter", allowed="ab")
        if placement == "b":
            before = " before"
        else:
            before = ""
        print("  extending by {0}{1}...".format(length, before))
        silence = np.zeros( shape=(ind(self.rate * length), 2) )
        if placement == "b":
            self.arr = np.vstack((silence, self.arr))
        else:
            self.arr = np.vstack((self.arr, silence))


    @public_process
    def swap_channels(self):
        """
        cat: edit
        desc: swap stereo channels
        """
        print("  swapping stereo channels...")
        self.arr = NpOps.swap_channels(self.arr)

    @public_process
    def pan(self, amount):
        """
        cat: edit
        desc: set pan value
        args:
            amount: number from -1 (left) to 1 (right); -1, 1;
        """
        amount = inpt_validate(amount, 'float', allowed=[-1, 1])
        print("  Setting pan to {0}...".format(amount))
        self.pan_val = amount


    def get_panned_rec(self, arr=None):
        """
        get panned version of self.arr, or arr if passed
        """
        if arr is None:
            arr = self.arr
        if self.pan_val > 0:
            return NpOps.join_channels(
                arr[:,0] * (1 - self.pan_val),
                arr[:,1] + (arr[:,0] * self.pan_val)
            )
        elif self.pan_val < 0:
            return NpOps.join_channels(
                arr[:,0] + (arr[:,1] * -self.pan_val), 
                arr[:,1] * (1 + self.pan_val)
            )
        else:
            return arr


    @public_process
    def trim(self, left, right=None):
        """
        cat: edit
        desc: trim to only contain audio between <left> and <right>
        args:
            left: beat/second; 0, 5;
            [right: beat/second. defaults to end; 10]
        """
        left = inpt_validate(left, 'beatsec')
        if right is None:
            print("  trimming first {0}".format(left))
            right = self.size_samps()
        else:
            right = inpt_validate(right, 'beatsec')
            print("  trimming everything outside {0} to {1}".format(left, right))
        left, right = left.to_secs(), right.to_secs()
        if left * self.rate > self.size_samps():
            print("  > this will empty the recording, confirm? [y/n]: ", end="")
            if not inpt("y-n"):
                return
            self.arr = np.empty(shape=(0,2))
        else:
            self.arr = self.arr[ind(left * self.rate) : ind(right * self.rate)]  


    @public_process
    def fade_in(self, dur, start=0):
        """
        cat: edit
        desc: fade in audio
        args:
            duration: duration in beats/seconds of fade-in; 0, 10;
            [start: beat/second to begin. defaults 0]
        """
        seconds = inpt_validate(dur, 'beatsec')
        start = ind(inpt_validate(start, 'beatsec'))
        print("  fading in {0} starting at {1}...".format(seconds, start))
        length = ind(self.rate * seconds)
        for i in range(length):
            try:
                self.arr[i + start][0] *= i / length
                self.arr[i + start][1] *= i / length
            except IndexError:
                if i + start >= 0:
                    return


    @public_process
    def fade_out(self, dur, end=None):
        """
        cat: edit
        desc: fade out audio
        args:
            duration: duration in beats/seconds of fade-out; 0, 10;
            [end: beat/second to end. defaults end of audio]
        """
        if end is None:
            end = self.size_secs()
        else:
            end = inpt_validate(end, "beatsec")
        seconds = inpt_validate(dur, "beatsec")
        print("  Fading out {0} ending at {1}...".format(seconds, end))
        length = ind(self.rate * seconds)
        for i in range(ind(end) - length, ind(end)):
            try:
                self.arr[i][0] *= (length - i) / length
                self.arr[i][1] *= (length - i) / length
            except IndexError:
                pass


    @public_process
    def random_method(self):
        """
        desc: implement random sound-editing on recording, with random args
        cat: edit
        """
        methods = [i[1] for i in self.method_data_by_category['Edits'].items()]
        method_data = rd.choice(methods)
        args = method_data.get_random_defaults()
        try:
            method_data.method_func(*args)
        except Exception as e:
            err_mess("Random Process error:")
            show_error(e)


    # Other #
    #TODO: duplicate


def sd_select_device(device_type='in'):
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
        if device_type in ('in', 'input'):
            if device['max_input_channels'] < 1:
                err_mess("Device cannot be used as an input")
                continue
        elif device_type in ('out', 'output'):
            if device['max_output_channels'] < 1:
                err_mess("Device cannot be used as an output")
        device_name = device['name']
        info_block("'{0}' selected".format(device_name))
        return [device_ind, device_name]



    # def command_line_init(self):
    #     """
    #     set source file from command line
    #     """

    #     indexes_to_del = []
    #     for i in range(1, len(sys.argv)):
    #         val = sys.argv[i].lower().strip()
    #         if re.fullmatch(r"^file=.+", val) or re.fullmatch(r"^f=.+", val):
    #             self.file = re.sub(r".+=", "", val)
    #             indexes_to_del.append(i)
    #         else:
    #             print("  > Unrecognized command line flag: '" + val +"'. Ignoring...")

    #     for i in sorted(indexes_to_del, reverse=True):
    #         del sys.argv[i]



def main_rec_obj():
    
    a = Recording(source='sources/t.wav', name='test')

    process(a)





if __name__ == "__main__":
    main_rec_obj()
