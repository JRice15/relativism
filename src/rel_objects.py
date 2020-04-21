
import json
import os
import random as rd
import re
import abc

import soundfile as sf

from src.data_types import *
from src.globals import RelGlobals, Settings
from src.input_processing import inpt, inpt_validate, input_dir, input_file
from src.output_and_prompting import (critical_err_mess, err_mess, info_block,
                                      info_line, info_list, info_title, nl, p,
                                      section_head, show_error, style, log_err)
from src.path import join_path, split_path
from src.errors import *



class RelativismObject(abc.ABC):
    """
    base rel object class
    """

    def __init__(self, parent):
        self.parent = parent

    @abc.abstractmethod
    def file_ref_repr(self):
        """
        how obj is referenced in other object's files
        """
        ...



class RelativismContainer(RelativismObject):
    """
    class for objects that are not saved to a file but directly as strings 
    in other files
    implement:
        load
        file_ref_data
    """

    setfile_extension = "rel-set"

    def __init__(self, parent):
        super().__init__(parent=parent)

    def class_data_repr(self):
        mod = self.__class__.__module__
        clss = self.__class__.__name__
        return "{0},{1}".format(mod, clss)

    def file_ref_repr(self):
        """
        don't override. string repr for standalone file references
        """
        data_str = json.dumps(self.file_ref_data(), separators=(",",":"))
        return self.class_data_repr() + ";" + data_str

    def get_set_filename(self, attr_name):
        return attr_name + "." + self.__class__.__name__

    def get_setfile_fullpath(self, attr_name, path):
        return join_path(path, self.get_set_filename(attr_name) + "." + self.setfile_extension)

    @abc.abstractmethod
    def file_ref_data(self):
        """
        data in primitive types form needed to restore obj with load()
        """
        ...

    @staticmethod
    @abc.abstractmethod
    def load(self_clss, data):
        """
        load object from data returned by file_ref_data
        """
        ...


class RelativismSavedObj(RelativismObject):
    """
    methods to implement on classes that inherit from this:
        save (if any additional file saving needed beyond save_metadata)
        parse_write_meta (for save_metadata)
        rename (that calls super, and only handles renaming files)
        file_ref_repr (if not the standard name.reltype)
        validate_child_name
        pre_process and post_process
    """

    datafile_extension = "rel-obj"

    def __init__(self, rel_id, reltype, name, path, parent):
        super().__init__(parent=parent)
        self.reltype = reltype
        self.name = name
        self.path = path # path including object's own directory
        self.rel_id = rel_id if rel_id is not None else RelGlobals.get_next_id()
        if path is not None and reltype != "Program":
            os.makedirs(self.path, exist_ok=True)

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

    def get_path(self, filename=None, extension="obj"):
        """
        get path of this object's files, or path in same dir of 'filename'.
        extension: "obj" for datafile_extension, anything else used as extension 
        with a dot
        """
        if filename is None:
            filename = self.name
        path = join_path(self.path, filename)
        if extension == "obj":
            path += "." + self.datafile_extension
        elif extension == "wav":
            path += ".wav"
        else:
            raise UnexpectedIssue("Unrecognized extension '{0}'. Add it in RelativismObject.get_path".format(extension))
        return path

    @public_process
    def rename(self, name=None):
        """
        dev: call this method via super, and implement renaming of files other than 
        datafile and its self.path directory
        """
        old_name = self.name

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
            if Settings.is_debug():
                show_error(
                    AttributeError("Parent obj '{0}' does not have validate_child_name".format(self.parent))
                )
            else:
                log_err("Parent object type {0} has no 'validate_child_name' method".format(self.parent.reltype))
            self.name = name
            info_block("Named '{0}'".format(name))
        
        # if actual renaming and not an initial naming
        if old_name is not None:
            new_path = join_path(self.parent.path, self.get_data_filename())
            # rename datafile
            os.rename(self.get_path(old_name), self.get_path())
            # rename dir
            os.rename(self.path, new_path)
            self.path = new_path

    @public_process
    def save(self):
        """
        cat: save
        dev: default save method, just calls save_metadata. override for additional saving
        """
        self.save_metadata()

    def save_metadata(self):
        """
        define parse_write_meta(dict: attrs) to define which attrs to write
        """
        info_block("saving {0} '{1}' metadata...".format(self.reltype, self.name))

        attrs = vars(self)
        del attrs["method_data_by_category"]
        attrs = self.parse_write_meta(attrs)
        attrs["__module__"] = self.__class__.__module__
        attrs["__class__"] = self.__class__.__name__

        from src.project_loader import RelTypeEncoder
        attrs = RelTypeEncoder.parse_container_obj_sets(attrs, self.path)

        fullpath = join_path(self.path, self.get_data_filename() + "." + self.datafile_extension)

        with open(fullpath, 'w') as f:
            json.dump(attrs, fp=f, cls=RelTypeEncoder, indent=2)

    def parse_write_meta(self, attrs):
        """
        remove attrs that shouldnt be json encoded to file (ex: audio data) by
        overriding this method
        """
        return attrs

    def save_audio(self):
        """
        base wav audio saving. requires 'rate' and 'arr' attributes
        """
        info_block("saving {0} '{1}' audio...".format(self.reltype, self.name))
        outfile = join_path(self.path, self.get_data_filename() + ".wav")
        sf.write(outfile, self.arr, self.rate.magnitude)

    def file_ref_repr(self):
        """
        how this object is referenced in other objects json data files
        """
        return self.get_data_filename()


class RelativismPublicObj(RelativismSavedObj):
    """
    methods to implement on classes that inherit from this:
        save (if any additional file saving needed beyond save_metadata)
        parse_write_meta (for save_metadata)
        rename (that calls super, and only handles renaming files)
        file_ref_repr (if not the standard name.reltype)
        validate_child_name
        pre_process and post_process
    """

    def __init__(self, rel_id, reltype, name, path, parent, mode):

        super().__init__(rel_id=rel_id, reltype=reltype, name=name, 
                        path=path, parent=parent)

        if mode == "create":
            section_head("Initializing {0}".format(reltype))
        elif mode == "load":
            info_line("Loading {0} '{1}'".format(reltype, name))
        else:
            raise UnexpectedIssue("Unknown mode '{0}'".format(mode))

        clss = self.__class__

        self.method_data_by_category = {}
        method_strs = [func for func in dir(clss) if callable(getattr(self, func))]
        public_method_strs = []
        for m in method_strs:
            method = getattr(self, m)
            if is_public_process(method):
                public_method_strs.append(m)
        for m in public_method_strs:
            m_data = RelativismPublicObj.MethodData(self, m)
            try:
                self.method_data_by_category[m_data.category][m_data.method_name] = m_data
            except KeyError:
                self.method_data_by_category[m_data.category] = {m_data.method_name : m_data}


    def get_method(self, method_name):
        """
        get public_process method
        """
        for i in self.method_data_by_category.items():
            try:
                return i[1][method_name]
            except KeyError:
                pass
        raise KeyError


    @public_process
    def options(self):
        """
        cat: info
        desc: list all process options that can be run on this object (shortcut 'o')
        """
        nl()
        with style("cyan"):
            info_block("{CATEGORY}", indent=2)
        info_line("- {Process}")
        info_line("{arguments in order, optional if in [square brackets]}", indent=8)
        nl()
        categories = list(self.method_data_by_category.keys())
        categories.sort()
        for cat in categories:
            with style("cyan"):
                info_line(str(cat).upper(), indent=2)
            for name, method in self.method_data_by_category[cat].items():
                if not method.is_alias:
                    method.display()

        
    @public_process
    def quit(self):
        """
        cat: save
        desc: exit to parent process (shortcut 'q')
        dev: this is handled in input_processing
        """
        raise Cancel


    class MethodData:

        def __init__(self, parent, method_name):
            """
            method: str
            """
            self.parent = parent
            self.method_name = method_name
            self.method_func = getattr(parent, method_name)
            self.is_alias = is_alias(self.method_func, self.method_name)

            self.category = None
            self.raw_category = None
            self.args = []
            self.desc = ""
            if not self.is_alias and hasattr(self.method_func, "__rel_aliases__"):
                self.aliases = self.method_func.__rel_aliases__
            else:
                self.aliases = None

            self.analayze_doc()
        

        def analayze_doc(self):
            doc = self.method_func.__doc__
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
                            elif title in ("args", "arguments", "arg"):
                                args_now = True
                        else:
                            arg_dt = RelativismPublicObj.ArgData(self, line)
                            self.args.append(arg_dt)
                    except:
                        err_mess("Error reading docstring method object data from method '" + self.method_name + ": " + str(line) + "'")
            
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
            """
            get the display version of the category
            """
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
            message = self.method_name.capitalize()
            message += ": " + self.desc
            if self.aliases is not None:
                message += " (alias"
                if len(self.aliases) > 1:
                    message += "es"
                message += ": '" + "', '".join(self.aliases) + "')"
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


