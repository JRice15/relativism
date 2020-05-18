

class AutofillError(Exception):
    """
    autofill couldnt find a suitable match
    """
    def __init__(self, word, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.word = word

class UnexpectedIssue(Exception):
    """
    there was an issue that is not suppoed to happen
    """

class Cancel(Exception):
    """
    the user cancelled out of whatever is going on.
    """

class TryAgain(Exception):
    """
    that input/something failed, try/prompt again
    """

class RateError(Exception):
    """
    Error with sampe rates
    """

class NoSuchProcess(Exception):
    """
    when command does not exist
    """

class PropertyError(Exception):
    """
    """