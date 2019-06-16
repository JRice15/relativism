""" SIGNAL ERRORS """

from freq_and_time import beat_options

class NameExistsError(Exception):
    """
    chosen name already exists
    """
    pass

class NameDoesntExistError(Exception):
    """
    chosen name cannot be found
    """
    pass

class NoPathError(Exception):
    """
    no path was chosen
    """
    pass


class UnexpectedIssue(Exception):
    """
    there was an issue that is not suppoed to happen
    """
    pass

class Cancel(Exception):
    """
    the user cancelled out of whatever is going on
    """
    pass


