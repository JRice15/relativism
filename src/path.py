"""

path object for handling paths

"""

import re
import os

class PathError(Exception):
    pass


class Path(os.PathLike):

    def __init__(self, directory="", name="", ext="", fullpath=""):
        """
        give either fullpath arg or a combo of the other three
        """
        self.dir = self.filename = self.ext = ""

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
                self.dir = fullpath
        
        # dir, fname, extension given directly
        else:
            self.dir = directory
            self.filename = name
            self.ext = ext
        
        # formatting
        self.filename = re.sub(r"/", "", self.filename)
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
            return self.fullpath == other.fullpath
        except:
            return False

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

    def append(self, other):
        if self.is_dir():
            raise PathError("Appending to non-directory")
        if not isinstance(other, Path):
            other = Path(fullpath=other)
        return Path(self._clean(self.fullpath + "/" + other))

    def remove_ext(self):
        return Path(self.dir, self.filename)


