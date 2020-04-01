

class AutofillError(Exception):
    """
    autofill couldnt find a suitable match
    """
    pass

class PathError(Exception):
    """
    Something wrong with path
    """
    pass


class UnexpectedIssue(Exception):
    """
    there was an issue that is not suppoed to happen
    """
    pass

class Cancel(Exception):
    """
    the user cancelled out of whatever is going on.
    """


class NoSuchProcess(Exception):
    """
    when process does not exist
    """


class RateError(Exception):
    """
    Error with sampe rates
    """

class InitOrderError(Exception):
    """
    when things are not initialized in the right order so
    something goes wrong
    """


