from recording_obj import *
from integraters import *
from generators import *
from name_and_path import *



"""

create sampler, add samples

set rhythms, frequencies

access any projects recs

"""




class Sample(Recording):
    """
    creates new Recording object from given, wraps in some Sample data
    Attributes:
        parent (Sampler): sampler object containing this
        rec (Recording): recording object
        on (bool)
        start (samples index)
        savefile
    name is attr of Rec obj
    if rec is not given, rec_source is required
    """

    # Initialization #
    def __init__(self, array=None, source=None, name=None, rate=44100, \
            parent=None):
        super().__init__(array=array, source=source, name=name, rate=rate,
            parent=parent, type_='Sample')


    def __repr__(self):
        string = "'{0}'. Sample object from".format(self.name)
        for ind in range(len(self.source) // 2):
            string += " {0}: {1};".format(self.source[2 * ind], self.source[2 * ind + 1])
        return string

    def get_name(self):
        return self.name

    def process__(self):
        process(self)

    def process_rec(self):
        process(self)

    def duplicate(self):
        new_sample = Sample(array=self.arr, source=self.source, rate=self.rate, \
            parent=self.parent)
        self.parent.add_sample(new_sample)

    def add_to_sampler(self, sampler_obj):
        sampler_obj.add_sample(self)

    def save(self):
        try:
            self.parent.save_child__(self)
        except (AttributeError, NotImplementedError):
            err_mess("Parent {0} '{1}' has not implemented save feature".format(
                self.parent.type, self.parent.get_name()))



class Rhythm:

    def __init__(self, parent=None, name=None, sample=None):
        print("\n* Initializing Rhythm")
        self.done_init = False
        self.parent = parent
        self.sample = sample
        self.type = 'Rhythm'
        self.name = name
        if name is None:
            self.rename()
        self.variability = None
        self.period = None
        self.length = None
        self.beats = [] # [place, length, start]

        print("\n  * Setting Rhythm attributes ('q' to cancel any time)")
        self.set_length()
        self.set_variability()
        self.set_period()
        self.done_init = True

    def __repr__(self):
        return "'{0}', Rhythm object. Variability {1}, Length {2} beats. {3} children beats are loaded".format(self.get_name(), self.variability, self.length, len(self.beats))

    def beat_repr__(self, beat):
        return "place: {0}, length: {1}, start: {2}".format(beat[0], beat[1], beat[2])

    def get_name(self):
        return self.name

    def info(self):
        raise NotImplementedError

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

    def rename(self, name=None):
        if name is None:
            print("  Enter a name for this Rhythm: ", end="")
            name = inpt("obj")
        else:
            name = inpt_process(name, 'obj')
        self.name = name
        print("  named '" + name + "'")

    def set_length(self, length=None):
        if length is None:
            p("Enter a number for the length in beats of this Rhythm")
            self.length = inpt('int')
        else:
            self.length = inpt_process(length, 'int')

    def set_variability(self, var=None):
        if var is None:
            p("Enter the variability (in percentage, 0-100%) of this Rhythm")
            self.variability = inpt('pcnt')
        else:
            self.variability = inpt_process(var, 'pcnt')

    def set_period(self, period=None):
        if period is None:
            p("Enter the period, or smallest beat/note that this Rhythm usually lands on, as " +\
                "a beat", i="for info on creating properly formed beats")
            self.period = inpt('beat', catch="i", catch_callback=beat_options)
        else:
            self.period = inpt_process(period, "beat")

    def add_beats(self):
        """
        create beats through prompts or pass 'beat' param to set
        """
        print("  Creating new Rhythm '{0}'".format(self.name))
        while True:
            info_block(
                "Enter a beat as <place in rhythm> <optional: length> <optional: start in sample> ('q' to finish, 'i' for more info)",
                indent=2,
                hang=2,
                trailing_newline=False
            )
            print("  : ", end="")
            try:
                new_beat = inpt("split", "beat", catch="i", catch_callback=self.rhythms_help)
            except Cancel:
                print("\n  Done creating Rhythm '{0}'".format(self.name))
                return
            if not (1 <= len(new_beat) <= 3):
                print("  > Wrong number of arguments! From 1 to 3 are required, {0} were supplied".format(len(new_beat)))
                continue
            if t(60, new_beat[0]) >= t(60, str(self.length) + 'b'):
                print("  > This beat begins after the end of the rhythm! Try again")
                continue
            
            self.beats.append(new_beat)

            while len(new_beat) < 3:
                new_beat.append(0)
            if new_beat[1] == 0:
                new_beat[1] = "all"
            print("  Added beat - " + self.beat_repr__(new_beat))

    def delete_beats(self):
        raise NotImplementedError

    def list_beats(self):
        sorted_beats = selection_sort(self.beats, ind=0, func_on_val=t, func_args=[60, 'val'], low_to_high=True)
        for i in sorted_beats:
            info_block("- " + self.beat_repr__(i), newlines=False)

    def save(self):
        try:
            self.parent.save_child__(self)
        except (AttributeError, NotImplementedError):
            info_block("Parent {0} '{1}' has not implemented save feature".format(
                self.parent.type, self.parent.get_name()))


class Active:

    def __init__(self, parent, act_rhythm, act_sample, muted=None):
        print("\n* Initializing active pair")
        self.rhythm = act_rhythm
        self.sample = act_sample
        self.muted = muted
        self.name = None
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

    def rename(self, name=None):
        if name is None:
            print("  Give this active pair a name: ", end="")
            name = inpt("obj")
            print("  named '{0}'".format(name))
        else:
            name = inpt_process(name, "obj")
        self.name = name

    def get_name(self):
        return self.name



class Sampler:
    """
    Attr:
        dir: directory
        name: name
        smps (list): [Samples]
        rhythms (list): [Rhythms]
        active (list): [Active]
        BPM (float): float
    """

    def __init__(self, name, directory, BPM=None):
        print("\n* Initializing sampler")
        self.type = 'Sampler'
        self.directory = directory
        self.name = name
        self.smps = []
        self.rhythms = []
        self.active = []
        self.BPM = BPM


    # Representation #
    def __repr__(self):
        raise NotImplementedError


    def info(self):
        raise NotImplementedError


    def get_name(self):
        return self.name


    def set_bpm(self, BPM=None):
        if BPM is not None:
            self.BPM = inpt_process(BPM, "flt", allowed=[1, 9999])
        else:
            self.BPM = inpt("flt", allowed=[1, 9999])


    # Handling Samples #
    def add_sample(self, new_samp=None):
        """
        add a sample from file, project, or another sampler
        """
        if not isinstance(new_samp, Sample):
            print("\n  Where would you like to select your sample from:")
            sample_mode = "not implemented"
            while sample_mode not in ("f", "p", "s", "q"):
                if sample_mode == "q":
                    raise Cancel
                print("  File on disk (F), a Project object (P), or another Sampler object (S)?")
                print("  : ", end="")
                sample_mode = inpt("letter", allowed='fps')
            if sample_mode == "f":
                print("  Choose the file to sample...")
                time.sleep(1)
                root = tk.Tk()
                root.withdraw()
                samp_path = filedialog.askopenfilename(initialdir = os.getcwd(), title = "Choose a sample")
                if samp_path == "":
                    raise NoPathError
                new_samp = Sample(self, rec_source=samp_path)
            else:
                # add other ways
                raise NotImplementedError
        self.smps.append(new_samp)
        self.list_samples()
        print("") #newline
        p("Process this sample? y/n")
        if inpt("yn"):
            process(new_samp)


    def edit_sample(self):
        while True:
            print("\n  Which sample would you like to edit? ('q' to cancel, 'list' to list samples): ", end="")
            try:
                sample = self.choose__("sample")
                sample.process()
            except Cancel:
                continue


    def list_samples(self):
        print("\n  Samples loaded into '{0}':".format(self.name))
        empty = True
        for obj in self.smps:
            info_list(str(obj))
            empty = False
        if empty:
            info_block("No samples loaded")
            return False


    # Handling Rhythms #
    def add_rhythm(self, new_rhythm=None):
        if not isinstance(new_rhythm, Rhythm):
            p("Create new rhythm (C) or Load from another sampler (L)?")
            source = inpt("letter", allowed="cl")
            if source == 'c':
                new_rhythm = Rhythm()
            else:
                # load from sampler
                raise NotImplementedError

        if new_rhythm.done_init:
            self.rhythms.append(new_rhythm)
            self.list_rhythms()
            p("Process this rhythm? y/n")
            if inpt("yn"):
                try:
                    process(new_rhythm)
                except Cancel:
                    pass
    

    def edit_rhythm(self):
        rhythm = self.choose__("rhythm")
        process(rhythm)


    def list_rhythms(self):
        print("\n  Rhythms loaded into '{0}':".format(self.name))
        empty = True
        for obj in self.rhythms:
            empty = False
            info_list(str(obj))
        if empty:
            info_block("No rhythms loaded")
            return False


    # Handling Active #
    def activate(self, act_rhythm=None, act_sample=None):
        if not isinstance(act_rhythm, Rhythm):
            p("Choose a rhythm for this active pair")
            act_rhythm = self.choose__('rhythm')
        if not isinstance(act_sample, Sample):
            p("Choose a sample for this active pair")
            act_sample = self.choose__('sample')
        new_active = Active(self, act_rhythm, act_sample)
        self.active.append(new_active)


    def list_active(self):
        info_title("Active pairs in '{0}':".format(self.name))
        empty = True
        for a in self.active:
            info_list(str(a))
            empty = False
        if empty:
            info_list("No active pairs created")
            return False


    def mute(self):
        """
        mute an active pair
        """
        info_block("Choose an active pair to mute")
        act = self.choose__('active')
        if act is not None:
            act.muted = True


    def unmute(self):
        """
        unmute an active pair
        """
        act = self.choose__('active')
        act.muted = False


    # Generating #
    def generate(self):
        p("Choose an integer number for length in beats to generate")
        beats = inpt("int", allowed=[0, None])
        generated_active = []
        for a in self.active:
            if not a.muted:
                generated_active.append(simple_generate(a, beats))
        final = mix_multiple(generated_active)
        final.playback()


    # Meta-functions & Helpers #
    def choose__(self, attr, name=None):
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
            return self.choose__(attr)
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
            return self.choose__(attr)
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
            return self.choose__(attr)


    def save_rhythm_to_rec(self):
        raise NotImplementedError


    def processes(self):
        raise NotImplementedError


    def process__(self):
        process(self)


    def save_child__(self, child):
        filename = child.type.lower() + "_" + child.get_name() + ".rel-obj"
        write_obj(child, filename, self.directory)


    def save(self):
        raise NotImplementedError




def simple_generate(active, length):
    rhyth = active.rhythm
    smp = active.sample
    reps = math.ceil(length / rhyth.length)
    beats_to_mix = []
    for i in rhyth.beats:
        offset = i[0]
        beats_to_mix.append([smp.rec, offset])
    mixed = mix_multiple(beats_to_mix)
    return mixed



def generate_part(part, length):
    reps = math.ceil(length / part.length)
    for i in part.active:
        pass






def create_sampler():
    """
    """
    print("* Initializing Sampler")
    proj_name, proj_dir, open_mode = namepath_init("sampler")
    if open_mode == "c":
        smp = Sampler(proj_name, proj_dir)
    else:
        # read data of project from file of some sort
        pass
    return smp


def quick_main():
    s = create_sampler()
    process(s)



if __name__ == "__main__":
    quick_main()