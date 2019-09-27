from relativism import *
from contextlib import contextmanager
import sys, os
import time
import timeit
from output_and_prompting import *
import functools
import numpy as np

@contextmanager
def suppress_output():
    """
    usage:
    with suppress_output():
        suppressed zone
    """
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout


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
    def sort(array, column=0, high_to_low=True):
        """
        sort by column. must set array variable equal to this call 
        (np arrays not mutable)
        """
        if high_to_low:
            return array[array[:, column].argsort()][::-1]
        else:
            return array[array[:, column].argsort()]




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




def util_main():
    pass

    

if __name__ == "__main__":
    util_main()