
import re
import random as rd
import json
import os

from src.output_and_prompting import *
from src.input_processing import *
from src.data_types import *
from src.relativism import *
from src.path import *

import soundfile as sf



# decorator
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


def parse_path(filename_or_fullpath, prefix_path):
    """
    parse path for reading and writing metadata. Scraps extension
    """
    filename_or_fullpath = re.sub(r"\..*", "", filename_or_fullpath)
    if prefix_path is None or len(prefix_path) == 0:
        prefix_path = ""
    elif prefix_path[-1] != '/':
        prefix_path += '/'
    fullpath = prefix_path + filename_or_fullpath
    fullpath = re.sub(r"//", "/", fullpath)
    return fullpath



class RelativismObject():
    """
    base class for objects that are saved and loaded
    """

    def __init__(self, rel_id, name, path):
        
        self.name = name
        self.path = path
        self.reltype = None
        self.rel_id = rel_id if rel_id is not None else Relativism.get_next_id()


    def __repr__(self):
        string = "'{0}'. {1} object".format(self.name, self.reltype)
        try:
            self.source_block
        except AttributeError:
            return string
        string += " from"
        for key, val in self.source_block.items():
            string += " {0}: {1};".format(key, val)
        return string

    def get_dirname(self):
        return self.name + "." + self.reltype
    
    def get_extension(self):
        return "." + self.reltype + ".relativism-obj"

    def get_filename(self):
        return self.name + self.get_extension()


    @public_process
    def rename(self, name=None):
        if name is None:
            p("Give this {0} a name".format(self.reltype))
            name = inpt("obj")
        else:
            name = inpt_validate(name, 'obj')

        # validate
        try:
            self.parent.validate_child_name(self)
            self.name = name
        except AttributeError:
            self.name = name
        
        info_block("Named '{0}'".format(name))



    def get_path(self, filename=None, extension="obj"):
        """
        get path of this object's files, or path in same dir of 'filename'.
        extension: "obj" for obj, anything else for .wav
        """
        if filename is None:
            filename = self.name
        path = Path(self.path, filename)
        if extension == "obj":
            path.ext = ".relativism-obj"
        else:
            path.ext = ".wav"
        return path


    def save_metadata(self, filename, path):
        """
        define parse_write_meta(dict: attrs) to define which attrs to write
        """
        attrs = {k:v for k,v in vars(self).items()}
        del attrs["method_data_by_category"]
        attrs["__module__"] = self.__class__.__module__
        attrs["__class__"] = self.__class__.__name__
        try:
            attrs = self.parse_write_meta(attrs)
        except AttributeError:
            pass
        os.makedirs(path, exist_ok=True)
        fullpath = Path(path, filename, self.get_extension())
        # RelTypeEncoder found in object_loading
        with open(fullpath, 'w') as f:
            json.dump(attrs, f, cls=RelTypeEncoder, indent=2)


    def save_audio(self, arr, rate, filename, path):
        """
        base wav audio saving
        """
        os.makedirs(path, exist_ok=True)
        outfile = Path(path, filename + "." + self.reltype + ".wav")
        try:
            rate = int(rate.to_rate().magnitude)
        except AttributeError:
            rate = int(rate)
        sf.write(outfile.fullpath(), arr, rate)



class RelativismPublicObject(RelativismObject):
    """
    implements methods for showing public process methods.
    use getitem to get method by str.
    inner classes: MethodData, ArgData
    """


    def __init__(self, rel_id, name, path, obj=None):
        super().__init__(rel_id, name, path)
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





class SourceInfo(RelativismObject):
    """
    class for saving source info
    """

    def __init__(self, s_type, s_name, s_info=None):
        self.s_type = s_type
        self.s_name = s_name
        self.s_info = {} if s_info is None else s_info
    

    def show(self):
        """
        like repr but prints directly
        """
        info_line("Sourced from {0} '{1}':".format(self.s_type, self.s_name))
        for k,v in self.s_info.items():
            info_list("{0}: {1}".format(k,v))

    def set_info(self, info):
        """
        set info from dict
        """
        self.s_info.update(info)


