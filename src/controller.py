import abc
from scipy.interpolate import interp1d

from src.output_and_prompting import (p, info_title, info_list, info_line, 
    section_head, info_block, nl, err_mess, critical_err_mess, show_error,
    rel_plot)
from src.input_processing import inpt, inpt_validate, input_dir, input_file
from src.utility import *
from src.rel_objects import (RelativismSavedObj, RelativismPublicObj, RelativismContainer)
from src.decorators import public_process, is_public_process, rel_alias, is_alias, rel_wrap
from src.errors import *



# testing

# def linear(start, startval, end, endval):
#     delta = (endval - startval) / (end - start)
#     return [startval + (delta * i) for i in range(end - start)]


# def smooth(start, startval, dstart, end, endval, dend):
#     prec = 10 # precision
#     full = []
#     frac_start = start
#     frac_sval = startval
#     frac_endval = 0
#     dfrac = dstart
#     for i in range(prec):
#         dfrac = (dfrac + dend) / 2
#         print(dfrac)
#         frac_end = end - ((prec - i - 1) * (end - start) // prec)
#         frac_endval = frac_sval + dfrac * (frac_end - frac_start)
#         full += linear(frac_start, frac_sval, frac_end, frac_endval)
#         frac_start = frac_end
#         frac_sval = frac_endval
#     return (np.array(full) - startval) * (endval - startval) / (frac_endval - startval) + startval


# lin = linear(100, 1, 120, 2)
# print(lin)

# plt.plot(lin)

# sm = smooth(100, 1, -20, 120, 2, 1)
# print(sm)

# plt.plot(sm)
# plt.show()






class DiscreteMarker(RelativismContainer):

    def __init__(self, beatsec, value):
        self.beatsec = beatsec
        self.value = value

    def __repr__(self):
        return "{0}: {1}".format(self.beatsec, self.value)

    def samps(self):
        return self.beatsec.to_samps()

    def file_ref_data(self):
        return [self.beatsec, self.value]
    
    @staticmethod
    def load(self_clss, data):
        return self_clss(*data)

class ContinuousMarker(DiscreteMarker):

    def __init__(self, beatsec, value, change_type):
        self.beatsec = beatsec
        self.value = value
        self.change_type = change_type

    def __repr__(self):
        return "{0}: {1} ({2} change)".format(self.beatsec, self.value, self.change_type)

    def file_ref_data(self):
        return [self.beatsec, self.value, self.change_type]
    



class Controller(RelativismPublicObj, abc.ABC):
    """
    discrete controlling of an attribute (pan, volume, bpm, etc.) over time.
    implement:
        validate_value(self, value)
        type_hint
        apply(self, target)
        [get_allowed_times]
    """

    def __init__(self, markers=None, time_units=None, start=None, reltype=None, 
            rel_id=None, name=None, path=None, parent=None, mode="load"):
        super().__init__(rel_id=rel_id, reltype=reltype, name=name, path=path, parent=parent, mode=mode)

        self.start = start
        self.markers = {} if markers is None else markers # {sample_ind : ControllerMarker}

        if time_mode is None or time_mode not in ("b", "s"):
            p("Select the timing units to be used for this controller, 'b' for beat/note notation, 's' for seconds")
            time_mode = inpt("letter", allowed="bs")
        self.time_units = time_mode

    def get_time_input_mode(self):
        if self.time_units == "b":
            return "beats"
        else:
            return "seconds"

    def get_allowed_times(self):
        """
        override to return a 2-list of [low, high]
        """
        return None

    @abc.abstractmethod
    @public_process
    def type_hint(self):
        """
        cat: info
        dev: display hints on what kind of data is accepted for add() args
        """
        ...

    @abc.abstractmethod
    def validate_value(self, value):
        """
        validate input for the value that is being controlled
        """
        ...

    @abc.abstractmethod
    def apply(self, target):
        """
        apply controller effect to target
        """
        ...

    def add_marker(self, sample_ind, marker):
        """
        method to be called by add() process
        """
        try:
            replaced = self.markers[sample_ind]
            info_line("Replacing marker '{0}' with '{1}'".format(replaced, marker))
        except KeyError:
            info_line("Added marker '{0}'".format(marker))
        self.markers[sample_ind] = marker

    @public_process
    def add(self, location, value):
        """
        cat: edit
        desc: add a new marker (see type_hint process for info on the specific types that arguments allow)
        args:
            location: the beat or sec (whatever the time mode of this controller is) where this marker should occur
            value: the value of this marker
        """
        beatsec = inpt_validate(location, self.get_time_input_mode(), allowed=self.get_allowed_times())
        sample_ind = beatsec.to_samps()
        value = self.validate_value(value)
        self.add_marker(sample_ind, DiscreteMarker(beatsec, value))

    @public_process
    def move(self, current, new):
        """
        desc: move a marker to a new location
        Args:
            current: the beat or sec of the marker to move
            new: the beat or sec to move it to
        """
        old_beatsec = inpt_validate(current, self.get_time_input_mode(), allowed=self.get_allowed_times())
        new_beatsec = inpt_validate(new, self.get_time_input_mode(), allowed=self.get_allowed_times())
        old_sample_ind = old_beatsec.to_samps()
        new_samp_ind = new_beatsec.to_samps()
        try:
            marker = self.markers[old_sample_ind]
        except KeyError:
            err_mess("No marker to move at {0}!".format(old_beatsec)) 
            return
        marker.beatsec = new_beatsec
        self.add_marker(new_samp_ind, marker)
        del self.markers[old_sample_ind]

    @rel_alias("rm")
    @public_process
    def delete(self, location):
        """
        cat: edit
        desc: delete a marker from this controller
        args:
            location: beat or sec of the marker to remove
        """
        beatsec = inpt_validate(location, self.get_time_input_mode(), allowed=self.get_allowed_times())
        sample_ind = beatsec.to_samps()
        try:
            marker = self.markers[sample_ind]
            info_line("Deleting marker '{0}'".format(marker))
            del self.markers[sample_ind]
        except KeyError:
            err_mess("No marker to delete at {0}".format(beatsec))
        
    @rel_alias("ls")
    @public_process
    def list_markers(self):
        """
        cat: info
        desc: list the markers in this controller
        """
        info_title("Controller for {0}".format(self.reltype))
        if len(self.beat_markers) == 0 and len(self.sec_markers) == 0:
            info_list("(empty)")
        for i in sorted(self.beat_markers):
            info_list(self.beat_markers[i])
        for i in sorted(self.sec_markers):
            info_list(self.sec_markers[i])

    @public_process
    def plot(self):
        """
        cat: info
        desc: plot this controller over time
        """
        if len(self.markers) == 0:
            err_mess("No data to plot!")
            return
        inds, vals = self.generate()
        channel = np.asarray(list(zip(inds, vals)))
        rel_plot(
            left_or_mono=channel,
            start=0,
            end=max(inds),
            rate=self.rate
        )

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


class ContinuousController(Controller):
    """
    controller that is continuous over time, instead of discrete  
    implement:
        validate_value(self, value)
        type_hint
        apply(self, target)
        [get_allowed_times]
    """

    change_type_options = ('hard', 'linear', 'smooth')

    def __init__(self, markers=None, time_units=None, change_types=None, start=None, reltype=None, 
            rel_id=None, name=None, path=None, parent=None, mode="load"):

        # super Controller
        super().__init__(rel_id=rel_id, reltype=reltype, name=name, path=path, parent=parent, 
            mode=mode, markers=markers, time_units=time_units, start=start)
        
        # validate change types
        if not all(i in self.change_type_options for i in change_types):
            raise UnexpectedIssue("Unknown change_type in '{0}'".format(change_types))
        self.valid_change_types = change_types

    def validate_change_type(self, change_type):
        while change_type not in self.valid_change_types:
            err_mess("Invalid change type '{0}'".format(change_type))
            p("Select one of: {0}".format(", ".join(self.valid_change_types)))
            change_type = inpt('alphanum')
        return change_type
    
    @public_process
    def add(self, location, value, change_type=None):
        """
        cat: edit
        desc: add a new marker (see type_hint process for info on the specific types that arguments allow)
        args:
            location: the beat or sec (whatever the time mode of this controller is) where this marker should occur
            value: the value of this marker
            [change type: how this marker's value transitions the following one]
        """
        beatsec = inpt_validate(location, self.get_time_input_mode(), allowed=self.get_allowed_times())
        sample_ind = beatsec.to_samps()
        value = self.validate_value(value)
        change_type = self.validate_change_type(change_type)
        self.add_marker(sample_ind, ContinuousMarker(beatsec, value, change_type))


class TestController(Controller):

    def __init__(self, rate):
        super().__init__(rate, "Volume")

    
    def validate_value(self, value):
        return inpt_validate(value, 'float', allowed=[0, 10])
    

    def apply(self, rec_arr):
        return rec_arr * self.markers[0]




def controller_main():
    pass


if __name__ == "__main__":
    controller_main()