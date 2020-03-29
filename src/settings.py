"""
settings
"""

class _SettingsContainer:
    """
    private container for global settings
    """

    debug = True
    autosave = False
    bpm = 120
    rate = 44100
    next_id = 0 # next rel_obj id
    process_num = 1 # process counter
    rel_instance = None
    project_instance = None
    error_log = None
    activity_log = None


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
        if _SettingsContainer.next_id is None:
            #TODO: open rel file
            pass
        val = _SettingsContainer.next_id
        _SettingsContainer.next_id += 1
        return val
        
    @staticmethod
    def get_process_num():
        _SettingsContainer.process_num += 1
        return _SettingsContainer.process_num - 1


    @staticmethod
    def get_rel_instance():
        return _SettingsContainer.rel_instance

    @staticmethod
    def set_rel_instance(rel):
        _SettingsContainer.rel_instance = rel

    @staticmethod
    def get_project_instance():
        return _SettingsContainer.project_instance
    
    @staticmethod
    def set_project_instance(proj):
        _SettingsContainer.project_instance = proj

    @staticmethod
    def is_debug():
        return _SettingsContainer.debug

    @staticmethod
    def debug_on():
        _SettingsContainer.debug = True
    
    @staticmethod
    def debug_off():
        _SettingsContainer.debug = False

    @staticmethod
    def set_error_log(error_log):
        _SettingsContainer.error_log = error_log
    
    @staticmethod
    def error_log():
        return _SettingsContainer.error_log
    
    @staticmethod
    def set_activity_log(activity_log):
        _SettingsContainer.activity_log = activity_log
    
    @staticmethod
    def activity_log():
        return _SettingsContainer.activity_log

    #TODO: get bpm, rate

