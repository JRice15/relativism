from src.output_and_prompting import info_block

class RelGlobal:


    _debug = True
    _autosave = False
    _bpm = 120
    _rate = 44100
    _next_id = 0
    _process_num = 1
    _instance = None

    @staticmethod
    def get_next_id():
        if RelGlobal._next_id is None:
            #TODO: open rel file
            pass
        temp = RelGlobal._next_id
        RelGlobal._next_id += 1
        return temp
        
    @staticmethod
    def get_rel_instance():
        return RelGlobal._instance

    @staticmethod
    def is_debug():
        return RelGlobal._debug

    @staticmethod
    def debug_on():
        info_block("Debug On. Errors may propogate to top level and halt execution with no save")
        RelGlobal._debug = True
    
    @staticmethod
    def debug_off(self):
        info_block("Debug Off")
        RelGlobal._debug = False

    @staticmethod
    def get_process_num():
        RelGlobal._process_num += 1
        return RelGlobal._process_num - 1
