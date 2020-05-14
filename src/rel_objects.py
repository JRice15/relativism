
import abc
import json
import os
import random as rd
import re

import soundfile as sf

from src.data_types import *
from src.errors import *
from src.globals import RelGlobals, Settings
from src.input_processing import inpt, inpt_validate, input_dir, input_file
from src.method_ops import (ArgData, Category, RelData, _ClsRelData,
                            add_reldata, add_reldata_arg, get_reldata,
                            get_wrap_all_encloser, has_aliases,
                            is_public_process, is_rel_wrap_all, public_process,
                            rel_wrap)
from src.output_and_prompting import (critical_err_mess, err_mess, info_block,
                                      info_line, info_list, info_title,
                                      log_err, nl, p, section_head, show_error,
                                      style)
from src.path import join_path, split_path


class RelObject(abc.ABC):
    """
    base rel object class
    """

    def __init__(self, **kwargs):
        super().__init__()
        for k,v in kwargs.items():
            setattr(self, k, v)
        if is_rel_wrap_all(self):
            self._do_wrap_all()

    def _do_wrap_all(self):
        """
        wrapping
        """
        encloser = get_wrap_all_encloser(self)
        for attr in dir(self):
            if "__" not in attr:
                if is_public_process(getattr(self, attr)):
                    print("a", type(getattr(self, attr)), getattr(self,attr).__name__)
                    new_val = rel_wrap(encloser)(getattr(self, attr))
                    setattr(self, attr, new_val)

    @abc.abstractmethod
    def file_ref_repr(self):
        """
        how obj is referenced in other object's files
        """
        ...



class RelContainer(RelObject):
    """
    class for objects that are not saved to a file but directly as strings 
    in other files
    implement:
        load(self_clss, data) # staticmethod
        file_ref_data(self)
    """

    setfile_extension = "rel-set"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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




class RelSavedObj(RelObject):
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

    def __init__(self, rel_id, reltype, name, path, parent, **kwargs):
        super().__init__(parent=parent, rel_id=rel_id, reltype=reltype, 
            name=name, path=path, **kwargs)
        self.parent = parent
        self.reltype = reltype
        self.name = name
        self.path = path # path not including object's own directory
        self.rel_id = rel_id if rel_id is not None else RelGlobals.get_next_id()
        if path is not None and reltype != "Program":
            os.makedirs(self.get_data_dir(), exist_ok=True)

    def __repr__(self):
        string = "'{0}'. {1} object".format(self.name, self.reltype)
        if hasattr(self, "source_block"):
            string += " from"
            for key, val in self.source_block.items():
                string += " {0}: {1};".format(key, val)
        return string

    def get_data_dir(self):
        """
        get the directory of this object's files
        """
        return join_path(self.path, self.get_data_filename(), is_dir=True)

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
        return join_path(self.get_data_dir(), self.get_data_filename(), ext=self.datafile_extension)

    def get_path(self, filename, extension="obj"):
        """
        get path to a file or dir 
        args:
            extension: "obj" for datafile_extension, "dir" for directory, or "wav"
        """
        is_dir = False
        if extension == "obj":
            extension = self.datafile_extension
        elif extension in ("wav",):
            pass
        elif extension == "dir":
            is_dir = True
            extension = None
        else:
            raise UnexpectedIssue("Unrecognized extension '{0}'. Add it in RelObject.get_path".format(extension))

        path = join_path(self.get_data_dir(), filename, ext=extension, is_dir=is_dir)
        return path

    @public_process
    def rename(self, name=None):
        """
        dev: call this method via super, and implement renaming of files other than 
        datafile and its self.path directory
        """
        old_name = self.name
        if old_name is not None:
            old_data_dir = self.get_data_dir()
            old_datafile_name = self.get_data_filename()

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
                try:
                    log_err("Parent object type {0} has no 'validate_child_name' method".format(self.parent.reltype))
                except AttributeError:
                    log_err("Parent object '{0}' of '{1}' has no 'validate_child_name' method".format(self.parent, self))
            self.name = name
            info_block("Named '{0}'".format(name))
        
        # if actual renaming and not an initial naming
        if old_name is not None:
            new_data_dir = self.get_data_dir()
            # rename datafile
            old_datafile = join_path(old_data_dir, old_datafile_name, ext=self.datafile_extension)
            new_datafile = self.get_datafile_fullpath()
            os.rename(old_datafile, new_datafile)
            # rename dir
            os.rename(old_data_dir, new_data_dir)


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

        # must copy list, otherwise we will edit this object's __dict__
        attrs = {k:v for k,v in vars(self).items()}
        attrs = self.parse_write_meta(attrs)
        try:
            del attrs["_rel_data"]
        except KeyError:
            pass
        attrs["__module__"] = self.__class__.__module__
        attrs["__class__"] = self.__class__.__name__

        from src.project_loader import RelTypeEncoder
        attrs = RelTypeEncoder.parse_container_obj_sets(attrs, self.get_data_dir())

        fullpath = self.get_datafile_fullpath()

        with open(fullpath, 'w') as f:
            json.dump(attrs, fp=f, cls=RelTypeEncoder, indent=2)

    def parse_write_meta(self, attrs):
        """
        override when applicable. remove attrs that shouldnt 
        be json encoded to file (e.g. audio data) by overriding this method
        """
        return attrs

    def file_ref_repr(self):
        """
        don't override. how this object is referenced in other objects json data files
        """
        return self.get_data_filename()


class RelAudioObj(RelSavedObj):
    """
    object with audio
    """

    def __init__(self, arr=None, rate=None, rel_id=None, reltype=None, name=None,
            path=None, parent=None, **kwargs):
        super().__init__(rel_id=rel_id, reltype=reltype, name=name, path=path,
            parent=parent, **kwargs)

        self.arr = arr
        self.rate = rate if rate is not None else None

    def get_audiofile_fullpath(self):
        """
        datafile path, but wav extension instead
        """
        return self.get_path(self.get_data_filename(), extension="wav")

    @public_process
    def save(self):
        """
        cat: save
        dev: default save method, just calls save_metadata. override for additional saving
        """
        self.save_metadata()
        self.save_audio()

    def parse_write_meta(self, attrs):
        """
        override with super() call when applicable. remove attrs that shouldnt 
        be json encoded to file (e.g. audio data) by overriding this method
        """
        del attrs['arr']
        attrs["file"] = self.get_audiofile_fullpath()
        return attrs

    def save_audio(self):
        """
        base wav audio saving. requires 'rate' and 'arr' attributes
        """
        info_block("saving audio of {0} '{1}'...".format(self.reltype, self.name))
        if self.arr is None:
            info_line("no audio to save...")
        else:
            sf.write(self.get_audiofile_fullpath(), self.arr, self.rate.magnitude)


class RelPublicObj(RelObject):
    """
    methods to implement on classes that inherit from this:
        save (if any additional file saving needed beyond save_metadata)
        parse_write_meta (for save_metadata)
        rename (that calls super, and only handles renaming files)
        file_ref_repr (if not the standard name.reltype)
        validate_child_name
        pre_process and post_process
    """

    def __init__(self, name, reltype, mode, **kwargs):

        super().__init__(name=name, reltype=reltype, **kwargs)

        if mode == "create":
            section_head("Initializing {0}".format(reltype))
        elif mode == "load":
            info_line("Loading {0} '{1}'".format(reltype, name))
        else:
            raise UnexpectedIssue("Unknown mode '{0}'".format(mode))

        self.name = name
        self.reltype = reltype

        self._do_aliases()
        self._do_props()


    def _do_props(self):
        from src.property import RelProperty
        props = [i for i in dir(self) if isinstance(getattr(self, i), RelProperty)]
        if len(props) > 0:

            # extra process to handle properties
            @public_process
            def edit_property(self, prop_name):
                """
                cat: edit
                """
                if prop_name not in props:
                    raise NoSuchProcess("Property '{0}' does not exist")
                # RelProp.process() method
                getattr(self, prop_name).process()

            self.edit_property = edit_property
            propstr = specialjoin(props, "', '", "', or '")
            desc = "edit a property. One of the following: '" + propstr + "'"
            add_reldata(self.edit_property, "desc", desc)
            add_reldata(self.edit_property, "category", Category.EDIT)
            add_reldata_arg(self.edit_property, "name: name of the property to edit")


    def _do_aliases(self):
        """
        add all aliases
        """
        if not hasattr(self, "_rel_data"):
            self._rel_data = _ClsRelData()
        alias_map = self._rel_data.alias_map
        # copy to prevent modifying what we iterate over
        dct = {k:getattr(self, k) for k in dir(self)}
        for meth_name,method in dct.items():
            if has_aliases(method):
                for alias in get_reldata(method, "aliases"):
                    if hasattr(self, alias) or alias in alias_map:
                        raise NameError("Class '{0}' already has method/name '{1}' that cannot be aliases".format(
                            self.__class__.__name__, alias))
                    alias_map[alias] = meth_name


    def get_process(self, name):
        """
        handles getting aliases too
        """
        # endswith to handle namespaced attr names
        if hasattr(self, name):
            return getattr(self, name)
        try:
            real_name = self._rel_data.alias_map[name]
            return getattr(self, real_name)
        except:
            raise AttributeError("Object '{0}' has not attribute '{1}'".format(self, name))


    def get_all_public_methods(self):
        """
        get the names of all public methods
        """
        return [func for func in dir(self) if is_public_process(getattr(self, func))]

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

        meths = {}
        for i in dir(self):
            mth = getattr(self, i)
            if is_public_process(mth):
                cat = get_reldata(mth, "category")
                try:
                    meths[cat].append(mth)
                except KeyError:
                    meths[cat] = [mth]

        categories = list(meths.keys())
        categories.sort(key=lambda x: x.value)
        for cat in categories:
            with style("cyan"):
                # category.value is the display version of the category
                info_line(cat.value.upper(), indent=2)
            for method in meths[cat]:
                method._rel_data.display()


    @public_process
    def quit(self):
        """
        cat: save
        desc: exit to parent process (shortcut 'q')
        dev: this is handled in input_processing
        """
        raise Cancel





class SourceInfo(RelObject):
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
