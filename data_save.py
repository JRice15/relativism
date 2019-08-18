import pickle



def write_obj(obj, filename_or_fullpath, directory=None):
    """
    if no directory arg filename is fullpath. do not include extension
    """
    filename_or_fullpath += '.relativism-obj'
    if directory is None:
        filepath = filename_or_fullpath
    else:
        if directory[-1] != '/':
            directory += '/'
        filepath = directory + filename_or_fullpath
    write_file = open(filepath, 'wb')
    pickle.dump(obj, write_file)


def read_obj(filename_or_fullpath, directory=None):
    """
    no dir arg means filename is full path. do not include extension
    """
    filename_or_fullpath += '.relativism-obj'
    if directory is None:
        filepath = filename_or_fullpath
    else:
        if directory[-1] != '/':
            directory += '/'
        filepath = directory + filename_or_fullpath
    read_file = open(filepath, 'rb')
    obj = pickle.load(read_file)
    return obj