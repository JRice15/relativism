from contextlib import contextmanager
import sys
import os
import time
import timeit
import functools
import numpy as np
import pylab
import matplotlib.pyplot as plt
import re




@contextmanager
def suppress_output(err_log_name="relativism_errors.log"):
    """
    usage:
    with suppress_output():
        <suppressed zone>
    errors written to err log
    """
    with open(os.devnull, "w") as devnull:
        with open(err_log_name, "w") as errlog:
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = devnull
            sys.stderr = errlog
            try:  
                yield
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr


@contextmanager
def time_this(process=''):
    t1 = time.time()
    try:
        yield
    finally:
        t2 = time.time()
        print("{0} Took {1:.4f} seconds".format(process, t2-t1))


def timeit_(func, args, reps=1000, times=7):
    time = min(timeit.Timer(functools.partial(func, *args)).repeat(times, reps))
    print("{0} took {1}".format(func.__name__, time))


def decimal_format(val):
    val = "{0:.5f}".format(val)
    val = re.sub(r"0+$", "", val)
    val = re.sub(r"\.$", "", val)
    return val


class Colors:
    """ ANSI color codes """
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"


@contextmanager
def style(*styles):
    try:
        if len(styles) == 1:
            styles = styles[0].split(',')
        for s in styles:
            s = s.upper().strip()
            try:
                print(getattr(Colors, s), end='')
            except:
                err_mess("No style {0} exists".format(s))
        yield
    finally:
        print(Colors.END, end='')


class NpOps:
    """
    custom helpful numpy operations
    """

    @staticmethod
    def stereoify(arr):
        """
        turn [0, 1, 2] into [ [0, 0], [1, 1], [2, 2] ]
        """
        transpose = arr.reshape(-1, 1)
        return np.hstack((transpose, transpose))

    @staticmethod
    def monoify(arr):
        return np.mean(arr, axis=1)

    @staticmethod
    def get_channels(arr):
        return arr[:,0], arr[:1]

    @staticmethod
    def join_channels(left, right):
        return np.vstack((left, right)).T

    @staticmethod
    def swap_channels(arr):
        arr[:,[0, 1]] = arr[:,[1, 0]]
        return arr

    @staticmethod
    def sort(array, column=0, high_to_low=True):
        """
        sort by column. must set array variable equal to this call 
        (np arrays not mutable)
        """
        if high_to_low:
            return array[array[:, column].argsort()][::-1]
        else:
            return array[array[:, column].argsort()]

    @staticmethod
    def column_min(arr, column=0):
        return arr[:,column].min()

    @staticmethod
    def column_max(arr, column=0):
        return arr[:,column].max()

    @staticmethod
    def set_indexes(arr, values_to_set):
        """
        set indexes of array in (index, value) pair forms with another array
        """
        indexes = np.intersect1d(arr[:,0], values_to_set[:,0], assume_unique=True, return_indices=True)
        arr[indexes[1]] = values_to_set[indexes[2]]
        return arr


def selection_sort(unsorted, ind, top_n=None, func_on_val=int, func_args=['val'], low_to_high=False):
    """
    func args as array of args, where 'val' is replaced with the value to sort on
    """
    if top_n is None:
        top_n = len(unsorted)
    sorted_final = []
    unsorted_map = []
    val_ind = func_args.index('val')
    for i in unsorted:
        func_args[val_ind] = i[ind]
        map_val = func_on_val(*func_args)
        unsorted_map.append(map_val)
    
    if low_to_high:
        for _ in range(top_n):
            lowest_ind = unsorted_map.index(min(unsorted_map))
            sorted_final.append(unsorted[lowest_ind])
            unsorted_map[lowest_ind] = 100000
    else:
        for _ in range(top_n):
            highest_ind = unsorted_map.index(max(unsorted_map))
            sorted_final.append(unsorted[highest_ind])
            unsorted_map[highest_ind] = -100000
    return sorted_final



def rel_plot(left_or_mono, start, end, rate, right=None, fill=None, title=None, 
        plot_type="line", obj_type=None, obj_name=None):
    """
    left and right must be numpy arr with shape (x, 2) arrays of (index, value) to plot.
    if right is not given, assumed to be mono left
    """
    info_block("Generating plot...")
    fig = pylab.gfc()
    fig.canvas.set_window_title("{0} '{1}'".format(obj_type, obj_name))

    # channels
    left = left_or_mono
    if right is None:
        right = left_or_mono
    # fill
    if fill is None:
        try:
            if min( (np.min(left[:,1]), np.min(right[:,1])) ) >= 0:
                fill = True
            else:
                fill = False
        except ValueError:
            pass
    # title
    if title is not None:
        fig.suptitle(title)
    # plot type
    if plot_type == "scatter":
        plot_func = plt.scatter
        fill = False
    elif plot_type == "bar":
        plot_func = plt.bar
    else:
        plot_func = plt.plot

    # left: top, beats labels
    axL = plt.subplot(211)
    pos = axL.get_position()
    pos.y0 -= 0.06
    pos.y1 -= 0.06
    axL.set_position(pos)
    axL.xaxis.tick_top()
    axL.xaxis.set_label_position('top')

    start_beats, _ = whole_beats(start / rate)
    end_beats, _ = whole_beats(end / rate)
    tick_size_beats = 1
    tick_number = end_beats - start_beats
    if tick_number < 2:
        start_beats = beats(start / rate)
        end_beats = beats(end / rate)
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
    for i in np.linspace(start_beats, end_beats, tick_number, endpoint=False):
        tick_locs.append(i)
        axL.axvline(i, linestyle="--", linewidth=0.3, color='#545454', 
            clip_on=False, zorder=11)
        tick_labels.append("{0:.{1}f}".format(i, decimal_precision_requires(i)))
    plt.xticks(tick_locs, tick_labels)
    for tick in axL.xaxis.get_major_ticks()[1::2]:
        tick.set_pad(15)

    plt.xlabel("Beats")
    plt.ylabel("Left amplitude")
    if len(left.shape) == 1:
        valuesL = left
        indexesL = range(start, start + len(left))
    else:
        indexesL, valuesL = zip(*left)
    indexesL = [beats(i/rate) for i in indexesL]
    plot_func(indexesL, valuesL)

    # right: bottom, seconds labels
    axR = plt.subplot(212)
    plt.xlabel("Seconds")
    plt.ylabel("Right amplitude")
    if len(right.shape) == 1:
        valuesR = right
        indexesR = range(start, start + len(right))
    else:
        indexesR, valuesR = zip(*right)
    indexesR = [i/rate for i in indexesR]
    for i in np.linspace(start_beats, end_beats, tick_number, endpoint=False):
        ind = secs(str(i) + "b")
        axR.axvline(ind, linestyle="--", linewidth=0.3, color='#545454', 
            clip_on=False, zorder=11)
    plot_func(indexesR, valuesR)

    info_block("Viewing waveform...")
    if fill and len(indexesR) < 1_000_000:
        axR.fill_between(indexesR, valuesR, color='#43C6FF')
        axL.fill_between(indexesL, valuesL, color='#43C6FF')
    plt.show()






def util_main():
    pass

    

if __name__ == "__main__":
    util_main()