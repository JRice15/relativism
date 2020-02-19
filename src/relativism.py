"""
highest-level parent. One instance of Relativism() per program
"""

import re

from src.input_processing import inpt, inpt_validate, input_dir, input_file
from src.output_and_prompting import (p, info_title, info_list, info_line, 
    section_head, info_block, nl, err_mess, critical_err_mess, show_error)
from src.project_loader import ProjectLoader
from src.object_data import (public_process, is_public_process, 
    RelativismObject, RelativismPublicObject)
from src.process import process
from src.path import Path, makepath


class Relativism(RelativismPublicObject):


    def __init__(self, rel_dir, relfile_path):
        section_head("* Initializing program")
        super().__init__(-1, "Program", "Relativism", rel_dir, None)
        self._instance = self

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
        self.choose_open_type()

    def choose_open_type(self):
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

        try:
            loader = ProjectLoader(
                Path(name="{0}.Project".format(proj_name)), proj_path, self
            )
            self.current_open_proj = loader.get_proj()
        except FileNotFoundError as e:
            err_mess("File Not Found: '{0}'".format(e.filename))
            p("Locate '{0}'?".format(proj_name), o="y/n")
            if inpt("y-n"):
                self.locate_proj(proj_name)
            self.choose_open_type()
            return

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

    def locate_proj(self, proj_name):
        p("Select the project's folder/directory (should be named '{0}.Project'".format(
            proj_name), start="\n")
        try:
            directory = input_dir()
        except Cancel:
            p("Remove this Project from known projects?", o="y/n")
            if inpt("y-n"):
                del self.projects[proj_name]

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


