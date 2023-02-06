def unordered_lists_are_equal(list1, list2):
    if len(list2) != len(list1):
        return False

    def _check_one_list_is_sublist_of_other(first, second):
        for element in first:
            if element not in second:
                return False

        return True

    return _check_one_list_is_sublist_of_other(
        list1, list2,
    ) and _check_one_list_is_sublist_of_other(list2, list1)


def dict_contains_sub_dict(dict_, sub_dict):
    for key, value in sub_dict.items():
        if key not in dict_ or dict_[key] != value:
            return False

    return True


def del_fields_from_dict(dict_, *fields):
    for field in fields:
        del dict_[field]

    return dict_
