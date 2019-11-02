# from relativism import *
from utility import *

def p(message, indent=2, o="", h=False, start=""):
    """
    user-prompt:
        o: "letter and full message for some options message" (add callback to inpt)
        'q' to quit (auto)
        h: bool for display help
        start: beginning of text for prompt (ie partial word to complete)
    """
    message_body = str(message)
    notices = " ("
    if o != "":
        notices += o + ", "
    notices += "'q' to quit/cancel"
    if h:
        notices += ", 'h' for help/info"
    notices += "):"
    info_block(message_body + notices, indent=indent, for_prompt=True, start=start)


def err_mess(message, indent=4, trailing_newline=False):
    """
    print error message with leading >, no newlines
    """
    print("")
    info_block("> " + str(message), indent=indent, trailing_newline=trailing_newline)


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
        hang = 2
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


def main_output():
    p('Choose sample rate to record at, in samples per second. Hit enter to use default 44100')





if __name__ == "__main__":
    main_output()