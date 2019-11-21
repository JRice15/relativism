"""
top level
"""

import os

RELATIVISM_DIR = os.path.dirname(os.path.abspath(__file__))
ERROR_LOG = RELATIVISM_DIR + "relativism_errors.log"


from src.utility import suppress_output

with suppress_output(ERROR_LOG):
    import sys
    from argparse import ArgumentParser

    from src.recording_obj import *
    from src.project import *
    from src.relativism import *








from ext.autodrummer.autodrummer import *




