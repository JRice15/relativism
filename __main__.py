"""
top level
"""

import os

global RELATIVISM_DIR, ERROR_LOG
RELATIVISM_DIR = os.path.dirname(os.path.abspath(__file__))
ERROR_LOG = RELATIVISM_DIR + "relativism_errors.log"


from src.utility import suppress_output

with suppress_output(ERROR_LOG):
    import sys
    from argparse import ArgumentParser

    from src.recording_obj import *
    from src.project import *
    from src.relativism import *
    from src.debug import *

from ext.autodrummer.autodrummer import *

rel = Relativism()

try:
    process(rel)
except Exception as e:
    show_error(e, force=True)
    raise UnexpectedIssue("Exception propogated to top level")



