from name_and_path import *
import random as rd


def process(obj):
    """
    process an object
    'self.get_name()', 'self.type' required. 'self.processes()' recommended
    """
    try:
        name = obj.name
    except AttributeError:
        name = obj.get_name()
    section_head("Processing object '{0}' of type '{1}'".format(name, obj.type))
    while True:
        p("What process to run on {0} '{1}'?".format(obj.type, name))
        command = inpt('split', 'alphanum')
        if command == []:
            err_mess("No command entered")
            command = "None"
            continue
        elif command == ['']:
            err_mess("Only alphanumeric characters, spaces, and underscores are allowed")
            continue
        elif command[0] in ("q", "e"):
            info_block("Exiting processing of {0} '{1}'...".format(obj.type, name))
            raise Cancel(obj)
        elif command[0] in ("o"):
            obj.show_processes()
        else:
            while True:
                try:
                    func, args = command[0], command[1:]

                    # pre process
                    try: 
                        obj.pre_process__(func)
                    except (NotImplementedError, AttributeError): 
                        pass

                    # call method
                    method = getattr(obj, func)
                    method(*args)

                    # post process
                    try: 
                        obj.post_process__(func)
                    except (NotImplementedError, AttributeError): 
                        pass
                    break
                except Exception as e:
                    if Relativism.DEBUG:
                        raise e
                    command = process_error_handling(e, command[0], obj)
                    if command is None:
                        break


def process_error_handling(e, process, obj):
    """
    recursive calls with NotImplementedError are for redirecting to the end else
    """
    message = str(e)
    if isinstance(e, TypeError):
        if 'object is not callable' in message:
            process_error_handling(SyntaxError(message), process, obj)
        elif 'positional argument' in message:
            print("  > Wrong number of arguments: {0}".format(message))
        else:
            process_error_handling(NotImplementedError(message), process, obj)
    elif isinstance(e, ValueError):
        print("  > Argument entered incorrectly: {0}".format(message))
    elif isinstance(e, AttributeError):
        if 'object has no attribute' in message:
            matches = get_similar_methods(obj, process)
            if len(matches) > 1:
                info_block("Multiple matches:", trailing_newline=False)
                info_list(matches)
                print("  Complete for intended process: " + process, end="")
                rest = inpt('split', 'alphanum', quit_on_q=False)
                return [process + rest[0]] + rest[1:]
            elif len(matches) == 1:
                info_list("> Autofilled '{0}'".format(matches[0]))
                return matches
            else:
                process_error_handling(SyntaxError(message), process, obj)
        else:
            process_error_handling(NotImplementedError(message), process, obj)
    elif isinstance(e, SyntaxError):
        print("  > Process '{0}' does not exist: {1}".format(process, message))
    elif isinstance(e, PermissionError):
        print("  > " + message)
    elif isinstance(e, Cancel):
        print("\n exiting processing...\n")
    else:
        print("  > " + str(type(e)) + ": " + message)



def get_similar_methods(obj, partial):
    obj_class = type(obj)
    matches = []
    methods = [func for func in dir(obj_class) if callable(getattr(obj_class, \
        func)) and "__" not in func]
    for m in methods:
        if m[:len(partial)] == partial:
            matches.append(m)
    return matches
    



