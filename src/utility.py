"""

Misc utility functions

"""

from contextlib import contextmanager
import sys
import os
import time
import numpy as np
import matplotlib.pyplot as plt
import re
from src.errors import *


# import numba

# def jitcomp(func):
#     """
#     decorator to compile arr[:,2]->arr[:,2] func using numba.jit
#     """
#     return numba.jit("float64[:,:](float64[:,:])",  nopython=True, cache=True)(func)

# def jitcompg(func):
#     """
#     decorator to compile general np func using numba.jit
#     """
#     return numba.jit(nopython=True, cache=True,)(func)



def specialjoin(iterable, sep=", ", last_sep=", or "):
    """
    join like a human would, with an "and" or "or" before the last item
    """
    if len(iterable) == 0:
        return ""
    if len(iterable) == 1:
        return iterable[1]
    return sep.join(iterable[:-1]) + last_sep + iterable[-1]
    



@contextmanager
def suppress_output(err_log_name="data/errors.log"):
    """
    usage:
    with suppress_output([log_file]):
        <suppressed zone>
    errors written to err log
    """
    with open(os.devnull, "w") as devnull:
        with open(err_log_name, "a") as errlog:
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = devnull
            sys.stderr = errlog
            try:  
                yield
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr



def decimal_format(val):
    val = "{0:.5f}".format(val)
    val = re.sub(r"0+$", "", val)
    val = re.sub(r"\.$", "", val)
    return val


class NpOps:
    """
    custom helpful numpy operations
    """

    @staticmethod
    def stereoify(arr):
        """
        creates stereo arr where left and right channels are both the input arr
        """
        transpose = arr.reshape(-1, 1)
        return np.hstack((transpose, transpose))

    @staticmethod
    def monoify(arr):
        """
        average channels to single channel
        """
        return np.mean(arr, axis=1)

    @staticmethod
    def get_channels(arr):
        """
        get left and right channels
        """
        return arr[:,0], arr[:,1]

    @staticmethod
    def join_channels(left, right):
        """
        join left and right channels into one stereo track
        """
        return np.vstack((left, right)).T

    @staticmethod
    def swap_channels(arr):
        """
        swap left and right
        """
        arr[:,[0, 1]] = arr[:,[1, 0]]
        return arr

    @staticmethod
    def sort(array, column=0, high_to_low=True):
        """
        sort by column. must use this call as an assignment
        (np arrays not mutable)
        """
        if high_to_low:
            return array[array[:, column].argsort()][::-1]
        else:
            return array[array[:, column].argsort()]

    @staticmethod
    def column_min(arr, column=0):
        """
        get min value in a column
        """
        return arr[:,column].min()

    @staticmethod
    def column_max(arr, column=0):
        """
        get max value in a column
        """
        return arr[:,column].max()

    @staticmethod
    def set_indexes(arr, values_to_set):
        """
        set indexes of array in (index, value) pair forms with another array
        """
        indexes = np.intersect1d(arr[:,0], values_to_set[:,0], assume_unique=True, return_indices=True)
        arr[indexes[1]] = values_to_set[indexes[2]]
        return arr


def selection_sort(unsorted, ind, top_n=None, func_on_val=int, func_args=None, low_to_high=False):
    """
    func args as array of args, where 'val' is replaced with the value to sort on
    """
    if func_args is None:
        func_args = ['val']
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





