
class MC_SuperGlobls():

    DEBUG = True
    TEST_BPM = 120


def p(message, indent=2, o="", i=""):
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
    info_block(message_body + notices, indent=indent, for_prompt=True)


def info_block(message, indent=None, hang=2, newlines=None, trailing_newline=True, leading_newline=True, for_prompt=False):
    """
    default indent is 4.
    for_prompt sets: indent=2 (or override), hang=2, formats for input after
    """
    # configuration
    end = "\n"
    if for_prompt:
        hang = 2
        if indent is None:
            indent = 2
        trailing_newline = False
        end = " "
    if indent is None:
        indent = 4
    if newlines is False:
        leading_newline = False
        trailing_newline = False
    
    # splitting at spaces
    lines = [""]
    for char in message:
        if len(lines[-1]) >= 65:
            if char != " ":
                lines[-1] += "--"
                lines.append("")
        if len(lines[-1]) >= 55:
            last_space = lines[-1].rfind(" ")
            if last_space != -1:
                text = lines[-1][last_space + 1:]
                lines[-1] = lines[-1][:last_space]
                lines.append(text)
                if char != " ":
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


def selection_sort(unsorted, ind, top_n=None, func_on_val=int, func_args=['val'], low_to_high=False):
    """
    func args as array of args, where 'val' is replaced with the value to sort on
    """
    if top_n is None:
        top_n = len(unsorted)
    sorted_final = []
    unsorted_map = []
    val_ind = func_args.index('val')
    for i in unsorted:
        func_args[val_ind] = i[ind]
        map_val = func_on_val(*func_args)
        unsorted_map.append(map_val)
    
    if low_to_high:
        for _ in range(top_n):
            lowest_ind = unsorted_map.index(min(unsorted_map))
            sorted_final.append(unsorted[lowest_ind])
            unsorted_map[lowest_ind] = 100000
    else:
        for _ in range(top_n):
            highest_ind = unsorted_map.index(max(unsorted_map))
            sorted_final.append(unsorted[highest_ind])
            unsorted_map[highest_ind] = -100000
    return sorted_final


def util_main():
    info_block(
        "2134567 1234567 1234567432 4656utyhregt4wr 5r 45r6h t g5e 6r  5dt e y5 6re yt6 u et y ry6 rw y w y w6 ry d y6d r5ey6 7r6t ret yt7j yt7h65gr",
        indent=2,
        for_prompt=True
    )

if __name__ == "__main__":
    util_main()