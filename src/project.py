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

    def __init__(self,
            name=None,
            rel_id=None,
            path=None,
            rate=None,
            children=None):
        
        # super sets rel_id, name, path
        super().__init__(rel_id, name, path)
        Project._instance = self
        self.reltype = "Project"
        if name is None:
            self.rename()

        self.path = path
        if path is None:
            p("Select a location for this project (folder will " + \
                "be created within selected location to house project files)")
            self.path = input_dir().append(self.get_data_dirname())
            makepath(self.path)

        self.children = []
        self.rate = rate
        # self.bpm_controller = "______" #TODO
        self.mix = None


    def __repr__(self):
        raise NotImplementedError

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



    @public_process
    def save(self, silent=False):
        """
        cat: save
        desc: save data
        """
        if not isinstance(silent, bool):
            silent = False
        self.save_metadata()
        for child in self.children:
            child.save()


    def parse_write_meta(self, dct):
        del dct['mix']
        return dct

    def make(self):
        recs = []
        for i in self.children:
            if issubclass(i, Recording):
                recs.append(i)
            elif issubclass(i, Sampler):
                recs.append(i.generate())
        mixed = mix_multiple(recs, name=self.name + "-mix")
        self.mix = mixed
    

    @public_process
    def playback(self, duration=0, start=0):
        """
        cat: info
        desc: mix and playback the whole project
        """
        self.make()
        self.mix.playback(duration, start)
    

    @public_process
    def list_children(self):
        """
        cat: info
        """
        info_title("Children in '{0}':".format(self.name))
        children = ["{0} ({1})".format(i.name, i.reltype) for i in self.children]
        if len(children) == 0:
            info_list("(empty)")
        else:
            info_list(children)


    @public_process
    def process_child(self, child_name=None):
        """
        cat: edit
        desc: edit a child member of this object
        args:
            [child_name: name of child to edit, omit to list children]
        """
        if child_name is None:
            self.list_children()
            child_name = inpt("name")
        else:
            child_name = inpt_validate(child_name, "name")
        child = None
        for i in self.children:
            if i.name == child_name:
                if child is not None:
                    raise UnexpectedIssue("Multiple children with name {0}".format(child_name))
                child = i
        process(i)
    

    @public_process
    def add_sampler(self):
        """
        desc: add a new sampler object
        """
        sampler = Sampler(parent=self)
        self.children.append(sampler)


    @public_process
    def add_recording(self):
        self.children.append(Recording(parent=self))



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
