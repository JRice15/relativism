"""
top level
"""

import os, time, sys

from src.utility import suppress_output

RELATIVISM_DIR = os.path.dirname(os.path.abspath(__file__))
ERROR_LOG = RELATIVISM_DIR + "/data/errors.log"
ACTIVITY_LOG = RELATIVISM_DIR + "/data/activity.log"

with suppress_output(ERROR_LOG):

    from src.project import *
    from src.relativism import *
    from src.debug import *

    #TODO load extensions dynamically
    from ext.autodrummer.autodrummer import *

with style("cyan, bold"):
    print("\n***** RELATIVISM *****\n")


try:
    with open(ACTIVITY_LOG, "r") as log:
        last = log.readlines()[-1]
        kind, secs = last.strip().split("\t")
        secs = float(secs)
        if kind == "sess-start":
            err_mess("Warning! May be multiple instances of the program running, " +
                "or it was exited improperly last session\n" +
                "  Last unended session start: {0:.4f} seconds ago, {1}".format(
                    time.time() - secs, time.strftime("%H:%M:%S %m-%d-%Y", time.localtime(secs))))
            err_mess("Ensure multiple instances are not running, and be careful " +
                "to exit properly so as to not lose any data")

except FileNotFoundError:
    pass

with open(ACTIVITY_LOG, "a") as log:
    log.write("sess-start\t{0}\n".format(time.time()))


while True:
    try:
        relfile_dir = join_path(RELATIVISM_DIR, "data", is_dir=True)
        relfile_path = join_path(relfile_dir, "relativism.relativism-data")
        rel = Relativism(relfile_dir, relfile_path)
        process(rel)
    except Exception as e:
        err_mess("EXCEPTION AT TOP LEVEL")
        show_error(e, force=True)



with open(ACTIVITY_LOG, "a") as log:
    log.write("sess-end\t{0}\n".format(time.time()))
