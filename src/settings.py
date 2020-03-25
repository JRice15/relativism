"""
settings
"""

class _SettingsContainer:
    """
    private container for global settings
    """

    _debug = True
    _autosave = False
    _bpm = 120
    _rate = 44100
    _next_id = 0 # next rel_obj id
    _process_num = 1 # process counter
    _rel_instance = None
    _project_instance = None


class Settings:
    """
    public access methods for global settings
    """

    @staticmethod
    def initialize(**kwargs):
        for k,v in kwargs.items():
            setattr(_SettingsContainer, k, v)

    @staticmethod
    def get_next_id():
        if _SettingsContainer._next_id is None:
            #TODO: open rel file
            pass
        val = _SettingsContainer._next_id
        _SettingsContainer._next_id += 1
        return val
        
    @staticmethod
    def get_process_num():
        _SettingsContainer._process_num += 1
        return _SettingsContainer._process_num - 1


    @staticmethod
    def get_rel_instance():
        return _SettingsContainer._rel_instance

    @staticmethod
    def set_rel_instance(rel):
        _SettingsContainer._rel_instance = rel

    @staticmethod
    def get_project_instance():
        return _SettingsContainer._project_instance
    
    @staticmethod
    def set_project_instance(proj):
        _SettingsContainer._project_instance = proj


    @staticmethod
    def is_debug():
        return _SettingsContainer._debug

    @staticmethod
    def debug_on():
        _SettingsContainer._debug = True
    
    @staticmethod
    def debug_off(self):
        _SettingsContainer._debug = False


    #TODO: get bpm, rate