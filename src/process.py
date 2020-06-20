

import random as rd

from src.rel_objects import RelSavedObj, RelPublicObj
from src.method_ops import public_process, is_public_process, rel_alias, is_alias
from src.input_processing import inpt, inpt_validate, input_dir, input_file, autofill
from src.output_and_prompting import (p, info_title, info_list, info_line, 
    section_head, info_block, nl, err_mess, critical_err_mess, show_error, style)
from src.globals import RelGlobals, Settings
from src.errors import *


def process(obj):
    """
    process an object.
    'self.name', 'self.reltype' required.
    """
    section_head("Processing {0} '{1}'".format(obj.reltype, obj.name))

    while True:

        try:
            obj.process_message()
        except AttributeError:
            pass

        with style("cyan, bold"):
            print("\n{0} ".format(RelGlobals.get_process_num()), end="")
        p("What process to run on {0} '{1}'?".format(obj.reltype, obj.name), 
            h=True, o="'o' to view process options", indent=0, hang=4, leading_newline=False)

        try:
            command = inpt(mode='split', split_modes='arg', help_callback=processes_help)
            if process_validate(command, obj):
                do_command(command, obj)
        except Cancel:
            return


def process_validate(command, obj):
    """
    check command as valid or one of the shortcuts
    return True on valid
    """
    if command == []:
        err_mess("No command entered")
        command = "None"
    elif command == ['']:
        err_mess("Only alphanumeric characters, spaces, and underscores are allowed")
    elif command[0] in ("q", "quit"):
        p("Save before exiting?")
        if inpt("yn"):
            obj.save()
        info_block("Exiting processing of {0} '{1}'...".format(obj.reltype, obj.name))
        raise Cancel(obj)
    elif command[0] in ("o", "options"):
        obj.options()
    elif command[0] in ("h", "help"):
        pass # callback handled during inpt()
    else:
        return True
    return False


def do_command(command, obj):
    """
    execute command
    """
    method_name, args = command[0], command[1:]

    all_methods = obj.get_all_public_method_names()
    try:
        # get full method name with autofill
        method_name = autofill(method_name, all_methods, "arg")
        method = obj.get_process(method_name)

    # missing process
    except Exception as e:
        if isinstance(e, Cancel):
            return
        handle_not_found(e, command, obj)
        return

    pre_process(obj, method)

    nl()

    # call process
    try:
        method(*args)
    except Exception as e:
        if isinstance(e, Cancel):
            return
        handle_bad_args(e, method_name, command[1:], obj)
    else:
        post_process(obj, method)



def pre_process(obj, method_obj):
    try:
        obj.pre_process(method_obj)
    except (NotImplementedError, AttributeError):
        pass

def post_process(obj, method_obj):
    try: 
        obj.post_process(method_obj)
    except (NotImplementedError, AttributeError):
        pass


def complete_args(e, method_name, args, obj):
    """
    handle wrong number of args
    """
    if method_name not in str(e):
        show_error(e)
    err_mess("Wrong number of arguments: {0}".format(str(e)))
    info_title("Arguments for {0}: ".format(method_name), indent=4)
    obj.get_process(method_name)._rel_data.display_args()
    # too many
    command_str = "\n      " + method_name + " "
    if "were given" in str(e):
        p("Enter intended arguments", start=command_str)
        new_args = inpt('split', 'arg')
        return [method_name] + new_args
    # not enough
    else:
        if len(args) > 0:
            command_str += " ".join(args) + " "
        p("Complete arguments", start=command_str)
        new_args = inpt('split', 'arg')
        return [method_name] + args + new_args


def handle_bad_args(e, method_name, args, obj):
    message = str(e)

    if isinstance(e, TypeError) and 'positional argument' in message:
        command = complete_args(e, method_name, args, obj)
        do_command(command, obj)
    elif isinstance(e, ValueError):
        err_mess("Argument entered incorrectly: {0}".format(message))
    else:
        show_error(e)


def handle_not_found(e, command, obj):
    process = command[0] if isinstance(command, list) else command
    message = str(e)

    if isinstance(e, (TypeError, KeyError, AutofillError, NoSuchProcess)):
        if isinstance(e, TypeError) and 'not callable' not in message:
            show_error(e)
        if isinstance(e, AutofillError):
            process = e.word
        err_mess("Process '{0}' does not exist: {1}".format(process, message))
    else:
        show_error(e)



def processes_help():
    info_block("To execute a process, enter its name followed by the " + \
        "desired values for its arguments. For example, if you wanted " + \
        "to have a fade-in effect on a Recording occur starting at 4 seconds and lasting " + \
        "for 2, you might enter:")
    info_block("fade_in 4 2    (or)", indent=8)
    info_block("fade-in 4 2    (the interpreter is not usually picky about underscores vs. dashes)", indent=8)
    info_block("Optional arguments are denoted by square brackets [], " +\
        "so fade-in's second argument could be omitted, in which case " +\
        "the default is used, like:")
    info_block("fade_in 4", indent=8)
    info_block("Which would use the default value 0, starting the fade-in " +\
        "at the beginning of the recording")
    info_block("Enter 'o' (the letter) to view processes")

