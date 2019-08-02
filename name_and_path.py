import os
from errors import *
import sys
import re
import tkinter as tk
from tkinter import filedialog
import time
from freq_and_time import *


""" Opening projects & samplers """

def namepath_init(open_type):
    """
    open a project or sampler
    """

    proj_name, proj_path = None, None

    if open_type == "project":
        for i in sys.argv[1:]:
            if re.fullmatch(r"^proj=.+", i) or re.fullmatch(r"^p=.+", i):
                proj_name = re.sub(r".+=", "", i)
            else:
                print("  > Unrecognized command line flag: '" + i +"'. Ignoring...")

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
        print("    defined {0} names:".format(open_type))
        for i in paths:
            if i[0] == open_type:
                print("      '" + i[1] + "' \t" + i[2])
    except FileNotFoundError:
        pass
    print("\n  Select name of project to open: ", end="")
    proj_name = inpt()
    proj_name = re.sub(r"\s+", "_", proj_name)
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



""" clean input """

def inpt(mode=None, split_modes=None, catch=None, catch_callback=None, allowed=None, required=True):
    """
    get and clean input via some specifications
        mode: str:
            obj, file, alphanum, name: whitespaces to underscore, alphanumeric
            y-n: yes or no question, returns bool
            beat: valid beat input
            note: valid note input
            int: integer, optional allowed list
            flt: float, optional allowed list
            pcnt: percentage, opt allowed list
            split: splits input, does split modes on each (inp longer than split modes uses last mode for rest)
            letter: one letter, str of allowed
        split_modes: str, or list of str
        catch: str to catch
        catch callback: function to call on catch
        allowed: str for letters, or two-list of inclusive low and high bound for num inputs
    """
    val = input().lower().strip()
    try: 
        allowed = allowed.lower()
    except:
        pass
    if val == catch:
        # for options call
        catch_callback()
        print("\n  enter intended value ('q' for quit): ", end="")
        return inpt(mode, split_modes=split_modes)
    if val == "q":
        raise Cancel
    if mode == "split":
        val = val.split()
        for i in range(len(val)):
            if split_modes is None:
                t_mode = None
            else:
                if isinstance(split_modes, str):
                    t_mode = split_modes
                else:
                    try:
                        t_mode = split_modes[i]
                    except IndexError:
                        t_mode = split_modes[-1]
            val[i] = inpt_process(val[i], t_mode)
    else:
        val = inpt_process(val, mode, allowed)
    if required and val == "":
        p("> A value is required. Enter intended value")
        val = inpt(mode, split_modes=split_modes, catch=catch, catch_callback=catch_callback, allowed=allowed, required=required)
    return val


def inpt_process(val, mode, allowed=None):
    """
    processes individual modes for inpt
    also used as input validation
    """
    if mode == None:
        return val
    elif mode in ("y-n", "y/n", "yn"):
        if len(val) == 0 or val[0] not in "yn":
            print("  > Enter 'y' or 'n': ", end="")
            return inpt("y-n")
        if val[0] == "y":
            val = True
        else:
            val = False
    elif mode in ("obj", "file", "alphanum", "name"):
        val = re.sub(r"\s+", "_", val)
        val = re.sub(r"-", "_", val)
        val = re.sub(r"[^_a-z0-9]", "", val)
        val = re.sub(r"_{2,}", "_", val)
    elif mode == "note":
        try:
            f(val)
        except TypeError:
            info_block(
                "> Value '{0}' is not a validly formed note. Enter intended value ('i' for info on how to make validly formed notes, 'q' to cancel): ".format(val),
                indent=2,
                for_prompt=True
            )
            val = inpt("note", catch="i", catch_callback=note_options)
    elif mode == "beat":
        try:
            t(60, val)
        except TypeError:
            info_block(
                "> Value '{0}' is not a validly formed beat. Enter intended value ('i' for info on how to make validly formed beats, 'q' to cancel): ".format(val),
                for_prompt=True
            )
            val = inpt("beat", catch="i", catch_callback=beat_options)
    # number inputs
    elif mode in ("pcnt", "int", "flt"):
        if mode == "pcnt":
            val = re.sub(r"%", "", val)
            try:
                val = float(val)
            except (ValueError):
                info_block(
                    "> Value '{0}' is not a valid percentage. Enter intended value (or 'q' to quit): ".format(val),
                    for_prompt=True
                )
                val = inpt("pcnt")
            if allowed is None:
                allowed = [0, None]
        elif mode == "int":
            try:
                val = int(val)
            except ValueError:
                info_block(
                    "> Value '{0}' is not a valid integer. Enter intended value (or 'q' to quit): ".format(val),
                    for_prompt=True
                )
                val = inpt("int")
        elif mode == "flt":
            try:
                val = float(val)
            except ValueError:
                info_block(
                    "> Value '{0}' is not a valid number. Enter intended value (or 'q' to quit): ".format(val),
                    for_prompt=True
                )
                val = inpt("int")
        try:
            if allowed is not None:
                if allowed[0] is not None: assert val >= allowed[0]
                if allowed[1] is not None: assert val <= allowed[1]
        except AssertionError:
            allowed_str = []
            if allowed[0] is not None:
                allowed_str.append("value must be greater than {0}".format(allowed[0]))
            if allowed[1] is not None:
                allowed_str.append("value must be less than {0}".format(allowed[1]))
            allowed_str = " and ".join(allowed_str)
            p("> Invalid: " + allowed_str)
            val = inpt(mode)
    elif mode == "letter":
        if (len(val) != 1) or (val not in allowed):
            p("> Select one of " + ", ".join(allowed.upper()))
            val = inpt("letter", allowed=allowed)
    return val


