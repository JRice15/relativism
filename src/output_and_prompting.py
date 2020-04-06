"""
output and prompting:
    p: prompt
    info_block (and derivitives): output formatted text
    rel_plot: graphing w/ matplotlib

"""

from contextlib import contextmanager
from src.errors import *
from src.utility import *
from src.data_types import *
import traceback

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
                raise UnexpectedIssue("No style '{0}' exists".format(s))
        yield
    finally:
        print(Colors.END, end='')




def p(message, indent=2, o="", h=False, q=True, start="", hang=2, leading_newline=True):
    """
    prompting.
    Args:
        o (str): description of additional options and their letter (remember to add callback to inpt)
        h (bool): if true display "'h' for help/info"
        q (bool): show 'q for quit' message
        start (str): beginning of text for prompt (ie partial word to complete)
    """
    message_body = str(message)
    notices = ""
    if (o != "") or q or h:
        notices = " ("
        if o != "":
            notices += o
            if q or h:
                notices += ", "
        if q:
            notices += "'q' to quit/cancel"
            if h:
                notices += ", "
        if h:
            notices += "'h' for help/info"
        notices += "):"
    info_block(message_body + notices, indent=indent, for_prompt=True, start=start, 
        hang=hang, leading_newline=leading_newline)


def err_mess(message, indent=4, trailing_newline=False, extra_leading_nl=True):
    """
    print error message with leading >, no newlines
    """
    if extra_leading_nl:
        print("")
    info_block("> " + str(message), indent=indent, trailing_newline=trailing_newline)


def show_error(e, force=False):
    """
    raise crit error message and give option to raise error if debug is on
    """
    from src.globals import Settings
    if not isinstance(e, Cancel) or force:
        critical_err_mess(e)
        if Settings.is_debug():
            p("Debug mode is on. Raise error? [y/n]")
            if input().lower().strip() == "y":
                raise e

def critical_err_mess(e):
    """
    show 'something is broken' message and log error
    """
    from src.globals import RelGlobals
    with open(RelGlobals.error_log(), "a") as log:
        log.write("Critical Error {\n")
        traceback.print_exc(file=log)
        log.write("}\n")
    with style('red'):
        info_title("Critical Error, something appears to be broken:")
        info_line(str(e), indent=8)
        info_line("Please contact the developer")
        nl()


def log_err(message):
    """
    log err message string to RelGlobal.error_log
    """
    from src.globals import RelGlobals
    with open(RelGlobals.error_log(), "a") as log:
        if message[-1] != "\n":
            message += "\n"
        log.write(message)


def info_title(message, indent=4):
    """
    line with leading newline
    """
    info_block(str(message), indent=indent, leading_newline=True, trailing_newline=False)


def info_list(message, indent=4, hang=2):
    """
    print messages with '-' list. message as str or list. prints (empty) on empty list
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
    with style("bold, cyan"):
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
        if len(lines[-1]) >= 78:
            if char != " ":
                lines[-1] += " -"
                lines.append("")
        # regular limit
        if len(lines[-1]) >= 70:
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




def decimal_precision_requires(float_val):
    """
    determine number of decimal places required to display
    data fully
    """
    float_val = str(float_val)
    # handle floating point rounding error
    float_val = re.sub(r"0000000.$", "", float_val)
    float_val = re.sub(r"9999999.$", "", float_val)
    no_trailing = str(float(float_val))
    decimal_ind = no_trailing.find(".")
    if decimal_ind is not -1:
        if no_trailing[0] != "0":
            minim = 2
        else:
            minim = 6
        return min(len(no_trailing) - decimal_ind - 1, minim)
    return 0



def rel_plot(left_or_mono, start, end, rate, right=None, fill=None, title=None, 
        plot_type="line", obj_type=None, obj_name=None):
    """
    left and right must be numpy arr with shape (x, 2) arrays of (index, value) to plot.
    if right is not given, assumed to be mono left
    """
    info_block("Generating plot...")
    fig = plt.gcf() # or pylab.gcf() ?
    fig.canvas.set_window_title("{0} '{1}'".format(obj_type, obj_name))

    # channels
    left = left_or_mono
    if right is None:
        right = left_or_mono
    # fill
    if fill is None:
        try:
            if min( (np.min(left[:,1]), np.min(right[:,1])) ) >= 0:
                fill = True
            else:
                fill = False
        except ValueError:
            pass
    # title
    if title is not None:
        fig.suptitle(title)
    # plot type
    if plot_type == "scatter":
        plot_func = plt.scatter
        fill = False
    elif plot_type == "bar":
        plot_func = plt.bar
    else:
        plot_func = plt.plot

    # left: top, beats labels
    axL = plt.subplot(211)
    pos = axL.get_position()
    pos.y0 -= 0.06
    pos.y1 -= 0.06
    axL.set_position(pos)
    axL.xaxis.tick_top()
    axL.xaxis.set_label_position('top')

    rate = rate.to_rate().magnitude

    start_beats = start.to_beats().magnitude
    end_beats = end.to_beats().magnitude
    start = start.to_samps().round().magnitude
    end = end.to_samps().round().magnitude

    tick_size_beats = 1
    tick_number = end_beats - start_beats
    if tick_number < 2:
        tick_size_beats = end_beats - start_beats
        tick_number = 1
    while tick_number > 10:
        tick_number /= 2
        tick_size_beats *= 2
    while tick_number < 5:
        tick_number *= 2
        tick_size_beats /= 2
    tick_locs = []
    tick_labels = []
    for i in np.linspace(start_beats, end_beats, tick_number, endpoint=False):
        tick_locs.append(i)
        axL.axvline(i, linestyle="--", linewidth=0.3, color='#545454', 
            clip_on=False, zorder=11)
        tick_labels.append("{0:.{1}f}".format(i, decimal_precision_requires(i)))
    plt.xticks(tick_locs, tick_labels)
    for tick in axL.xaxis.get_major_ticks()[1::2]:
        tick.set_pad(15)

    plt.xlabel("Beats")
    plt.ylabel("Left amplitude")
    if len(left.shape) == 1:
        valuesL = left
        indexesL = range(start, start + len(left))
    else:
        indexesL, valuesL = zip(*left)
    indexesL = [i/rate for i in indexesL]
    plot_func(indexesL, valuesL)

    # right: bottom, seconds labels
    axR = plt.subplot(212)
    plt.xlabel("Seconds")
    plt.ylabel("Right amplitude")
    if len(right.shape) == 1:
        valuesR = right
        indexesR = range(start, start + len(right))
    else:
        indexesR, valuesR = zip(*right)
    indexesR = [i/rate for i in indexesR]
    for i in np.linspace(start_beats, end_beats, tick_number, endpoint=False):
        ind = Units.beats(str(i) + "b").to_secs().magnitude
        axR.axvline(ind, linestyle="--", linewidth=0.3, color='#545454', 
            clip_on=False, zorder=11)
    plot_func(indexesR, valuesR)

    info_block("Viewing waveform...")
    if fill and len(indexesR) < 1_000_000:
        axR.fill_between(indexesR, valuesR, color='#43C6FF')
        axL.fill_between(indexesL, valuesL, color='#43C6FF')
    plt.show()


