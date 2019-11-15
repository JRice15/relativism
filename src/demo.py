import os
from os.path import dirname
import sys

global relativism_dir
relativism_dir = dirname(dirname(os.path.abspath(__file__)))
sys.path.append(relativism_dir)


from src.recording_obj import *
from src.process import *

if __name__ == "__main__":
    a = Recording()
    process(a)