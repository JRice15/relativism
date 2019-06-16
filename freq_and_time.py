"""
http://pages.mtu.edu/~suits/notefreqs.html

"""

import re







def f(note):
    """
    returns frequency of note as int
    raises NotANoteError if note name is misformed
    C0-B8 is hard coded, above or below (not recommended anyway) is extrapolated
    Args:
        note: freq as string or name of note in C#1 or Db1 notation
    Returns:
        int: frequency
    """
    # note is number already, in any form
    try:
        return float(note)
    except:
        pass
    note = note.lower().strip()
    # if note is not formed properly
    if re.match(r"^[a-g][b#]{0,1}([0-9]|10)$", note) == None:
        print("Note '{0}' is not properly formed or out of octave range 0-10".format(note))
        raise TypeError
    # note is regular
    return get_freq(note)


def get_freq(note):
    freq_arr = [
        ["c0", 16.35],
        ["c#0", 17.32],
        ["db0", 17.32],
        ["d0", 18.35],
        ["d#0", 19.45],
        ["eb0", 19.45],
        ["e0", 20.60],
        ["f0", 21.83],
        ["f#0", 23.12],
        ["gb0", 23.12],
        ["g0", 24.50],
        ["g#0", 25.96],
        ["ab0", 25.96],
        ["a0", 27.50],
        ["a#0", 29.14],
        ["bb0", 29.14],
        ["b0", 30.87],
        ["c1", 32.70],
        ["c#1", 34.65],
        ["db1", 34.65],
        ["d1", 36.71],
        ["d#1", 38.89],
        ["eb1", 38.89],
        ["e1", 41.20],
        ["f1", 43.65],
        ["f#1", 46.25],
        ["gb1", 46.25],
        ["g1", 49.00],
        ["g#1", 51.91],
        ["ab1", 51.91],
        ["a1", 55.00],
        ["a#1", 58.27],
        ["bb1", 58.27],
        ["b1", 61.74],
        ["c2", 65.41],
        ["c#2", 69.30],
        ["db2", 69.30],
        ["d2", 73.42],
        ["d#2", 77.78],
        ["eb2", 77.78],
        ["e2", 82.41],
        ["f2", 87.31],
        ["f#2", 92.50],
        ["gb2", 92.50],
        ["g2", 98.00],
        ["g#2", 103.83],
        ["ab2", 103.83],
        ["a2", 110.00],
        ["a#2", 116.54],
        ["bb2", 116.54],
        ["b2", 123.47],
        ["c3", 130.81],
        ["c#3", 138.59],
        ["db3", 138.59],
        ["d3", 146.83],
        ["d#3", 155.56],
        ["eb3", 155.56],
        ["e3", 164.81],
        ["f3", 174.61],
        ["f#3", 185.00],
        ["gb3", 185.00],
        ["g3", 196.00],
        ["g#3", 207.65],
        ["ab3", 207.65],
        ["a3", 220.00],
        ["a#3", 233.08],
        ["bb3", 233.08],
        ["b3", 246.94],
        ["c4", 261.63],
        ["c#4", 277.18],
        ["db4", 277.18],
        ["d4", 293.66],
        ["d#4", 311.13],
        ["eb4", 311.13],
        ["e4", 329.63],
        ["f4", 349.23],
        ["f#4", 369.99],
        ["gb4", 369.99],
        ["g4", 392.00],
        ["g#4", 415.30],
        ["ab4", 415.30],
        ["a4", 440.00],
        ["a#4", 466.16],
        ["bb4", 466.16],
        ["b4", 493.88],
        ["c5", 523.25],
        ["c#5", 554.37],
        ["db5", 554.37],
        ["d5", 587.33],
        ["d#5", 622.25],
        ["eb5", 622.25],
        ["e5", 659.25],
        ["f5", 698.46],
        ["f#5", 739.99],
        ["gb5", 739.99],
        ["g5", 783.99],
        ["g#5", 830.61],
        ["ab5", 830.61],
        ["a5", 880.00],
        ["a#5", 932.33],
        ["bb5", 932.33],
        ["b5", 987.77],
        ["c6", 1046.50],
        ["c#6", 1108.73],
        ["db6", 1108.73],
        ["d6", 1174.66],
        ["d#6", 1244.51],
        ["eb6", 1244.51],
        ["e6", 1318.51],
        ["f6", 1396.91],
        ["f#6", 1479.98],
        ["gb6", 1479.98],
        ["g6", 1567.98],
        ["g#6", 1661.22],
        ["ab6", 1661.22],
        ["a6", 1760.00],
        ["a#6", 1864.66],
        ["bb6", 1864.66],
        ["b6", 1975.53],
        ["c7", 2093.00],
        ["c#7", 2217.46],
        ["db7", 2217.46],
        ["d7", 2349.32],
        ["d#7", 2489.02],
        ["eb7", 2489.02],
        ["e7", 2637.02],
        ["f7", 2793.83],
        ["f#7", 2959.96],
        ["gb7", 2959.96],
        ["g7", 3135.96],
        ["g#7", 3322.44],
        ["ab7", 3322.44],
        ["a7", 3520.00],
        ["a#7", 3729.31],
        ["bb7", 3729.31],
        ["b7", 3951.07],
        ["c8", 4186.01],
        ["c#8", 4434.92],
        ["db8", 4434.92],
        ["d8", 4698.63],
        ["d#8", 4978.03],
        ["eb8", 4978.03],
        ["e8", 5274.04],
        ["f8", 5587.65],
        ["f#8", 5919.91],
        ["gb8", 5919.91],
        ["g8", 6271.93],
        ["g#8", 6644.88],
        ["ab8", 6644.88],
        ["a8", 7040.00],
        ["a#8", 7458.62],
        ["bb8", 7458.62],
        ["b8", 7902.13],
        ["c9", 4186.01 * 2],
        ["c#9", 4434.92 * 2],
        ["db9", 4434.92 * 2],
        ["d9", 4698.63 * 2],
        ["d#9", 4978.03 * 2],
        ["eb9", 4978.03 * 2],
        ["e9", 5274.04 * 2],
        ["f9", 5587.65 * 2],
        ["f#9", 5919.91 * 2],
        ["gb9", 5919.91 * 2],
        ["g9", 6271.93 * 2],
        ["g#9", 6644.88 * 2],
        ["ab9", 6644.88 * 2],
        ["a9", 7040.00 * 2],
        ["a#9", 7458.62 * 2],
        ["bb9", 7458.62 * 2],
        ["b9", 7902.13 * 2],
        ["c10", 4186.01 * 4],
        ["c#10", 4434.92 * 4],
        ["db10", 4434.92 * 4],
        ["d10", 4698.63 * 4],
        ["d#10", 4978.03 * 4],
        ["eb10", 4978.03 * 4],
        ["e10", 5274.04 * 4],
        ["f10", 5587.65 * 4],
        ["f#10", 5919.91 * 4],
        ["gb10", 5919.91 * 4],
        ["g10", 6271.93 * 4],
        ["g#10", 6644.88 * 4],
        ["ab10", 6644.88 * 4],
        ["a10", 7040.00 * 4],
        ["a#10", 7458.62 * 4],
        ["bb10", 7458.62 * 4],
        ["b10", 7902.13 * 4],
    ]
    # if note is wrong sharp/flat (ie E#)
    note = re.sub("e#", "f", note)
    note = re.sub("fb", "e", note)
    note = re.sub("b#", "c", note)
    note = re.sub("cb", "b", note)
    for i in freq_arr:
        if i[0] == note:
            return i[1]
    raise UnexpectedIssue


def t(BPM, note):
    """
    get time from beat-appreviation
    """
    ### check validity here
    note = note.lower().strip()
    if re.match(r"^[0-9]*[a-z]{1,2}$", note) is None:
        raise TypeError
    sec_per_beat = 60 / BPM
    frac = get_beat_frac(note)
    return frac * sec_per_beat



def get_beat_frac(note):
    note_fracs = [
        ["sf", 1/16, "sixty-fourth note"],
        ["ts", 1/8, "thirty-second note"],
        ["s", 1/4, "sixteenth note"],
        ["e", 1/2, "eighth note"],
        ["q", 1, "quarter note"],
        ["h", 2, "half note"],
        ["w", 4, "whole note (always 4 quarter notes)"]
    ]
    beat_fracs = [
        ["sb", 1/16, "sixteenth of a beat"],
        ["eb", 1/8, "eighth of a beat"],
        ["qb", 1/4, "quarter of a beat"],
        ["hb", 1/2, "half of a beat"],
        ["b", 1, "one beat"],
    ]
    for i in note_fracs:
        if note == i[0]:
            return i[1]
    for i in beat_fracs:
        if note == i[0]:
            return i[1]
    raise TypeError




def beat_options():
    note_fracs = [
        ["sf", 1/16, "sixty-fourth note"],
        ["ts", 1/8, "thirty-second note"],
        ["s", 1/4, "sixteenth note"],
        ["e", 1/2, "eighth note"],
        ["q", 1, "quarter note"],
        ["h", 2, "half note"],
        ["w", 4, "whole note (always 4 quarter notes)"]
    ]
    beat_fracs = [
        ["sb", 1/16, "sixteenth of a beat"],
        ["eb", 1/8, "eighth of a beat"],
        ["qb", 1/4, "quarter of a beat"],
        ["hb", 1/2, "half of a beat"],
        ["b", 1, "one beat"],
        ["", "", ""],
        ["", "", ""]
    ]
    print("\n  There are two methods of signifying beat lengths:\n")
    for i in range(7):
        print("    ", note_fracs[i][0], note_fracs[i][2], "|", beat_fracs[i][0], beat_fracs[i][2])




if __name__ == "__main__":
    beat_options()