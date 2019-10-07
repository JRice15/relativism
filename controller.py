from object_data import *
from input_processing import *
from output_and_prompting import *
import abc

class ControllerMarker:

    def __init__(self, sample_ind, beatsec, value, change_type):
        self.sample_ind = sample_ind
        self.beatsec = beatsec
        self.value = value
        self.change_type = change_type


    def __repr__(self):
        return "{0}: {1} ({2} change)".format(self.beatsec, self.value, self.change_type)


class Controller(abc.ABC):
    """
    for controlling an attribute (pan, volume, bpm, etc.) over time.
    abstract methods 'validate_value' and 'apply'.
    call 'edit' to change markers
    """

    valid_change_types = ('hard', 'linear', 'smooth')
    valid_edit_types = {
        'add': ['add'],
        'del': ['delete', 'del', 'remove', 'rm'],
        'view': ['view', 'show'],
        'move': ['mv', 'move']
    }
    edit_descriptions = {
        'add': "add <beat/sec> <value> <change-type, default 'hard'>",
        'del': 'del <beat/sec>',
        'view': 'view',
        'move': 'move <current beat/sec> <new beat/sec>'
    }

    def __init__(self, rate, _type):
        self.rate = rate
        self.type = _type
        self.markers = {} # key: samps; value: ControllerNode
    

    def display_markers(self):
        info_title("Controller for {0}".format(self.type))
        if len(self.markers) == 0:
            info_list("(empty)")
        for i in sorted(self.markers):
            info_list(self.markers[i])

    def validate_edit_type(self, edit_type):
        edit_type = inpt_process(edit_type, 'alphanum')
        for t in self.valid_edit_types.values():
            if edit_type in t:
                return edit_type
        err_mess("invalid edit type")
        p("Select one of: {0}".format(", ".join(self.valid_edit_types)))
        edit_type = inpt('alphanum')
        self.validate_edit_type(edit_type)

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


    def edit(self):
        """
        run edit loop. describe value parameters in public function that calls this one
        """
        info_title("Valid commands ('q' to quit, 'h' for help):")
        for i in self.valid_edit_types.keys():
            info_list(i + ": " + self.edit_descriptions[i])
        info_title("Valid change types are:")
        info_list(self.valid_change_types)
        while True:
            print("\n    : ", end="")
            command = inpt('split', split_modes=['alphanum', 'beat', 'stnd'], 
                help_callback=self.edit)
            edit_type = self.validate_edit_type(command[0])
            if edit_type in self.valid_edit_types['view']:
                self.display_markers()
                continue
            try:
                beatsec = inpt_process(command[1], 'beat')
            except IndexError:
                p("Choose a beat/sec for this marker to occur at")
                beatsec = inpt('beat')
            sample_ind = samps(beatsec, self.rate)
            if edit_type in self.valid_edit_types['del']:
                try:
                    del self.markers[sample_ind]
                except KeyError:
                    err_mess("No marker to delete at {0}".format(beatsec))
            elif edit_type in self.valid_edit_types['move']:
                try:
                    marker = self.markers[sample_ind]
                    try:
                        replace = self.markers[sample_ind]
                        info_line("Replacing marker {0}".format(replace.beatsec))
                    except KeyError:
                        pass
                    info_line("Moved marker from {0} to {1}".format(marker.beatsec, beatsec))
                    self.markers[sample_ind] = marker
                except KeyError:
                    err_mess("No marker to delete at {0}".format(beatsec))                  
            elif edit_type in self.valid_edit_types['add']:
                try:
                    value = self.validate_value(command[2])
                except IndexError:
                    p("Choose a value to add")
                    value = self.validate_value(inpt('stnd'))
                try:
                    change_type = self.validate_change_type(command[3])
                except IndexError:
                    change_type = 'hard'
                try:
                    replace = self.markers[sample_ind]
                    info_line("Replacing marker {0}".format(replace.beatsec))
                except KeyError:
                    pass
                new_marker = ControllerMarker(sample_ind, beatsec, value, change_type)
                info_line("Added marker {0}".format(new_marker))
                self.markers[sample_ind] = new_marker
            else:
                err_mess("Command '{0}' not recognized!".format(edit_type))
        





class VolumeController(Controller):

    def __init__(self, rate):
        super().__init__(rate, "Volume")

    
    def validate_value(self, value):
        return inpt_process(value, 'float', allowed=[0, 2])
    

    def apply(self, rec_arr):
        return rec_arr * self.markers[0]




a = VolumeController(44100)

a.edit()