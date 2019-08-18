from name_and_path import *



def process(obj):
    """
    process an object
    'self.get_name()', 'self.type' required. 'self.processes()' recommended
    """
    print("\n* Processing object '{0}' of type '{1}'".format(obj.get_name(), obj.type))
    while True:
        print("\nWhat process to run on {0} '{1}'? ('q' to quit, 'o' to view options): ".format(
            obj.type, obj.get_name()), end="")
        command = inpt('split', 'alphanum')
        if command == []:
            print("  > No command entered")
            command = "None"
            continue
        elif command == ['']:
            print("  > Only alphanumeric characters, spaces, and underscores are allowed")
            continue
        elif command[0] in ("q", "e"):
            print("\n  Exiting processing of {0} '{1}'...\n".format(obj.type, obj.get_name()))
            raise Cancel(obj)
        elif command[0] in ("o"):
            process_get_methods(obj)
        else:
            while True:
                try:
                    # pre process
                    try: obj.pre_process__()
                    except (NotImplementedError, AttributeError): pass
                    # call method
                    func, args = command[0], command[1:]
                    func = eval("obj." + func)
                    func(*args)
                    # post process
                    try: obj.post_process__()
                    except (NotImplementedError, AttributeError): pass
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
                info_block("Autofilled '{0}'".format(matches[0]))
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


def process_get_methods(obj):
    try:
        obj.processes()
    except (NotImplementedError, AttributeError) :
        print("\n  {processes}\n")
        obj_class = type(obj)
        methods = [func for func in dir(obj_class) if callable(getattr(obj_class, \
            func)) and "__" not in func]
        for i in methods:
            print("  -", i)


def get_similar_methods(obj, partial):
    obj_class = type(obj)
    matches = []
    methods = [func for func in dir(obj_class) if callable(getattr(obj_class, \
        func)) and "__" not in func]
    for m in methods:
        if m[:len(partial)] == partial:
            matches.append(m)
    return matches
    
