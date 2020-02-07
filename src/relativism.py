"""
highest-level parent. One instance of Relativism() per program
"""

import re

from src.input_processing import *
from src.output_and_prompting import *
from src.object_loading import *
from src.object_data import *

class Relativism(RelativismPublicObject):

    _debug = True
    _autosave = False
    _bpm = 120
    _rate = 44100
    _next_id = 0
    _process_num = 1

    def __init__(self, rel_dir, relfile_path):
        section_head("* Initializing program")
        super().__init__(-1, "Program", "Relativism", rel_dir, None)
        # set default output
        self.output = 'Built-in Output'
        self.reltype = "Program"
        self.relfile_path = relfile_path

        # read project names
        try:
            data_file = open(self.relfile_path, "r")
            paths = data_file.readlines()
            data_file.close()
            paths = [re.sub(r"    ", "\t", i) for i in paths]
            paths = [i.strip().split("\t") for i in paths]
            paths = {i[0]:Path(i[1]) for i in paths if len(i) > 1}
        except FileNotFoundError:
            makepath(self.relfile_path.get_dir())
            path_f = open(self.relfile_path, "w")
            path_f.close()
            paths = {}
        # maps name to Path, which is path to that proj's datafile
        self.projects = paths
        self.current_open_proj = None
        
        # if projects is empty, create, otherwise prompt for create or open existing
        if bool(self.projects):
            p("Open existing project (O) or Create new (C)?")
            open_or_create = inpt("letter", allowed="oc")

            if open_or_create == 'c':
                self.create_proj()
            else:
                self.open_proj()
        else:
            self.create_proj()


    def validate_child_name(self, name):
        if name in self.projects:
            err_mess("Project named '{0}' already exists!")
            return False
        return True

    @public_process
    def open_proj(self):
        section_head("Opening Project")

        self.list_projects()
        p("Enter name of project you want to open")
        proj_name = inpt("obj")

        try:
            proj_path = self.projects[proj_name]
        except KeyError:
            proj_name = autofill(proj_name, self.projects.keys(), "name")
            proj_path = self.projects[proj_name]

        self.current_open_proj = ProjectLoader(
            Path(name="{0}.Project".format(proj_name)), proj_path
        )

        p("Process this project?", o="[y/n]")
        if inpt("y-n"):
            self.process_project()

    @public_process
    def create_proj(self):
        section_head("Creating New Project")
        self.current_open_proj = Project(parent=self)
        self.projects[self.current_open_proj.name] = self.current_open_proj.path.fullpath()

        with open(self.relfile_path, "a") as relfile:
            relfile.write("{0}\t{1}\n".format(self.current_open_proj.name, self.current_open_proj.path))

        p("Process this project?", o="y/n")
        if inpt("y-n"):
            self.process_project()

    @public_process
    def list_projects(self):
        info_title("Existing projects:")
        info_list(list(self.projects.keys()))

    @public_process
    def process_project(self):
        try:
            process(self.current_open_proj)
        except Cancel:
            pass

    @staticmethod
    def get_next_id():
        if Relativism._next_id is None:
            #TODO: open rel file
            pass
        temp = Relativism._next_id
        Relativism._next_id += 1
        return temp
        

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
    def get_process_num():
        Relativism._process_num += 1
        return Relativism._process_num - 1



def autofill(partial, possibles, inpt_mode="name"):
    """
    matches partial word to one or more of the possible options
    """
    matches = []
    for pos in possibles:
        if pos[:len(partial)] == partial:
            matches.append(pos)
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


