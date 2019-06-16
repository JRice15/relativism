from recording_obj import *
from generators import *
from recording_obj import *
from integraters import *
from sampler import *




"""

"""






class Project:
    """
    """

    def __init__(self, name, directory):
        """
        """
        self.name = name
        self.dir = directory
        self.recs = {}


    def create_sampler(self):
        """
        create a new sampler object
        """
        print("* Initializing sampler")
        proj_name, proj_dir, open_mode = NameAndPath.namepath_init("project")
        if open_mode == "c":
            smp = Sampler(proj_name, proj_dir)
        else:
            # read data of project from file of some sort
            pass


    def update_name(self, obj, old_name, new_name):
        """
        """
        self.smps[new_name] = obj
        try:
            del self.smps[old_name]
        except:
            pass



def main_project():
    """
    Main project interface
    """
    print("* Initializing Project")
    proj_name, proj_dir, open_mode = NameAndPath.namepath_init("project")
    if open_mode == "c":
        proj = Project(proj_name, proj_dir)
    else:
        # read data of project from file of some sort
        pass







def main_all():
    """
    master main
    """

    #main_project()

    






def help_desk():
    """
    welcome to the help desk, how may we be of service?
    """





if __name__ == "__main__":
    main_all()
