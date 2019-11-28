"""
creating data with units

Units.samps/secs/freq/rate etc should be the means of creating units when
possible. Units.new() is method to create other arbitrary units.

Project.rate is used for sample-related conversions, and you must pass a bpm
context to conversion methods <value>.secs/.samps/.beats when converting to
or from beats (as bpm can be variable throughout project). Bpm context is handled
in Project.get_bpm()
"""


import pint
import math
import re
import json

from src.errors import *
from src.utility import *


def RelUnit(number, type_):
    """
    shortcut function for creating data
    """
    return Units.new(number, type_)



def proj_rate_wrapper():
    """
    get rate, for initializing units when project hasnt been yet, defaults to 44100hz
    """
    try:
        return Project.get_rate()
    except NameError:
        return Units.rate(44100)

def proj_bpm_wrapper(bpm_context):
    """
    get bpm or 120 default
    """
    try:
        return Project.get_bpm(bpm_context)
    except NameError:
        return Units.bpm(120)


def numerize(val):
    """
    turn into an int if it has no decimal portion
    """
    val = float(val)
    if val % 1 == 0.0:
        return int(val)
    return val


class Units:
    """
    class for creating data with units. use new() method or the name of the units
    shorthand method (secs(), samps(), freq(), etc.)
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
        if len(args) == 0:
            raise TypeError("No args supplied to Units.new()")
        if isinstance(args[0], Units._reg.Quantity):
            try:
                return args[0].to(args[1])
            except:
                return args[0]
        else:
            return Units._reg.Quantity(*args)

    # RATE

    @staticmethod
    def rate(val):
        try:
            val.check("[sample_time]/[time]")
            return val.to_rate()
        except:
            return Units.new(numerize(val), "samples/second")

    @staticmethod
    def bpm(val):
        try:
            val.check("[beat_time]/[time]")
            return val
        except:
            return Units.new(numerize(val), "beats/minute")

    # BEATS/TIME

    @staticmethod
    def samps(val):
        try:
            val.check("[sample_time]")
            return val.to_samps()
        except:
            return Units.new(numerize(val), "samples")

    @staticmethod
    def secs(val):
        try:
            val.check("[beat_time]")
            return val.to_secs()
        except:
            return Units.new(numerize(val), "seconds")

    @staticmethod
    def beats(beat_str):
        """
        must pass beat-string (b, 2qn, 5 eb, etc)
        """
        # already have beat-type in string
        try:
            val.check("[beat_time]")
            return val
        except:  
            val = Units.new(beat_str)
            if val.check("[beat_time]"):
                return val
            else:
                raise ValueError("Invalid beat string, dimension was '{}'".format(val.dimensionality))

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
    @staticmethod
    def freq(val):
        if isinstance(val, PitchUnits):
            return val.to_freq()
        return RelFreq(numerize(val))
    
    @staticmethod
    def note(val):
        if isinstance(val, PitchUnits):
            return val.to_note()
        return RelNote(val)
        
    # Misc Makers

    @staticmethod
    def pcnt(val):
        return Units.new(numerize(val), "percent")





class UnitOperations:
    """
    methods to be aliased onto Units._reg.Quantity, below
    """

    @staticmethod
    def to_samps(value, bpm_context=None):
        """
        convert to samples, with optional bpm_context
        """
        with Units.bpm_convert_context(bpm_context):
            return value.to('samples')

    @staticmethod
    def to_invsamps(value, bpm_context=None):
        """
        convert to inverse samples, 1 / samples
        """
        with Units.bpm_convert_context(bpm_context):
            return (1 / (1 / value).to_samps())

    @staticmethod
    def to_secs(value, bpm_context=None):
        """
        convert to secs, with optional bpm_context
        """
        with Units.bpm_convert_context(bpm_context):        
            return value.to('seconds')

    @staticmethod
    def to_beats(value, bpm_context=None):
        """
        convert to beats, with optional bpm_context
        """
        with Units.bpm_convert_context(bpm_context):
            return value.to('beats')

    @staticmethod
    def to_rate(value, bpm_context=None):
        """
        convert to samples/sec, with optional bpm_context
        """
        with Units.bpm_convert_context(bpm_context):
            return value.to("samples/sec")

    @staticmethod
    def trunc(value):
        """
        truncate value
        """
        return Units.new(int(value.magnitude), value.units)


    @staticmethod
    def beat_repr(value):
        if value.check('[beat_time]'):
            for i in Units._get_beat_frac_tables():
                if i[2] == str(value.units):
                    return "{0}{1}".format(value.magnitude, i[0])
        else:
            raise TypeError("Non-beat argument for beat_repr")


"""
hacky method creation by aliasing
"""

# conversion
Units._reg.Quantity.to_samps = UnitOperations.to_samps
Units._reg.Quantity.to_secs = UnitOperations.to_secs
Units._reg.Quantity.to_beats = UnitOperations.to_beats
Units._reg.Quantity.to_invsamps = UnitOperations.to_invsamps
Units._reg.Quantity.to_rate = UnitOperations.to_rate
Units._reg.Quantity.beat_repr = UnitOperations.beat_repr

# base units alias
Units._reg.Quantity.bu = Units._reg.Quantity.to_base_units

# truncating and int()
Units._reg.Quantity.trunc = UnitOperations.trunc

# indexing function and aliasing
def ind(value):
    """
    get magnitude of sample value for indexing
    """
    try:
        return int(value.to_samps().magnitude)
    except:
        raise TypeError("Value to be used as an index could not converted to samples")

Units._reg.Quantity.__index__ = ind



# init
Units.setup()





class PitchUnits():
    """
    half static, half semi-abstact, pitch units class
    """

    _freq_table = {
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

    def get_period(self):
        return proj_rate_wrapper() / Units.new(self.frequency, "1/second")

    def __eq__(self, other):
        if isinstance(other, PitchUnits):
            return abs(self.frequency - other.frequency) <= 0.01
        return False

    @staticmethod
    def valid_pitch(note):
        """
        returns frequency of note as int. raises TypeError if note name is misformed.
        C0-B8 is hard coded, above or below (not recommended anyway) is extrapolated
        Args:
            note: freq as string or name of note in C#1 or Db1 notation
        Returns:
            int: frequency
        """
        # note is number already, in any form
        try:
            note = abs(float(note))
            if note == 0:
                raise TypeError
            return RelFreq(note)
        except ValueError:
            pass
        note = note.lower().strip()
        # if note is not formed properly
        if re.match(r"^[a-g][b#]{0,1}([0-9]|10)$", note) is None:
            err_mess("Note '{0}' is not properly formed or out of octave range 0-10 (inclusive)".format(note))
            raise TypeError
        # if note is wrong sharp/flat (ie E#)
        note = re.sub("e#", "f", note)
        note = re.sub("fb", "e", note)
        note = re.sub("b#", "c", note)
        note = re.sub("cb", "b", note)
        return RelNote(note)

    @staticmethod
    def show_freq_table():
        info_title('Note\tFrequency (Hz)')
        for i in RelPitch._freq_table.items():
            info_line(str(i[0]).capitalize() + ": \t" + str(i[1]))

    @staticmethod
    def freq_to_note(freq_val):
        """
        pass frequency as raw float
        """
        freq_to_note = {v:k for k,v in PitchUnits._freq_table.items()}
        closest_note = freq_to_note[freq_val] if freq_val \
            in freq_to_note else freq_to_note[min(freq_to_note.keys(), key=lambda k: abs(k-freq_val))]
        closest_note_freq = PitchUnits._freq_table[closest_note]
        cents = 1200 * math.log(freq_val/closest_note_freq, 2)
        return (closest_note, cents)

    @staticmethod
    def note_to_freq(note_val, cents_val):
        """
        convert to frequency
        """
        freq = PitchUnits._freq_table[note_val.lower().strip()]
        cents_freq = 2**(cents_val/1200) * freq
        return cents_freq

    @staticmethod
    def note_options():
        print("Notes can be entered either as their direct frequency ('440', '228.3', etc), " +\
            "or as their musical notation note name and octave ('C4', 'Ab6', 'F#3', etc")




class RelFreq(PitchUnits):

    def __init__(self, frequency):
        self.frequency = frequency

    def __repr__(self):
        return "{0}hz".format(decimal_format(self.frequency))

    def to_freq(self):
        return self
    
    def to_note(self):
        note, cents = PitchUnits.freq_to_note(self.frequency)
        return RelNote(note, cents)

    def to_whole_note(self):
        """
        convert to whole tone (no cents)
        """
        note, cents = PitchUnits.freq_to_note(self.frequency)
        return RelNote(note)

    def shift_octaves(self, n):
        """
        shift up or down by n octaves
        """
        return self.shift_semitones(12 * int(n))

    def shift_semitones(self, n):
        return RelFreq(self.frequency * (2 ** ( float(n)/12) ) )





class RelNote(PitchUnits):

    def __init__(self, note, cents=0):
        self.note_value = note
        self.cents_value = cents
        self.frequency = PitchUnits.note_to_freq(self.note_value, self.cents_value)

    def __repr__(self):
        if self.cents_value == 0:
            return "{0}".format(self.note_value.capitalize())
        elif self.cents_value > 0:
            return "{0}+{1}cents".format(self.note_value.capitalize(), decimal_format(self.cents_value))
        else:
            return "{0}{1}cents".format(self.note_value.capitalize(), decimal_format(self.cents_value))

    def to_note(self):
        return self

    def to_whole_note(self):
        return RelNote(self.note_value)

    def to_freq(self):
        return RelFreq(self.frequency)

    def shift_octaves(self, n):
        """
        shift up or down by n octaves
        """
        return self.shift_semitones(12 * int(n))

    def shift_semitones(self, n):
        """
        return new instance, shifted n semitones
        """
        shifted = self.to_freq().shift_semitones(n)
        if (self.cents_value == 0) and (n % 1 == 0):
            return shifted.to_whole_note()
        else:
            return shifted.to_note()




"""
how to have multiple loaded objects point to same instance,
not create conflicting copies of child?
"""


class RelTypeEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Units._reg.Quantity):
            return "<PINTQUANT>" + str(obj)

        elif isinstance(obj, RelativismObject):
            return "<REL-{0}>".format(obj.reltype) + 

        else:
            return json.JSONEncoder.default(self, obj)


def RelTypeDecoder(dct):

    for k,v in dct.items():

        if "<PINTQUANT>" in str(v):
            v = re.sub("<PINTQUANT>", "", v)
            dct[k] = Units.new(v)

    return dct



