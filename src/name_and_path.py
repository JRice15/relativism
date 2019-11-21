import os
import sys
import re
import tkinter as tk
from tkinter import filedialog
import time

from src.errors import *
from src.input_processing import *
from src.output_and_prompting import *


""" Opening projects & samplers """


class ObjectFactory():
    """
    open_type: class to create: "project", "sampler", "recording";
    open_mode: "o" (open) or "c" (create)
    """

    def __init__(self, open_type=None, open_mode=None):
        # command line init for projects
        if open_type == "project":
            for i in sys.argv[1:]:
                if re.fullmatch(r"^proj=.+", i) or re.fullmatch(r"^p=.+", i):
                    proj_name = re.sub(r".+=", "", i)
                else:
                    err_mess("Unrecognized command line flag: '" + i +"'. Ignoring...")
        
        # type and mode for open
        if open_type is None:
            self.open_type = self.choose_open_type()
        else:
            self.open_type = open_type
        if open_mode is None:
            self.choose_open_mode()
        else:
            self.open_mode = open_mode




    def choose_open_type(self):
        info_block("What object would you like to create? Enter the letter corresponding with your choice:")
        info_list(["(P) Project", "(S) Sampler", ""])
        self.open_mode = inpt("letter", allowed="oc")

    def choose_open_mode(self):
        p("Create new {0} (C), or Open existing (O)?")
        self.open_mode = inpt("letter", allowed="oc")



    def read_metadata(self, filename_or_fullpath, directory="."):
        """
        no dir arg means filename is full path. do not include extension
        """
        fullpath = parse_path(filename_or_fullpath, directory)
        with open(fullpath, 'r') as f:
            data = json.load(f)
        return data


def namepath_init(open_type):
    """
    open a project or sampler
    """

    if proj_name is None:
        open_mode = select_init_mode(open_type)
    else:
        open_mode = "o"

    while True:
        if open_mode == "c":
            try:
                proj_name, proj_path = select_create_name_path(open_type)
                verify_create_name(open_type, proj_name)
                os.mkdir(proj_path + "/" + proj_name)
                path_f = open(".paths.tsv", "a")
                path_f.write(open_type + "\t" + proj_name + "\t" + proj_path + "\n")
                path_f.close()
                break
            except NameExistsError:
                open_mode = select_init_mode(open_type)
            except NoPathError:
                open_mode = select_init_mode(open_type)
            # except ValueError as e:
            #     print("  > there may be an issue with file '.paths.tsv': {0}".format(e))
            #     sys.exit()
        elif open_mode == "o":
            proj_name = select_open_name(open_type)
            try:
                proj_path = get_open_path(open_mode, open_type, proj_name, proj_path)
                break
            except NameDoesntExistError:
                open_mode = select_init_mode(open_type)

    return proj_name, proj_path, open_mode

def select_init_mode(open_type):
    """
    select Open or Create new
    """
    open_mode = None
    while open_mode not in ("o", "c"):
        print("  Open existing {0} (O), Create new (C), or Quit (Q)?: ".format(open_type), end="")
        open_mode = inpt()
        if open_mode == "q":
            print("\n  exiting...\n")
            sys.exit()
        if open_mode not in ("o", "c"):
            print("  > enter a 'O' (as in Orca) or 'C' (as in Crab) to select mode")
    return open_mode

def select_open_name(open_type):
    """
    choose name for open
    open_type: 'project' or 'sampler' so far
    """
    try:
        path_f = open(".paths.tsv", "r")
        paths = path_f.readlines()
        for i in range(len(paths)):
            paths[i] = re.sub(r"    ", "\t", paths[i])
        paths = [i.strip().split("\t") for i in paths]
        paths = [i for i in paths if len(i) > 1]
        info_block("Defined {0} names:".format(open_type))
        for i in paths:
            if i[0] == open_type:
                print("      '" + i[1] + "' \t" + i[2])
    except FileNotFoundError:
        pass
    p("Select name of project to open")
    proj_name = inpt('file')
    return proj_name

def get_open_path(open_mode, open_type, proj_name, proj_path):
    """
    find path from name in paths.tsv
    """
    try:
        path_f = open(".paths.tsv", "r")
        paths = path_f.readlines()
        for i in range(len(paths)):
            paths[i] = re.sub(r"    ", "\t", paths[i])
        paths = [i.strip().split("\t") for i in paths]
        paths = [i for i in paths if len(i) > 1]
        path_f.close()
        for type_, name, path in paths:
            if name == proj_name and type_ == open_type:
                return path
        print("  > Name '{0}' not found".format(proj_name))
        raise NameDoesntExistError
    except FileNotFoundError:
        print("  > Name '{0}' not found".format(proj_name))
        raise NameDoesntExistError

def select_create_name_path(open_type):
    """
    prompt user for name and path
    """
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

def verify_create_name(open_type, proj_name):
    """
    verify name of newly created project
    """
    try:
        path_f = open(".paths.tsv", "r")
        paths = path_f.readlines()
        for i in range(len(paths)):
            paths[i] = re.sub(r"    ", "\t", paths[i])
        paths = [i.strip().split("\t") for i in paths]
        paths = [i for i in paths if len(i) > 1]
        path_f.close()
        for type_, name, path in paths:
            if open_type == type_ and name == proj_name:
                print("  > Name '{0}' already exists!".format(proj_name))
                raise NameExistsError
        return True
    except FileNotFoundError:
        path_f = open(".paths.tsv", "w")
        path_f.close()



