"""
output and prompting


"""

from contextlib import contextmanager
from src.errors import *
from src.utility import *

@contextmanager
def style(*styles):
    """
    color and stylize text. pass styles one comma seperated str or multiple strings
    """
    class Colors:
        """ ANSI color codes """
        BLACK = "\033[0;30m"
        RED = "\033[0;31m"
        GREEN = "\033[0;32m"
        BROWN = "\033[0;33m"
        BLUE = "\033[0;34m"
        PURPLE = "\033[0;35m"
        CYAN = "\033[0;36m"
        LIGHT_GRAY = "\033[0;37m"
        DARK_GRAY = "\033[1;30m"
        LIGHT_RED = "\033[1;31m"
        LIGHT_GREEN = "\033[1;32m"
        YELLOW = "\033[1;33m"
        LIGHT_BLUE = "\033[1;34m"
        LIGHT_PURPLE = "\033[1;35m"
        LIGHT_CYAN = "\033[1;36m"
        LIGHT_WHITE = "\033[1;37m"
        BOLD = "\033[1m"
        FAINT = "\033[2m"
        ITALIC = "\033[3m"
        UNDERLINE = "\033[4m"
        BLINK = "\033[5m"
        NEGATIVE = "\033[7m"
        CROSSED = "\033[9m"
        END = "\033[0m"
    try:
        if len(styles) == 1:
            styles = styles[0].split(',')
        for s in styles:
            s = s.upper().strip()
            try:
                print(getattr(Colors, s), end='')
            except:
                critical_err_mess("No style {0} exists".format(s))
        yield
    finally:
        print(Colors.END, end='')




def p(message, indent=2, o="", h=False, start="", hang=2, leading_newline=True):
    """
    prompting.
    Args:
        o (str): description of additional options and their letter (remember to add callback to inpt)
        h (bool): if true display "'h' for help/info"
        start (str): beginning of text for prompt (ie partial word to complete)
    """
    message_body = str(message)
    notices = " ("
    if o != "":
        notices += o + ", "
    notices += "'q' to quit/cancel"
    if h:
        notices += ", 'h' for help/info"
    notices += "):"
    info_block(message_body + notices, indent=indent, for_prompt=True, start=start, 
        hang=hang, leading_newline=leading_newline)


def err_mess(message, indent=4, trailing_newline=False):
    """
    print error message with leading >, no newlines
    """
    print("")
    info_block("> " + str(message), indent=indent, trailing_newline=trailing_newline)


def show_error(e, force=False):
    if not isinstance(e, Cancel) or force:
        critical_err_mess(e.__class__.__name__ + ": " + str(e))

        from src.rel_global import RelGlobal
        if RelGlobal.is_debug():
            p("Raise error? [y/n]")
            if input().lower().strip() == 'y':
                raise e

def critical_err_mess(message):
    """
    """
    with style('red'):
        print("\nCritical Error, something appears to be broken:")
        print("   ", message)
        print("Please contact the developer\n")


def info_title(message, indent=4):
    info_block(str(message), indent=indent, leading_newline=True, trailing_newline=False)


def info_list(message, indent=4, hang=2):
    """
    print messages with '-' list. message as str or list
    """
    if isinstance(message, list) or isinstance(message, tuple):
        if len(message) == 0:
            info_block("- (empty)", indent=indent, newlines=False, hang=hang)
        else:
            for m in message:
                info_block("- " + str(m), indent=indent, newlines=False, hang=hang)
    else:
        info_block("- " + str(message), indent=indent, newlines=False, hang=hang)


def info_line(message, indent=4, hang=2):
    """
    no newlines
    """
    info_block(str(message), indent=indent, newlines=False, hang=hang)


def section_head(message, indent=0):
    """
    * at front, leading newline
    """
    info_block("* " + str(message), indent=indent)


def nl(num=1):
    """
    print num newlines
    """
    for _ in range(num):
        print("")


def info_block(message, indent=None, hang=2, newlines=None, trailing_newline=False, 
        leading_newline=True, for_prompt=False, start=""):
    """
    default indent is 4.
    for_prompt sets: indent=2 (or override), hang=2, formats for input after.
    start is the beginning of text for a prompt
    """
    # configuration
    end = "\n"
    if for_prompt:
        if indent is None:
            indent = 2
        trailing_newline = False
        end = " "
        if start != "":
            end += start
    if indent is None:
        indent = 4
    if newlines is False:
        leading_newline = False
        trailing_newline = False
    elif newlines is True:
        leading_newline = True
        trailing_newline = True

    # splitting at spaces
    lines = [""]
    for char in str(message):
        # hard break if super long with no spaces (url, path, etc)
        if len(lines[-1]) >= 65:
            if char != " ":
                lines[-1] += "--"
                lines.append("")
        # regular limit
        if len(lines[-1]) >= 55:
            last_space = lines[-1].rfind(" ")
            if last_space != -1:
                text = lines[-1][last_space + 1:]
                lines[-1] = lines[-1][:last_space]
                lines.append(text)
                lines[-1] += char
            else:
                if char == " ":
                    lines.append("")
                else:
                    lines[-1] += char
        else:
            lines[-1] += char
        
    # outputting lines
    first_line = True
    for i in range(len(lines)):
        if first_line and leading_newline:
            print("") # starting newline
        if i == len(lines) - 1: # last line
            print((" " * indent) + lines[i], end=end)
        else:
            print((" " * indent) + lines[i])
        if first_line:
            first_line = False
            indent += hang
    if trailing_newline:
        print("")


