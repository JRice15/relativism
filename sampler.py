from recording_obj import *
from integraters import *
from generators import *
from name_and_path import *



"""

create sampler, add samples

set rhythms, frequencies

access any projects recs

"""




class Sample:
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

    def __init__(self, parent, rec=None, rec_source=None, on=False, start=0, name=None, savefile=None):
        self.parent = parent
        if rec is None:
            if rec_source is None:
                raise UnexpectedIssue
            self.rec = Recording(source=rec_source, name=name)
            self.source = ["sampled from Recording from", rec_source.split("/")[-1]]
        else:
            self.rec = Recording(
                    array=rec.arr,
                    source=["sampled from Recording named", rec.name],
                    name=name,
                    savefile=savefile
                )
        self.on = on
        self.start = start
        if self.rec.name is None:
            self.rec.rename()


    def __repr__(self):
        string = "'{0}'. Sample object from".format(self.rec.name)
        for ind in range(len(self.rec.source) // 2):
            string += " {0}: {1};".format(self.rec.source[2 * ind], self.rec.source[2 * ind + 1])
        return string

    def process(self):
        self.rec.process()

    def duplicate(self):
        new_sample = Sample(self.parent, self.rec)


    def update_name(self, old_name, new_name):
        """
        """
        self.parent.update_name(old_name, new_name)



class Rhythm:

    def __init__(self, name=None, length=None):
        print("  Creating a rhythm")
        self.name = None
        self.length = length
        self.parts = {}
        if self.name is None:
            self.rename()        
        if self.length is None:
            self.choose_len()
        self.create_parts(self.length)


    def rename(self):
        print("  Enter a name for this Rhythm: ", end="")
        self.name = input().lower().strip()

    def choose_len(self):
        while True:
            print("  Enter a length (in beats) for this rhythm: ", end="")
            try:
                self.length = int(input().strip())
                break
            except ValueError:
                print("  > enter a number for length in beats")

    def create_parts(self, length):
        """
        length in number of beats
        """
        print("  Creating a new rhythm ('d', for done)")
        self.part_options()
        parts = {}
        i = 0
        while True:
            print("  Enter a part ('d' for done, 'o' for options again):")
            new_part = input().lower().strip().split()
            if new_part[0] in ("d", "done"):
                print("  Done creating rhythm")
                break
            if "beat_info" in new_part:
                beat_options()
            elif new_part[0] in ("o", "options"):
                self.part_options()
            else:
                try:
                    self.verify_part(new_part)
                    parts[new_part[0]] = new_part[1:]
                except someError:
                    print("  part is not properly formatted")

    def part_options(self):
        print("  Format for each part:")
        print("    <n> <w> <v> <b...>")
        print("    - Name (n): name/id of this part (will overwrite if already exists in this rhythm)")
        print("    - Weight (w): number 1-4, 1 being frequent, 4 being infrequent")
        print("    - Variability (v) 1-10, 10 is most variable")
        print("    - Beats (b): one or more space-seperated beats ('beat_info' for more info)")


    def verify_part(self, part):
        """
        verify part as well formatted
        """



class Sampler:
    """
    Attr:
        dir: directory
        name: name
        smps (dict): [name, Sample] pairs of its samples
    """

    def __init__(self, name, directory, BPM=None):
        print("\n* Initializing sampler")
        self.dir = directory
        self.name = name
        self.smps = {}
        self.rhythms = {}
        self.BPM = BPM


    def set_BPM(self, BPM=None):
        if BPM is not None:
            self.BPM = BPM
        else:
            try:
                print("  Enter a BPM: ", end="")
                BPM = int(input().strip())
                self.BPM = BPM
            except ValueError:
                self.set_BPM()


    def add_sample(self):
        """
        add a sample from file, project, or another sampler
        """
        print("\n  Where would you like to select your sample from:")
        sample_mode = "not implemented"
        while sample_mode not in ("f", "p", "s", "q"):
            if sample_mode == "q":
                raise Cancel
            print("  File on disk (F), a Project object (P), or another Sampler object (S)?")
            print("  : ", end="")
            sample_mode = input().strip().lower()
        if sample_mode == "f":
            print("  Choose the file to sample...")
            time.sleep(1)
            root = tk.Tk()
            root.withdraw()
            samp_path = filedialog.askopenfilename(initialdir = os.getcwd(), title = "Choose a sample")
            if samp_path == "":
                raise NoPathError
            new_samp = Sample(self, rec_source=samp_path)
            self.smps[new_samp.rec.name] = new_samp
        else:
            # add other ways
            pass


    def list_samples(self):
        print("\n  Samples loaded into '{0}':".format(self.name))
        for name, obj in self.smps.items():
            print("    " + str(obj))


    def update_name(self, obj, old_name, new_name):
        """
        """
        self.smps[new_name] = obj
        try:
            del self.smps[old_name]
        except:
            pass

    def create_rhythm(self):
        new_rhythm = Rhythm()

    
    def save_rhythm_to_rec(self):
        pass




def main_sampler():
    """
    """
    print("* Initializing Sampler")
    proj_name, proj_dir, open_mode = NameAndPath.namepath_init("sampler")
    if open_mode == "c":
        smp = Sampler(proj_name, proj_dir)
        smp.add_sample()
    else:
        # read data of project from file of some sort
        pass


def quick_main():
    smp = Sampler("test1", "test1")
    smp.add_sample()
    smp.add_sample()
    smp.list_samples()



if __name__ == "__main__":
    #main_sampler()
    quick_main()