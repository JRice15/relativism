"""
chance-based generative Sampler object
"""


from src.data_types import *
from src.recording_obj import Recording
from src.integraters import mix, mix_multiple, concatenate
from src.object_data import (public_process, is_public_process, 
    RelativismSavedObj, RelativismPublicObj)
from src.controller import Controller
from src.output_and_prompting import (p, info_title, info_list, info_line, 
    section_head, info_block, nl, err_mess, critical_err_mess, show_error)
from src.input_processing import inpt, inpt_validate, input_dir, input_file
from src.globals import RelGlobals, Settings
from src.path import join_path, split_path
from src.process import process

"""


create sampler, add samples

set rhythms, frequencies

access any projects recs

"""


class SampleGroup(RelativismPublicObj):
    """
    containing one or more audio samples
    """

    def __init__(self, 
            name=None, 
            mode="load",
            rel_id=None, 
            reltype="Sample Group", 
            path=None, 
            parent=None,
            samples=None,
        ):

        super().__init__(rel_id=rel_id, reltype=reltype, name=name, 
            path=path, parent=parent, mode=mode)

        if name is None:
            self.rename()
        self.samples = {} if samples is None else samples

        if mode == "create":
            self.save()

    @public_process
    def list_samples(self):
        info_title("Samples in Sample Group '{0}':".format(self.name))
        info_list(list(self.samples.keys()))

    @public_process
    def process_child_sample(self, name=None):
        """
        desc: process a sample contained in this group
        """
        while True:
            if name is None:
                self.list_samples()
                p("Enter the name of the Sample to process")
                name = inpt('name')
            else:
                name = inpt_validate(name, 'name')
            try:
                self.samples[name]
                break
            except KeyError:
                err_mess("> Sample '{0}' does not exist!".format(name))
        process(self.samples[name])

    def validate_child_name(self, name):
        return name not in self.samples

    @add_sample
    def add_sample(self, new_sample):
        if isinstance(new_sample, Recording):
            if not self.validate_child_name(new_sample.name):
                err_mess("Sample with name '{0}' already exists in Sample Group '{1}'! You may rename it and add it again".format(
                    new_sample.name, self.name))
        else:
            new_sample = Recording(mode="create", parent=self, reltype="Sample")
        self.samples[new_sample.name] = new_sample

    @public_process
    def save(self):
        self.save_metadata()


class Rhythm(RelativismPublicObj):

    def __init__(self, 
            name=None, 
            mode="load",
            rel_id=None,
            reltype="Rhythm", 
            path=None, 
            parent=None,
            period=None,
            length=None,
            beats=None
        ):

        super().__init__(rel_id=rel_id, reltype=reltype, name=name, 
            path=path, parent=parent, mode=mode)

        if name is None:
            self.rename()

        self.beats = [] if beats is None else beats
        self.length = None
        self.period = None
        self.set_length_and_period(length, period)

        if mode == "create":
            self.save()

    def __repr__(self):
        return "'{0}', Rhythm object. Length {1} beats. {2} children beats are loaded".format(
            self.name, self.length, len(self.beats))

    def beat_repr(self, beat):
        return "place: {0}, length: {1}, start: {2}".format(beat[0], beat[1], beat[2])

    @public_process
    def info(self):
        raise NotImplementedError

    @public_process
    def rhythms_help(self):
        info_block(
            "Rhythms are made up of multiple beats. Each beat follows the format of " + \
            "<place> <length> <optional: start>, all of which are in beat notation: ", 
            trailing_newline=False
        )
        info_block(
            "<place>: the time at which this beat starts within the rhythm. For example" +\
            " 'qn' would mean this beat starts one quarter-note after the beginning of the rhythm",
            trailing_newline=False
        )
        info_block(
            "<length>: how long the snippet of the sample will be. 'qn' would mean it lasts for one quarter-note. " +\
            "no entry, or 0, means that the entire sample will be used",
            trailing_newline=False
        )
        info_block(
            "<start>: an optional parameter, which selects where in the sample to start playback " +\
            "for this one beat, as if trimming it on the front. 'qn' means the beat would begin " +\
            "from one quarter-note in to the sample",
            trailing_newline=False
        )
        print("        3q 1q")
        info_block(
            "will create a beat that start on the third quarter of the rhythm, and" + \
            "lasts for one quarter note"
        )
        p("Do you need info on how to create properly formed beats?", o="y/n")
        if inpt('y-n'):
            beat_options()

    @public_process
    def set_length_and_period(self, length=None, period=None):
        """
        cat: edit
        desc: set the length and period of this rhythm. Give 0 for either argument to keep the current value
        args:
            length: length of the rhythm in beats
            period: standard subdivision of this rhythm, in beats
        """
        if length == 0 and self.length is not None:
            pass
        elif length is None:
            p("Enter a length in beats for this Rhythm")
            length = inpt('beats')
            if length != 0:
                self.length = length
            elif self.length is None:
                err_mess("There is no current value for length, enter a valid value in beats")
                return self.set_length_and_period(None, period)
        else:
            self.length = inpt_validate(length, 'beats')

        if period == 0 and self.period is not None:
            pass
        elif period is None:
            p("Enter the period, or smallest beat that this Rhythm usually lands on", h=True)
            self.period = inpt('beat')
        else:
            self.period = inpt_validate(period, "beat")

    @public_process
    def add_beats(self):
        """
        create beats through prompts or pass 'beat' param to set
        """
        info_block("Creating new Rhythm '{0}'".format(self.name))
        while True:
            info_block(
                "Enter a beat as <place in rhythm> <optional: length> ('q' to finish, 'i' for more info)",
                indent=2,
                hang=2,
                trailing_newline=False
            )
            print("  : ", end="")
            try:
                new_beat = inpt("split", "beat", help_callback=self.rhythms_help)
            except Cancel:
                info_block("Finished creating Rhythm '{0}'".format(self.name))
                return
            if not (1 <= len(new_beat) <= 2):
                err_mess("Wrong number of arguments! From 1 to 2 are required, {0} were supplied".format(len(new_beat)))
                continue
            if secs(new_beat[0]) >= secs(str(self.length) + 'b'):
                err_mess("This beat begins after the end of the rhythm! Try again")
                continue
            
            self.beats.append(new_beat)

            while len(new_beat) < 3:
                new_beat.append(0)
            if new_beat[1] == 0:
                new_beat[1] = "all"
            info_line("  Added beat - " + self.beat_repr(new_beat))

    @public_process
    def delete_beats(self):
        raise NotImplementedError

    @public_process
    def list_beats(self):
        sorted_beats = selection_sort(self.beats, ind=0, func_on_val=secs, func_args=[60, 'val'], low_to_high=True)
        for i in sorted_beats:
            info_block("- " + self.beat_repr(i), newlines=False)


class Active(RelativismPublicObj):

    def __init__(self, parent, path, act_rhythm, act_sample, reltype=None, 
            name=None, rel_id=None, muted=None):

        super().__init__(rel_id, reltype, name, path, parent)
        print("\n* Initializing active pair")
        self.reltype = "ActivePair"
        self.rhythm = act_rhythm
        self.sample = act_sample
        self.muted = muted
        self.variability = Active.Variability()
        if name is None:
            self.rename()
        if muted is None:
            p("Should this active pair begin muted?", o='y/n')
            self.muted = inpt('y-n')

    def __repr__(self):
        out_str = "'{0}', Active Rhythm-Sample pair".format(self.get_name())
        if self.muted:
            out_str += " (muted)"
        out_str += ": Rhythm '{0}', Sample '{1}'".format(self.rhythm.get_name(), self.sample.get_name())
        return out_str

    @public_process
    def info(self):
        """
        cat: info
        desc: 
        """
        print(str(self))

    @public_process
    def rename(self, name=None):
        if name is None:
            print("  Give this active pair a name: ", end="")
            name = inpt("obj")
            print("  named '{0}'".format(name))
        else:
            name = inpt_validate(name, "obj")
        self.name = name

    @public_process
    def get_name(self):
        return self.name

    @public_process
    def set_variability(self, var=None):
        if var is None:
            p("Enter the variability (in percentage, 0-100%) of this Rhythm")
            self.variability = inpt('pcnt')
        else:
            self.variability = inpt_validate(var, 'pcnt')


    def generate_active(self, length):
        """
        generate this active pair. length is samples
        """
        length = length // self.rhythm.length
        beats_to_mix = []
        base_offset = 0
        biggest_offset = 0
        while biggest_offset < length:
            for i in self.rhythm.beats:
                offset = i[0] + base_offset
                biggest_offset = offset if offset > biggest_offset else biggest_offset
                if biggest_offset >= length:
                    break
                beats_to_mix.append([self.sample.rec, offset])
            base_offset += self.rhythm.length
        mixed = mix_multiple(beats_to_mix)
        return mixed


    class Variability(Controller):

        def __init__(self):
            super().__init__(self.sample.rate, "variability")
        

        def validate_value(self, value):
            return inpt_validate(value, 'pcnt')

        def apply(self, rec_arr):
            raise NotImplementedError



    class SamplerVariationGenerator():

        def __init__(self):
            pass





class Sampler(RelativismPublicObj):
    """
    Attr:
        dir: directory
        name: name
        smps (list): [Samples]
        rhythms (list): [Rhythms]
        active (list): [Active]
        BPM (float): float
    """

    def __init__(self,
        name=None,
        parent=None,
        hidden=False,
        smps=None,
        active=None,
        rhythms=None,
        bpm=None,
        reltype="Sampler",
        rel_id=None,
        path=None,
    ):
        super().__init__(rel_id, reltype, name, path, parent)

        self.reltype = reltype
        if name is None:
            self.rename()

        if (path is None) and (parent is not None):
            self.path = join_path(self.parent.path, self.get_data_filename(), is_dir=True)
            os.makedirs(self.path, exist_ok=True)
        
        if not hidden:
            print("\n* Initializing {0} '{1}'".format(self.reltype, self.name))

        self.smps = [] if smps is None else smps
        self.rhythms = [] if rhythms is None else rhythms
        self.active = [] if active is None else active
        #TODO: BPM_Controller()
        self.bpm = Units.rate(120) if bpm is None else bpm 

    # Representation #
    def __repr__(self):
        raise NotImplementedError

    @public_process
    def info(self):
        """
        cat: info
        """
        section_head("{0} '{1}'".format(self.reltype, self.name))
        info_line("{0} samples".format(len(self.smps)))
        info_line("{0} rhythms".format(len(self.rhythms)))
        info_line("{0} active pairs".format(len(self.active)))
        info_line("(use list_samples/rhythms/active to view them)")

    @public_process
    def rename(self, name=None):
        """
        cat: meta
        desc: rename (and resave) this object
        args:
            name: name for this object
        """
        old_name = self.name

        super().rename(name)

        # rename files
        if old_name is not None:
            try:
                os.rename(self.get_path(old_name), self.get_path())
            except OSError:
                pass


    @public_process
    def edit_bpm(self):
        raise NotImplementedError

    # Handling Samples #
    @public_process
    def add_sample(self, new_samp=None):
        """
        desc: add a sample from file, project, or another sampler
        cat: edit
        """
        if isinstance(new_samp, Recording):
            new_samp.reltype = "Sample"
        else:
            new_samp = Recording(reltype="Sample", parent=self)
        self.smps.append(new_samp)
        self.list_samples()
        nl()
        p("Process this sample? y/n")
        if inpt("yn"):
            process(new_samp)

    @public_process
    def add_sample_group(self):
        """
        """
        # TODO: add sample group
        self.smps.append(SampleGroup())

    @public_process
    def edit_sample(self):
        """
        cat: edit
        desc: select sample to process
        """
        while True:
            print("\n  Which sample of {0} '{1}' would you like to edit? ('q' to cancel, 'list' to list samples): "
                .format(self.reltype, self.name), end="")
            sample = self.choose("sample")
            try:
                process(sample)
            except Cancel:
                continue

    @public_process
    def list_samples(self):
        """
        desc: list samples in this sampler
        cat: info
        dev:
            returns bool, false if nothing to list
        """
        print("\n  Samples loaded into '{0}':".format(self.name))
        empty = True
        for obj in self.smps:
            info_list(str(obj))
            empty = False
        if empty:
            info_block("No samples loaded")
            return False

    # Handling Rhythms #
    @public_process
    def add_rhythm(self, new_rhythm=None):
        if not isinstance(new_rhythm, Rhythm):
            p("Create new rhythm (C) or Load from another sampler (L)?")
            source = inpt("letter", allowed="cl")
            if source == 'c':
                new_rhythm = Rhythm()
            else:
                # load from sampler
                raise NotImplementedError

        self.rhythms.append(new_rhythm)
        self.list_rhythms()
        p("Process this rhythm? y/n")
        if inpt("yn"):
            try:
                process(new_rhythm)
            except Cancel:
                pass

    @public_process
    def edit_rhythm(self):
        rhythm = self.choose("rhythm")
        process(rhythm)

    @public_process
    def list_rhythms(self):
        """
        desc: list rhythms in this sampler
        cat: info
        dev:
            returns bool, false if nothing to list
        """
        print("\n  Rhythms loaded into '{0}':".format(self.name))
        empty = True
        for obj in self.rhythms:
            empty = False
            info_list(str(obj))
        if empty:
            info_block("No rhythms loaded")
            return False

    # Handling Active #
    @public_process
    def activate(self, act_rhythm=None, act_sample=None):
        if not isinstance(act_rhythm, Rhythm):
            p("Choose a rhythm for this active pair")
            act_rhythm = self.choose('rhythm')
        if not isinstance(act_sample, Recording):
            p("Choose a sample for this active pair")
            act_sample = self.choose('sample')
        new_active = Active(self, act_rhythm, act_sample)
        self.active.append(new_active)

    @public_process
    def list_active(self):
        """
        desc: list active pairs in this sampler
        cat: info
        dev:
            returns bool, false if nothing to list
        """
        info_title("Active pairs in '{0}':".format(self.name))
        empty = True
        for a in self.active:
            info_list(str(a))
            empty = False
        if empty:
            info_list("No active pairs created")
            return False

    @public_process
    def mute(self):
        """
        cat: edit
        desc: mute an active pair
        """
        info_block("Choose an active pair to mute")
        act = self.choose('active')
        if act is not None:
            act.muted = True

    @public_process
    def unmute(self):
        """
        cat: edit
        desc: unmute an active pair
        """
        act = self.choose('active')
        act.muted = False

    @public_process
    def generate(self, reps=None):
        """
        desc: generate variable sampler output
        args:
            active name: name of active pair to generate
            reps: number of repetitions of active rhythm to generate
        """
        length = samps(inpt('beats'), RelGlobals.DEFAULT_SAMPLERATE)
        recs = []
        for a in self.active:
            if not a.muted:
                recs.append( a.generate_active(length) )
        mixed = mix_multiple(recs)
        mixed.playback()



    # Meta-functions & Helpers #
    def choose(self, attr, name=None):
        """
        get an object from attribute ('sample', 'rhythm', or 'active') by name
        """
        if attr == 'active':
            if name is None:
                if self.list_active() is False:
                    return
                print("  : ", end="")
                name = inpt('name')
            for i in self.active:
                if i.get_name() == name:
                    return i
            print("  > Name doesnt exist. Enter intended value (q to quit): ")
            return self.choose(attr)
        elif attr == "sample":
            if name is None:
                if self.list_samples() is False:
                    return
                print("  : ", end="")
                name = inpt('name')
            for i in self.smps:
                if i.get_name() == name:
                    return i
            print("  > Name doesnt exist. Enter intended value (q to quit): ")
            return self.choose(attr)
        elif attr == "rhythm":
            if name is None:
                if self.list_rhythms() is False:
                    return
                print("  : ", end="")
                name = inpt('name')
            for i in self.rhythms:
                if i.get_name() == name:
                    return i
            print("  > Name doesnt exist. Enter intended value (q to quit): ")
            return self.choose(attr)


    @public_process
    def save(self, silent=False):
        self.save_metadata(self.name, self.directory)






