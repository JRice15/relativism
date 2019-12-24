"""
highest-level parent. One instance of Relativism() per program
"""

import re

from src.input_processing import *
from src.output_and_prompting import *


class Relativism():

    _debug = True
    _autosave = False

    _bpm = 120
    _rate = 44100

    _relativism_file_path = "relativism.relativism-data"

    _next_id = None

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
            paths = [i for i in paths if len(i) > 1]
        except FileNotFoundError:
            path_f = open(self._relativism_file_path, "w")
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
            proj_path = input_dir()
            print("  '" + proj_name + "': " + proj_path)
            return proj_name, proj_path


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




class BPM:

    def __init__(self, initial_BPM):
        self.bpm_markers = [0, initial_BPM] # 





