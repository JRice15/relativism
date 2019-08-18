from relativism import *





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
    pass

    

if __name__ == "__main__":
    util_main()