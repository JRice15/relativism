"""
high-powered dynamic ruining of all your favorite classes, functions, and methods

_rel_data format:
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
from inspect import signature, Parameter
import functools

from src.errors import *
from src.output_and_prompting import err_mess, info_block, info_list, info_line, log_err


""" Classes """

class Category(Enum):
    """
    category attr of methods
    """

    OTHER = "Other"
    EDIT = "Edits"
    META = "Metadata"
    INFO = "Object Info"
    SAVE = "Saving & Data Handling"
    EFFECT = "Effects"

    @staticmethod
    def get(category, kind="std"):
        """
        get category  
        kind: "std" for Enum obj, anything else for display category
        """
        category = category.lower()
        if category in ("edit", "edits"):
            val = Category.EDIT
        elif category in ("meta", "metadata"):
            val = Category.META
        elif category in ("info", "repr", "representation"):
            val = Category.INFO
        elif category in ("save", "saving"):
            val = Category.SAVE
        elif category in ("eff", "effects", "fx", "efx", "effx", "effect"):
            val = Category.EFFECT
        else:
            val = Category.OTHER
        if kind == "std":
            return val
        return val.value


class _ClsRelData:
    """
    reldata for classes
    """

    __slots__ = ["wrap_all_encloser", "alias_map"]

    def __init__(self):
        self.wrap_all_encloser = None
        self.alias_map = {} # maps alias to actual method name


class RelData:
    """
    data for methods
    """

    __slots__ = ["public", "name", "category", "desc", "args", "aliases", "is_alias"]

    def __init__(self, name, is_alias=False):
        self.name = name
        self.public = False
        self.category = Category.OTHER
        self.desc = None
        self.args = []
        self.aliases = []
        self.is_alias = is_alias

    def display(self):
        message = self.name.capitalize()
        message += ": " + self.desc
        if len(self.aliases) > 0:
            message += " (alias"
            if len(self.aliases) > 1:
                message += "es"
            message += ": '" + "', '".join(self.aliases) + "')"
        info_list(message, hang=4)
        for i in self.args:
            info_line("• " + i.get_display(), indent=8)

    def get_random_defaults(self):
        defs = []
        for i in self.args:
            d = i.choose_random_defaults()
            if d is None:
                break
            defs.append(d)
        return defs

    def oneline_arg_list(self):
        argstr = []
        for i in self.args:
            if i.optional:
                argstr.append("[" + i.name + "]")
            else:
                argstr.append(i.name)
        return ", ".join(argstr)


class ArgData:

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


def add_reldata(obj, attrname, value, overwrite=True, kind="meth"):
    """
    obj._rel_data.attrname = value  
    if overwrite false, will not overwrite an existing value  
    kind: "meth", or "clss"
    """
    if hasattr(obj, "_rel_data"):
        if (not overwrite):
            return
    else:
        if kind == "meth":
            obj._rel_data = RelData(obj.__name__)
        else:
            obj._rel_data = _ClsRelData()
    setattr(obj._rel_data, attrname, value)


def add_reldata_arg(method, arg_docline):
    """
    obj._rel_data.args.append(ArgData(parent=obj, docline=arg_docline))
    """
    args = get_reldata(method, "args")
    args.append(
        ArgData(method, arg_docline)
    )


def get_reldata(obj, attrname):
    """
    obj._rel_data.attrname, or KeyError on failure
    """
    return getattr(obj._rel_data, attrname)




""" Checking functions """


def is_edit_rec(method):
    """
    is category that the rec.arr should be saved on
    """
    return get_reldata(method, "category") in (Category.EDIT, Category.EFFECT)

def is_edit_meta(method):
    """
    if is catg that rec metadata should be save on
    """
    return get_reldata(method, "category") in (Category.META)

def is_public_process(method_obj):
    try:
        return get_reldata(method_obj, "public")
    except AttributeError:
        return False

def is_alias(method_obj, name):
    """
    check if name is alias of method
    """
    try:
        return name in get_reldata(method_obj, "aliases")
    except AttributeError:
        return False

def has_aliases(method):
    try:
        return len(get_reldata(method, "aliases")) > 0
    except:
        return False

def is_rel_wrap_all(clss):
    """
    check if wrap_all_encloser is not None
    """
    try:
        return get_reldata(clss, "wrap_all_encloser") is not None
    except AttributeError:
        return False

def get_wrap_all_encloser(clss):
    return get_reldata(clss, "wrap_all_encloser")




""" Public Processes and Decorators """

def _do_public_process(method, name=None):
    """
    add reldata, convert docstring
    """
    if name is None:
        name = method.__name__

    add_reldata(method, "public", True)
    add_reldata(method, "name", name)
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
                        cat = Category.get(content.strip())
                        add_reldata(method, "category", cat)
                    elif title in ("args", "arguments", "arg"):
                        args_now = True
                else:
                    add_reldata_arg(method, line)
            except Exception as e:
                err_mess("Error reading docstring method object data from method '" + method.__name__ + "'", trailing_newline=False)
                info_line("Docline: '" + str(line) + "'", indent=8)
                info_line("Exception: " + str(e), indent=8)
    
    return method


def public_process(*modes, allowed=None):
    """
    decorator: make a method a public process.  
    implement arg checking by passing inpt_validate modes as args.  
    allowed=([low,high], None, "abc", ..., "more") # 1st, 3rd, last args have allowed (counting all optionals).
    
    Not to be thought of a type system for python, but instead as sanitizing user input
    """
    from src.input_processing import inpt_validate
    
    # called with no args
    if len(modes) == 1 and allowed is None and callable(modes[0]):
        return _do_public_process(modes[0])

    # called with args
    def called_on_process(method):

        @functools.wraps(method)
        def public_process_wrapper(*args):
            nonlocal allowed, modes
            allowed = _expand_ellipses(len(modes), allowed)

            func_args = [ args[0] ] # self as first arg
            for i in range(len(args) - 1):
                try:
                    mode = modes[i]
                except IndexError:
                    func_args.append(args[i+1])
                else:
                    val = inpt_validate(args[i+1], mode, allowed=allowed[i])
                    func_args.append(val)
            
            # do default args
            params = list(signature(method).parameters.values())
            for i in range(len(args) - 1, len(modes)):
                if params[i+1].default == Parameter.empty:
                    break
                val = inpt_validate(params[i+1].default, modes[i], allowed=allowed[i])
                func_args.append(val)

            return method(*func_args)

        _bootstrap_reldata(public_process_wrapper, method)
        newmethod = _do_public_process(public_process_wrapper, name=method.__name__)
        return newmethod

    return called_on_process


def rel_alias(*args):
    """
    decorator: aliases for a method. the actual aliasing happens in Public Object's _do_aliases method  
    args: *args of strings to alias
    """
    if len(args) == 0 or (len(args) == 1 and callable(args[0])):
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

        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            return encloser(method, *args, **kwargs)
        
        _bootstrap_reldata(wrapper, method)
        return wrapper

    return wrapper_wrapper


def rel_wrap_all(encloser):
    """
    rel_wrap all public methods (and aliases). wrapping happens in 
    RelObject._do_wrap_all  
    args: 
        encloser with signature 'enc(obj, method, *args, **kwargs)'
    """
    def wrap_all(clss):
        add_reldata(clss, "wrap_all_encloser", encloser, kind="clss")
        return clss
    return wrap_all



def _bootstrap_reldata(this_func, old_func):
    """
    bootstrap special attrs from old_func to this_func
    """
    if hasattr(old_func, "_rel_data"):
        this_func._rel_data = old_func._rel_data


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

