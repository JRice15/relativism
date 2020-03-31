"""
highest-level parent. One instance of Relativism() per program
"""

import os
import re

from src.errors import *
from src.globals import RelGlobals, Settings
from src.input_processing import (autofill, inpt, inpt_validate, input_dir,
                                  input_file)
from src.object_data import (RelativismObject, RelativismPublicObject,
                             is_public_process, public_process)
from src.output_and_prompting import (critical_err_mess, err_mess, info_block,
                                      info_line, info_list, info_title, nl, p,
                                      section_head, show_error)
from src.path import join_path, split_path
from src.process import process
from src.project import Project
from src.project_loader import ProjectLoader


class Relativism(RelativismPublicObject):


    def __init__(self, reldata_dir, proj_filename):
        section_head("Initializing program")
        super().__init__(rel_id=-1, reltype="Program", name="Relativism", path=reldata_dir, parent=None)

        RelGlobals.set_rel_instance(self)

        self.relfile_path = join_path(reldata_dir, proj_filename)

        # set default output
        self.output = "Built-in Output"
        self.reltype = "Program"

        # maps name : path to that proj's datafile
        self.projects = self.read_proj_file()
        self.current_open_proj = None


    def main_menu(self):
        section_head("Relativism Main Menu")
        p("Would you like to edit Projects (P), Settings (S), or get Help (H)?")
        choice = inpt("letter", allowed="psh")
        if choice == "p":
            self.do_projects()
        elif choice == "s":
            self.do_settings()
        else:
            self.do_help()
    

    def do_settings(self):
        try:
            Settings.process()
        except Cancel:
            pass

    def do_projects(self):
        """
        top menu for opening or creating projects
        """
        while True:
            while self.current_open_proj is None:
                self.choose_open_type()

            p("Process project '{0}'? [y/n]".format(self.current_open_proj.name))
            if inpt("y-n"):
                self.process_project()
            else:
                self.current_open_proj.save()
                self.current_open_proj = None

    def do_help(self):
        raise NotImplementedError

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
        
    def list_projects(self):
        info_title("Existing projects:")
        for k,v in self.projects.items():
            if v == "None":
                info_list(k + " (Not found)")
            else:
                info_list(k)

    def process_project(self):
        if self.current_open_proj is None:
            err_mess("No project is currently open! Open or create one")
        else:
            try:
                process(self.current_open_proj)
            except Cancel:
                self.current_open_proj.save()
                self.current_open_proj = None

    def read_proj_file(self):
        """
        read projects.data file
        """
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

    def write_proj_file(self):
        """
        write projects.data file
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

        self.write_proj_file()

    def save(self):
        """
        cleanup actions for Relativism object
        """
        if self.current_open_proj is not None:
            self.current_open_proj.save()
        self.write_proj_file()



class BPM:

    def __init__(self, initial_BPM):
        self.bpm_markers = [0, initial_BPM] # 
