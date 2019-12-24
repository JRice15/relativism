"""
helpful debugging functions
"""


from contextlib import contextmanager
import time
import timeit
import functools



class _TimerAssistant:

    count = 0

@contextmanager
def time_this(process_name="This"):
    """
    debugging timer contextmanager
    """
    t1 = time.time()
    try:
        yield
    finally:
        t2 = time.time()
        print("{0}: {1} took {2:.4f} seconds".format(_TimerAssistant.count, process_name, t2-t1))
    _TimerAssistant.count += 1


def timeit_(func, args, reps=1000, times=7):
    """
    debugging timer for very fast operations
    """
    time = min(timeit.Timer(functools.partial(func, *args)).repeat(times, reps))
    print("{0} took {1}".format(func.__name__, time))



