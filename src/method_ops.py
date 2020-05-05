"""
high-powered dynamic ruining of all your favorite classes, functions, and methods

__rel_data format:
{
    "public": bool
    "name": str
    "desc": str
    "category": str
    "aliases": [..., ...]
    "wrap_all_encloser": ...
}

"""



from enum import Enum, auto
import random as rd
import re

from src.errors import *
from src.input_processing import err_mess, inpt_validate, info_block, info_list, info_line



class _RelData:
    """
    data for methods
    """

    __slots__ = ["public", "name", "cat", "desc", "args", "aliases"]
    def __init__(self):
        self.public = False
        self.name = None
        self.cat = _Category.OTHER
        self.desc = ""
        self.args = []
        self.aliases = []

    def display(self):
        message = self.name.capitalize()
        message += ": " + self.desc
        if self.aliases is not None:
            message += " (alias"
            if len(self.aliases) > 1:
                message += "es"
            message += ": '" + "', '".join(self.aliases) + "')"
        info_list(message, hang=4)
        for i in self.args:
            info_line("• " + i.get_display(), indent=8)

    def get_random_defaults(self):
        return [i.choose_random_default() for i in self.args]

    def oneline_arg_list(self):
        argstr = []
        for i in self.args:
            if i.optional:
                argstr.append("[" + i.name + "]")
            else:
                argstr.append(i.name)
        return ", ".join(argstr)



class _Category(Enum):
    OTHER = "Other"
    EDIT = "Edits"
    META = "Metadata"
    INFO = "Object Info"
    SAVE = "Saving & Data Handling"
    EFFECT = "Effects"


def _get_category(category, kind="std"):
    """
    get category  
    kind: "std" for Enum obj, anything else for display category
    """
    category = category.lower()
    if category in ("edit", "edits"):
        val = _Category.EDIT
    elif category in ("meta", "metadata"):
        val = _Category.META
    elif category in ("info", "repr", "representation"):
        val = _Category.INFO
    elif category in ("save", "saving"):
        val = _Category.SAVE
    elif category in ("eff", "effects", "fx", "efx", "effx", "effect"):
        val = _Category.EFFECT
    else:
        val = _Category.OTHER
    if kind == "std":
        return val
    return val.value



class _ArgData:

    def __init__(self, parent, doc_line):
        self.optional = False
        if doc_line[0] == "[":
            doc_line = doc_line.strip("[").strip("]")
            self.optional = True

        name,rest = doc_line.split(":", maxsplit=1)
        self.desc = rest.split(';')[0].strip()
        self.name = name.strip()

        self.defaults = [None, None]
        defaults = rest.split(";")
        if len(defaults) > 1:
            defaults = defaults[1].split(',')
            try:
                self.defaults[0] = float(defaults[0])
                self.defaults[1] = float(defaults[1])
            except:
                err_mess("Badly formed defaults on '{0}': {1}".format(parent, defaults))

    def get_display(self):
        string = self.name + ": " + self.desc
        if self.optional:
            string = "[" + string + "]"
        return string

    def choose_random_default(self):
        if None in self.defaults:
            return None
        else:
            num = rd.random()
            arg = (self.defaults[0] * (1 - num)) + (self.defaults[1] * (num))
            return arg




def is_edit_rec(method):
    """
    is category that the rec.arr should be saved on
    """
    return method.__rel_data["category"] in ('edit', 'effect')

def is_edit_meta(method):
    """
    if is catg that rec metadata should be save on
    """
    return method.__rel_data["category"] in ('meta')

def is_public_process(method_obj):
    try:
        return method_obj.__rel_data["public"]
    except AttributeError:
        return False

def is_alias(method_obj, name):
    """
    check if name is alias of method
    """
    try:
        return name in method_obj.__rel_data["aliases"]
    except AttributeError:
        return False

def is_rel_wrap_all(clss):
    """
    check if wrap_all_encloser is not None
    """
    try:
        return clss.__rel_data["wrap_all_encloser"] is not None
    except AttributeError:
        return False

def get_wrap_all_encloser(clss):
    return clss.__rel_data["wrap_all_encloser"]








def _do_public_process(method):
    """
    add reldata, convert docstring
    """

    add_reldata(method, "public", True)
    add_reldata(method, "name", method.__name__, overwrite=False)
    add_reldata(method, "desc", "")

    doc = method.__doc__
    if doc is not None:
        doc = [
            j for j in 
            [re.sub(r"\s+", " ", i.strip()) for i in doc.split('\n')]
            if j not in ("", " ")
            ]
        args_now = False
        for line in doc:
            try:
                title, content = line.split(":")[0].lower(), line.split(":")[1]
                if title == "dev":
                    break
                if not args_now:
                    if title in ("desc", "descrip", "description"):
                        add_reldata(method, "desc", content.strip())
                    elif title in ("catg", "cat", "category", "catgry", "categry"):
                        cat = _MethodOps.get_std_category(content.strip())
                        add_reldata(method, "category", cat)
                    elif title in ("args", "arguments", "arg"):
                        args_now = True
                else:
                    arg_dt = _ArgData(self, line)
                    if "args" not in method.__rel_data:
                        add_reldata(method, "args", [])
                    method.__rel_data["args"].append(arg_dt)
            except:
                err_mess("Error reading docstring method object data from method '" + method.__name__ + ": " + str(line) + "'")
    
    add_reldata(method, "category", "other", overwrite=False)

    return method



def public_process(*modes, allowed=None):
    """
    decorator: make a method a public process.  
    implement arg checking by passing inpt_validate modes as args.  
    allowed=([low,high], None, "abc", ..., "more") # 1st, 3rd, last args have allowed (counting all optionals).
    
    Not to be thought of a type system for python, but instead as sanitizing user input
    """
    # called with no args
    if len(modes) == 1 and allowed is None and callable(modes[0]):
        return _do_public_process(modes[0])

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

        _bootstrap_reldata(public_process_wrapper, method)
        return _do_public_process(public_process_wrapper)

    return called_on_process


def rel_alias(*args):
    """
    decorator: aliases for a method. the actual aliasing happens in Public Object's _do_aliases method  
    args: *args of strings to alias
    """
    if len(args) == 0:
        raise UnexpectedIssue("No aliases provided to alias decorator")

    def wrapper(method):
        add_reldata(method, "aliases", args)
        return method

    return wrapper



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
        
        _bootstrap_reldata(wrapper, method)
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
        add_reldata(clss, "wrap_all_encloser", encloser)
        return clss
    return wrap_all




def _bootstrap_reldata(this_func, old_func):
    """
    bootstrap special attrs from old_func to this_func
    """
    if hasattr(old_func, "__rel_data"):
        dct = old_func.__rel_data
        if hasattr(this_func, "__rel_data"):
            dct.update(this_func.__rel_data)
        this_func.__rel_data = dct


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


def add_reldata(obj, attrname, value, overwrite=True):
    """
    obj.__rel_data["attrname"] = value  
    if overwrite false, will not overwrite an existing value
    """
    if hasattr(obj, "__rel_data"):
        if (not overwrite) and (attrname in obj.__rel_data):
            return
        obj.__rel_data[attrname] = value
    else:
        obj.__rel_data = {attrname: value}

def get_reldata(obj, attrname):
    """
    obj.__rel_data[attrname], or KeyError on failure
    """
    try:
        return obj.__rel_data[attrname]
    except:
        raise KeyError("Obj '{0}' has no reldata '{1}'".format(obj, attrname))
