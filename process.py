from name_and_path import *
import random as rd
from object_data  import *


def process(obj):
    """
    process an object
    'self.name()', 'self.type' required
    """
    section_head("Processing object '{0}' of type '{1}'".format(obj.name, obj.type))
    while True:
        p("What process to run on {0} '{1}'?".format(obj.type, obj.name), o="'o' to view process options")
        command = inpt('split', 'arg')
        if command == []:
            err_mess("No command entered")
            command = "None"
            continue
        elif command == ['']:
            err_mess("Only alphanumeric characters, spaces, and underscores are allowed")
            continue
        elif command[0] in ("q", "e"):
            info_block("Exiting processing of {0} '{1}'...".format(obj.type, obj.name))
            raise Cancel(obj)
        elif command[0] in ("o"):
            obj.show_processes()
        else:
            while True:
                process_exists = False
                try:
                    method_name, args = command[0], command[1:]

                    # pre process
                    try:
                        obj.pre_process(method_name)
                    except (NotImplementedError, AttributeError):
                        pass

                    # call method
                    try:
                        method = obj[method_name].method_func
                        process_exists = True
                    except KeyError:
                        raise AttributeError("{0} '{1}' has no process {2}".format(obj.type, obj.name, method_name))
                    try:
                        method(*args)
                    except TypeError as e:
                        if 'positional argument' in str(e):
                            command = process_complete_args(e, command, obj)
                            continue
                        else:
                            raise e

                    # post process
                    try: 
                        obj.post_process(method_name)
                    except (NotImplementedError, AttributeError): 
                        pass
                    break
                except Exception as e:
                    if process_exists and 'required positional argument' not in str(e):
                        show_error(e)
                        break
                    command = process_error_handling(e, command, obj)
                    if command is None:
                        break



def process_complete_args(e, command, obj):
    err_mess("Wrong number of arguments: {0}".format(str(e)))
    info_title("Args for {0}: ".format(command[0]))
    info_line(obj[command[0]].oneline_arg_list(), indent=6)
    # too many
    command_str = "\n      " + command[0] + " "
    if "were given" in str(e):
        p("Complete arguments", start=command_str)
        new_args = inpt('split')
        return [command[0]] + new_args
    # not enough
    else:
        if len(command[1:]) > 0:
            command_str += " ".join(command[1:]) + " "
        p("Complete arguments", start=command_str)
        new_args = inpt('split')
        return command + new_args


def process_error_handling(e, command, obj):
    """
    recursive calls with NotImplementedError are for redirecting to the end else
    """
    process = command[0]

    message = str(e)
    if isinstance(e, TypeError):
        if 'object is not callable' in message:
            process_error_handling(SyntaxError(message), process, obj)
        elif 'positional argument' in message:
            process_complete_args(e, command, obj)
        else:
            process_error_handling(NotImplementedError(message), process, obj)
    elif isinstance(e, ValueError):
        err_mess("Argument entered incorrectly: {0}".format(message))
    elif isinstance(e, AttributeError):
        if 'has no process' in message:
            matches = get_similar_methods(obj, process)
            if len(matches) > 1:
                info_block("Multiple matches:", trailing_newline=False)
                info_list(matches)
                print("  Complete for intended process: " + process, end="")
                rest = inpt('split', 'alphanum', quit_on_q=False)
                return [process + rest[0]] + rest[1:]
            elif len(matches) == 1:
                print("  -> Autofilled '{0}'".format(matches[0]))
                return matches + command[1:]
            else:
                process_error_handling(SyntaxError(message), process, obj)
        else:
            process_error_handling(NotImplementedError(message), process, obj)
    elif isinstance(e, SyntaxError):
        err_mess("Process '{0}' does not exist: {1}".format(process, message))
    elif isinstance(e, PermissionError):
        err_mess(message)
    elif isinstance(e, Cancel):
        print("\n exiting processing...\n")
    else:
        show_error(e)



def show_error(e):
    if not isinstance(e, Cancel):
        critical_err_mess(e.__class__.__name__ + ": " + str(e))
        if Relativism.DEBUG:
                p("Raise error? [y/n]")
                if input().lower().strip() == 'y':
                    raise e


def get_similar_methods(obj, partial):
    obj_class = type(obj)
    matches = []
    methods = [func for func in dir(obj_class) if callable(getattr(obj_class, \
        func)) and is_public_process(getattr(obj_class, func))]
    for m in methods:
        if m[:len(partial)] == partial:
            matches.append(m)
    return matches


