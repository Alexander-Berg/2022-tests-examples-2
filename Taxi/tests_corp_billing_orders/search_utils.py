def get_values_by_key(dct, key=None):
    if key is None:
        return dct.values()
    if key in dct:
        return [dct[key]]
    return []
