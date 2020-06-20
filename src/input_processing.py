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
from src.method_ops import rel_alias, rel_wrap, _ClsRelData


def help_(help_func):
    """
    decorator for _InptValidate methods to provide help
    """
    def wrapper(method):
        method._help_func = help_func
        return method
    return wrapper

def do_allowed(method, val, mode, allowed):
    """
    allowed-checking wrapper for _InptValidate methods
    """
    val = method(val, mode, allowed)
    # expanding for methods that edit allowed, ie percent()
    if isinstance(val, tuple):
        val, allowed = val
    try:
        if allowed is not None:
            if allowed[0] is not None: 
                assert val >= inpt_validate(allowed[0], mode)
            if allowed[1] is not None: 
                assert val <= inpt_validate(allowed[1], mode)
    except AssertionError:
        p("> Invalid: value '{0}' must be ".format(val) + allowed_repr(allowed))
        raise TryAgain
    return val


class _InptValidate:
    """
    methods (with aliased names) for validating user input
    """

    @staticmethod
    def none(val, mode, allowed):
        return val
    
    @staticmethod
    def standard(val, mode, allowed):
        return re.sub(r"[^-_a-z9-9. ]", "", val)

    std = stnd = stdrd = standard

    @staticmethod
    def arg(val, mode, allowed):
        val = re.sub(r"[^-_.a-z0-9]", "", val)
        return re.sub(r"-", "_", val)

    args = arg

    @staticmethod
    def yesno(val, mode, allowed):
        if len(val) == 0 or val[0] not in "yn":
            info_block("> Enter 'y' or 'n': ", for_prompt=True)
            raise TryAgain
        if val[0] == "y":
            return True
        return False
        
    y_n = yn = yesno

    @staticmethod
    def letter(val, mode, allowed):
        if (len(val) != 1) or (allowed is not None and val not in allowed.lower()):
            p("> Select one of " + ", ".join(allowed.upper()))
            raise TryAgain
        return val

    lttr = ltr = lett = letter

    @staticmethod
    def alphanum(val, mode, allowed):
        val = re.sub(r"\s+", "_", val)
        val = re.sub(r"-", "_", val)
        val = re.sub(r"[^_a-z0-9]", "", val)
        val = re.sub(r"_{2,}", "_", val)
        return val

    obj = file = name = alphanum

    @staticmethod
    @help_(PitchUnits.note_options)
    def freq(val, mode, allowed):
        try:
            return PitchUnits.valid_pitch(val)
        except TypeError:
            info_block(
                "> Value '{0}' is not a validly formed note. Enter intended value ('h' for help on how to make validly formed notes, 'q' to cancel): ".format(val),
                indent=2,
                for_prompt=True
            )
            raise TryAgain

    note = frq = frequency = freq

    @staticmethod
    @rel_wrap(do_allowed)
    @help_(Units.beat_options)
    def beat(val, mode, allowed):
        try:
            return Units.beats(val)
        except:
            info_block(
                "> Value '{0}' is not a validly formed beat. Enter intended value ('h' for help on how to make validly formed beats, 'q' to cancel): ".format(val),
                for_prompt=True
            )
            raise TryAgain


    beats = b = beat

    @staticmethod
    @rel_wrap(do_allowed)
    def sec(val, mode, allowed):
        try:
            return Units.secs(val)
        except:
            info_block(
                "> Value '{0}' is not a validly seconds string (must be of the form '4s' or '4sec', not '4'). Enter intended value ('q' to cancel): ".format(val),
                for_prompt=True
            )
            raise TryAgain

    secs = second = seconds = sec

    @staticmethod
    @rel_wrap(do_allowed)
    @help_(Units.beat_options)
    def beatsec(val, mode, allowed):
        try:
            val = Units.beats(val)
        except ValueError:
            try:
                val = Units.secs(val)
            except:
                info_block(
                    "> Value '{0}' is not a validly formed beat or second (must be of the form '4s' or '4b', not '4'). Enter intended value ('q' to cancel): ".format(val),
                    for_prompt=True
                )
                raise TryAgain
        return val

    beat_sec = beatsecs = beat_secs = beatsec

    @staticmethod
    @rel_wrap(do_allowed)
    def percent(val, mode, allowed):
        if isinstance(val, str):
            val = re.sub(r"%", "", val)
        try:
            val = Units.pcnt(val)
        except (ValueError):
            p("> Value '{0}' is not a valid percentage. Enter intended value".format(val))
            raise TryAgain
        if allowed is None:
            allowed = [0, None]
        try:
            allowed[0] = Units.pcnt(allowed[0])
        except: pass
        try:
            allowed[1] = Units.pcnt(allowed[1])
        except: pass
    
        return (val, allowed)

    pct = pcnt = percent

    @staticmethod
    @rel_wrap(do_allowed)
    def integer(val, mode, allowed):
        try:
            return int(val)
        except ValueError:
            p("> Value '{0}' is not a valid integer (ie, whole number). Enter intended value".format(val))
            raise TryAgain

    int = integer

    @staticmethod
    @rel_wrap(do_allowed)
    def decimal(val, mode, allowed):
        try:
            return float(val)
        except ValueError:
            p("> Value '{0}' is not a valid number (decimal number allowed). Enter intended value".format(val))
            raise TryAgain

    flt = float = decimal

    @staticmethod
    @rel_wrap(do_allowed)
    def bpm(val, mode, allowed):
        try:
            val = Units.bpm(val)
        except ValueError:
            p("> Invalid beats-per-minute '{0}'. Enter the intended value as a single number (decimal allowed)".format(val))
            raise TryAgain
        if val.magnitude <= 0:
            info_block("> Value cannot be negative or zero. Enter intended value")
            raise TryAgain
        return val

    @staticmethod
    @rel_wrap(do_allowed)
    def rate(val, mode, allowed):
        try:
            val = Units.rate(val)
        except ValueError:
            p("> Invalid samplerate '{0}'. Enter the intended value".format(val))
            raise TryAgain
        if val.magnitude <= 0:
            info_block("> Samplerate cannot be negative or zero. Enter intended value")
            raise TryAgain
        return val

    samplerate = rate



def do_help_msg(mode, help_callback):
    """
    try to print a help message, either from help_callback, or from
    modemethod._help_func
    """
    if callable(help_callback):
        help_callback()
    else:
        try:
            getattr(getattr(_InptValidate, mode), "_help_func")()
        except AttributeError: 
            err_mess("No help is configured for this action")


def inpt(mode, split_modes=None, help_callback=None, catch=None, catch_callback=None, 
        allowed=None, required=True, quit_on_q=True):
    """
    get and clean input via some specifications
        mode: str:
            obj, file, alphanum, name: whitespaces to underscore, alphanumeric
            yn: yes or no question, returns bool
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
    while True:
        try:

            val = input().lower().strip()

            if val == catch:
                catch_callback()
                p("Enter intended value")
                raise TryAgain

            if val == "q" and quit_on_q:
                raise Cancel

            if val == "":
                if required:
                    err_mess("A value is required. Enter intended value")
                    raise TryAgain
                else:
                    return val

            if val in ("h", "help"):
                do_help_msg(mode, help_callback)
                p("Enter intended value")
                raise TryAgain

            if mode == "split":
                val = val.split()
                for i in range(len(val)):
                    if split_modes is None:
                        raise ValueError("Must supply a mode to inpt, but recieved None for split_modes")
                    if isinstance(split_modes, str):
                        this_mode = split_modes
                    else:
                        try:
                            this_mode = split_modes[i]
                        except IndexError:
                            this_mode = split_modes[-1]
                    val[i] = inpt_validate(val[i], this_mode, True)
            else:
                val = inpt_validate(val, mode, allowed, True)

        except TryAgain:
            continue
        else:
            break

    return val



def inpt_validate(val, mode, allowed=None, _from_inpt=False):
    """
    processes individual modes for inpt
    also used as input validation
    mode: str:
        standard, stnd: whitespace, alphnum, underscore and dash, periods commas
        obj, file, alphanum, name: whitespaces to underscore, alphanumeric
        yn: yes or no question, returns bool
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

    if isinstance(val, str):
        val = val.lower().strip()
    mode = mode.lower().strip()

    try:
        method = getattr(_InptValidate, mode)
    except AttributeError:
        raise UnexpectedIssue("Unknown mode '{0}'".format(mode))

    try:
        return method(val, mode, allowed)
    except TryAgain as e:
        # inpt has more info, so we would rather re-call from there if possible
        if _from_inpt:
            raise e
        return inpt(mode, allowed=allowed)


def allowed_repr(allowed):
    """
    return str explaining conditions of allowed
    """
    if allowed is None:
        return ""
    allowed_conditions = []
    if allowed[0] is not None:
        allowed_conditions.append("less than or equal to {0}".format(allowed[0]))
    if allowed[1] is not None:
        allowed_conditions.append("less than or equal to {0}".format(allowed[1]))
    allowed_str = " and ".join(allowed_conditions)
    return allowed_str


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
        raise AutofillError(partial, "No autofill matches for '{0}'".format(partial))
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
