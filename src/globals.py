"""
settings
"""

import json

from src.errors import *
from src.input_processing import autofill, inpt, p
from src.output_and_prompting import (err_mess, info_block, info_list,
                                      info_title, section_head)
from src.decorators import public_process, is_public_process, rel_alias, is_alias


def init_globals():
    RelGlobals.init_globals()
    Settings.init_settings()

def save_globals():
    RelGlobals.save_globals()
    Settings.save_settings()


class _RelGlobalsContainer:
    """
    private container for global settings and variables
    """

    # vars that get written to rel globals file (persistent)
    _write_vars = ["next_id"]

    # persistent data with its default value
    next_id = 0

    # session-dependant data
    process_num = 1
    bpm = None
    rate = None
    rel_instance = None
    project_instance = None
    error_log = None
    data_file = None
    settings_file = None


class RelGlobals:
    """
    programmer access to global variables via static methods
    """

    @staticmethod
    def init_globals():
        """
        read vars from data file
        """
        info_block("Loading data...")
        if RelGlobals.data_file() is None:
            raise AttributeError("data_file attr not yet set in _RelGlobalContainer")
        try:
            with open(RelGlobals.data_file(), "r") as f:
                dct = json.load(f)
        except FileNotFoundError:
            dct = {i:getattr(_RelGlobalsContainer, i) for i in _RelGlobalsContainer._write_vars}
        for k,v in dct.items():
            setattr(_RelGlobalsContainer, k, v)

    @staticmethod
    def save_globals():
        """
        dct: dict of vars to save
        """
        info_block("Saving data...")
        dct = {i:getattr(_RelGlobalsContainer, i) for i in _RelGlobalsContainer._write_vars}
        with open(RelGlobals.data_file(), "w") as f:
            json.dump(dct, f, indent=2)

    @staticmethod
    def get_next_id():
        val = _RelGlobalsContainer.next_id
        _RelGlobalsContainer.next_id += 1
        return val
        
    @staticmethod
    def get_process_num():
        _RelGlobalsContainer.process_num += 1
        return _RelGlobalsContainer.process_num - 1

    @staticmethod
    def get_rel_instance():
        return _RelGlobalsContainer.rel_instance

    @staticmethod
    def set_rel_instance(rel):
        _RelGlobalsContainer.rel_instance = rel

    @staticmethod
    def get_project_instance():
        return _RelGlobalsContainer.project_instance
    
    @staticmethod
    def set_project_instance(proj):
        _RelGlobalsContainer.project_instance = proj

    @staticmethod
    def set_error_log(error_log):
        _RelGlobalsContainer.error_log = error_log
    
    @staticmethod
    def error_log():
        return _RelGlobalsContainer.error_log

    @staticmethod
    def set_data_file(file):
        _RelGlobalsContainer.data_file = file
    
    @staticmethod
    def data_file():
        return _RelGlobalsContainer.data_file

    @staticmethod
    def set_settings_file(file):
        _RelGlobalsContainer.settings_file = file
    
    @staticmethod
    def settings_file():
        return _RelGlobalsContainer.settings_file

    #TODO: get bpm, rate


class _SettingsContainer:
    """
    private container for user settings
    """

    debug = None
    autosave = None

    # default setting values, not to be confused with __defaults__
    _defaults = {
        "debug": True,
        "autosave": False
    }


class Settings():
    """
    public access methods for global settings
    """

    @staticmethod
    def init_settings():
        info_block("Loading settings...")
        if RelGlobals.settings_file() is None:
            raise AttributeError("settings_file attr not yet set in _RelGlobalContainer")
        try:
            with open(RelGlobals.settings_file(), "r") as f:
                dct = json.load(f)
        except FileNotFoundError:
            dct = _SettingsContainer._defaults
        for k,v in dct.items():
            setattr(_SettingsContainer, k, v)


    @staticmethod
    def save_settings():
        """
        save settings to settingsfile
        """
        info_block("Saving settings...")
        attrs = [attr for attr in dir(_SettingsContainer) if "__" not in attr and attr != "_defaults"]
        dct = {i:getattr(_SettingsContainer, i) for i in attrs}
        with open(RelGlobals.settings_file(), "w") as f:
            json.dump(dct, f, indent=2)

    @staticmethod
    def process():
        section_head("Editing User Settings")
        method_strs = [func for func in dir(Settings) if "__" not in func and 
            is_public_process(getattr(Settings, func))]
        while True:
            info_title("Available processes:")
            info_list(method_strs)
            p("What process to run?")
            proc = inpt("alphanum")
            try:
                proc = autofill(proc, method_strs)
                method = getattr(Settings, proc)
                if is_public_process(method):
                    method()
                else:
                    raise AttributeError
            except (AutofillError, AttributeError) as e:
                err_mess("No process matches '{0}'!".format(proc))

    @staticmethod
    @public_process
    def show_settings():
        info_title("Settings:")
        attrs = [attr for attr in dir(_SettingsContainer) if "__" not in attr and attr != "_defaults"]
        maxlen = max(len(i) for i in attrs)
        for name in attrs:
            value = getattr(_SettingsContainer, name)
            if value == True:
                value = "On"
            if value == False:
                value = "Off"
            info_list(name + ": " + (" " * abs(maxlen - len(name))) + str(value))


    @staticmethod
    def is_debug():
        return _SettingsContainer.debug

    @staticmethod
    @public_process
    def debug_on():
        info_block("Debug is now on")
        _SettingsContainer.debug = True
    
    @staticmethod
    @public_process
    def debug_off():
        info_block("Debug is now off")
        _SettingsContainer.debug = False

    @staticmethod
    @public_process
    def restore_defaults():
        for k,v in _SettingsContainer._defaults.items():
            setattr(_SettingsContainer, k, v)

    #TODO: set input, output
    #TODO: autosave
