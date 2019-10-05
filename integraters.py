from recording_obj import *
from utility import *


"""


"""




def mix(rec1, rec2, mix_level=None, offset=0, name=None):
    """
    mix two recordings into new recording object
        offset (beat/sec): rec2 will be this beats behind rec1
        mix_level: 0-1: post-mix amplification
    """
    section_head("Mixing '" + rec1.name + "' and '" + rec2.name + "' ...")
    if rec1.rate != rec2.rate:
        raise RateError("Two recordings must have the same sample rate to be mixed")
    offset = samps(offset)
    arr1 = rec1.get_panned_rec__()
    arr2 = rec2.get_panned_rec__()
    total_length = arr1.shape[0] if arr1.shape[0] > offset + arr2.shape[0] else arr2.shape[0]
    # mixing
    mix_arr = np.zeros((total_length, 2))
    mix_arr[ 0 : arr1.shape[0]] = arr1
    mix_arr[ offset : offset + arr2.shape[0]] = arr2
    mix_arr *= mix_level
    # format
    source = ["mix", rec1.name + " with " + rec2.name]
    mix_rec = Recording(mix_arr, source=source, name=name)
    return mix_rec



def mix_multiple(*args, mix_level=None, name=None):
    """
    Mix multiple recording objected together
        *args: Rec objects to mix, or list of lists as [rec obj, offset (beat/sec)]
        mix_level: post-mix amplification
    """
    section_head("Mixing Multiple ...")
    rec1 = args[0]
    if isinstance(rec1, (list, tuple)):
        rec1 = args[0][0]
    for rec2 in args[1:]:
        offset2 = 0
        if isinstance(rec2, (list, tuple)):
            offset2 = rec2[1]
            rec2 = rec2[0]
        rec1 = mix(rec1, rec2, offset=offset2, name="mix multiple")
    if mix_level is not None:
        rec1.amplify(mix_level)
    rec1.rename()
    return rec1



def concatenate(*recs):
    """
    add rec2 directly to back of rec1
    """
    string = "Concatenating '" + recs[0].name + "'"
    source = ["concatenation", recs[0].name]
    for i in recs[1:]:
        string += " and '" + i.name + "'"
        source[1] += " + " + i.name
    section_head(string)
    arr = np.concatenate([i.get_panned_rec() for i in recs])
    return Recording(array=arr, source=source)











def main_integration():
    """
    """
    infile, outfile = initialize()






if __name__ == "__main__":
    main_integration()