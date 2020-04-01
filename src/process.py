

import random as rd

from src.object_data import (public_process, is_public_process, 
    RelativismObject, RelativismPublicObject)
from src.input_processing import inpt, inpt_validate, input_dir, input_file, autofill
from src.output_and_prompting import (p, info_title, info_list, info_line, 
    section_head, info_block, nl, err_mess, critical_err_mess, show_error, style)
from src.globals import RelGlobals, Settings
from src.errors import *


def process(obj):
    """
    process an object.
    'self.name', 'self.reltype' required.
    caller must try/except handle Cancel error
    """
    section_head("Processing {0} '{1}'".format(obj.reltype, obj.name))

    while True: # broken by raise Cancel

        with style("cyan, bold"):
            print("\n{0} ".format(RelGlobals.get_process_num()), end="")
        p("What process to run on {0} '{1}'?".format(obj.reltype, obj.name), 
            h=True, o="'o' to view process options", indent=0, hang=4, leading_newline=False)

        command = inpt(mode='split', split_modes='arg', help_callback=processes_help)

        if process_validate(command, obj):
            do_command(command, obj)


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
        if inpt("y-n"):
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
    try:
        method_name, args = command[0], command[1:]

        # get full method name with autofill
        method_name = process_autofill(method_name, obj)
        method = obj.get_method(method_name).method_func

        pre_process(obj, method_name)

        # call process
        try:
            nl()
            method(*args)
        except TypeError as e:
            if 'positional argument' in str(e):
                command = process_complete_args(e, command, obj)
                do_command(command, obj)
                return
            else:
                raise e
        
        post_process(obj, method_name)

    # error handling & autofill
    except Exception as e:
        process_error_handling(e, command, obj)


def pre_process(obj, method_name):
    try:
        obj.pre_process(method_name)
    except (NotImplementedError, AttributeError):
        pass

def post_process(obj, method_name):
    try: 
        obj.post_process(method_name)
    except (NotImplementedError, AttributeError):
        pass

def process_complete_args(e, command, obj):
    """
    handle wrong number of args
    """
    if command[0] not in str(e):
        show_error(e)
    err_mess("Wrong number of arguments: {0}".format(str(e)))
    info_title("Args for {0}: ".format(command[0]))
    info_line(obj.get_method(command[0]).oneline_arg_list(), indent=6)
    # too many
    command_str = "\n      " + command[0] + " "
    if "were given" in str(e):
        p("Enter intended arguments", start=command_str)
        new_args = inpt('split', 'arg')
        return [command[0]] + new_args
    # not enough
    else:
        if len(command[1:]) > 0:
            command_str += " ".join(command[1:]) + " "
        p("Complete arguments", start=command_str)
        new_args = inpt('split', 'arg')
        return command + new_args


def process_autofill(method_name, obj):
    methods = [func for func in dir(obj.__class__) if callable(getattr(obj.__class__, \
        func)) and is_public_process(getattr(obj.__class__, func))]
    try:
        return autofill(method_name, methods, "arg")
    except AutofillError as e:
        process_error_handling(NoSuchProcess(str(e)), method_name, obj)


def process_error_handling(e, command, obj):
    """
    recursive calls with UnknownError are for redirecting to the end else
    """
    process = command[0] if isinstance(command, list) else command
    message = str(e)

    if isinstance(e, TypeError):
        if 'object is not callable' in message:
            process_error_handling(NoSuchProcess(message), process, obj)
        elif 'positional argument' in message:
            process_complete_args(e, command, obj)
        else:
            show_error(e)

    elif isinstance(e, ValueError):
        err_mess("Argument entered incorrectly: {0}".format(message))

    elif isinstance(e, (KeyError, AutofillError, NoSuchProcess)):
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

