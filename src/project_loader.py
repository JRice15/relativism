from src.data_types import *
import importlib
from src.path import Path, makepath
from src.object_data import RelativismObject
from src.rel_global import RelGlobal


class RelTypeEncoder(json.JSONEncoder):
    """
    for saving objects to files. See object_loading.ProjectLoader._decoder
    """

    def default(self, obj):
        if isinstance(obj, Units._reg.Quantity):
            return "<PINTQUANT>" + str(obj)

        elif isinstance(obj, RelativismObject):

            from src.relativism import Relativism
            if isinstance(obj, Relativism):
                return "<RELATIVISM-PROGRAM>"
            return "<RELOBJ>" + re.sub(r"/", "", obj.get_data_dirname().fullpath())
        
        elif isinstance(obj, Path):
            return "<PATH>" + str(obj)

        else:
            return json.JSONEncoder.default(self, obj)



class ProjectLoader:

    def __init__(self, filename, path, rel_instance):
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

    def load(self, filename, directory=None):
        """
        load and return object from a file
        """
        if directory is None:
            directory = Path()
        prev_path = self.current_path
        self.current_path = directory
        path = Path(directory, filename, "relativism-obj")

        with open(path.fullpath(), "r") as f:
            attrs = json.load(f, object_hook=self._decoder)

        mod = importlib.import_module(attrs.pop("__module__"))
        obj_class = getattr(mod, attrs.pop("__class__"))
        self.current_path = prev_path

        obj = obj_class(**attrs)
        for i in self.need_parent:
            i.parent = obj
        self.need_parent = []

        return obj


    def _decoder(self, dct):
        """
        for loading objects from files. See object_data.RelTypeEncoder
        """

        print(dct)
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
                return RelGlobal.get_instance()

            elif "<RELOBJ>" in str(val):
                val = re.sub("<RELOBJ>", "", val)
                obj = self.load(val, self.current_path.append_dir(val))
                self.need_parent.append(obj)
                return obj
            
            elif "<PATH>" in str(val):
                val = re.sub("<PATH>", "", val)
                return Path(fullpath=val)
        
        return val

