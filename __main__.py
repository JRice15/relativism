"""
top level
"""

### Initialize


import os, time, sys
SESS_START = time.time()

from src.utility import suppress_output
from src.path import join_path

# paths

RELATIVISM_DIR = os.path.dirname(os.path.abspath(__file__))
RELDATA_DIR = join_path(RELATIVISM_DIR, "data/", is_dir=True)
os.makedirs(RELDATA_DIR, exist_ok=True)
ERROR_LOG = join_path(RELDATA_DIR, "errors.log")
DATA_FILE = join_path(RELDATA_DIR, "data.json")
SETTINGS_FILE = join_path(RELDATA_DIR, "settings.json")
PROJFILE_NAME = "projects.relativism-data"

# parameters

MAX_SESS_LOGS = 20


with open(ERROR_LOG, "a") as log:
    log.write("\nsess-start\t{0}\n".format(SESS_START))

with suppress_output(ERROR_LOG):

    from src.relativism import *
    from src.debug import *
    from src.output_and_prompting import *
    from src.globals import RelGlobals, Settings, init_globals, save_globals

    #TODO load extensions dynamically
    try:
        from ext.autodrummer.autodrummer import *
    except:
        pass

with style("cyan, bold"):
    print("\n***** RELATIVISM *****\n")

RelGlobals.set_error_log(ERROR_LOG)
RelGlobals.set_data_file(DATA_FILE)
RelGlobals.set_settings_file(SETTINGS_FILE)

# read globals and settings
init_globals()


with open(ERROR_LOG, "r") as log:

    # check multiple open sessions
    info_block("Checking activity...")
    lines = log.readlines()
    last = [i for i in lines if i.startswith("sess-start") or i.startswith("sess-end")][-1]
    kind, secs = last.strip().split("\t")
    secs = float(secs)
    if kind == "sess-start":
        err_mess("Warning! There may be multiple instances of the program running, " +
            "or it was exited improperly last session. Last unended session start: " +
            "{0:.4f} seconds ago, {1}".format(
                time.time() - secs, time.strftime("%H:%M:%S %m-%d-%Y", time.localtime(secs))))
        err_mess("Ensure multiple instances are not running, and be careful " +
            "to exit properly so as to not lose any data", extra_leading_nl=False)
    
    # keep 20 most recent sessions logs
    start_count = 0
    for i in range(len(lines) - 1, 0, -1):
        if lines[i].startswith("sess-start"):
            start_count += 1
        if start_count > MAX_SESS_LOGS:
            break

# rewrite logs
if start_count > MAX_SESS_LOGS and i != 0:
    lines = lines[i:]
    with open(ERROR_LOG, "w") as log:
        log.write("{0} most recent session logs are kept\n\n".format(MAX_SESS_LOGS))
        log.writelines(lines)


### Main loop

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

with open(ERROR_LOG, "a") as log:
    log.write("sess-end\t{0}\n".format(time.time()))