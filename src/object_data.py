
import json
import os
import random as rd
import re

import soundfile as sf

from src.data_types import *
from src.globals import RelGlobals, Settings
from src.input_processing import inpt, inpt_validate, input_dir, input_file
from src.output_and_prompting import (critical_err_mess, err_mess, info_block,
                                      info_line, info_list, info_title, nl, p,
                                      section_head, show_error)
from src.path import join_path, split_path


class RelativismObject():
    """
    base class for objects that are saved and loaded
    """

    datafile_extension = "relativism-obj"

    def __init__(self, rel_id, reltype, name, path, parent):
        
        self.name = name
        self.path = path # path including object's own directory
        self.parent = parent
        self.reltype = reltype
        self.rel_id = rel_id if rel_id is not None else RelGlobals.get_next_id()

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

    def get_data_filename(self):
        """
        name.reltype : name of directory and datafiles
        this part of the path is included in self.path
        """
        return self.name + "." + self.reltype

    def get_datafile_fullpath(self):
        """
        fullpath of datafile
        """
        return join_path(self.path, self.get_data_filename() + "." + self.datafile_extension)

    def get_audiofile_fullpath(self):
        """
        datafile path, but wav extension instead
        """
        return join_path(self.path, self.get_data_filename() + ".wav")

    def rename(self, name=None):
        """
        should call this method via super, and implement any file saving as needed
        """
        if name is None:
            p("Give this {0} a name".format(self.reltype))
            name = inpt("obj")
        else:
            name = inpt_validate(name, 'obj')

        # validate
        try:
            if self.parent.validate_child_name(name):
                self.name = name
                info_block("Named '{0}'".format(name))
            else:
                info_block("Invalid name")
                self.rename()
        except AttributeError:
            with open(RelGlobals.error_log(), "a") as f:
                f.write("Object type {0} has no 'validate_child_name' method\n".format(self.parent.reltype))
            if Settings.is_debug():
                show_error(
                    NameError("parent obj '{0}' does not have validate_child_name".format(self.parent))
                )
            self.name = name
            info_block("Named '{0}'".format(name))
        



    def get_path(self, filename=None, extension="obj"):
        """
        get path of this object's files, or path in same dir of 'filename'.
        extension: "obj" for obj, anything else for .wav
        """
        if filename is None:
            filename = self.name
        path = join_path(self.path, filename)
        if extension == "obj":
            path += "." + self.datafile_extension
        else:
            path += ".wav"
        return path


    def save_metadata(self):
        """
        define parse_write_meta(dict: attrs) to define which attrs to write
        """
        from src.project_loader import RelTypeEncoder
        info_block("saving '{0}' metadata...".format(self.name))
        attrs = {k:v for k,v in vars(self).items()}
        del attrs["method_data_by_category"]
        attrs["__module__"] = self.__class__.__module__
        attrs["__class__"] = self.__class__.__name__
        try:
            attrs = self.parse_write_meta(attrs)
        except AttributeError:
            pass
        fullpath = join_path(self.path, self.get_data_filename() + "." + self.datafile_extension)
        # RelTypeEncoder found in object_loading
        with open(fullpath, 'w') as f:
            json.dump(attrs, f, cls=RelTypeEncoder, indent=2)


    def save_audio(self):
        """
        base wav audio saving
        """
        info_block("saving '{0}' audio...".format(self.name))
        os.makedirs(self.path, exist_ok=True)
        outfile = join_path(self.path, self.get_data_filename() + ".wav")
        try:
            rate = int(self.rate.to_rate().magnitude)
        except AttributeError:
            rate = int(rate)
        sf.write(outfile, self.arr, rate)



class RelativismPublicObject(RelativismObject):
    """
    implements methods for showing public process methods.
    use getitem to get method by str.
    inner classes: MethodData, ArgData
    """


    def __init__(self, 
            rel_id=None, reltype=None, name=None, 
            path=None, parent=None, obj=None):

        super().__init__(rel_id=rel_id, reltype=reltype, name=name, path=path, parent=parent)

        if obj is None:
            obj = self
        if isinstance(obj, type):
            obj_class = obj
        else:
            obj_class = obj.__class__

        self.method_data_by_category = {}
        method_strs = [func for func in dir(obj_class) if callable(getattr(obj, func))]
        public_method_strs = []
        for m in method_strs:
            method = getattr(obj, m)
            if is_public_process(method):
                public_method_strs.append(m)
        for m in public_method_strs:
            m_data = RelativismPublicObject.MethodData(self, obj, m)
            try:
                self.method_data_by_category[m_data.category][m_data.method_name] = m_data
            except KeyError:
                self.method_data_by_category[m_data.category] = {m_data.method_name : m_data}



    def get_method(self, arg):
        """
        get public_process method
        """
        for i in self.method_data_by_category.items():
            try:
                return i[1][arg]
            except KeyError:
                pass
        raise KeyError


    @public_process
    def options(self):
        """
        cat: info
        desc: list all process options that can be run on this object (shortcut 'o')
        """
        print("")
        info_block("# {Category} #", indent=2)
        info_line("- {Process}")
        info_line("{arguments in order, optional if in [square brackets]}", indent=8)
        nl()
        methods = {}
        for i in self.method_data_by_category.items():
            info_line(str(i[0]).upper(), indent=2)
            for j in i[1].items():
                methods[j[0]] = j[1]
        meth_list = list(methods)
        meth_list.sort()
        for i in meth_list:
            methods[i].display()
        
    @public_process
    def quit(self):
        """
        cat: save
        desc: quit (shortcut 'q')
        """


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
