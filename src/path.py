"""

path object for handling paths

"""

import re
import os
import stat

from src.errors import *


class Path(os.PathLike):

    def __init__(self, directory="", name="", ext="", fullpath=""):
        """
        give either fullpath arg or a combo of the other three
        """
        self.dir = self.filename = self.ext = ""

        if isinstance(fullpath, Path):
            fullpath = fullpath.fullpath()

        # parse from whole string
        if fullpath != "":
            fullpath = self._clean(fullpath)
            if "/" in fullpath:

                maybe_filename = fullpath.split("/")[-1]
                maybe_dir = "/".join(fullpath.split("/")[:-1])
                # if last name has extension, it is a file, otherwise is a dir
                if "." in maybe_filename:
                    # leading period does not mean extension follows
                    if (maybe_filename[0] == "."):
                        if (maybe_filename.count(".") > 1):
                            self.filename = ".".join(maybe_filename.split(".")[:-1])
                            self.ext = maybe_filename.split(".")[-1]
                            self.dir = maybe_dir
                        else:
                            self.dir = self._clean(self.dir + "/" + maybe_filename)
                    else:
                        self.filename = ".".join(maybe_filename.split(".")[:-1])
                        self.ext = maybe_filename.split(".")[-1]
                        self.dir = maybe_dir
                else:
                    self.dir = fullpath

            else:
                # possible filename with directory given
                if fullpath.count(".") == 1 and fullpath[0] == ".":
                    self.dir = fullpath
                elif fullpath.count(".") > 0:
                    self.filename = ".".join(fullpath.split(".")[:-1])
                    self.ext = fullpath.split(".")[-1]
        
        # dir, fname, extension given directly
        else:
            self.dir = directory
            self.filename = name
            self.ext = ext
        
        # formatting
        if isinstance(directory, Path):
            self.dir = directory.dir
        else:
            self.dir = "/" + self.dir
        self.dir = self._clean(self.dir)
        if isinstance(name, Path):
            self.filename = name.filename
        else:
            self.filename = re.sub(r"/", "", self.filename)
        if isinstance(ext, Path):
            self.ext = ext.ext
        else:
            self.ext = re.sub(r"\.", "", self.ext)


    def _parse_filename_and_ext(self, filename):
        if (filename[0] == "."):
            if (filename.count(".") > 1):
                self.filename = ".".join(filename.split(".")[:-1])
                self.ext = filename.split(".")[-1]
            else:
                self.dir = self._clean(self.dir + "/" + filename)
        else:
            self.filename = ".".join(filename.split(".")[:-1])
            self.ext = filename.split(".")[-1]

    def __fspath__(self):
        return self.fullpath()

    def __repr__(self):
        return self.fullpath()
    
    def __eq__(self, other):
        try:
            return self.fullpath() == other.fullpath()
        except:
            return False

    def _dont_share_path_element(self, other):
        """
        makes sure two paths dont both have a dir, a filename, or an extension
        """
        return (not (self.dir != "" and other.dir != "")) and \
            (not (self.filename != "" and other.filename != "")) and \
            (not (self.ext != "" and other.ext != ""))


    def merge(self, other):
        if not isinstance(other, Path):
            other = Path(fullpath=other)

        if self._dont_share_path_element(other):

            if (self.filename != "" or other.filename != ""):

                dirc = other.dir if self.dir == "" else self.dir
                fname = other.filename if self.filename == "" else self.filename
                ext = other.ext if self.ext == "" else self.ext
                return Path(dirc, fname, ext)

        if self.is_dir():
            self.append(other)

        raise PathError("Paths '{0}' and '{1}' cannot be merged", self, other)

    def append(self, other):
        if not isinstance(other, Path):
            other = Path(fullpath=other)
        if self.is_dir():
            return Path(fullpath=self.fullpath() + "/" + other.fullpath())
        raise PathError("Paths '{0}' and '{1}' cannot be appended", self, other)


    def _clean(self, string):
        return re.sub(r"//+", "/", string)

    def filename_w_ext(self):
        if not self.is_dir():
            return self.filename + "." + self.ext
        return ""

    def fullpath(self):
        return self._clean(self.dir + "/" + self.filename_w_ext())
    
    def is_dir(self):
        return (self.dir != "") and (self.filename == "") and \
            (self.ext == "")

    def is_empty(self):
        return (self.dir == "") and (self.filename == "") and \
            (self.ext == "")


    def remove_ext(self):
        return Path(self.dir, self.filename)


def makepath(path):
    os.makedirs(path, exist_ok=True)

