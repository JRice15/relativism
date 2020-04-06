"""
project class
"""


from src.data_types import *
from src.globals import RelGlobals, Settings
from src.input_processing import inpt, inpt_validate, input_dir, input_file, autofill
from src.integraters import concatenate, mix, mix_multiple
from src.object_data import (RelativismObject, RelativismPublicObject,
                             is_public_process, public_process)
from src.output_and_prompting import (critical_err_mess, err_mess, info_block,
                                      info_line, info_list, info_title, nl, p,
                                      section_head, show_error)
from src.path import join_path, split_path
from src.process import process
from src.project_loader import ProjectLoader
from src.recording_obj import Recording
from src.sampler import Sampler


class Project(RelativismPublicObject):
    """
    """

    # global access for the current instance
    _instance = None

    TESTBPM = Units.bpm(120)

    def __init__(self,
            parent=None,
            name=None,
            rel_id=None,
            mode="load",
            path=None,
            rate=None,
            reltype="Project",
            children=None
        ):
        
        super().__init__(rel_id=rel_id, reltype=reltype, name=name, 
            path=path, parent=parent, mode=mode)

        RelGlobals.set_project_instance(self)

        if name is None:
            self.rename()

        if path is None:
            p("Select a location for this project (folder will " + \
                "be created within selected location to house project files)")
            self.path = join_path(input_dir(), self.get_data_filename(), is_dir=True)
            os.makedirs(self.path, exist_ok=False)

        if children is None:
            children = []
        self.children = children
        self.rate = rate
        # self.bpm_controller = "______" #TODO
        self.arr = None

        if mode == "create":
            self.save()


    def __repr__(self):
        return "{0} '{1}', stored at: {2}. {3} direct children objects".format(
            self.reltype, self.name, self.path, len(self.children)
        )

    def validate_child_name(self, name):
        for c in self.children:
            if c.name == name:
                err_mess("Child with name '{0}' already exists!".format(name))
                return False
        return True

    @staticmethod
    def get_proj_path():
        return RelGlobals.get_project_instance().path

    @staticmethod
    def get_rate():
        return RelGlobals.get_project_instance().rate

    @staticmethod
    def get_bpm(context=None):
        return Project.TESTBPM
        return Project._instance.bpm_controller.get_bpm(context)

    @public_process
    def info(self):
        info_block("{0} '{1}'".format(self.reltype, self.name))
        info_line("Stored at '{0}'".format(self.path))
        info_line("Samplerate: {0}".format(self.rate))
        self.list_children()

    @public_process
    def set_bpm(self, bpm):
        #TODO
        raise NotImplementedError

    @public_process
    def save(self):
        """
        cat: save
        desc: save data
        """
        self.save_metadata()
        for child in self.children:
            child.save()

    def parse_write_meta(self, dct):
        del dct['mix']
        return dct

    def make(self):
        recs = []
        for i in self.children:
            if isinstance(i, Recording):
                recs.append(i)
            elif isinstance(i, Sampler):
                recs.append(i.generate())
            else:
                raise UnexpectedIssue("Unknown child type '{0}'".format(type(i)))
        mixed = mix_multiple(recs, name=self.name + "-mix")
        self.arr = mixed
    
    @public_process
    def playback(self, duration=0, start=0):
        """
        cat: info
        desc: mix and playback the whole project
        """
        self.make()
        self.arr.playback(duration, start)
    
    @public_process
    def list_children(self):
        """
        cat: info
        """
        info_block("Children in '{0}':".format(self.name))
        children = ["{0} ({1})".format(i.name, i.reltype) for i in self.children]
        info_list(children)

    @public_process
    def process_child(self, child_name=None):
        """
        cat: edit
        desc: edit a child member of this object
        args:
            [child_name: name of child to edit, omit to list children]
        """
        if len(self.children) == 0:
            err_mess("This Project has no children to process!")
        if child_name is None:
            self.list_children()
            p("Enter the name of the child you wish to edit")
            child_name = inpt("name")
        else:
            child_name = inpt_validate(child_name, "name")
        try:
            child_name = autofill(child_name, [i.name for i in self.children])
        except AutofillError:
            err_mess("Child name '{0}' not found".format(child_name))
            self.process_child()
            return
        child = None
        for i in self.children:
            if i.name == child_name:
                if child is not None:
                    raise UnexpectedIssue("Multiple children with name {0}".format(child_name))
                child = i
        try:
            process(child)
        except Cancel:
            child.save()

    def add_child(self, child):
        """
        backend of add_x processes
        """
        self.children.append(child)
        self.save_metadata()
        p("Process new {0} '{1}'? [y/n]".format(child.reltype, child.name))
        if inpt("y-n"):
            self.process_child(child.name)

    @public_process
    def add_sampler(self):
        """
        desc: add a new sampler object
        """
        self.add_child(
            Sampler(parent=self, mode="create")
        )

    @public_process
    def add_recording(self):
        """
        desc: create a new Recording from an audio file or live recording
        """
        self.add_child(
            Recording(parent=self, mode="create")
        )







def help_desk():
    """
    welcome to the help desk, how may we be of service?
    """


