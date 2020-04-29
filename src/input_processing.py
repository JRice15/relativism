""" 
cleaning input
    importer must import relativism
"""

import re
import time
import tkinter as tk
from tkinter import filedialog

from src.data_types import *
from src.errors import *
from src.output_and_prompting import (critical_err_mess, err_mess, info_block,
                                      info_line, info_list, info_title, nl, p,
                                      section_head, show_error)
from src.path import join_path, split_path
from src.utility import *


def inpt(mode, split_modes=None, help_callback=None, catch=None, catch_callback=None, 
        allowed=None, required=True, quit_on_q=True):
    """
    get and clean input via some specifications
        mode: str:
            obj, file, alphanum, name: whitespaces to underscore, alphanumeric
            y-n: yes or no question, returns bool
            beat: valid beat input
            note, freq: valid note/freq input
            int: integer, optional allowed list
            flt: float, optional allowed list
            pcnt: percentage, opt allowed list
            split: splits input, does split modes on each (inp longer than split modes uses last mode for rest)
            letter: one letter, str of allowed
            arg: for process arg entry
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
        catch_callback()
        print("\n  enter intended value ('q' for quit): ", end="")
        return inpt(mode, split_modes=split_modes)
    if val == "q" and quit_on_q:
        raise Cancel
    if val == "":
        if required:
            p("> A value is required. Enter intended value")
            return inpt(mode, split_modes=split_modes, catch=catch, 
                catch_callback=catch_callback, allowed=allowed, required=required)
        else:
            return val
    if val in ("h", "help"):
        try:
            help_callback()
            val = "h"
        except:
            if mode in ("beat", "beats", "b"):
                Units.beat_options()
            else:
                err_mess("No help is configured for this action")
    if mode == "split":
        val = val.split()
        for i in range(len(val)):
            if split_modes is None:
                raise ValueError("Must supply a mode to inpt, but recieved None for split_modes")
            else:
                if isinstance(split_modes, str):
                    this_mode = split_modes
                else:
                    try:
                        this_mode = split_modes[i]
                    except IndexError:
                        this_mode = split_modes[-1]
            val[i] = inpt_validate(val[i], this_mode)
    else:
        val = inpt_validate(val, mode, allowed)
    return val


def inpt_validate(val, mode, allowed=None):
    """
    processes individual modes for inpt
    also used as input validation
    mode: str:
        standard, stnd: whitespace, alphnum, underscore and dash, periods commas
        obj, file, alphanum, name: whitespaces to underscore, alphanumeric
        y-n: yes or no question, returns bool
        beat: valid beat input
        sec: float as second
        beatsec: beat or second
        note, freq: valid note/freq input
        int: integer, optional allowed list
        flt: float, optional allowed list
        pcnt: percentage, opt allowed list
        split: splits input, does split modes on each (inp longer than split modes uses last mode for rest)
        letter: one letter, str of allowed
        arg: for process arg entry
    """
    if mode is None:
        raise ValueError("Must supply a mode to inpt_validate, but recieved None")

    elif mode == "none":
        return val

    elif mode in ("standard", 'stnd'):
        val = re.sub(r"[^-_a-z0-9. ]", "", val)

    elif mode in ("arg", "args"):
        val = re.sub(r"[^-_.a-z0-9]", "", val)
        val = re.sub(r"-", "_", val)

    elif mode in ("y-n", "y/n", "yn", "yesno", "yes/no"):
        if len(val) == 0 or val[0] not in "yn":
            print("  > Enter 'y' or 'n': ", end="")
            return inpt(mode)
        if val[0] == "y":
            val = True
        else:
            val = False

    elif mode in ("letter", "lttr", "ltr", "lett"):
        if (allowed is not None) and (len(val) != 1 or val not in allowed):
            p("> Select one of " + ", ".join(allowed.upper()))
            val = inpt(mode, allowed=allowed)

    elif mode in ("obj", "file", "alphanum", "name"):
        val = re.sub(r"\s+", "_", val)
        val = re.sub(r"-", "_", val)
        val = re.sub(r"[^_a-z0-9]", "", val)
        val = re.sub(r"_{2,}", "_", val)

    elif mode in ("note", "freq", "frq", "frequency"):
        try:
            val = PitchUnits.valid_pitch(val)
        except TypeError:
            info_block(
                "> Value '{0}' is not a validly formed note. Enter intended value ('h' for help on how to make validly formed notes, 'q' to cancel): ".format(val),
                indent=2,
                for_prompt=True
            )
            val = inpt(mode, help_callback=PitchUnits.note_options)

    elif mode in ("beat", "beats", "b"):
        try:
            val = Units.beats(val)
        except:
            info_block(
                "> Value '{0}' is not a validly formed beat. Enter intended value ('h' for help on how to make validly formed beats, 'q' to cancel): ".format(val),
                for_prompt=True
            )
            val = inpt(mode, help_callback=Units.beat_options)

    elif mode in ("sec", "secs", "second", "seconds"):
        try:
            val = Units.secs(val)
        except:
            info_block(
                "> Value '{0}' is not a validly number for seconds. Enter intended value ('q' to cancel): ".format(val),
                for_prompt=True
            )
            val = inpt(mode)

    elif mode in ("beatsec", "beat/sec"):
        try:
            val = Units.beats(val)
        except ValueError:
            try:
                val = Units.secs(val)
            except:
                info_block(
                    "> Value '{0}' is not a validly formed beat or second. Enter intended value ('q' to cancel): ".format(val),
                    for_prompt=True
                )
                val = inpt(mode)


    # number inputs
    elif mode in ("pcnt", "pct", "percent", "int", "flt", "float"):

        if mode in ("pcnt", "pct", "percent"):
            if isinstance(val, str):
                val = re.sub(r"%", "", val)
            try:
                val = Units.pcnt(val)
            except (ValueError):
                info_block(
                    "> Value '{0}' is not a valid percentage. Enter intended value (or 'q' to quit): ".format(val),
                    for_prompt=True
                )
                val = inpt(mode)
            if allowed is None:
                allowed = [0, None]
            try:
                allowed[0] = Units.pcnt(allowed[0])
            except: pass
            try:
                allowed[1] = Units.pcnt(allowed[1])
            except: pass

        elif mode == "int":
            try:
                val = int(val)
            except ValueError:
                info_block(
                    "> Value '{0}' is not a valid integer. Enter intended value (or 'q' to quit): ".format(val),
                    for_prompt=True
                )
                val = inpt(mode)

        elif mode in ("flt", "float"):
            try:
                val = float(val)
            except ValueError:
                info_block(
                    "> Value '{0}' is not a valid number (decimal allowed). Enter intended value (or 'q' to quit): ".format(val),
                    for_prompt=True
                )
                val = inpt(mode)

        try:
            if allowed is not None:
                if allowed[0] is not None: 
                    assert val >= allowed[0]
                if allowed[1] is not None: 
                    assert val <= allowed[1]
        except AssertionError:
            allowed_str = "value must be "
            allowed_conditions = []
            if allowed[0] is not None:
                allowed_conditions.append("less than or equal to {0}".format(allowed[0]))
            if allowed[1] is not None:
                allowed_conditions.append("less than or equal to {0}".format(allowed[1]))
            allowed_str += " and ".join(allowed_conditions)
            p("> Invalid: " + allowed_str)
            val = inpt(mode)

    else:
        raise UnexpectedIssue("Unknown mode for inpt_validate")

    return val




def input_file():
    """
    dialog box to choose a file. Raises Cancel on no selection
    """
    sys.stdout.flush()
    with suppress_output():
        root = tk.Tk()
        root.withdraw()
        root.update()
        file = filedialog.askopenfilename(initialdir=os.getcwd(), title="Choose a file")
        root.update()
        root.destroy()
    if file == "":
        raise Cancel
    nl()
    return file



def input_dir():
    """
    dialog box to choose a directory. Raises Cancel on no selection
    """
    sys.stdout.flush()
    with suppress_output():
        root = tk.Tk()
        root.withdraw()
        root.update()
        directory = filedialog.askdirectory(initialdir=os.getcwd(), title="Choose a directory/folder")
        root.update()
        root.destroy()
    if directory == "":
        raise Cancel
    nl()
    return join_path(directory, is_dir=True)



def autofill(partial, possibles, inpt_mode="name"):
    """
    matches partial word to one or more of the possible options.
    Raises AutofillError on failure and no message (alert in caller)
    """
    matches = []
    for pos in possibles:
        if pos[:len(partial)] == partial:
            matches.append(pos)
    if len(matches) == 0:
        raise AutofillError("No autofill matches for '{0}'".format(partial))
    elif len(matches) == 1:
        if matches[0] != partial: # only display on imperfect match
            info_block("-> Autofilled '{0}'".format(matches[0]))
        return matches[0]
    else:
        info_title("Multiple matches:")
        info_list(matches)
        p("Complete the word", start=partial)
        rest = inpt(inpt_mode)
        return autofill(partial + rest, matches, inpt_mode=inpt_mode)
