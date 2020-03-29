"""
highest-level parent. One instance of Relativism() per program
"""

import re
import os

from src.input_processing import inpt, inpt_validate, input_dir, input_file
from src.output_and_prompting import (p, info_title, info_list, info_line, 
    section_head, info_block, nl, err_mess, critical_err_mess, show_error)
from src.project_loader import ProjectLoader
from src.object_data import (public_process, is_public_process, 
    RelativismObject, RelativismPublicObject)
from src.process import process
from src.path import join_path, split_path
from src.errors import *
from src.project import Project


class Relativism(RelativismPublicObject):


    def __init__(self, reldata_dir):
        section_head("Initializing program")
        super().__init__(-1, "Program", "Relativism", reldata_dir, None)
        self._instance = self

        self.relfile_path = join_path(reldata_dir, "projects.data")

        # set default output
        self.output = "Built-in Output"
        self.reltype = "Program"

        # maps name : path to that proj's datafile
        self.projects = self.read_proj_file()
        self.current_open_proj = None
        self.run()

    def run(self):
        section_head("Relativism Main Menu")
        while True:
            while self.current_open_proj is None:
                self.choose_open_type()

            p("Process this project?", o="[y/n]")
            if inpt("y-n"):
                self.process_project()
            else:
                self.current_open_proj.save()
                self.current_open_proj = None

    def choose_open_type(self):
        """
        if projects is empty, create, otherwise prompt for create or open existing
        """
        if bool(self.projects):
            p("Open existing project (O) or Create new (C)?")
            open_or_create = inpt("letter", allowed="oc")

            try:
                if open_or_create == 'c':
                    self.create_proj()
                else:
                    self.open_proj()
            except Cancel:
                return
        else:
            info_block("No existing projects. Defaulting to create new")
            self.create_proj()

    def validate_child_name(self, name):
        if name in self.projects:
            err_mess("Project named '{0}' already exists!".format(name))
            return False
        return True

    @public_process
    def open_proj(self):
        """
        desc: open a project
        """
        section_head("Opening Project")

        self.list_projects()
        p("Enter name of project you want to open")
        proj_name = inpt("obj")

        try:
            proj_path = self.projects[proj_name]
        except KeyError:
            try:
                proj_name = autofill(proj_name, self.projects.keys(), "name")
            except AutofillError:
                err_mess("No project matches name '{0}'".format(proj_name))
                return
            proj_path = self.projects[proj_name]

        if proj_path == "None":
            err_mess("Project {0} is missing".format(proj_name))
            self.handle_missing_proj(proj_name)
            return

        try:
            loader = ProjectLoader("{0}.Project".format(proj_name), proj_path, self)
            self.current_open_proj = loader.get_proj()
        except FileNotFoundError as e:
            err_mess("File Not Found: '{0}'".format(e.filename))
            self.handle_missing_proj(proj_name)
            return

    @public_process
    def create_proj(self):
        """
        desc: create a new project
        """
        section_head("Creating New Project")
        while True:
            try:
                self.current_open_proj = Project(parent=self, mode="create")
                break
            except FileExistsError:
                err_mess("The directory already exists and cannot be overwritten. Choose another name or location")

        self.current_open_proj.save()

        self.projects[self.current_open_proj.name] = self.current_open_proj.path
        with open(self.relfile_path, "a") as relfile:
            relfile.write("{0}\t{1}\n".format(self.current_open_proj.name, self.current_open_proj.path))
        
    @public_process
    def list_projects(self):
        info_title("Existing projects:")
        for k,v in self.projects.items():
            if v == "None":
                info_list(k + " (Not found)")
            else:
                info_list(k)

    @public_process
    def process_project(self):
        try:
            process(self.current_open_proj)
        except Cancel:
            self.current_open_proj.save()
            self.current_open_proj = None

    def read_proj_file(self):
        # read project names
        try:
            data_file = open(self.relfile_path, "r")
            paths = data_file.readlines()
            data_file.close()
            paths = [re.sub(r"    ", "\t", i) for i in paths]
            paths = [i.strip().split("\t") for i in paths]
            paths = {i[0]:i[1] for i in paths if len(i) > 1}
        except FileNotFoundError:
            dirc,_,_ = split_path(self.relfile_path)
            os.makedirs(dirc, exist_ok=True)
            path_f = open(self.relfile_path, "w")
            path_f.close()
            paths = {}
        return paths

    def write_proj_file(self, proj_name):
        """
        set self.proj path entry to "None"
        """
        paths = [str(k) + "\t" + str(v) + "\n" for k,v in self.projects.items()]
        with open(self.relfile_path, "w") as f:
            f.writelines(paths)

    def handle_missing_proj(self, proj_name):
        """
        locate or remove proj, rewrite file
        """
        self.projects[proj_name] = "None"

        p("Locate '{0}'?".format(proj_name), o="y/n")

        located = False
        if inpt("y-n"):
            p("Select the project's folder/directory (should be named '{0}.Project'".format(
                proj_name), start="\n")
            try:
                directory = input_dir()
                self.projects[proj_name] = directory
                located = True
            except Cancel:
                pass

        if not located:
            p("Failed to locate. Remove this Project from known projects?", o="y/n")
            if inpt("y-n"):
                del self.projects[proj_name]

        self.write_proj_file(proj_name)



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


