"""
top level
"""

import sys

from src.recording_obj import *
from src.project import *
from src.relativism import *


if ("-t" in sys.argv) or ("--test" in sys.argv):
    from testcases.testcases import *
    unittest.main()





from ext.autodrummer.autodrummer import *



