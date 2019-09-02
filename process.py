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
    print("\n* Processing object '{0}' of type '{1}'".format(name, obj.type))
    while True:
        print("\nWhat process to run on {0} '{1}'? ('q' to quit, 'o' to view options): ".format(
            obj.type, name), end="")
        command = inpt('split', 'alphanum')
        if command == []:
            print("  > No command entered")
            command = "None"
            continue
        elif command == ['']:
            print("  > Only alphanumeric characters, spaces, and underscores are allowed")
            continue
        elif command[0] in ("q", "e"):
            print("\n  Exiting processing of {0} '{1}'...\n".format(obj.type, name))
            raise Cancel(obj)
        elif command[0] in ("o"):
            obj.obj_data.display()
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
    



class Arg_Data:

    def __init__(self, parent, doc_line):
        self.parent = parent
        self.optional = False
        if doc_line[0] == "[":
            doc_line = doc_line.strip("[").strip("]")
            self.optional = True
        name, rest = doc_line.split(":")
        self.name = name.strip()
        self.desc = rest.split(';')[0].strip()

        self.defaults_low, self.defaults_high = None, None
        try:
            defaults = rest.split(";")[1].split(',')
            self.defaults_low = float(defaults[0])
            self.defaults_high = float(defaults[1])
        except:
            pass

    def get_display(self):
        string = self.name + ": " + self.desc
        if self.optional:
            string = "[" + string + "]"
        return string


    def choose_random_default(self):
        if self.defaults_high is None:
            return None
        else:
            num = rd.random()
            arg = (self.defaults_low * (1 - num)) + (self.defaults_high * (num))
            return arg


class Method_Data:

    def __init__(self, parent, obj, method):
        """
        method: str
        """
        self.parent = parent
        self.obj = obj
        self.method_name = method

        self.category = None
        self.args = []
        self.desc = ""

        self.analayze_doc()
    
    def analayze_doc(self):
        doc = getattr(self.obj, self.method_name).__doc__
        if doc is not None:
            doc = [
                j for j in 
                [re.sub(r"\s+", " ", i.strip()) for i in doc.split('\n')]
                if j not in ("", " ")
                ]
            args_now = False
            for line in doc:
                try:
                    title, content = line.split(":")[0].lower(), line.split(":")[1]
                    if not args_now:
                        if title == "dev":
                            break
                        elif title in ("desc", "descrip", "description"):
                            self.desc = content.strip()
                        elif title in ("catg", "cat", "category", "catgry", "categry"):
                            self.set_category(content.strip())
                        elif title in ("args", "arguments"):
                            args_now = True
                    else:
                        arg_dt = Arg_Data(self, line)
                        self.args.append(arg_dt)
                except:
                    err_mess("Error in " + self.method_name + ": " + str(line))
        
        if self.category is None:
            self.category = "Other"
                    
    def set_category(self, category):
        if category in ("edit", "edits"):
            category = "Edits"
        elif category in ("meta", "metadata"):
            category = "Metadata"
        elif category in ("info", "repr", "representation"):
            category = "Object Info"
        elif category in ("save", "saving"):
            category = "Saving & Data Handling"
        else:
            category = "Other"
        self.category = category


    def display(self):
        message = self.method_name.capitalize() + ": " + self.desc
        info_list(message)
        for i in self.args:
            info_line(i.get_display(), indent=8)


    def get_random_defaults(self):
        args = []
        for i in self.args:
            arg = i.choose_random_default() 
            if arg is None:
                break
            else:
                args.append(arg)
        return args


class Object_Data:

    def __init__(self, obj):
        self.obj = obj
        self.methods_by_category = {}
        if isinstance(obj, type):
            obj_class = obj
        else:
            obj_class = obj.__class__
        public_method_strs = [func for func in dir(obj_class) if "__" not in func and \
            callable(getattr(obj, func))]
        for m in public_method_strs:
            m_data = Method_Data(self, obj, m)
            try:
                self.methods_by_category[m_data.category][m_data.method_name] = m_data
            except KeyError:
                self.methods_by_category[m_data.category] = {m_data.method_name : m_data}


    def __getitem__(self, arg):
        for i in self.methods_by_category.items():
            try:
                return i[1][arg]
            except KeyError:
                pass
        raise KeyError


    def display(self):
        info_block("# {Category} #", indent=2)
        info_line("- {Process}")
        info_line("{arguments in order, optional if in [square brackets]}", indent=8)
        for i in self.methods_by_category.items():
            info_title("# " + str(i[0]).upper() + " #", indent=2)
            for j in i[1].items():
                j[1].display()


