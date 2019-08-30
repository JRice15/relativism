from relativism import *


def p(message, indent=2, o="", i="", start=""):
    """
    user-prompt:
        indent: spaces,
        o="options for before quit message
        ('q' to quit) auto
        i="for info message"
    """
    message_body = message
    notices = " ("
    if o != "":
        notices += o + ", "
    notices += "'q' to quit"
    if i != "":
        notices += ", 'i' " + i
    notices += "):"
    info_block(message_body + notices, indent=indent, for_prompt=True, start=start)


def err_mess(message, indent=4, trailing_newline=True):
    """
    print error message with leading >, no newlines
    """
    info_block("> " + message, indent=indent, newlines=False)


def info_title(message, indent=4):
    info_block(message, indent=indent, leading_newline=True, trailing_newline=False)


def info_list(message, indent=4):
    """
    print messages with '-' list. message as str or list
    """
    if isinstance(message, list) or isinstance(message, tuple):
        for m in message:
            info_block("- " + m, indent=indent, newlines=False)
    else:
        info_block("- " + message, indent=indent, leading_newline=False, trailing_newline=True)


def info_line(message, indent=4):
    info_block(message, indent=indent, newlines=False)


def section_head(message, indent=0):
    info_block("* " + message, indent=indent)


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
    for char in message:
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