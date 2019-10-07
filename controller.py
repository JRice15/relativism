from object_data import *
from input_processing import *
from output_and_prompting import *
import abc

class ControllerNode:

    def __init__(self, sample_ind, beatsec, value, change_type):
        self.sample_ind = sample_ind
        self.beatsec = beatsec
        self.value = value
        self.change_type = change_type


class Controller(RelativismPublicObject, abc.ABC):
    """
    for controlling an attribute (pan, volume, bpm, etc.) over time.
    abstract methods 'validate_value' and 'apply'.
    call 'edit' to change markers
    """

    valid_change_types = ('hard', 'linear', 'smooth')
    valid_edit_types = {
        'add': ['add'],
        'del': ['delete', 'del', 'remove', 'rm'],
        'view': ['view', 'show']
    }

    def __init__(self, rate, _type=None):
        super().__init__()
        self.rate = rate
        self.type = _type
        self.markers = {} # key: samps; value: ControllerNode
    

    def validate_edit_type(self, edit_type):
        change_type = inpt_process(change_type, 'alphanum')
        for t in self.valid_edit_types.values:
            if change_type in t:
                return change_type
        err_mess("invalid edit type")
        p("Select one of: {0}".format(" ".join(self.valid_edit_types)))
        change_type = inpt('alphanum')
        self.validate_change_type(change_type)

    def validate_change_type(self, change_type):
        change_type = inpt_process(change_type, 'alphanum')
        if change_type in self.valid_change_types:
            return change_type
        else:
            err_mess("invalid change type")
            p("Select one of: {0}".format(" ".join(self.valid_change_types)))
            change_type = inpt('alphanum')
            self.validate_change_type(change_type)

    @abc.abstractmethod
    def validate_value(self, value):
        """
        validate format of input value that is being controlled
        """
        ...

    @abc.abstractmethod
    def apply(self, rec_arr):
        """
        apply controller effect to rec_arr
        """
        ...


    @public_process
    def edit(self, edit_type, beatsec, value=None, change_type="hard"):
        """
        
        """
        info_block("Enter commands as <edit-type> <beats/secs> <value> <change-type>")
        while True:

        edit_type = self.valid_edit_types(edit_type)
        beatsec = inpt_process(beatsec, 'beat')
        sample_ind = samps(beatsec, self.rate)
        if edit_type in self.valid_edit_types['del']:
            


        value = self.validate_value(value)
        change_type = self.validate_change_type(change_type)



        self.markers[sample_ind] = ControllerNode(sample_ind, beatsec, value, change_type)




class VolumeController(Controller):

