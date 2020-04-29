

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

class RateError(Exception):
    """
    Error with sampe rates
    """


class NoSuchProcess(Exception):
    """
    when command does not exist
    """

class ArgumentError(Exception):
    """
    when process recieves too many or few arguments
    """



