import abc

from scipy.interpolate import interp1d

from src.data_types import *
from src.errors import *
from src.input_processing import inpt, inpt_validate, input_dir, input_file
from src.method_ops import (is_alias, is_public_process, public_process,
                            rel_alias, rel_wrap, get_reldata, add_reldata)
from src.output_and_prompting import (critical_err_mess, err_mess, info_block,
                                      info_line, info_list, info_title, nl, p,
                                      rel_plot, section_head, show_error)
from src.rel_objects import RelContainer, RelPublicObj, RelSavedObj
from src.utility import *


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






class DiscreteMarker(RelContainer):

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
    """
    change type is the change leading up to this marker
    """

    def __init__(self, beatsec, value, change_type):
        self.beatsec = beatsec
        self.value = value
        self.change_type = change_type

    def __repr__(self):
        return "{0}: {1} ({2} change)".format(self.beatsec, self.value, self.change_type)

    def file_ref_data(self):
        return [self.beatsec, self.value, self.change_type]
    



class Controller(RelPublicObj, RelSavedObj):
    """
    discrete controlling of an attribute (pan, volume, bpm, etc.) over time.
    args:
        time_units (str): inpt mode either beats or secs
        val_units (str): units of the value, inpt mode
    """

    def __init__(self, name, val_units, time_units="beats", 
            val_allowed=None, time_allowed=None, start=None, reltype="Controller", 
            rel_id=None, path=None, markers=None, parent=None, mode="create", **kwargs):
        super().__init__(rel_id=rel_id, reltype=reltype, name=name, path=path, parent=parent, mode=mode, **kwargs)

        self.start = start
        self.markers = {} if markers is None else markers # {sample_ind : ControllerMarker}

        if time_units is None or time_units not in ("beat", "beats", "sec", "secs", "second", "seconds"):
            p("Select the timing units to be used for this controller, 'b' for beats notation (recommended), 's' for seconds")
            time_mode = inpt("letter", allowed="bs")
            if time_mode == "b":
                time_units = "beats"
            else:
                time_units = "secs"
        self.time_units = time_units
        self.val_units = val_units
        self.val_allowed = val_allowed
        self.time_allowed = (Units.beats("0b"), None)

        desc = get_reldata(self.add, "desc")
        try:
            new_desc = desc.format(
                val_units=self.val_units, 
                time_units=time_units
            )
        except:
            # if format fails, it means add docstring is overridden somewhere, 
            # and will be handled there
            pass 
        else:
            add_reldata(self.add, "desc", new_desc)

    def add_marker(self, sample_ind, marker):
        """
        method to be called by add() process
        """
        if isinstance(sample_ind, Units.Quant):
            sample_ind = sample_ind.magnitude
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
            location: the time where this marker should occur, in '{time_units}'
            value: the value of this marker, in/as a '{val_units}'
        dev: this docstring is .format()ed in init
        """
        beatsec = inpt_validate(location, self.time_units, allowed=self.time_allowed)
        value = inpt_validate(value, self.val_units, allowed=self.val_allowed)
        sample_ind = beatsec.to_samps()
        self.add_marker(sample_ind, DiscreteMarker(beatsec, value))

    @rel_alias("mv")
    @public_process
    def move(self, current, new):
        """
        cat: edit
        desc: move a marker to a new location
        Args:
            current: the beat or sec of the marker to move
            new: the beat or sec to move it to
        """
        old_beatsec = inpt_validate(current, self.time_units, allowed=self.time_allowed)
        new_beatsec = inpt_validate(new, self.time_units, allowed=self.time_allowed)
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
        beatsec = inpt_validate(location, self.time_units, allowed=self.time_allowed)
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
        info_list(list(self.markers.values()))

    @public_process
    def plot(self):
        """
        cat: info
        desc: plot this controller over time
        """
        if not self.markers:
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
    args:
        time_units: inpt mode either beats or secs
        val_units: units of the value, inpt mode
        change_types: tuple of allowed change types, the first being the default
    """

    change_type_options = ('hard', 'linear', 'smooth')

    def __init__(self, name, val_units, time_units=None, 
            val_allowed=None, time_allowed=None, markers=None, start=None, reltype="Controller", 
            change_types="all", rel_id=None, path=None, parent=None, mode="create", **kwargs):

        super().__init__(rel_id=rel_id, reltype=reltype, name=name, path=path, parent=parent, 
            mode=mode, markers=markers, time_units=time_units, val_units=val_units,
            val_allowed=val_allowed, start=start, time_allowed=time_allowed, **kwargs)
            
        # validate change types
        if change_types == "all":
            change_types = self.change_type_options
        elif not all(i in self.change_type_options for i in change_types):
            raise UnexpectedIssue("Unknown change_type in '{0}' in Controller constructor".format(change_types))
        self.valid_change_types = change_types

        desc = get_reldata(self.add, "desc")
        try:
            new_desc = desc.format(
                val_units=self.val_units, 
                time_units=time_units,
                change_types="', '".join(self.valid_change_types)
            )
        except:
            # if format fails, it means add docstring is overridden somewhere, 
            # and will be handled there
            pass 
        else:
            add_reldata(self.add, "desc", new_desc)


    def validate_change_type(self, change_type):
        if change_type is None:
            return self.change_type_options[0]
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
            location: the time where this marker should occur, in '{time_units}'
            value: the value of this marker, in/as '{val_units}'
            [change type: how the value transitions from the previous marker to this one, one of '{change_types}']
        dev: this docstring is .format()ed in init
        """
        beatsec = inpt_validate(location, self.time_units, self.time_allowed)
        sample_ind = beatsec.to_samps()
        value = inpt_validate(value, self.val_units, self.val_allowed)
        change_type = self.validate_change_type(change_type)
        self.add_marker(sample_ind, ContinuousMarker(beatsec, value, change_type))

