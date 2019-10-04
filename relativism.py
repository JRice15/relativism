"""
root relativism
"""
import re
from recording_obj import *
from input_processing import *
from output_and_prompting import *


class Relativism():

    DEBUG = True
    TEST_BPM = 120

    RELATIVISM_PATH_FILE = ".relativism.tsv"

    def __init__(self):
        # set default output
        self.output = 'Built-in Output'

        # read project names
        try:
            data_file = open(self.RELATIVISM_PATH_FILE, "r")
            paths = data_file.readlines()
            data_file.close()
            paths = [re.sub(r"    ", "\t", i) for i in paths]
            paths = [i.strip().split("\t") for i in paths]
            paths = [i for i in paths if len(i) > 1]
        except FileNotFoundError:
            path_f = open(self.RELATIVISM_PATH_FILE, "w")
            path_f.close()
            paths = []
        self.names_and_paths = {}
        for i in paths:
            self.names_and_paths[i[0]] = i[1]
        
        # init
        p("Open existing project (O) or Create new (C)?")
        open_or_create = inpt("letter", "oc")

        if open_or_create == 'c':
            # create
            print("  Enter a unique name for your {0}: ".format(open_type), end="")
            proj_name = inpt("obj")
            verify_create_name(open_type, proj_name)
            print("  name: '{0}'".format(proj_name))
            print("  Choose a path where your {0} will be stored. Launching...".format(open_type))
            time.sleep(1)
            root = tk.Tk()
            root.withdraw()
            proj_path = filedialog.askdirectory(initialdir = os.getcwd(), title = "Directory to Store Your Project")
            if proj_path == "":
                raise NoPathError
            print("  '" + proj_name + "': " + proj_path)
            return proj_name, proj_path

    def debug_on(self):
        info_block("Debug On. Errors may propogate to top level and halt execution with no save")
        self.DEBUG = True
    
    def debug_off(self):
        info_block("Debug Off")
        self.DEBUG = False

    def set_output(self):
        pass