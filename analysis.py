import matplotlib.pyplot as plt
from input_processing import *
from output_and_prompting import *
import numpy as np
from os.path import dirname
import math


class Analysis():
    """
    pass start and end as samples.
    pass modified analysis arr to plot, not orig rec
    """

    def __init__(self, rec=None, start=0, end=None):
        if rec is None:
            rec = Recording(parent=self)
        self.obj = rec
        self.rate = rec.rate

        self.start = start
        self.end = end
        if end is None:
            self.end = self.obj.size_samps()
        if self.end <= self.start:
            err_mess("End cannot be before or equal to start")
            raise Cancel

        self.arr = rec.arr[self.start:self.end]
        self.mono_arr = np.mean(self.arr, axis=1)
        self.samp_len = self.end - self.start
        self.sec_len = self.samp_len / self.rate
        self.average_amplitude = np.mean(np.abs(self.mono_arr))

        self.frame_length = None
        self.frame_step = None


    def set_frame_fractions(self, length_frac, step_frac=None):
        """
        set length and step of frames, in fracs of second. step frac defaulr 1/5
        """
        if step_frac is None:
            step_frac = 1/5
        self.set_frame_lengths(
            int(self.rate * length_frac),
            int(self.rate * step_frac)
        )

    def set_frame_lengths(self, length, step=None):
        """
        set frame length and step in raw samples. step default 1/5 of length
        """
        if step is None:
            step = 1/5 * length
        self.frame_length = max(int(length), 1)
        self.frame_step = max(int(step), 1)

    def maybe_playback(self):
        p("Playback before analyzing? [y/n]")
        playback_yn = inpt()
        if playback_yn:
            self.obj.playback()


    def plot(self, left, right=None, plot_type="line", fill=None, title=None):
        if left.shape[0] == 0:
            err_mess("No data to plot!")
        else:
            rel_plot(
                left, 
                start=self.start, 
                end=self.end, 
                rate=self.rate,
                right=right,
                fill=fill,
                plot_type=plot_type,
                title=title,
                obj_name=self.obj.name,
                obj_type=self.obj.type
            )


    def get_frames_left(self, **kwargs):
        info_block("Calculating left channel frames...")
        return self.get_frames(self.arr[:, 1], **kwargs)

    def get_frames_right(self, **kwargs):
        info_block("Calculating right channel frames...")
        return self.get_frames(self.arr[:, 1], **kwargs)

    def get_frames_mono(self, **kwargs):
        info_block("Calculating frames...")
        return self.get_frames(self.mono_arr, **kwargs)

    def get_frames(self, array, length_frac=None, step_frac=None, length=None, step=None):
        """
        take and average data from recording into frames.
        frame len defaults: 1/20, 1/100 secs
        """
        if self.frame_length is None:
            if length is not None:
                self.set_frame_lengths(length, step)
            else:
                if length_frac is not None:
                    self.set_frame_fractions(length_frac, step_frac)
                else:
                    self.set_frame_fractions(1/20, 1/100)

        frames = [] # start index, avg amplitude
        for i in range(0, self.samp_len - self.frame_length, self.frame_step):
            frame = array[ i : i + self.frame_length]
            frame_avg = np.mean(np.abs(frame))
            frames.append( (i + self.start, frame_avg) )

        return np.array(frames) # (start index, avg amplitude)

    def play_frame(self, samp_start, samp_dur=None):
        if samp_dur is None:
            samp_dur = self.frame_length
        sec_start = samp_start / self.rate
        dur = samp_dur / self.rate
        self.obj.playback(dur, sec_start)


    def find_peaks(self, frames):
        """
        returns peaks as (sample index, slope)
        """
        info_block("Finding peaks...")

        # find highest positive slopes between frames
        slopes = []
        frm_ind = 0
        while frm_ind < len(frames): # (index, avg amp)
            highest_slope = 0
            compare_ind = frm_ind + 1
            # get highest slope from this frame, with no dips in between
            while ( # while frame is highest than last and not past end
                    compare_ind < len(frames) ) and (
                    frames[compare_ind][1] > frames[compare_ind - 1][1]
                ):
                # 1000 is arbitrary, just to make the numbers nicer
                new_slope = 1000 * (frames[compare_ind][1] - frames[frm_ind][1]) / (compare_ind - frm_ind)
                highest_slope = new_slope if new_slope > highest_slope else highest_slope
                compare_ind += 1
            if highest_slope != 0:
                slopes.append((frames[frm_ind][0], highest_slope))
            frm_ind += 1

        return np.asarray(slopes)

    def filter_peaks(self, peaks):
        """
        returns peaks as (sample_index, slope)
        """
        info_block("Filtering peaks...")

        avg_slope = np.mean(peaks[:,1])
        peaks = peaks[peaks[:,1] >= avg_slope]

        sorted_peaks = NpOps.sort(peaks, 1)

        p_ind = 0
        while p_ind < sorted_peaks.shape[0]:
            comp_ind = p_ind + 1
            while comp_ind < sorted_peaks.shape[0]:
                comp_val = sorted_peaks[comp_ind][0]
                # remove smaller items. 4 seems to get them all
                if (comp_val - (5 * self.frame_length) <
                    sorted_peaks[p_ind][0] <
                    comp_val + (5 * self.frame_length)
                ):
                    sorted_peaks = np.delete(sorted_peaks, comp_ind, 0)
                else:
                    comp_ind += 1
            p_ind += 1

        return sorted_peaks # (sample_index, slope)







def decimal_precision_requires(float_val):
    """
    determine number of decimal places required to display
    data fully
    """
    float_val = str(float_val)
    # handle floating point rounding error
    float_val = re.sub(r"0000000.$", "", float_val)
    float_val = re.sub(r"9999999.$", "", float_val)
    no_trailing = str(float(float_val))
    decimal_ind = no_trailing.find(".")
    if decimal_ind is not -1:
        if no_trailing[0] != "0":
            minim = 2
        else:
            minim = 6
        return min(len(no_trailing) - decimal_ind - 1, minim)
    return 0





