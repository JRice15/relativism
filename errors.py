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
    pass obj to save it to file
    """
    def __init__(self, obj=None):
        if obj is not None:
            obj.save()

class RateError(Exception):
    """
    Error with sampe rates
    """


class TestError(Exception):
    """
    """
    def __init__(self, num):
        self.num = num
        self.print_num()
    
    def print_num(self):
        print(self.num)