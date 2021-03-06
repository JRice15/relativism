"""

set FULLREC to true to test all Recording public processes


"""


import unittest
from unittest.mock import patch

import os, sys, re

global relativism_dir
relativism_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(relativism_dir)

import matplotlib
matplotlib.use("TkAgg")


from src.data_types import *
from src.input_processing import *
from src.relativism import *
from src.project import *
from src.path import *
from src.utility import *



global FULLREC
FULLREC = True



@contextmanager
def test_input_call(correct_input):
    try:
        with suppress_output():
            with patch("builtins.input", return_value=correct_input):
                yield
    finally:
        pass


class TestCases(unittest.TestCase):

    assert Project.get_rate() == Units.rate(44100)

    def test_data_types(self):

        # creation and conversion
        samps = Units.samps(44100)
        self.assertEqual(samps.to_secs(), Units.secs("1s"))
        self.assertEqual(samps.to_beats(), Units.beats("2b"))
        self.assertEqual(samps.to_secs().to_beats().to_samps(), samps)

        self.assertEqual(Units.beats("6b"), Units.beats("12hb"))
        self.assertNotEqual(Units.beats("4b"), Units.new("8.0000001hb"))

        mult = Units.rate(44100/2) * Units.secs("0.2s")
        made = Units.secs("0.1s").to_samps()
        self.assertEqual(made, mult)

        a = Units.rate(44100)
        b = Units.rate(a)
        self.assertEqual(a, b)

        # beat and time addition and conversion
        beats = Units.beats("4b")
        beats += Units.secs("1.3s").to_beats()
        self.assertEqual(beats, Units.new("13.2b") / 2)

        self.assertEqual(Units.beats("12.2 qb").beat_repr(), "12.2qb")

        # freq and note conversion and comparison
        a3note = Units.note("a3")
        a4 = a3note.shift_octaves(1)
        cS5 = a4.shift_semitones(4).to_freq().shift_semitones(-48).to_whole_note().shift_octaves(4).to_freq()
        self.assertEqual(cS5, Units.note("C#5"))

        self.assertEqual(Units.freq(44100 / 4).get_period(), Units.samps(4))

        # Quantity.trunc
        samps *= 3.22134567
        self.assertEqual(samps.trunc().magnitude % 1, 0)
        self.assertEqual(samps.to_secs().trunc().magnitude, 3)

        # percent
        a = Units.pcnt("20")
        b = a * Units.secs("4s")
        self.assertEqual(b, Units.secs("0.8s"))

        # ind() func
        a = Units.rate("200") * Units.new(2, "second") * Units.new("10 percent")
        self.assertEqual(ind(a), 40)


    def test_input_processing(self):
        self.assertEqual(inpt_validate("42hb", "beat"), Units.new(42, "hb"))

        self.assertEqual(inpt_validate("42", "pcnt"), Units.new("42pcnt"))

        with test_input_call(correct_input="4.29"):
            self.assertEqual(inpt_validate("4.333333b", "float"), 4.29)

        with test_input_call(correct_input="L"):
            self.assertEqual(inpt_validate("G", "letter", allowed="MLK"), "l")

        self.assertEqual(inpt_validate("42.8b", "beatsec"), Units.beats("42.8b"))
        self.assertEqual(inpt_validate("42.8", "beatsec"), Units.secs("42.8s"))


    def test_recording(self):

        if FULLREC:
            with suppress_output():
                obj = Recording(mode="file", 
                    file="/Users/user1/Desktop/CS/music/relativism/testcases/soundvision.wav", 
                    name="soundvision-test-out")
                self.assertEqual(obj.rate, Units.rate("44100"))
                methods = [i[1] for i in obj.method_data_by_category['Edits'].items()]

                for m in methods:
                    args = m.get_random_defaults()
                    m.method_func(*args)


if __name__ == "__main__":
    unittest.main()