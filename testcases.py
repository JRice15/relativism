import unittest

from data_types import *
from input_processing import *
from relativism import *
from project import *



class TestCases(unittest.TestCase):

    def test_data_types(self):
        assert Project.get_rate() == Units.rate(44100)

        # creation and conversion
        samps = Units.samps(44100)
        self.assertEqual(samps.secs(), Units.secs(1))
        self.assertEqual(samps.beats(), Units.beats(2.0))
        self.assertEqual(samps.secs().beats().samps(), samps)

        # Quantity.trunc
        samps *= 3.22134567
        self.assertEqual(samps.trunc().magnitude % 1, 0)
        self.assertEqual(samps.secs().trunc().magnitude, 3)



    def test_input_processing(self):

        self.assertEqual(inpt_validate("42hb", "beat"), Units.new(42, "hb"))



if __name__ == "__main__":
    unittest.main()