import importlib

from src.data_types import *
from src.object_data import RelativismObject
from src.path import join_path, split_path
from src.globals import RelGlobals, Settings
from src.output_and_prompting import section_head


class RelTypeEncoder(json.JSONEncoder):
    """
    for saving objects to files. project_loader.ProjectLoader._decoder is inverse
    """

    def default(self, obj):
        if isinstance(obj, Units._reg.Quantity):
            return "<PINTQUANT>" + str(obj)

        elif isinstance(obj, RelativismObject):

            from src.relativism import Relativism
            if isinstance(obj, Relativism):
                return "<RELATIVISM-PROGRAM>"

            return "<RELOBJ>" + obj.get_data_filename()

        else:
            return json.JSONEncoder.default(self, obj)



class ProjectLoader:

    def __init__(self, filename, path, rel_instance):
        section_head("Loading '{0}'".format(filename))
        self.proj_file_dir = path
        self.current_path = path
        self.filename = filename
        self.rel_instance = rel_instance

        # because leaf children loaded before the root, need to add parents retroactively
        self.need_parent = []
        self.project = None

    def get_proj(self):
        self.project = self.load(self.filename, self.current_path)
        self.project.parent = self.rel_instance
        return self.project

    def load(self, filename, directory=""):
        """
        load and return object from a file
        """
        prev_path = self.current_path
        self.current_path = directory
        path = join_path(directory, filename + "." + RelativismObject.datafile_extension)

        with open(path, "r") as f:
            attrs = json.load(f, object_hook=self._decoder)

        mod = importlib.import_module(attrs.pop("__module__"))
        obj_class = getattr(mod, attrs.pop("__class__"))
        self.current_path = prev_path

        obj = obj_class(**attrs)
        print("attrs:", attrs)
        for i in self.need_parent:
            i.parent = obj
        self.need_parent = []

        return obj


    def _decoder(self, dct):
        """
        for loading objects from files. See object_data.RelTypeEncoder
        """

        for key, val in dct.items():

            if key != "parent":
                dct[key] = self._decode_one(val)

        return dct
    
    def _decode_one(self, val):

        if isinstance(val, (list, tuple)):
            for i in range(len(val)):
                val[i] = self._decode_one(val[i])
            return val

        elif isinstance(val, dict):
            return self._decoder(val)

        elif isinstance(val, str):
            if "<PINTQUANT>" in str(val):
                val = re.sub("<PINTQUANT>", "", val)
                return Units.new(val)

            elif "<RELATIVISM-PROGRAM>" in str(val):
                return RelGlobals.get_rel_instance()

            elif "<RELOBJ>" in str(val):
                val = re.sub("<RELOBJ>", "", val)
                obj = self.load(val, join_path(self.current_path, val, is_dir=True))
                self.need_parent.append(obj)
                return obj
        
        return val
