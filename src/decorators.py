"""
high-powered dynamic ruining of all your favorite classes, functions, and methods

"""

from src.errors import *


_rel_special_func_attrs = [
    "__rel_public",
    "__rel_aliases",
    "__rel_wrap_all_encloser"
]


def public_process(_func):
    """
    decorator: allow user access via 'process'
    args: none
    """
    _func.__rel_public = True
    return _func

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
    wrap a process in another function. encloser can be a function or a 
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
            
        # bootstrap special attrs up to wrapper
        for a in _rel_special_func_attrs:
            if hasattr(method, a):
                setattr(wrapper, a, getattr(method, a))
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
