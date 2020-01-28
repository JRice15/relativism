"""
project class
"""


from src.data_types import *
from src.recording_obj import *
from src.generators import *
from src.recording_obj import *
from src.integraters import *
from src.sampler import *
from src.object_loading import *





class Project(RelativismPublicObject):
    """
    """

    # global access for the current instance
    _instance = None

    TESTRATE = Units.rate(44100)
    TESTBPM = Units.bpm(120)

    def __init__(self, name=None, rel_id=None, path=None, rate=None):
        """
        """
        super().__init__(rel_id, name, path)
        Project._instance = self
        self.name = name
        self.reltype = 'Project'
        self.path = path
        self.recs = {}
        self.rate = rate
        # self.bpm_controller = "______" #TODO


    @staticmethod
    def get_instance():
        return Project._instance

    @staticmethod
    def get_proj_path():
        return Project._instance.path

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


    @public_process
    def save(self, silent=False):
        """
        cat: save
        desc: save data
        """
        if not isinstance(silent, bool):
            silent = False
        self.save_metadata(self.name, self.path)
        for i,rec in self.recs.items():
            rec.save()




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
