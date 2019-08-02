from name_and_path import *



def process(obj):
    """
    process an object
    method get_name(), attr type required. processes() recommended
    """
    print("\n* Processing object '{0}' of type '{1}'".format(obj.get_name(), obj.type))
    command = [None]
    while command[0] != "q":
        print("\nWhat process to run on {0} '{1}'? ('q' to quit, 'o' to view options): ".format(obj.type, obj.get_name()), end="")
        last_command = command
        command = inpt('split', 'alphanum')
        if command == []:
            print("  > No command entered")
            command = "None"
            continue
        elif command == ['']:
            print("  > Only alphanumeric characters, spaces, and underscores are allowed")
            continue
        elif command[0] in ("q", "e"):
            print("\n  exiting...\n")
            return
        elif command[0] in ("o"):
            process_get_methods(obj)
        else:
            if command[0] == "\x1b[A":
                command[0] = last_command
            if command[0] == "process":
                print("  > You are already processing")
                continue
            command[0] = re.sub(r"^write$", "write_to_file", command[0])
            try:
                func, args = command[0], command[1:]
                func = eval("obj." + func)
                func(*args)
            except Exception as e:
                if MC_SuperGlobls.DEBUG:
                    raise e
                process_error_handling(e, command[0])


def process_error_handling(e, process):
    """
    recursive calls with NotImplementedError are for redirecting to the end else
    """
    message = str(e)
    if isinstance(e, TypeError):
        if 'object is not callable' in message:
            process_error_handling(SyntaxError(message), process)
        elif 'positional argument' in message:
            print("  > Wrong number of arguments: {0}".format(message))
        else:
            process_error_handling(NotImplementedError(message), process)
    elif isinstance(e, ValueError):
        print("  > Argument entered incorrectly: {0}".format(message))
    elif isinstance(e, AttributeError):
        if 'object has no attribute' in message:
            process_error_handling(SyntaxError(message), process)
        else:
            process_error_handling(NotImplementedError(message), process)
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