def _blank(val):
    return val is None or val == ''

def _allblank(test_list):
    return reduce(lambda cur, new: cur and _blank(new), test_list, False)
