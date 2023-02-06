PARK_LIST = ['999011', '999012', '999013', '111500',
             '100504', '111666', '111501', '111502',
             '111503']


def excluded(permitted=('999011',)):
    """
    Returns list of excluded parks, except permitted.
    """
    parks = PARK_LIST.copy()
    for park in permitted:
        parks.remove(park)
    return parks
