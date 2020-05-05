"""
highest-level parent. One instance of Relativism() per program
"""

import os
import re

from src.errors import *
from src.globals import RelGlobals, Settings
from src.input_processing import (autofill, inpt, inpt_validate, input_dir,
                                  input_file)
from src.rel_objects import RelativismSavedObj, RelativismPublicObj, RelativismContainer
from src.method_ops import public_process, is_public_process, rel_alias, is_alias
from src.output_and_prompting import (critical_err_mess, err_mess, info_block,
                                      info_line, info_list, info_title, nl, p,
                                      section_head, show_error)
from src.path import join_path, split_path
from src.process import process
from src.project import Project
from src.project_loader import ProjectLoader


class Relativism():


    def __init__(self, reldata_dir, proj_filename):
        section_head("Initializing Program")

        RelGlobals.set_rel_instance(self)

        self.relfile_path = join_path(reldata_dir, proj_filename)

        # set default output
        self.output = "Built-in Output"
        self.reltype = "Program"

        # maps name : path to that proj's datafile
        self.projects = self.read_proj_file()
        self.current_open_proj = None


    def main_menu(self):
        while True:
            section_head("Relativism Main Menu")
            p("Would you like to edit Projects (P), Settings (S), or get Help (H)?")
            choice = inpt("letter", allowed="psh")
            try:
                if choice == "p":
                    self.projects_menu()
                elif choice == "s":
                    self.settings_menu()
                else:
                    self.help_menu()
            except Cancel:
                pass
    
    def settings_menu(self):
        try:
            Settings.process()
        except Cancel:
            pass

    def projects_menu(self):
        """
        top menu for opening or creating projects
        """
        while True:
            section_head("Projects Menu")

            # choose open type: open or create
            while self.current_open_proj is None:
                if bool(self.projects):
                    p("Open existing project (O) or Create new (C)?")
                    open_or_create = inpt("letter", allowed="oc")

                    if open_or_create == 'c':
                        self.create_proj()
                    else:
                        self.open_proj()
                else:
                    info_block("No existing projects. Defaulting to create new")
                    self.create_proj()

            p("Process project '{0}'? [y/n]".format(self.current_open_proj.name))
            if inpt("y-n"):
                self.process_project()
            else:
                self.current_open_proj.save()
                self.current_open_proj = None

    def help_menu(self):
        #TODO
        raise NotImplementedError


    def validate_child_name(self, name):
        if name in self.projects:
            err_mess("Project named '{0}' already exists!".format(name))
        elif name == "see":
            err_mess("'see' is a protected keyword. Choose another name")
        else:
            return True
        return False

    def open_proj(self):
        """
        desc: open a project
        """
        section_head("Opening Project")

        self.list_projects()
        p("Enter name of project you want to open, or 'see <name>' to see info about that project")
        name_input = inpt("split", "obj")
        see = False
        if name_input[0] == "see":
            proj_name = name_input[1]
            see = True
        else:
            proj_name = name_input[0]

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

        if see:
            self.see_proj(proj_name, proj_path)
            self.open_proj()
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

        self.projects[self.current_open_proj.name] = self.current_open_proj.path
        with open(self.relfile_path, "a") as relfile:
            relfile.write("{0}\t{1}\n".format(self.current_open_proj.name, self.current_open_proj.path))
        
    def see_proj(self, proj_name, proj_path):
        info_block("Previewing Project '{0}'".format(proj_name))
        info_block("Children:")
        fullpath = join_path(proj_path, proj_name + ".Project." + RelativismPublicObj.datafile_extension)
        with open(fullpath, "r") as f:
            lines = f.readlines()
            in_children = False
            for i in lines:
                if '"children":' in i:
                    in_children = True
                elif "]," in i:
                    in_children = False
                elif in_children:
                    info = i.strip().strip('"')
                    info = re.sub("<RELOBJFILE>", "", info)
                    name, reltype = info.split(".")
                    info_list("{0} '{1}'".format(reltype, name))

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
            process(self.current_open_proj)
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
