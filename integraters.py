from recording_obj import *
from utility import *


"""


"""




def mix(rec1, rec2, mix_level=None, offset=0, name=None):
    """
    mix two recordings into new recording object
        offset (beat): rec2 will be this beats behind rec1
        mix_level: 0-1: post-mix amplification
    """
    section_head("Mixing '" + rec1.name + "' and '" + rec2.name + "' ...")
    if rec1.rate != rec2.rate:
        raise RateError("Two recordings must have the same sample rate to be mixed")
    offset = int(secs(offset) * rec1.rate)
    arr1 = rec1.get_panned_rec__()
    arr2 = rec2.get_panned_rec__()
    new_arr = []
    for i in range(max(rec1.size_samps(), offset + rec2.size_samps())):
        if rec1.size_samps() <= i < offset:
            amp = [0, 0]
        elif i >= rec1.size_samps():
            amp = arr2[i - offset]
        elif i >= rec2.size_samps():
            amp = arr1[i]
        elif i < offset:
            amp = arr1[i]
        else:
            amp = [arr1[i][0] + arr2[i - offset][0], \
                arr1[i][1] + arr2[i - offset][1]]
        new_arr.append(amp)
    source = ["mix", rec1.name + " with " + rec2.name]
    mix_rec = Recording(new_arr, source=source, name=name)
    if mix_level is not None:
        mix_rec.amplify(mix_level)
    return mix_rec



def mix_multiple(*args, mix_level=None, name=None):
    """
    Mix multiple recording objected together
        *args: Rec objects to mix, or list of lists as [rec obj, offset (beats)]
        mix_level: post-mix amplification
    """
    section_head("Mixing Multiple ...")
    rec1 = args[0]
    print(rec1)
    if isinstance(rec1, list):
        rec1 = args[0][0]
    print(rec1)
    for rec2 in args[1:]:
        offset2 = 0
        if isinstance(rec2, list):
            offset2 = rec2[1]
            rec2 = rec2[0]
        rec1 = mix(rec1, rec2, offset=offset2, name="mix multiple")
    if mix_level is not None:
        rec1.amplify(mix_level)
    rec1.rename()
    rec1.change_savefile()
    return rec1


def concatenate(*recs):
    """
    add rec2 directly to back of rec1
    """
    string = "Concatenating '" + recs[0].name + "'"
    arr = recs[0].get_panned_rec__()
    source = ["concatenation", recs[0].name]
    for i in recs[1:]:
        string += " and '" + i.name + "'"
        source[1] += " + " + i.name
        arr += i.get_panned_rec__()
    section_head(string)
    return Recording(array=arr, source=source)











def main_integration():
    """
    """
    infile, outfile = initialize()






if __name__ == "__main__":
    main_integration()