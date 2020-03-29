"""
top level
"""

# Initialization

import os, time, sys

from src.utility import suppress_output

RELATIVISM_DIR = os.path.dirname(os.path.abspath(__file__))
ERROR_LOG = RELATIVISM_DIR + "/data/errors.log"
ACTIVITY_LOG = RELATIVISM_DIR + "/data/activity.log"

with suppress_output(ERROR_LOG):

    from src.relativism import *
    from src.debug import *
    from src.output_and_prompting import *
    from src.settings import Settings

    #TODO load extensions dynamically
    from ext.autodrummer.autodrummer import *

Settings.set_activity_log(ACTIVITY_LOG)
Settings.set_error_log(ERROR_LOG)

with style("cyan, bold"):
    print("\n***** RELATIVISM *****\n")


# check multiple open sessions
try:
    with open(ACTIVITY_LOG, "r") as log:
        last = log.readlines()[-1]
        kind, secs = last.strip().split("\t")
        secs = float(secs)
        if kind == "sess-start":
            err_mess("Warning! There may be multiple instances of the program running, " +
                "or it was exited improperly last session\n" +
                "  Last unended session start: {0:.4f} seconds ago, {1}".format(
                    time.time() - secs, time.strftime("%H:%M:%S %m-%d-%Y", time.localtime(secs))))
            err_mess("Ensure multiple instances are not running, and be careful " +
                "to exit properly so as to not lose any data")

except FileNotFoundError:
    pass

with open(ACTIVITY_LOG, "a") as log:
    log.write("sess-start\t{0}\n".format(time.time()))


# Main loop
while True:
    try:
        reldata_dir = join_path(RELATIVISM_DIR, "data", is_dir=True)
        rel = Relativism(reldata_dir)
        process(rel)
    except Exception as e:
        if isinstance(e, Cancel):
            p("Exit?", o="y/n", q=False)
            if inpt("y-n", quit_on_q=False):
                info_block("Exiting...")
                break
        else:
            err_mess("EXCEPTION AT TOP LEVEL")
            show_error(e, force=True)

nl()

# Cleanup
with open(ACTIVITY_LOG, "a") as log:
    log.write("sess-end\t{0}\n".format(time.time()))
