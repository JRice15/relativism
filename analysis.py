import matplotlib.pyplot as plt
from input_processing import *
from output_and_prompting import *
import numpy as np
from os.path import dirname
import math
import pylab



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


    def plot(self, left, right, fill=False):
        """
        left and right as shape (x, 2) arrays of (index, value) to plot
        """
        info_block("Generating plot...")
        fig = pylab.gcf()
        fig.canvas.set_window_title("Waveform of {0} '{1}'".format(self.obj.type, self.obj.name))

        # left: top, beats labels
        axL = plt.subplot(211)
        pos = axL.get_position()
        pos.y0 -= 0.06
        pos.y1 -= 0.06
        axL.set_position(pos)
        axL.xaxis.tick_top()
        axL.xaxis.set_label_position('top')

        start_beats, _ = whole_beats(self.start / self.rate)
        end_beats, _ = whole_beats(self.end / self.rate)
        tick_size_beats = 1
        tick_number = end_beats - start_beats
        if tick_number < 2:
            start_beats = beats(self.start / self.rate)
            end_beats = beats(self.end / self.rate)
            tick_size_beats = end_beats - start_beats
            tick_number = 1
        while tick_number > 10:
            tick_number /= 2
            tick_size_beats *= 2
        while tick_number < 5:
            tick_number *= 2
            tick_size_beats /= 2
        tick_locs = []
        tick_labels = []
        decimals = 2
        for _ in range(int(math.log((0.05 / tick_size_beats)))):
            decimals += 1
        for i in np.linspace(start_beats, end_beats, tick_number, endpoint=False):
            tick_locs.append(i)
            axL.axvline(i, linestyle="--", linewidth=0.3, color='#545454', clip_on=False)
            tick_labels.append("{0:.{1}f}".format(i, decimals))
        plt.xticks(tick_locs, tick_labels)
        for tick in axL.xaxis.get_major_ticks()[1::2]:
            tick.set_pad(15)

        plt.xlabel("Beats")
        plt.ylabel("Left amplitude")
        if len(left.shape) == 1:
            valuesL = left
            indexesL = range(self.start, self.start + len(left))
        else:
            indexesL, valuesL = zip(*left)
        indexesL = [beats(i/self.rate) for i in indexesL]
        plt.plot(indexesL, valuesL)

        # right: bottom, seconds labels
        axR = plt.subplot(212)
        plt.xlabel("Seconds")
        plt.ylabel("Right amplitude")
        if len(right.shape) == 1:
            valuesR = right
            indexesR = range(self.start, self.start + len(right))
        else:
            indexesR, valuesR = zip(*right)
        indexesR = [i/self.rate for i in indexesR]
        for i in np.linspace(start_beats, end_beats, tick_number, endpoint=False):
            ind = secs(str(i) + "b")
            axR.axvline(ind, linestyle="--", linewidth=0.3, color='#545454', clip_on=False)
        plt.plot(indexesR, valuesR)

        info_block("Viewing waveform...")
        # plt.rcParams['agg.path.chunksize'] = 99999999999999999
        if fill and len(indexesR) < 1_000_000:
            axR.fill_between(indexesR, valuesR, color='#43C6FF')
            axL.fill_between(indexesL, valuesL, color='#43C6FF')
        plt.show()


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



    def play_samps(self, samp_start, samp_dur):
        sec_start = samp_start / self.rate
        dur = samp_dur / self.rate
        self.obj.playback(dur, sec_start)



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


