from src.rel_objects import RelContainer, RelPublicObj, RelSavedObj
from src.method_ops import public_process, is_public_process, rel_alias, is_alias
from src.process import process
from src.input_processing import inpt, inpt_validate, input_dir, input_file
from src.output_and_prompting import (p, info_title, info_list, info_line, 
    section_head, info_block, nl, err_mess, critical_err_mess, show_error)
from src.controller import Controller, ContinuousController
from src.data_types import *


class RelProperty(RelContainer, RelPublicObj):
    """
    property that wraps a pint quant or controller.
    args:
        name (str)
        inpt_mode (str): valid inpt() mode
        desc (str): user-viewable description
        controllable (bool): whether property can be turned into a controller
        cont_type (str|None): "c" for default "continuous", None for not controllable, or any other value for discrete
    """

    def __init__(self, name, inpt_mode, desc="", cont_type="c",
            mode="load", reltype="Property"):
        super().__init__(name=name, reltype=reltype, mode=mode)
        self.name = name
        self.inpt_mode = inpt_mode
        self.desc = desc
        self.val = None
        self.cont_type = cont_type
        if self.cont_type is None:
            self.control.__rel_public = False

    def file_ref_data(self):
        # all the rest is statically generated every time
        return self.val
    
    @staticmethod
    def load(data):
        # the actually loading will be done by __set__
        return data

    def __call__(self, context=None):
        return self.val.__call__(context)

    def __get__(self, instance, owner):
        return self

    def __set__(self, instance, value):
        if isinstance(value, (Units.Quant, Controller)):
            self.val = value
        else:
            raise TypeError("Invalid type '{0}' of object '{1}' for RelProperty with units '{2}'".format(type(value), value, self.units))

    def process(self):
        if isinstance(self.val, Units.Quant):
            process(self)
        else:
            process(self.val)
    
    @public_process
    def set(self, value):
        """
        cat: edit
        args:
            value: the new value of this property
        """
        self.val = inpt_validate(value, self.inpt_mode)

    @public_process
    def control(self):
        """
        cat: edit
        desc: turn this property's value into a controller, which allows it to be changed over time
        """
        if self.cont_type == "c":
            cont = ContinuousController()

