from data_types import *
from errors import *
import re
import time
from output_and_prompting import *
from utility import *
from relativism import *

""" clean input """


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
        # for options call
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
            return ""
    if val in ("h", "help"):
        try:
            help_callback()
            val = ""
        except:
            err_mess("No help is configured for this action")
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
            val[i] = inpt_validate(val[i], t_mode)
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
        note, freq: valid note/freq input
        int: integer, optional allowed list
        flt: float, optional allowed list
        pcnt: percentage, opt allowed list
        split: splits input, does split modes on each (inp longer than split modes uses last mode for rest)
        letter: one letter, str of allowed
        arg: for process arg entry
    """
    if mode == "none":
        return val
    elif mode in ("standard", 'stnd'):
        val = re.sub(r"[^-_a-z0-9. ]", "", val)
    elif mode == "arg":
        val = re.sub(r"[^-_.a-z0-9]", "", val)
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
    elif mode in ("note", "freq"):
        try:
            val = Units.freq(val)
        except TypeError:
            info_block(
                "> Value '{0}' is not a validly formed note. Enter intended value ('h' for help on how to make validly formed notes, 'q' to cancel): ".format(val),
                indent=2,
                for_prompt=True
            )
            val = inpt("note", help_callback=Units.note_options)
    elif mode in ("beat", "beats", "b"):
        try:
            val = Units.beats(val)
            if not val.check('[beat_time]'):
                raise ValueError
        except:
            info_block(
                "> Value '{0}' is not a validly formed beat. Enter intended value ('h' for help on how to make validly formed beats, 'q' to cancel): ".format(val),
                for_prompt=True
            )
            val = inpt("beat", help_callback=Units.beat_options)
    elif mode in ("sec", "second", "seconds"):
        try:
            val = Units.secs(val)
            if not val.check('[time]'):
                raise ValueError
        except:
            info_block(
                "> Value '{0}' is not a validly formed second. Enter intended value ('q' to cancel): ".format(val),
                for_prompt=True
            )
            val = inpt("second")
    # number inputs
    elif mode in ("pcnt", "percent", "int", "flt", "float"):
        if mode in ("pcnt", "percent"):
            if isinstance(val, str):
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
        elif mode in ("flt", "float"):
            try:
                val = float(val)
            except ValueError:
                info_block(
                    "> Value '{0}' is not a valid number (decimal allowed). Enter intended value (or 'q' to quit): ".format(val),
                    for_prompt=True
                )
                val = inpt("float")
        try:
            if allowed is not None:
                if allowed[0] is not None: assert val >= allowed[0]
                if allowed[1] is not None: assert val <= allowed[1]
        except AssertionError:
            allowed_str = []
            if allowed[0] is not None:
                allowed_str.append("value must be greater than or equal to {0}".format(allowed[0]))
            if allowed[1] is not None:
                allowed_str.append("value must be less than or equal to {0}".format(allowed[1]))
            allowed_str = " and ".join(allowed_str)
            p("> Invalid: " + allowed_str)
            val = inpt(mode)
    elif mode == "letter":
        if (len(val) != 1) or (allowed is not None and val not in allowed):
            p("> Select one of " + ", ".join(allowed.upper()))
            val = inpt("letter", allowed=allowed)
    else:
        raise UnexpectedIssue("Unknown process mode")
    return val


