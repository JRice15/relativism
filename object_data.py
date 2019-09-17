import re
from output_and_prompting import *


def public_process(func):
    """
    decorator: allow user access via 'process'
    """
    func.__rel_public__ = True
    return func


def is_public_process(func):
    try:
        return func.__rel_public__
    except AttributeError:
        return False


class Rel_Object_Data:
    """
    implements methods for showing public process methods
    """

    def __init__(self, obj=None, include=None):
        if obj is None:
            obj = self
        self.method_data_by_category = {}
        if isinstance(obj, type):
            obj_class = obj
        else:
            obj_class = obj.__class__
        method_strs = [func for func in dir(obj_class) if callable(getattr(obj, func))]
        public_method_strs = []
        for m in method_strs:
            method = getattr(obj, m)
            try:
                if getattr(method, '__rel_public__') == True:
                    public_method_strs.append(m)
            except AttributeError:
                pass
        for m in public_method_strs:
            m_data = Method_Data(self, obj, m)
            try:
                self.method_data_by_category[m_data.category][m_data.method_name] = m_data
            except KeyError:
                self.method_data_by_category[m_data.category] = {m_data.method_name : m_data}


    def __getitem__(self, arg):
        for i in self.method_data_by_category.items():
            try:
                return i[1][arg]
            except KeyError:
                pass
        raise KeyError


    def show_processes(self):
        """
        cat: info
        desc: list all processes that can be run on this object
        """
        info_block("# {Category} #", indent=2)
        info_line("- {Process}")
        info_line("{arguments in order, optional if in [square brackets]}", indent=8)
        for i in self.method_data_by_category.items():
            info_title("# " + str(i[0]).upper() + " #", indent=2)
            for j in i[1].items():
                j[1].display()


    def process__(self):
        process(self)



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
                    if title == "dev":
                        break
                    if not args_now:
                        if title in ("desc", "descrip", "description"):
                            self.desc = content.strip()
                        elif title in ("catg", "cat", "category", "catgry", "categry"):
                            self.set_category(content.strip())
                        elif title in ("args", "arguments"):
                            args_now = True
                    else:
                        arg_dt = Arg_Data(self, line)
                        self.args.append(arg_dt)
                except:
                    err_mess("Error getting object data from method " + self.method_name + ": " + str(line))
        
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
        elif category in ("eff", "effects", "fx", "efx", "effx", "effect"):
            category = "Effects"
        else:
            category = "Other"
        self.category = category


    def display(self):
        message = self.method_name.capitalize() + ": " + self.desc
        info_list(message, hang=4)
        for i in self.args:
            info_line(i.get_display(), indent=12)


    def get_random_defaults(self):
        args = []
        for i in self.args:
            arg = i.choose_random_default() 
            if arg is None:
                break
            else:
                args.append(arg)
        return args



class Arg_Data:

    def __init__(self, parent, doc_line):
        self.parent = parent
        self.optional = False
        self.parse_arg_doc(doc_line)

    
    def parse_arg_doc(self, doc_line):
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


