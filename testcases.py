import unittest
from unittest.mock import patch

from data_types import *
from input_processing import *
from relativism import *
from project import *




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
        self.assertEqual(samps.to_secs(), Units.secs(1))
        self.assertEqual(samps.to_beats(), Units.beats("2b"))
        self.assertEqual(samps.to_secs().to_beats().to_samps(), samps)

        # Quantity.trunc
        samps *= 3.22134567
        self.assertEqual(samps.trunc().magnitude % 1, 0)
        self.assertEqual(samps.to_secs().trunc().magnitude, 3)

        # beat and time addition and conversion
        beats = Units.beats("4b")
        beats += Units.secs(1.3).to_beats()
        self.assertEqual(beats, Units.new("13.2b") / 2)

        # freq and note conversion and comparison
        a3note = Units.note("a3")
        a4 = a3note.shift_octaves(1)
        cS5 = a4.shift_semitones(4).to_freq().shift_semitones(-48).to_whole_note().shift_octaves(4).to_freq()
        self.assertEqual(cS5, Units.note("C#5"))

        self.assertEqual(Units.freq(44100 / 4).get_period(), Units.samps(4))


        # percent
        a = Units.pcnt("20")
        b = a * Units.secs(4)
        self.assertEqual(b, Units.secs(0.8))



    def test_input_processing(self):
        self.assertEqual(inpt_validate("42hb", "beat"), Units.new(42, "hb"))

        self.assertEqual(inpt_validate("42", "pcnt"), Units.new("42pcnt"))

        with test_input_call(correct_input="4.29"):
            self.assertEqual(inpt_validate("4.333333b", "float"), 4.29)

        with test_input_call(correct_input="L"):
            self.assertEqual(inpt_validate("G", "letter", allowed="MLK"), "l")




if __name__ == "__main__":
    unittest.main()