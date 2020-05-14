"""

path object for handling paths

"""

import re


def join_path(*args, is_dir=False, ext=None):
    """
    join *args strings into a path
    """
    path = "/".join(args)
    if is_dir:
        assert ext is None
        path += "/"
    if ext is not None:
        path += "." + ext
    path = re.sub(r"//", "/", path)
    return path

def split_path(path):
    """
    split path into dir, filename, extension. Assumes filenames must have
    extensions, directories must have a '/' leading or trailing
    Returns:
        directory, filename, extension (str|None)
    """
    filename = ext = directory = None

    if "/" in path:

        maybe_filename = path.split("/")[-1]
        maybe_dir = "/".join(path.split("/")[:-1])
        # if last name has extension, it is a file, otherwise is a dir
        if "." in maybe_filename:
            # leading period does not mean extension follows
            if (maybe_filename[0] == "."):
                if (maybe_filename.count(".") > 1):
                    filename = ".".join(maybe_filename.split(".")[:-1])
                    ext = maybe_filename.split(".")[-1]
                    directory = maybe_dir
                else:
                    directory = path
            else:
                filename = ".".join(maybe_filename.split(".")[:-1])
                ext = maybe_filename.split(".")[-1]
                directory = maybe_dir
        else:
            directory = path

    else:
        # possible filename with directoy given
        if path.count(".") == 1 and path[0] == ".":
            directory = path
        elif path.count(".") > 1:
            filename = ".".join(path.split(".")[:-1])
            ext = path.split(".")[-1]
    
    return directory, filename, ext

