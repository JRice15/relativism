
from src.data_types import *
from src.recording_obj import *
from src.generators import *
from src.recording_obj import *
from src.integraters import *
from src.sampler import *



"""

"""


class RelTypeEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Units._reg.Quantity):
            return "<PINTQUANT>" + str(obj)

        elif isinstance(obj, RelativismObject):
            return "<REL-{0}>".format(obj.reltype) + ""

        else:
            return json.JSONEncoder.default(self, obj)


def RelTypeDecoder(dct):

    for k,v in dct.items():

        if "<PINTQUANT>" in str(v):
            v = re.sub("<PINTQUANT>", "", v)
            dct[k] = Units.new(v)

    return dct






class ProjectLoader:

    _obj_map = {}

    def __init__(self, proj_filename):
        


    def load(filename, directory=None):
        """
        load and return object from a file
        """
        path = parse_path(filename, directory) + RelativismObject._rel_obj_extension
        with open(path, "r") as f:
            attrs = json.load(f, object_hook=RelTypeDecoder)
        mod = importlib.import_module(attrs.pop("__module__"))
        obj_class = getattr(mod, attrs.pop("__class__"))
        return obj_class(**attrs)

    @staticmethod
    def is_obj_present(self, obj_id):
        return (obj_id in ProjectLoader._obj_map) and (ProjectLoader._obj_map[obj_id] != None)
    
    @staticmethod
    def get_obj(self, obj_id):
        return ProjectLoader._obj_map[obj_id]
    
    @staticmethod
    def set_obj(self, obj_id, obj):
        if self.is_obj_present(obj_id):
            raise KeyError("ProjectDirectory already has object with id '{0}'".format(obj_id))
        ProjectLoader._obj_map[obj_id] = obj




class Project(RelativismPublicObject):
    """
    """

    # global access for the current instance
    _instance = None

    TESTRATE = Units.rate(44100)
    TESTBPM = Units.bpm(120)

    def __init__(self, name, directory, rate, obj_map):
        """
        """
        Project._instance = self
        self.name = name
        self.reltype = 'Project'
        self.directory = directory
        self.recs = {}
        self.rate = rate
        self.bpm_controller = "______" #TODO
        self.obj_map = obj_map




    @staticmethod
    def get_rate():
        return Project.TESTRATE
        return Project._instance.rate

    @staticmethod
    def get_bpm(context=None):
        return Project.TESTBPM
        return Project._instance.bpm_controller.get_bpm(context)



    def create_sampler(self):
        """
        create a new sampler object
        """
        print("* Initializing sampler")
        proj_name, proj_dir, open_mode = namepath_init("project")
        if open_mode == "c":
            smp = Sampler(proj_name, proj_dir)
        else:
            # read data of project from file of some sort
            pass


    def update_name(self, obj, old_name, new_name):
        """
        """
        pass





def create_project():
    """
    Main project interface
    """
    print("* Initializing Project")
    proj_name, proj_dir, open_mode = namepath_init("project")
    if open_mode == "c":
        proj = Project(proj_name, proj_dir)
    else:
        # read data of project from file of some sort
        pass







def main_master():
    """
    """

    create_project()

    






def help_desk():
    """
    welcome to the help desk, how may we be of service?
    """





if __name__ == "__main__":
    main_master()
