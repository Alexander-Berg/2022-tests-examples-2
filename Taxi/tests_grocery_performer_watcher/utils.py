def is_subdict(l_dict, r_dict):
    for key, value in r_dict.items():
        if l_dict[key] != value:
            return False
    return True
