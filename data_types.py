"""
dont import this import input processing
"""

import abc
import re
from utility import *
import math

class RelativismData(abc.ABC):
    """
    abstract methods:
        __repr__
        __eq__
    """

    @abc.abstractmethod
    def __repr__(self):
        ...

    @abc.abstractmethod
    def __eq__(self, other):
        ...

    def strict_eq(self, other):
        return (self == other) and (self.type == other.type)

    def __add__(self, other):
        raise NotImplementedError
    def __sub__(self, other):
        raise NotImplementedError
    def __mul__(self, other):
        raise NotImplementedError
    def __matmul__(self, other):
        raise NotImplementedError
    def __truediv__(self, other):
        raise NotImplementedError
    def __floordiv__(self, other):
        raise NotImplementedError
    def __mod__(self, other):
        raise NotImplementedError
    def __divmod__(self, other):
        raise NotImplementedError
    def __pow__(self, other, modulo=None):
        raise NotImplementedError
    def __lshift__(self, other):
        raise NotImplementedError
    def __rshift__(self, other):
        raise NotImplementedError
    def __and__(self, other):
        raise NotImplementedError
    def __xor__(self, other):
        raise NotImplementedError
    def __or__(self, other):
        raise NotImplementedError

    #These methods are called to implement the binary arithmetic operations (+, 
    # -, *, @, /, //, %, divmod(), pow(), **, <<, >>, &, ^, |). For instance, 
    # to evaluate the expression x + y, where x is an instance of a class that 
    # has an __add__() method, x.__add__(y) is called. The __divmod__() method 
    # should be the equivalent to using __floordiv__() and __mod__(); it should 
    # not be related to __truediv__(). Note that __pow__() should be defined to 
    # accept an optional third argument if the ternary version of the built-in 
    # pow() function is to be supported.

    #If one of those methods does not support the operation with the supplied 
    # arguments, it should return NotImplemented.

    def __radd__(self, other):
        raise NotImplementedError
    def __rsub__(self, other):
        raise NotImplementedError
    def __rmul__(self, other):
        raise NotImplementedError
    def __rmatmul__(self, other):
        raise NotImplementedError
    def __rtruediv__(self, other):
        raise NotImplementedError
    def __rfloordiv__(self, other):
        raise NotImplementedError
    def __rmod__(self, other):
        raise NotImplementedError
    def __rdivmod__(self, other):
        raise NotImplementedError
    def __rpow__(self, other):
        raise NotImplementedError
    def __rlshift__(self, other):
        raise NotImplementedError
    def __rrshift__(self, other):
        raise NotImplementedError
    def __rand__(self, other):
        raise NotImplementedError
    def __rxor__(self, other):
        raise NotImplementedError
    def __ror__(self, other):
        raise NotImplementedError

    #These methods are called to implement the binary arithmetic operations (+, 
    # -, *, @, /, //, %, divmod(), pow(), **, <<, >>, &, ^, |) with reflected 
    # (swapped) operands. These functions are only called if the left operand 
    # does not support the corresponding operation 3 and the operands are of 
    # different types. 4 For instance, to evaluate the expression x - y, where 
    # y is an instance of a class that has an __rsub__() method, y.__rsub__(x) 
    # is called if x.__sub__(y) returns NotImplemented.

    #Note that ternary pow() will not try calling __rpow__() (the coercion rules 
    # would become too complicated).

    #Note If the right operand’s type is a subclass of the left operand’s type and 
    # that subclass provides the reflected method for the operation, this method 
    # will be called before the left operand’s non-reflected method. This behavior 
    # allows subclasses to override their ancestors’ operations.

    def __iadd__(self, other):
        raise NotImplementedError
    def __isub__(self, other):
        raise NotImplementedError
    def __imul__(self, other):
        raise NotImplementedError
    def __imatmul__(self, other):
        raise NotImplementedError
    def __itruediv__(self, other):
        raise NotImplementedError
    def __ifloordiv__(self, other):
        raise NotImplementedError
    def __imod__(self, other):
        raise NotImplementedError
    def __ipow__(self, other, modulo=None):
        raise NotImplementedError
    def __ilshift__(self, other):
        raise NotImplementedError
    def __irshift__(self, other):
        raise NotImplementedError
    def __iand__(self, other):
        raise NotImplementedError
    def __ixor__(self, other):
        raise NotImplementedError
    def __ior__(self, other):
        raise NotImplementedError

    #These methods are called to implement the augmented arithmetic assignments 
    # (+=, -=, *=, @=, /=, //=, %=, **=, <<=, >>=, &=, ^=, |=). These methods 
    # should attempt to do the operation in-place (modifying self) and return 
    # the result (which could be, but does not have to be, self). If a specific 
    # method is not defined, the augmented assignment falls back to the normal 
    # methods. For instance, if x is an instance of a class with an __iadd__() 
    # method, x += y is equivalent to x = x.__iadd__(y) . Otherwise, x.__add__(y) 
    # and y.__radd__(x) are considered, as with the evaluation of x + y. In certain 
    # situations, augmented assignment can result in unexpected errors (see Why 
    # does a_tuple[i] += [‘item’] raise an exception when the addition works?), 
    # but this behavior is in fact part of the data model.

    def __neg__(self):
        raise NotImplementedError
    def __abs__(self):
        raise NotImplementedError
    def __invert__(self):
        raise NotImplementedError

    #Called to implement the unary arithmetic operations (-, +, abs() and ~).


    #Called to implement operator.index(), and whenever Python needs to 
    # losslessly convert the numeric object to an integer object 
    # (such as in slicing, or in the built-in bin(), hex() and oct() 
    # functions). Presence of this method indicates that the numeric 
    # object is an integer type. Must return an integer.

    #Note In order to have a coherent integer type class, when __index__() is 
    # defined __int__() should also be defined, and both should return the same value.

    def __int__(self):
        raise NotImplementedError

    def __index__(self):
        raise NotImplementedError


class RelTime(RelativismData):

    def __init__(self, samples_value, type_):
        self.samples_value = samples_value
        self.type = type_


    def __eq__(self, other):
        try:
            return self.samples_value == other.samples_value
        except:
            return False


    def samps(self):
        return RelSamps(self.samples_value)


    def secs(self):
        return RelSecs(self.samples_value / Relativism.rate())


    def beats(self):
        beat_num = self.samples_value * Relativism.bpm() / (Relativism.rate() * 60)
        return RelBeats(str(beat_num) + "b")


    #static conversion helpers

    @staticmethod
    def valid_beatsec(beat):
        """
        used by inpt_processing only
        raise TypeError on invalid,
        return RelBeats/RelSecs on correct
        """
        # beat is number already, in secs
        try:
            return RelSecs(secs_val=abs(float(beat.strip())))
        except ValueError:
            pass

        beat = str(beat).lower().strip()
        # split number and beat name
        beat = re.sub(r'%', '', beat)
        if re.match(
            #  num   decimal        sci notation        beat name
            r"^[0-9]*(\.[0-9]+){0,1}(e-{0,1}[0-9]+){0,1}[a-z]{1,3}$", beat
        ) is None:
            raise TypeError
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
            ["sfn", 1/16, "sixty-fourth note"],
            ["tsn", 1/8, "thirty-second note"],
            ["sn", 1/4, "sixteenth note"],
            ["en", 1/2, "eighth note"],
            ["qn", 1, "quarter note"],
            ["hn", 2, "half note"],
            ["wn", 4, "whole note (always 4 quarter notes)"],

            ["sb", 1/16, "sixteenth of a beat"],
            ["eb", 1/8, "eighth of a beat"],
            ["qb", 1/4, "quarter of a beat"],
            ["hb", 1/2, "half of a beat"],
            ["b", 1, "one beat"],
        ]


    # arithmetic expressions
    def __add__(self, other):
        if (not isinstance(other, RelTime)):
            other = RelTime.valid_beatsec(other)
        return RelSamps(self.samples_value + other.samples_value)
    def __sub__(self, other):
        if (not isinstance(other, RelTime)):
            other = RelTime.valid_beatsec(other)
        return RelSamps(self.samples_value - other.samples_value)
    def __mul__(self, other):
        return RelSamps(int(self.samples_value * other))
    def __truediv__(self, other):
        return RelSamps(int(self.samples_value / other))      
    def __mod__(self, other):
        return RelSamps(int(self.samples_value % other))      

    def __index__(self):
        return int(self.samples_value)

    def __radd__(self, other):
        return self + other
    def __rsub__(self, other):
        return -self + other
    def __rmul__(self, other):
        return self * other

    def __neg__(self):
        return RelSamps(-self.samples_value)


class RelSamps(RelTime):

    def __init__(self, samples_value):
        super().__init__(samples_value, "sample")


    def __repr__(self):
        return "{0}samp".format(self.samples_value)


    def samps(self):
        return self


class RelSecs(RelTime):

    def __init__(self, secs_val):
        samples_value = int(secs_val * Relativism.rate())
        super().__init__(
            samples_value=samples_value,
            type_="second"
        )
        self.secs_val = self.samples_value / Relativism.rate()


    def __repr__(self):
        return "{0}sec".format(decimal_format(self.secs_val))


    def secs(self, rate):
        return self


class RelBeats(RelTime):

    def __init__(self, beat_num="", beat_type="b"):
        samples_value = Conversion.beats_to_samps(beat_num, beat_type)
        super().__init__(
            samples_value=samples_value,
            type_="beat"
        )
        self.beat_num = beat_num
        self.beat_type = beat_type


    def __repr__(self):
        return "{0}{1}".format(decimal_format(self.beat_num), self.beat_type)


    def beats(self):
        return self


    def whole_beats(self):
        """
        get num of beats (quarter-notes) from seconds.
        return (beats, remainder in sec)
        """
        bps = Relativism.bpm() / 60
        beat_num = int(self.secs() * bps)
        remainder = self.secs() % bps
        return (RelBeats(beat_num), RelSecs(remainder))






class RelPitch(RelativismData):


    def __init__(self, frequency, type_):
        self.frequency = frequency
        self.type = type_


    def __eq__(self, other):
        try:
            return self.frequency == other.frequency
        except:
            return False


    def octave(self, num):
        return self * (2 ** num)


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
        # note is number already, in any form
        try:
            note = abs(float(note))
            if note == 0:
                raise TypeError
            return note
        except ValueError:
            pass
        note = note.lower().strip()
        # if note is not formed properly
        if re.match(r"^[a-g][b#]{0,1}([0-9]|10)$", note) is None:
            err_mess("Note '{0}' is not properly formed or out of octave range 0-10 (inclusive)".format(note))
            raise TypeError
        # note is regular
        return RelPitch._get_freq(note)

    @staticmethod
    def _get_freq(note):
        """
        get formatted freq from table
        """
        freq_arr = RelPitch._get_freq_table()
        # if note is wrong sharp/flat (ie E#)
        note = re.sub("e#", "f", note)
        note = re.sub("fb", "e", note)
        note = re.sub("b#", "c", note)
        note = re.sub("cb", "b", note)
        return freq_arr[note]

    @staticmethod
    def _get_freq_table():
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
        for i in RelPitch._get_freq_table():
            info_line(str(i[0]).capitalize() + ": \t" + str(i[1]))


    def __add__(self, other):
        new_freq = 2**(other/12) * self.frequency
        return RelFreq(new_freq)
    def __sub__(self, other):
        new_freq = 2**(-other/12) * self.frequency
        return RelFreq(new_freq)
    def __mul__(self, other):
        return RelFreq(self.frequency * other)
    def __truediv__(self, other):
        return RelFreq(self.frequency / other)

    def __radd__(self, other):
        return self + other
    def __rmul__(self, other):
        return self * other



class RelFreq(RelPitch):

    def __init__(self, frequency):
        self.frequency = frequency
    

    def __repr__(self):
        return "{0}hz".format(decimal_format(self.frequency))


    def _freq_to_note(self):
        freq_to_note = {v:k for k,v in RelPitch._get_freq_table().items()}
        closest_note = freq_to_note[self.frequency] if self.frequency \
            in freq_to_note else freq_to_note[min(freq_to_note.keys(), key=lambda k: abs(k-self.frequency))]
        closest_note_freq = RelPitch._get_freq_table()[closest_note]
        cents = 1200 * math.log(self.frequency/closest_note_freq, 2)
        return (closest_note, cents)


    def freq(self):
        return self
    

    def note(self):
        note, cents = self._freq_to_note()
        return RelNote(note, cents)


    def whole_note(self):
        return RelNote(self._freq_to_note()[0])



class RelNote(RelPitch):

    def __init__(self, note, cents=0):
        self.note_value = note
        self.cents_value = cents
        self.frequency = self._note_to_freq()


    def __repr__(self):
        if self.cents_value == 0:
            return "{0}".format(self.note_value.capitalize())
        elif self.cents_value > 0:
            return "{0}+{1}cents".format(self.note_value.capitalize(), decimal_format(self.cents_value))
        else:
            return "{0}{1}cents".format(self.note_value.capitalize(), decimal_format(self.cents_value))


    def _note_to_freq(self):
        freq = RelPitch._get_freq(self.note_value.lower().strip())
        cents_freq = 2**(self.cents_value/1200) * freq
        return cents_freq


    def note(self):
        return self

    def whole_note(self):
        return RelNote(self.note)

    def freq(self):
        return RelFreq(self.frequency)




class Conversion:


    # freq


    # beat/freq help

    @staticmethod
    def note_options():
        print("Notes can be entered either as their direct frequency ('440', '228.3', etc), " +\
            "or as their musical notation note name and octave ('C4', 'Ab6', 'F#3', etc")

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






def data_main():
    pass



if __name__ == "__main__":
    data_main()