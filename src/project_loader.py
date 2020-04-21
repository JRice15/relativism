import importlib

from src.data_types import *
from src.rel_objects import RelativismSavedObj, RelativismObject, RelativismContainer
from src.path import join_path, split_path
from src.globals import RelGlobals, Settings
from src.output_and_prompting import section_head



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
        path = join_path(directory, filename + "." + RelativismSavedObj.datafile_extension)

        with open(path, "r") as f:
            attrs = json.load(f, object_hook=self._decoder)

        self.current_path = prev_path
        mod = importlib.import_module(attrs.pop("__module__"))
        obj_class = getattr(mod, attrs.pop("__class__"))

        obj = obj_class(**attrs)
        for i in self.need_parent:
            i.parent = obj
        self.need_parent = []

        return obj


    def _decoder(self, dct):
        """
        for loading objects from files. See RelTypeEncoder
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
            if val.startswith("<PINTQUANT>"):
                val = re.sub("<PINTQUANT>", "", val)
                return Units.new(val)

            elif val.startswith("<RELATIVISM-PROGRAM>"):
                return RelGlobals.get_rel_instance()

            elif val.startswith("<RELOBJFILE>"):
                val = re.sub("<RELOBJFILE>", "", val)
                obj = self.load(val, join_path(self.current_path, val, is_dir=True))
                self.need_parent.append(obj)
                return obj
            
            elif val.startswith("<RELSET>"):
                filename = re.sub("<RELSET>", "", val)
                with open(filename + "." + RelativismContainer.setfile_extension, "r") as f:
                    data = f.readlines()
                mod_name = data.pop(0).strip()
                clss_name = data.pop(0).strip()
                mod = importlib.import_module(mod_name)
                clss = getattr(mod, clss_name)

                val = json.loads("\n".join(data))
                if isinstance(val, dict):
                    for k,v in val.items():
                        val[k] = clss.load(clss, v)
                elif isinstance(val, (list, tuple)):
                    for i in range(len(val)):
                        val[i] = clss.load(clss, val[i])
                else:
                    raise UnexpectedIssue("this really shouldnt happen")

            elif val.startswith("<RELOBJ>"):
                val = re.sub("<RELOBJ>", "", val)
                ind = val.index(";")
                class_data, val = val[:ind], val[ind+1:]
                mod_name, clss_name = class_data.split(",")
                mod = importlib.import_module(mod_name)
                clss = getattr(mod, clss_name)
                val = json.loads(val)
                return clss.load(clss, val)

        return val


class RelTypeEncoder(json.JSONEncoder):
    """
    for saving objects to files. project_loader.ProjectLoader._decoder is inverse
    """

    def default(self, obj):
        if isinstance(obj, Units._reg.Quantity):
            return "<PINTQUANT>" + str(obj)

        elif isinstance(obj, RelativismObject):

            if isinstance(obj, RelativismSavedObj):
                return "<RELOBJFILE>" + obj.file_ref_repr()

            elif isinstance(obj, RelativismContainer):
                return "<RELOBJ>" + obj.file_ref_repr()

            # RELSET handled by parse_container_obj_sts below            

        return json.JSONEncoder.default(self, obj)

    @staticmethod
    def parse_container_obj_sets(attrs, save_dir):
        """
        parse sets of container objects into a more compact form
        """
        for name,attr in attrs.items():
            first_val = None
            new_attr = None

            if isinstance(attr, dict) and len(attr) > 1:
                first_val = list(attr.values())[0]
                if isinstance(first_val, RelativismContainer) and \
                    all([type(v) == type(first_val) for v in attr.values()]
                ):
                    new_attr = {k:v.file_ref_data() for k,v in attr.items()}

            elif isinstance(attr, (list, tuple)) and len(attr) > 1:

                first_val = attr[0]
                if isinstance(first_val, RelativismContainer) and \
                    all([type(v) == type(first_val) for v in attr]
                ):
                    new_attr = [v.file_ref_data() for v in attr]

            if new_attr is not None:
                filename = first_val.get_setfile_fullpath(name, save_dir)
                with open(filename, "w") as fp:
                    fp.write(first_val.__class__.__module__ + "\n")
                    fp.write(first_val.__class__.__name__ + "\n")
                    json.dump(new_attr, fp=fp)
                attrs[name] = "<RELSET>{0}".format(first_val.get_set_filename(name))
        
        return attrs


