import re
from output_and_prompting import *
import random as rd
import json


#decorator
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


def parse_path(filename_or_fullpath, directory):
    """
    parse path for reading and writing metadata
    """
    filename_or_fullpath = re.sub(r"\..*", "", filename_or_fullpath)
    filename_or_fullpath += '.relativism-obj'
    if directory[-1] != '/':
        directory += '/'
    fullpath = directory + filename_or_fullpath
    return fullpath


class RelativismObject():
    """
    base class for objects that are saved and loaded
    """

    def __init__(self, reload_data=None):
        
        self.name = None
        self.type = None

    def write_metadata(self, filename_or_fullpath, directory="."):
        """
        if no directory arg filename is fullpath. do not include extension.
        create 'parse_metadata' method to override default
        """
        try:
            data = self.parse_metadata()
        except AttributeError:
            data = vars(self)
        fullpath = parse_path(filename_or_fullpath, directory)
        with open(fullpath, 'w') as f:
            json.dump(data, f)


class RelativismPublicObject(RelativismObject):
    """
    implements methods for showing public process methods.
    use getitem to get method by str.
    inner classes: MethodData, ArgData
    """

    def __init__(self, obj=None, include=None):
        super().__init__()
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
            m_data = RelativismPublicObject.MethodData(self, obj, m)
            try:
                self.method_data_by_category[m_data.category][m_data.method_name] = m_data
            except KeyError:
                self.method_data_by_category[m_data.category] = {m_data.method_name : m_data}


    def get_method(self, arg):
        for i in self.method_data_by_category.items():
            try:
                return i[1][arg]
            except KeyError:
                pass
        raise KeyError


    @public_process
    def show_processes(self):
        """
        cat: info
        desc: list all processes that can be run on this object
        """
        print("")
        info_block("# {Category} #", indent=2)
        info_line("- {Process}")
        info_line("{arguments in order, optional if in [square brackets]}", indent=8)
        for i in self.method_data_by_category.items():
            info_title("# " + str(i[0]).upper() + " #", indent=2)
            for j in i[1].items():
                j[1].display()



    class MethodData:

        def __init__(self, parent, obj, method):
            """
            method: str
            """
            self.parent = parent
            self.obj = obj
            self.method_name = method
            self.method_func = getattr(obj, method)

            self.category = None
            self.raw_category = None
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
                                self.category = self.display_category(content.strip())
                                self.raw_category = self.parse_category(content.strip())
                            elif title in ("args", "arguments"):
                                args_now = True
                        else:
                            arg_dt = RelativismPublicObject.ArgData(self, line)
                            self.args.append(arg_dt)
                    except:
                        err_mess("Error getting object data from method " + self.method_name + ": " + str(line))
            
            if self.category is None:
                self.category = "Other"



        def parse_category(self, category):
            category = category.lower()
            if category in ("edit", "edits"):
                category = "edit"
            elif category in ("meta", "metadata"):
                category = "meta"
            elif category in ("info", "repr", "representation"):
                category = "info"
            elif category in ("save", "saving"):
                category = "save"
            elif category in ("eff", "effects", "fx", "efx", "effx", "effect"):
                category = "effect"
            else:
                category = "other"
            return category


        def display_category(self, category):
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
            return category


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


        def oneline_arg_list(self):
            argstr = []
            for i in self.args:
                if i.optional:
                    argstr.append("[" + i.name + "]")
                else:
                    argstr.append(i.name)
            return ", ".join(argstr)


        def is_edit_rec(self):
            """
            is category that the rec.arr should be saved on
            """
            return self.raw_category in ('edit', 'effect')

        def is_edit_meta(self, cat):
            """
            if is catg that rec metadata should be save on
            """
            return self.raw_category in ('meta')



    class ArgData:

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


