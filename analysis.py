import matplotlib.pyplot as plt
from input_processing import *
from output_and_prompting import *


class Analysis():

    def __init__(self, rec=None):
        if rec is None:
            rec = Recording(parent=self)
        self.rec = rec
        self.arr = rec.arr
        self.mono_arr = [(i + j) / 2 for i, j in rec.arr]
        self.rate = rec.rate
        self.samp_len = rec.size_samps()
        self.average_amplitude = average(self.mono_arr)

        self.frame_length = None
        self.frame_step = None


    def set_frame_fractions(self, length_frac, step_frac):
        """
        set length and step of frames, in fracs of second
        """
        self.frame_length = int(self.rate * length_frac)
        self.frame_step = int(self.rate * step_frac)


    def maybe_playback(self):
        p("Playback before analyzing? [y/n]")
        playback_yn = inpt()
        if playback_yn:
            self.rec.playback()


    def get_frames(self, length_frac=None, step_frac=None):
        """
        take and average data from recording into frames
        """
        info_block("Calculating frames")
        if self.frame_length is None:
            self.set_frame_fractions(length_frac, step_frac)

        frames = [] # start index, avg amplitude
        for i in range(0, self.samp_len - self.frame_length, self.frame_step): 
            frame = self.mono_arr[ i : i + self.frame_length]
            frame = numpy.take(frame, range(len(frame)))
            frame_avg = average([abs(j) for j in frame])
            if frame_avg > self.average_amplitude:
                frames.append( (i, frame_avg) )

        return frames # (start index, avg amplitude)



    def play_samps(self, samp_start, samp_dur):
        sec_start = samp_start / self.rate
        dur = samp_dur / self.rate
        self.rec.playback(dur, sec_start)



    def find_peaks(self, frames):
        """
        """
        info_block("Finding peaks")

        # find highest positive slopes between frames
        slopes = []
        frm_ind = 0
        while frm_ind < len(frames): # (index, avg amp)
            highest_slope = 0
            compare_ind = frm_ind + 1
            # get highest slope from this frame, with no dips in between
            while (
                    compare_ind < len(frames) ) and (
                    frames[compare_ind] > frames[compare_ind - 1]
                ):
                # 1000 is arbitrary, just to make the numbers nicer
                new_slope = 1000 * (frames[compare_ind][1] - frames[frm_ind][1]) / (compare_ind - frm_ind)
                highest_slope = new_slope if new_slope > highest_slope else highest_slope
                compare_ind += 1
            if highest_slope != 0:
                slopes.append((frames[frm_ind][0], highest_slope))
            frm_ind += 1

        indexes = [i[0] for i in slopes]
        values = [i[1] for i in slopes]
        plt.plot(indexes, values)
        plt.show()



def average(the_list):
    """
    average items of a list
    """
    return sum(the_list) / len(the_list)


def super_sort(the_list, ind=None, ind2=None, high_to_low=False):
    """
    list, index1, index2, reverse.
    sorted by list[ind1][ind2] keys, for given indexs
    """
    if ind != None:
        if ind2 != None:
            return sorted(the_list, key=lambda i: i[ind][ind2], reverse=high_to_low)
        return sorted(the_list, key=lambda i: i[ind], reverse=high_to_low)
    return sorted(the_list, reverse=high_to_low)


