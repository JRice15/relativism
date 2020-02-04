"""
highest-level parent. One instance of Relativism() per program
"""

import re

from src.input_processing import *
from src.output_and_prompting import *
from object_loading import *


class Relativism():
    global RELATIVISM_DIR

    TEST_OUT_DIR = "/Users/user1/Desktop/CS/music/out-test"

    _debug = True
    _autosave = False
    _bpm = 120
    _rate = 44100
    _next_id = 0

    _relativism_file_path = Path(dir=RELATIVISM_DIR, name="relativism", ext="relativism-data")

    def __init__(self):
        # set default output
        self.output = 'Built-in Output'

        # read project names
        try:
            data_file = open(self._relativism_file_path, "r")
            paths = data_file.readlines()
            data_file.close()
            paths = [re.sub(r"    ", "\t", i) for i in paths]
            paths = [i.strip().split("\t") for i in paths]
            paths = {i[0]:Path(i[1]) for i in paths if len(i) > 1}
        except FileNotFoundError:
            path_f = open(self._relativism_file_path, "w")
            path_f.close()
            paths = {}
        # maps name to Path, which is path to that proj's datafile
        self.projects = paths
        self.open_proj = None
        
        # init
        p("Open existing project (O) or Create new (C)?")
        open_or_create = inpt("letter", "oc")

        if open_or_create == 'c':
            # create
            self.open_proj = Project()
            self.projects[proj.name] = proj.path.fullpath()
        else:
            info_title("Existing projects:")
            info_list(self.projects.keys())
            nl()
            p("")
            try:
                proj_path = self.projects[proj_name]
            except KeyError:
                proj_name = autofill(proj_name, self.projects.keys(), "name")
                proj_path = self.projects[proj_name]
            self.open_proj = ProjectLoader(
                Path(name="{0}.Project.relativism-obj".format(proj_name)), 
                proj_path
            )


    def validate_child_name(name):


    @staticmethod
    def debug():
        return Relativism._debug

    def debug_on(self):
        info_block("Debug On. Errors may propogate to top level and halt execution with no save")
        self._debug = True
    
    def debug_off(self):
        info_block("Debug Off")
        self._debug = False

    @staticmethod
    def autosave():
        return Relativism.autosave

    #TODO: get/set autosave

    @staticmethod
    def get_next_id():
        if Relativism._next_id is None:
            #TODO: open rel file
            pass
        temp = Relativism._next_id
        Relativism._next_id += 1
        return temp
        
    @staticmethod
    def bpm():
        return Relativism._bpm

    def set_bpm(self, bpm):
        self._bpm = bpm

    @staticmethod
    def rate():
        return Relativism._rate

    def set_rate(self, rate):
        Relativism._rate = rate

    def set_output(self):
        pass



def autofill(partial, possibles, inpt_mode="name"):
    """
    matches partial word to one or more of the possible options
    """
    matches = []
    for pos in possibles:
        if pos[:len(partial)] == partial:
            matche.append(pos)
    if len(matches) == 0:
        raise AutofillError("No matches for '{0}'".format(partial))
    elif len(matches) == 1:
        return matches[0]
    else:
        info_title("Multiple matches:")
        info_list(matches)
        p("Complete the word", start=partial)
        rest = inpt(inpt_mode)
        return autofill(partial + rest, matches, inpt_mode=inpt_mode)
    




class BPM:

    def __init__(self, initial_BPM):
        self.bpm_markers = [0, initial_BPM] # 


