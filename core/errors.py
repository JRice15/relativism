""" SIGNAL ERRORS """


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
    the user cancelled out of whatever is going on.
    """



class RateError(Exception):
    """
    Error with sampe rates
    """


class UnknownError(Exception):
    """
    fallback case for error that is unsure how to be handled
    """

class InitOrderError(Exception):
    """
    when things are not initialized in the right order so
    something goes wrong
    """


