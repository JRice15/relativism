from output_and_prompting import *
from input_processing import *
import abc
from scipy.interpolate import interp1d
from utility import *
from object_data import *


class ControllerMarker(RelativismObject):

    def __init__(self, sample_ind, beatsec, value, change_type):
        self.sample_ind = sample_ind
        self.beatsec = beatsec
        self.value = value
        self.change_type = change_type


    def __repr__(self):
        return "{0}: {1} ({2} change)".format(self.beatsec, self.value, self.change_type)


class Controller(RelativismObject, abc.ABC):
    """
    for controlling an attribute (pan, volume, bpm, etc.) over time.
    abstract methods 'validate_value' and 'apply'. create convert method if value
    if non-numerical. call 'edit' to change markers
    """

    valid_change_types = ('hard', 'linear', 'smooth')
    valid_edit_types = {
        'add': ['add'],
        'del': ['delete', 'del', 'remove', 'rm'],
        'view': ['view', 'show', 'list', 'ls'],
        'plot': ['plot', 'plt'],
        'move': ['mv', 'move']
    }
    edit_descriptions = {
        'add': "add <beat/sec> <value> <change-type, default 'hard'>",
        'del': 'del <beat/sec>',
        'view': 'view',
        'plot': 'plot',
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

    def plot(self):
        ind, val = self.generate()
        channel = np.asarray(list(zip(ind, val)))
        print(channel)
        rel_plot(
            left_or_mono=channel,
            start=0,
            end=max(ind),
            rate=self.rate
        )

    def validate_edit_type(self, edit_type):
        edit_type = inpt_process(edit_type, 'alphanum')
        for t in self.valid_edit_types.values():
            if edit_type in t:
                return edit_type
        err_mess("Invalid edit type '{0}'".format(edit_type))
        p("Select one of: {0}".format(", ".join(self.valid_edit_types)))
        edit_type = inpt('alphanum')
        return self.validate_edit_type(edit_type)

    def validate_change_type(self, change_type):
        change_type = inpt_process(change_type, 'alphanum')
        if change_type in self.valid_change_types:
            return change_type
        else:
            err_mess("Invalid change type '{0}'".format(change_type))
            p("Select one of: {0}".format(", ".join(self.valid_change_types)))
            change_type = inpt('alphanum')
            return self.validate_change_type(change_type)

    @abc.abstractmethod
    def validate_value(self, value):
        """
        validate format of input value that is being controlled
        """
        ...

    def generate(self):
        # TODO
        i = 0
        indexes = [i.sample_ind for i in self.markers.values()]
        try:
            values = [self.convert(i.value) for i in self.markers.values()]
        except AttributeError:
            values = [i.value for i in self.markers.values()]
        output = np.array([])
        new_indexes = np.arange(max(indexes))
        try:
            func = interp1d(indexes, values, kind="cubic", bounds_error=False, fill_value='extrapolate')
            plt.plot(new_indexes, func(new_indexes))
        except ValueError:
            try:
                func = interp1d(indexes, values, kind="quadratic")
                plt.plot(new_indexes, func(new_indexes))
            except ValueError:
                try:
                    func = interp1d(indexes, values, kind="linear")
                    plt.plot(new_indexes, func(new_indexes))
                except ValueError:
                    plt.scatter(indexes, values)
        plt.show()
        return new_indexes, func(new_indexes)

        # while i < len(markers):
        #     output = np.concatenate


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
        info_title("Valid commands ('q' to quit, 'o' for options):")
        for i in self.valid_edit_types.keys():
            info_list(i + ": " + self.edit_descriptions[i], hang=4)
        info_title("Valid change types are:")
        info_list(self.valid_change_types)
        while True:

            print("\n  Command: ", end="")
            command = inpt('split', split_modes=['alphanum', 'beat', 'stnd', 'alphanum'], 
                catch='o', catch_callback=self.edit)

            try:
                edit_type = self.validate_edit_type(command[0])

                if edit_type in self.valid_edit_types['view']:
                    self.display_markers()
                    continue
                elif edit_type in self.valid_edit_types['plot']:
                    if len(self.markers) == 0:
                        err_mess("No data to plot!")
                    else:
                        self.plot()
                    continue

                try:
                    beatsec = inpt_process(command[1], 'beat')
                except IndexError:
                    p("Choose a beat/sec for this marker to occur at")
                    beatsec = inpt('beat')
                sample_ind = samps(beatsec, self.rate)

                if edit_type in self.valid_edit_types['del']:
                    try:
                        marker = self.markers[sample_ind]
                        info_line("Deleted marker {0}".format(marker.beatsec))
                        del self.markers[sample_ind]
                    except KeyError:
                        err_mess("No marker to delete at {0}".format(beatsec))

                elif edit_type in self.valid_edit_types['move']:
                    try:
                        marker = self.markers[sample_ind]
                    except KeyError:
                        err_mess("No marker to move at {0}".format(beatsec))    
                        continue
                    del self.markers[sample_ind]
                    new_beatsec = inpt_process(command[2], 'beat')
                    new_samp_ind = samps(new_beatsec, self.rate)
                    try:
                        replace = self.markers[new_samp_ind]
                        info_line("Replacing marker {0}".format(replace))
                    except KeyError:
                        pass
                    info_line("Moved marker from {0} to {1}".format(marker.beatsec, new_beatsec))
                    self.markers[new_samp_ind] = ControllerMarker(new_samp_ind,
                        new_beatsec, marker.value, marker.change_type)

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
                        info_line("Replacing marker {0}".format(replace))
                    except KeyError:
                        pass
                    new_marker = ControllerMarker(sample_ind, beatsec, value, change_type)
                    info_line("Added marker {0}".format(new_marker))
                    self.markers[sample_ind] = new_marker
                else:
                    err_mess("Command '{0}' not recognized!".format(edit_type))

            except Cancel:
                pass
        


    def get_help(self):
        pass



class TestController(Controller):

    def __init__(self, rate):
        super().__init__(rate, "Volume")

    
    def validate_value(self, value):
        return inpt_process(value, 'float', allowed=[0, 2])
    

    def apply(self, rec_arr):
        return rec_arr * self.markers[0]




def controller_main():
    pass


if __name__ == "__main__":
    controller_main()