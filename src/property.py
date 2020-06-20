from src.controller import ContinuousController, Controller, DiscreteMarker, ContinuousMarker
from src.data_types import *
from src.input_processing import inpt, inpt_validate, input_dir, input_file
from src.method_ops import (add_reldata, is_alias, is_public_process,
                            public_process, rel_alias)
from src.output_and_prompting import (critical_err_mess, err_mess, info_block,
                                      info_line, info_list, info_title, nl, p,
                                      section_head, show_error)
from src.process import process
from src.rel_objects import RelContainer, RelPublicObj, RelSavedObj


"""
This is the code I'm least/most proud of so far. RelProperty creates a 
static class property that manages dynamic access to instance-specific property
values. The point is to be able to set attributes normally, and have them type
checked:

x = classWithRelProp()  
# this value will be passed to inpt_validate to see if it matches the property's declared type
x.relprop = 4

However, when accessing the attribute, it must be called, with optional context

print(x.relprop) # prints a RelProperty object
print(x.relprop()) # prints '4'
print(x.relprop(context=context)) # print '4', but contextually

The context is useful for accessing BPM and things that can vary over time

"""


class RelProperty(RelContainer, RelPublicObj):
    """
    property that wraps a pint quant or controller.
    args:
        name (str)
        inpt_mode (str): valid inpt() mode
        desc (str): user-viewable description
        cont_type (str|None): "c" for default "continuous", None for not controllable, or any other value for discrete
    """

    attr_prefix = "_relprop_"

    def __init__(self, name, inpt_mode, allowed=None, default=None, desc="", 
            cont_type="c", change_types="all", mode="prop", reltype="Property"):
        super().__init__(name=name, reltype=reltype, mode=mode)

        self.name = name
        self.inpt_mode = inpt_mode
        self.allowed = allowed
        self.desc = desc
        self.cont_type = cont_type
        if self.cont_type is None:
            # makes the control() method private again
            add_reldata(self.control, "public", False)
        self.caller = None
        self.default = default
        self.change_types = change_types

    def attrname(self):
        return self.attr_prefix + self.name

    def file_ref_data(self):
        # this should not be needed
        raise UnexpectedIssue("Attemping to file_ref_repr a RelProperty")
    
    @staticmethod
    def load(data):
        # the actually loading will be done by __set__
        return data

    def __call__(self, context=None):
        if self.caller is None:
            raise PropertyError("Property call not bound to a caller. Make sure to call all properties at the time of accessing them")
        try:
            val = self.get_val()
        except AttributeError:
            self.__set__(self.caller, self.default)
        self.caller = None
        if isinstance(val, Controller):
            return val.__call__(context)
        return val

    def __get__(self, instance, owner):
        self.caller = instance
        return self

    def __set__(self, instance, value):
        if not isinstance(value, (Units.Quant, Controller)):
            value = inpt_validate(value, self.inpt_mode, self.allowed)
        setattr(instance, self.attrname(), value)

    def get_val(self):
        return getattr(self.caller, self.attrname())

    def process_message(self):
        """
        this is only called when the prop is not a controller
        """
        try:
            val = self.get_val()
        except AttributeError:
            info_block("{0} '{1}' has no value assigned yet. Use the 'set' process".format(self.reltype, self.name), indent=2)
        else:
            info_block("{0} '{1}' has a value of {2}".format(self.reltype, self.name, val), indent=2)

    def process(self):
        if self.caller is None:
            raise PropertyError("Property is not bound to a caller. Make sure to call properties at the time of access")
        try:
            val = self.get_val()
        except AttributeError:
            setattr(self.caller, self.attrname(), None)
            val = None
        if isinstance(val, Controller):
            process(val)
        else:
            process(self)
    
    @public_process
    def set(self, value):
        """
        cat: edit
        args:
            value: the new value of this property
        """
        value = inpt_validate(value, self.inpt_mode, self.allowed)
        setattr(self.caller, self.attrname(), value)

    @public_process
    def control(self):
        """
        cat: edit
        desc: turn this property's value into a controller, which allows it to be changed over time
        """
        val = self.get_val()
        if self.cont_type == "c":
            if val is not None:
                markers = {0: ContinuousMarker(Units.beats("0b"), val, "hard")}
            else:
                markers = None
            cont = ContinuousController(
                name=self.name,
                val_units=self.inpt_mode,
                val_allowed=self.allowed,
                markers=markers,
                change_types=self.change_types,
                parent=self.caller
            )
        else:
            if val is not None:
                markers = {0: DiscreteMarker(Units.beats("0b"), val)}
            else:
                markers = None
            cont = Controller(
                name=self.name,
                val_units=self.inpt_mode,
                val_allowed=self.allowed,
                markers=markers,
                parent=self.caller
            )
        setattr(self.caller, self.attrname(), cont)
        add_reldata(cont.rename, "public", False)
        process(cont)
