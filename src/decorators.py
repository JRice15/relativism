"""
high-powered dynamic ruining of all your favorite classes, functions, and methods

"""

from src.errors import *
from src.input_processing import inpt_validate


_rel_special_func_attrs = [
    "__rel_public",
    "__rel_aliases",
    "__rel_wrap_all_encloser"
]

def _bootstrap_special_attrs(this_func, old_func):
    """
    bootstrap special attrs from old_func to this_func
    """
    for a in _rel_special_func_attrs:
        if hasattr(old_func, a):
            setattr(this_func, a, getattr(old_func, a))


def _expand_ellipses(length, tup):
    """
    tup: tuple or None, to be expanded to length
    """
    # checking
    if tup is None:
        tup = (None,)
    if not isinstance(tup, tuple):
        raise SyntaxError("public_process argument modifiers must be a tuple, recieved '{0}'".format(tup))
    if len(tup) > length:
        raise SyntaxError("Improper length of public_process argument " + 
            "modifier: '{0}' (expected length {1})".format(tup, length))
    if tup.count(Ellipsis) > 1:
        raise SyntaxError("public_process modifier slice has more than one Ellipsis: {0}".format(tup))

    # basic case
    if Ellipsis not in tup:
        expanded = [i for i in tup]
        for i in range(length - len(tup)):
            expanded.append(None)
        return expanded
    
    # case with ellipsis somewhere
    expanded = []
    i = 0
    while tup[i] is not Ellipsis:
        expanded.append(tup[i])
        i += 1
    rest_i = i + 1
    len_rest = len(tup) - i
    while i < length - len_rest + 1:
        expanded.append(None)
        i += 1
    while i < length:
        expanded.append(tup[rest_i])
        i += 1
        rest_i += 1
    return expanded


def public_process(*modes, allowed=None):
    """
    decorator: make a method a public process.  
    implement arg checking by passing inpt_validate modes as args.  
    allowed=([low,high], None, "abc", ..., "more") # 1st, 3rd, last args have allowed (counting all optionals).
    
    Not to be thought of a type system for python, but instead as sanitizing user input
    """
    # called with no args
    if len(modes) == 1 and allowed is None and callable(modes[0]):
        modes[0].__rel_public = True
        return modes[0]

    # called with args
    def called_on_process(method):

        def public_process_wrapper(*args):
            nonlocal allowed, modes
            allowed = _expand_ellipses(len(modes), allowed)

            func_args = []
            for i in range(len(args)):
                mode = modes[i]
                val = inpt_validate(args[i], mode, allowed=allowed[i])
                func_args.append(val)

            return method(*func_args)

        _bootstrap_special_attrs(public_process_wrapper, method)
        public_process_wrapper.__rel_public = True
        return public_process_wrapper

    return called_on_process



def is_public_process(method_obj):
    try:
        return method_obj.__rel_public
    except AttributeError:
        return False


def rel_alias(*args):
    """
    decorator: aliases for a method. the actual aliasing happens in Public Object's _do_aliases method  
    args: *args of strings to alias
    """
    if len(args) == 0:
        raise UnexpectedIssue("No aliases provided to alias decorator")
    def wrapper(method):
        method.__rel_aliases = args
        return method
    return wrapper


def is_alias(method_obj, name):
    try:
        return name in method_obj.__rel_aliases
    except AttributeError:
        return False


def rel_wrap(encloser):
    """
    decorator: wrap a process in another function. encloser can be a function or a 
    static method in the class.  
    args:
        enclosing function with signature 'enc(method, *args, **kwargs)'
    """
    if not callable(encloser):
        encloser = encloser.__func__

    # its wrap-ception baby
    def wrapper_wrapper(method):

        def wrapper(*args, **kwargs):
            return encloser(method, *args, **kwargs)
        
        _bootstrap_special_attrs(wrapper, method)
        return wrapper

    return wrapper_wrapper


def rel_wrap_all(encloser):
    """
    rel_wrap all public methods (and aliases). wrapping happens in 
    RelativismObject._do_wrap_all  
    args: 
        encloser with signature 'enc(obj, method, *args, **kwargs)'
    """
    def wrap_all(clss):
        clss.__rel_wrap_all_encloser = encloser
        return clss
    return wrap_all


def is_rel_wrap_all(clss):
    try:
        return clss.__rel_wrap_all_encloser is not None
    except AttributeError:
        return False

def get_wrap_all_encloser(clss):
    return clss.__rel_wrap_all_encloser
