"""
highest-level parent. One instance of Relativism() per program
"""

import os
import re
import json

from src.errors import *
from src.globals import RelGlobals, Settings
from src.input_processing import (autofill, inpt, inpt_validate, input_dir,
                                  input_file)
from src.rel_objects import RelSavedObj, RelPublicObj, RelContainer
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

            self.process_project()

    def help_menu(self):
        #TODO
        raise NotImplementedError

    def validate_child_name(self, child, new_name):
        if new_name in self.projects:
            err_mess("Project named '{0}' already exists!".format(new_name))
            return False
        if new_name == "see":
            err_mess("'see' is a protected keyword. Choose another name")
            return False

        # if no path, we have to wait until after path is selected to check.
        # this is verified in create_proj()
        if child.path is not None:
            newpath = join_path(child.path, child.get_data_filename(new_name), is_dir=True)
            if os.path.exists(newpath):
                err_mess("Something already exists at path '{0}'".format(newpath))
                return False
        
            # update projects file
            try:
                del self.projects[child.name]
            except KeyError: pass
            self.projects[new_name] = child.get_data_dir()
            self.write_proj_file()
        
        return True

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
            try:
                proj_name = name_input[1]
            except IndexError:
                err_mess("No name provided to 'see'")
                self.open_proj()
                return
            see = True
        else:
            proj_name = name_input[0]

        try:
            proj_path = self.projects[proj_name]
        except KeyError:
            try:
                proj_name = autofill(proj_name, self.projects.keys(), "name")
            except AutofillError as e:
                err_mess("No project matches name '{0}'".format(e.word))
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

        self.projects[self.current_open_proj.name] = self.current_open_proj.get_data_dir()
        self.write_proj_file()
        
    def see_proj(self, proj_name, proj_path):
        info_block("Previewing Project '{0}'".format(proj_name))
        fullpath = join_path(proj_path, proj_name + ".Project." + RelSavedObj.datafile_extension)
        with open(fullpath, "r") as f:
            data = json.load(f)
        info_title("Path: " + data["path"])
        info_line("Audio file: " + str(data["file"]))
        info_line("Children:")
        children = [re.sub(r"<.*>", "", i).split(".") for i in data["children"]]
        children = ["{0} '{1}'".format(i[1], i[0]) for i in children]
        info_list(children)


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
        if inpt("yn"):
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
            if inpt("yn"):
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
