from src.data_types import *
import importlib
from src.paths import *



class RelTypeEncoder(json.JSONEncoder):
    """
    for saving objects to files. See object_loading.ProjectLoader._decoder
    """

    def default(self, obj):
        if isinstance(obj, Units._reg.Quantity):
            return "<PINTQUANT>" + str(obj)

        elif isinstance(obj, RelativismObject):
            return "<RELOBJ>" + obj.get_dirname()
        
        elif isinstance(obj, Path):
            return "<PATH>" + str(obj)

        else:
            return json.JSONEncoder.default(self, obj)





class ProjectLoader:

    def __init__(self, filename, path):
        self.proj_file_path = path
        self.current_path = path
        self.project = self.load(filename, path)


    def _decoder(self, dct):
        """
        for loading objects from files. See object_data.RelTypeEncoder
        """

        for key, val in dct.items():

            if "<PINTQUANT>" in str(val):
                val = re.sub("<PINTQUANT>", "", val)
                dct[key] = Units.new(val)

            elif "<RELOBJ>" in str(val):
                val = re.sub("<RELOBJ>", "", val)
                dct[key] = self.load(val, self.current_path.append(val))
            
            elif "<PATH>" in str(val):
                val = re.sub("<PATH>", "", val)
                dct[key] = Path(val)

        return dct

    def load(self, filename, directory=Path()):
        """
        load and return object from a file
        """
        prev_path = self.current_path
        self.current_path = directory
        path = Path(directory, filename, "relativism-obj")
        with open(path.fullpath(), "r") as f:
            attrs = json.load(f, object_hook=self._decoder)
        mod = importlib.import_module(attrs.pop("__module__"))
        obj_class = getattr(mod, attrs.pop("__class__"))
        self.current_path = prev_path
        return obj_class(**attrs)


    # _obj_map = {}

    # @staticmethod
    # def is_obj_present(self, obj_name):
    #     return (obj_name in ProjectLoader._obj_map) and (ProjectLoader._obj_map[obj_name] != None)
    
    # @staticmethod
    # def get_obj(self, obj_name):
    #     return ProjectLoader._obj_map[obj_name]
    
    # @staticmethod
    # def set_obj(self, obj_name, obj):
    #     if self.is_obj_present(obj_name):
    #         raise KeyError("ProjectLoader already has object with id '{0}'".format(obj_name))
    #     ProjectLoader._obj_map[obj_name] = obj


