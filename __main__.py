"""
top level
"""

import os, time, sys

from src.utility import suppress_output
from src.path import join_path

### Initialize

RELATIVISM_DIR = os.path.dirname(os.path.abspath(__file__))
RELDATA_DIR = join_path(RELATIVISM_DIR, "data/", is_dir=True)
os.makedirs(RELDATA_DIR, exist_ok=True)
ERROR_LOG = join_path(RELDATA_DIR, "errors.log")
ACTIVITY_LOG = join_path(RELDATA_DIR, "activity.log")
DATA_FILE = join_path(RELDATA_DIR, "data.json")
SETTINGS_FILE = join_path(RELDATA_DIR, "settings.json")

with suppress_output(ERROR_LOG):

    from src.relativism import *
    from src.debug import *
    from src.output_and_prompting import *
    from src.globals import RelGlobals, Settings, init_globals, save_globals

    #TODO load extensions dynamically
    from ext.autodrummer.autodrummer import *

with style("cyan, bold"):
    print("\n***** RELATIVISM *****\n")

RelGlobals.set_activity_log(ACTIVITY_LOG)
RelGlobals.set_error_log(ERROR_LOG)
RelGlobals.set_data_file(DATA_FILE)
RelGlobals.set_settings_file(SETTINGS_FILE)

# read globals and settings
init_globals()

# check multiple open sessions
try:
    info_block("Checking activity...")
    with open(ACTIVITY_LOG, "r") as log:
        last = log.readlines()[-1]
        kind, secs = last.strip().split("\t")
        secs = float(secs)
        if kind == "sess-start":
            err_mess("Warning! There may be multiple instances of the program running, " +
                "or it was exited improperly last session. Last unended session start: " +
                "{0:.4f} seconds ago, {1}".format(
                    time.time() - secs, time.strftime("%H:%M:%S %m-%d-%Y", time.localtime(secs))))
            err_mess("Ensure multiple instances are not running, and be careful " +
                "to exit properly so as to not lose any data", extra_leading_nl=False)

except FileNotFoundError:
    pass

with open(ACTIVITY_LOG, "a") as log:
    log.write("sess-start\t{0}\n".format(time.time()))


### Main loop

PROJFILE_NAME = "projects.relativism-data"
rel = Relativism(RELDATA_DIR, PROJFILE_NAME)

while True:
    try:
        rel.main_menu()
    except Exception as e:
        if isinstance(e, Cancel):
            p("Exit Relativism?", o="y/n", q=False)
            if inpt("y-n", quit_on_q=False):
                break
        else:
            err_mess("EXCEPTION AT TOP LEVEL")
            show_error(e, force=True)

### Cleanup

rel.save()

# writes settings and data files
save_globals()

info_block("Exiting...")
nl()

with open(ACTIVITY_LOG, "a") as log:
    log.write("sess-end\t{0}\n".format(time.time()))