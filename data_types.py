"""
creating data with units

Units.new() is method to create arbitrary units, and Units.samps/.secs/.beats
are shortcuts to common ones. 

Project.rate is used for sample-related conversions, and you must pass a bpm
context to conversion methods <value>.secs/.samps/.beats when converting to
or from beats (as bpm can be variable throughout project). Bpm context is handled
in Project.get_bpm()
"""


import pint
from errors import *

import math
import re





def RelUnit(number, type_):
    """
    shortcut function for creating data
    """
    return Units.new(number, type_)



def proj_rate_wrapper():
    try:
        return Project.get_rate()
    except NameError:
        return Units.rate(44100)

def proj_bpm_wrapper(bpm_context):
    try:
        return Project.get_bpm(bpm_context)
    except NameError:
        return Units.bpm(120)



class Units:
    """
    class for creating data with units
    """

    # unit registry
    _reg = pint.UnitRegistry()

    @staticmethod
    def setup():
        """
        initalize beat, samplerate, and percent units
        """

        # define beats
        for i in Units._get_beat_frac_tables():
            if i[2] == "beat":
                Units._reg.define("beat = [beat_time] = b")
            else:
                Units._reg.define("{0} = {1} beat = {2}".format(i[2], i[1], i[0]))

        # define samples
        Units._reg.define("sample = [sample_time] = samp")

        # percent
        Units._reg.define(pint.unit.UnitDefinition('percent', 'pct', ('pct', 'pcnt'), 
            pint.converters.ScaleConverter(1 / 100.0)))

        # samplerate
        cont = pint.Context('samplerate')
        cont.add_transformation("[sample_time]", "[time]", 
            lambda reg, x: x / proj_rate_wrapper())
        cont.add_transformation("[time]", "[sample_time]",
            lambda reg, x: x * proj_rate_wrapper())
        Units._reg.add_context(cont)
        Units._reg.enable_contexts('samplerate')

        # bpm
        cont = pint.Context("bpm")
        cont.add_transformation("[beat_time]", "[time]", 
            lambda reg, x, bpm_context: x / proj_bpm_wrapper(bpm_context).to("beats/second"))
        cont.add_transformation("[time]", "[beat_time]", 
            lambda reg, x, bpm_context: x * proj_bpm_wrapper(bpm_context).to("beats/second"))
        Units._reg.add_context(cont)

    @staticmethod
    def bpm_convert_context(bpm_context):
        return Units._reg.context('bpm', bpm_context=bpm_context)

    @staticmethod
    def new(*args):
        if isinstance(args[0], Units._reg.Quantity):
            try:
                return args[0].to(args[1])
            except:
                return args[0]
        else:
            return Units._reg.Quantity(*args)

    # Rate Makers

    @staticmethod
    def rate(val):
        return Units.new(val, "samples/second")

    @staticmethod
    def bpm(val):
        return Units.new(val, "beats/minute")

    # Time Makers

    @staticmethod
    def samps(val):
        return Units.new(val, "samples")

    @staticmethod
    def secs(val):
        return Units.new(val, "seconds")

    @staticmethod
    def beats(val):
        try:
            int(val)
            return Units.new(val, 'beats')
        except ValueError:
            # already have beat-type in string
            return Units.new(val)


    # static conversion helpers
    @staticmethod
    def valid_beatsec(beat):
        """
        used by inpt_processing only
        raise TypeError on invalid,
        return RelBeats/RelSecs on correct
        """
        # is beatsec already
        if isinstance(beat, Units._reg.Quantity):
            if beat.check('[rhythm_time]'):
                return beat
            elif beat.check('[time]'):
                return beat
            else:
                raise TypeError("Invalid beat/sec")

        beat = str(beat).lower().strip()
        # split number and beat name
        beat = re.sub(r'%', '', beat)
        if re.match(
            #  num   decimal        sci notation        beat name
            r"^[0-9]*(\.[0-9]+){0,1}(e-{0,1}[0-9]+){0,1}[a-z]{1,3}$", beat
        ) is None:
            raise TypeError("Invalid beat/sec")
        temp_split = re.sub(r"^([0-9]*(\.[0-9]+){0,1}(e-{0,1}[0-9]+){0,1})", r"\1%", beat)
        num, beat_type = temp_split.split("%")
        RelTime._get_beat_frac(beat_type)
        return RelBeats(num, beat_type)

    @staticmethod
    def beats_to_samps(num, beat_type):
        # handle number
        if num == "":
            num = 1
        else:
            num = float(num)
        sec_per_beat = 60 / Relativism.bpm()
        frac = RelTime._get_beat_frac(beat_type)
        return num * frac * sec_per_beat * Relativism.rate()

    @staticmethod
    def _get_beat_frac(beat):
        fracs = RelTime._get_beat_frac_tables()
        for i in fracs:
            if beat == i[0]:
                return i[1]
        raise TypeError

    @staticmethod
    def _get_beat_frac_tables():
        return [
            ["sfn", 1/16, "sixtyfourth-note"],
            ["tsn", 1/8, "thirtysecond-note"],
            ["sn", 1/4, "sixteenth-note"],
            ["en", 1/2, "eighth-note"],
            ["qn", 1, "quarter-note"],
            ["hn", 2, "half-note"],
            ["wn", 4, "whole-note"],

            ["sb", 1/16, "sixteenth-beat"],
            ["eb", 1/8, "eighth-beat"],
            ["qb", 1/4, "quarter-beat"],
            ["hb", 1/2, "half-beat"],
            ["b", 1, "beat"],
        ]


    @staticmethod
    def beat_options():
        note_fracs = [
            "Music Notation style\t",
            "sfn: sixty-fourth note\t",
            "tsn: thirty-second note\t",
            "sn:  sixteenth note\t\t",
            "en:  eighth note\t\t",
            "qn:  quarter note\t\t",
            "hn:  half note\t\t",
            "wn:  whole note\t\t"
        ]
        beat_fracs = [
            "Beat Notation style",
            "sb: sixteenth of a beat",
            "eb: eighth of a beat",
            "qb: quarter of a beat",
            "hb: half of a beat",
            "b:  one beat",
            "2b",
            "4b",
        ]
        print("\n  There are two methods of signifying beat lengths. Both work equally well:\n")
        print("   ", note_fracs[0], "\t" + beat_fracs[0])
        print("   ", "-" * 20, " "*14, "-"*19)
        for i in range(1, 8):
            print("   ", note_fracs[i], "=", "\t" + beat_fracs[i])
        print("\n    (half notes are always two")
        print("    quarter notes, whole notes")
        print("    are always four)\n")
        print("    Beats are signified by one of these notations, with an optional")
        print("    leading number. For example, '3qn' would be 3 quarter notes, ")
        print("    the equivilant of '3b', and also '6en' and '6hb'.")
        print("\n    Time can also be indicated with just a number, which will be")
        print("    interpreted as seconds")

    # FREQUENCY

    def _freq_to_note(self):
        freq_to_note = {v:k for k,v in RelPitch._get_freq_table().items()}
        closest_note = freq_to_note[self.frequency] if self.frequency \
            in freq_to_note else freq_to_note[min(freq_to_note.keys(), key=lambda k: abs(k-self.frequency))]
        closest_note_freq = RelPitch._get_freq_table()[closest_note]
        cents = 1200 * math.log(self.frequency/closest_note_freq, 2)
        return (closest_note, cents)


    def _note_to_freq(self):
        freq = RelPitch._get_freq(self.note_value.lower().strip())
        cents_freq = 2**(self.cents_value/1200) * freq
        return cents_freq


    def octave(self, num):
        return self * (2 ** num)


    def get_period(self, rate):
        """
        get period in samples of this frequency
        """
        return rate / self.frequency

    # static freq helpers

    @staticmethod
    def valid_freq(note):
        """
        returns frequency of note as int. raises TypeError if note name is misformed.
        C0-B8 is hard coded, above or below (not recommended anyway) is extrapolated
        Args:
            note: freq as string or name of note in C#1 or Db1 notation
        Returns:
            int: frequency
        """
        # is already relpitch
        if isinstance(note, RelPitch):
            return note
        # note is number already, in any form
        try:
            note = abs(float(note))
            if note == 0:
                raise TypeError("Zero frequency is not permitted")
            return RelFreq(note)
        except ValueError:
            pass
        note = note.lower().strip()
        # if note is not formed properly
        if re.match(r"^[a-g][b#]{0,1}([0-9]|10)$", note) is None:
            err_mess("Note '{0}' is not properly formed or out of octave range 0-10 (inclusive)".format(note))
            raise TypeError("Invalid note/frequency")
        # note is regular
        return RelFreq( RelPitch._get_freq(note) )

    @staticmethod
    def _get_freq(note):
        """
        get formatted freq from table
        """
        freq_arr = Units._get_freq_table()
        # if note is wrong sharp/flat (ie E#)
        note = re.sub("e#", "f", note)
        note = re.sub("fb", "e", note)
        note = re.sub("b#", "c", note)
        note = re.sub("cb", "b", note)
        return freq_arr[note]

    @staticmethod
    def _get_freq_table():
        """
        big note-name to freq mapping
        """
        return {
            "c0": 16.35,
            "c#0": 17.32,
            "db0": 17.32,
            "d0": 18.35,
            "d#0": 19.45,
            "eb0": 19.45,
            "e0": 20.60,
            "f0": 21.83,
            "f#0": 23.12,
            "gb0": 23.12,
            "g0": 24.50,
            "g#0": 25.96,
            "ab0": 25.96,
            "a0": 27.50,
            "a#0": 29.14,
            "bb0": 29.14,
            "b0": 30.87,
            "c1": 32.70,
            "c#1": 34.65,
            "db1": 34.65,
            "d1": 36.71,
            "d#1": 38.89,
            "eb1": 38.89,
            "e1": 41.20,
            "f1": 43.65,
            "f#1": 46.25,
            "gb1": 46.25,
            "g1": 49.00,
            "g#1": 51.91,
            "ab1": 51.91,
            "a1": 55.00,
            "a#1": 58.27,
            "bb1": 58.27,
            "b1": 61.74,
            "c2": 65.41,
            "c#2": 69.30,
            "db2": 69.30,
            "d2": 73.42,
            "d#2": 77.78,
            "eb2": 77.78,
            "e2": 82.41,
            "f2": 87.31,
            "f#2": 92.50,
            "gb2": 92.50,
            "g2": 98.00,
            "g#2": 103.83,
            "ab2": 103.83,
            "a2": 110.00,
            "a#2": 116.54,
            "bb2": 116.54,
            "b2": 123.47,
            "c3": 130.81,
            "c#3": 138.59,
            "db3": 138.59,
            "d3": 146.83,
            "d#3": 155.56,
            "eb3": 155.56,
            "e3": 164.81,
            "f3": 174.61,
            "f#3": 185.00,
            "gb3": 185.00,
            "g3": 196.00,
            "g#3": 207.65,
            "ab3": 207.65,
            "a3": 220.00,
            "a#3": 233.08,
            "bb3": 233.08,
            "b3": 246.94,
            "c4": 261.63,
            "c#4": 277.18,
            "db4": 277.18,
            "d4": 293.66,
            "d#4": 311.13,
            "eb4": 311.13,
            "e4": 329.63,
            "f4": 349.23,
            "f#4": 369.99,
            "gb4": 369.99,
            "g4": 392.00,
            "g#4": 415.30,
            "ab4": 415.30,
            "a4": 440.00,
            "a#4": 466.16,
            "bb4": 466.16,
            "b4": 493.88,
            "c5": 523.25,
            "c#5": 554.37,
            "db5": 554.37,
            "d5": 587.33,
            "d#5": 622.25,
            "eb5": 622.25,
            "e5": 659.25,
            "f5": 698.46,
            "f#5": 739.99,
            "gb5": 739.99,
            "g5": 783.99,
            "g#5": 830.61,
            "ab5": 830.61,
            "a5": 880.00,
            "a#5": 932.33,
            "bb5": 932.33,
            "b5": 987.77,
            "c6": 1046.50,
            "c#6": 1108.73,
            "db6": 1108.73,
            "d6": 1174.66,
            "d#6": 1244.51,
            "eb6": 1244.51,
            "e6": 1318.51,
            "f6": 1396.91,
            "f#6": 1479.98,
            "gb6": 1479.98,
            "g6": 1567.98,
            "g#6": 1661.22,
            "ab6": 1661.22,
            "a6": 1760.00,
            "a#6": 1864.66,
            "bb6": 1864.66,
            "b6": 1975.53,
            "c7": 2093.00,
            "c#7": 2217.46,
            "db7": 2217.46,
            "d7": 2349.32,
            "d#7": 2489.02,
            "eb7": 2489.02,
            "e7": 2637.02,
            "f7": 2793.83,
            "f#7": 2959.96,
            "gb7": 2959.96,
            "g7": 3135.96,
            "g#7": 3322.44,
            "ab7": 3322.44,
            "a7": 3520.00,
            "a#7": 3729.31,
            "bb7": 3729.31,
            "b7": 3951.07,
            "c8": 4186.01,
            "c#8": 4434.92,
            "db8": 4434.92,
            "d8": 4698.63,
            "d#8": 4978.03,
            "eb8": 4978.03,
            "e8": 5274.04,
            "f8": 5587.65,
            "f#8": 5919.91,
            "gb8": 5919.91,
            "g8": 6271.93,
            "g#8": 6644.88,
            "ab8": 6644.88,
            "a8": 7040.00,
            "a#8": 7458.62,
            "bb8": 7458.62,
            "b8": 7902.13,
            "c9": 4186.01 * 2,
            "c#9": 4434.92 * 2,
            "db9": 4434.92 * 2,
            "d9": 4698.63 * 2,
            "d#9": 4978.03 * 2,
            "eb9": 4978.03 * 2,
            "e9": 5274.04 * 2,
            "f9": 5587.65 * 2,
            "f#9": 5919.91 * 2,
            "gb9": 5919.91 * 2,
            "g9": 6271.93 * 2,
            "g#9": 6644.88 * 2,
            "ab9": 6644.88 * 2,
            "a9": 7040.00 * 2,
            "a#9": 7458.62 * 2,
            "bb9": 7458.62 * 2,
            "b9": 7902.13 * 2,
            "c10": 4186.01 * 4,
            "c#10": 4434.92 * 4,
            "db10": 4434.92 * 4,
            "d10": 4698.63 * 4,
            "d#10": 4978.03 * 4,
            "eb10": 4978.03 * 4,
            "e10": 5274.04 * 4,
            "f10": 5587.65 * 4,
            "f#10": 5919.91 * 4,
            "gb10": 5919.91 * 4,
            "g10": 6271.93 * 4,
            "g#10": 6644.88 * 4,
            "ab10": 6644.88 * 4,
            "a10": 7040.00 * 4,
            "a#10": 7458.62 * 4,
            "bb10": 7458.62 * 4,
            "b10": 7902.13 * 4,
        }

    @staticmethod
    def show_freq_table():
        info_title('Note\tFrequency (Hz)')
        for i in Units._get_freq_table().items():
            info_line(str(i[0]).capitalize() + ": \t" + str(i[1]))


    @staticmethod
    def note_options():
        print("Notes can be entered either as their direct frequency ('440', '228.3', etc), " +\
            "or as their musical notation note name and octave ('C4', 'Ab6', 'F#3', etc")




class UnitOperations:
    """
    methods to be aliased onto Units._reg.Quantity, below
    """

    @staticmethod
    def samps(value, bpm_context=None):
        """
        convert to samples, with optional bpm_context
        """
        with Units.bpm_convert_context(bpm_context):
            return value.to('samples')

    @staticmethod
    def secs(value, bpm_context=None):
        """
        convert to secs, with optional bpm_context
        """
        with Units.bpm_convert_context(bpm_context):        
            return value.to('seconds')

    @staticmethod
    def beats(value, bpm_context=None):
        """
        convert to beats, with optional bpm_context
        """
        with Units.bpm_convert_context(bpm_context):
            return value.to('beats')

    @staticmethod
    def trunc(value):
        """
        truncate value
        """
        return Units.new(int(value.magnitude), value.units)

"""
hacky method creation by aliasing
"""

# common unit alias methods for Quantity
Units._reg.Quantity.samps = UnitOperations.samps
Units._reg.Quantity.secs = UnitOperations.secs
Units._reg.Quantity.beats = UnitOperations.beats

# base units alias
Units._reg.Quantity.bu = Units._reg.Quantity.to_base_units

# round
Units._reg.Quantity.trunc = UnitOperations.trunc

# init
Units.setup()

