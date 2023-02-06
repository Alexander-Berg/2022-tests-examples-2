def patch_classes(data):
    type_data = type(data)

    if type_data is list:
        for value in data:
            patch_classes(value)

    elif type_data is dict:
        for key, value in data.items():
            if key == 'classes' and isinstance(value, list):
                value.sort()
            else:
                patch_classes(value)

    return data


def remove_extra_keys(actual, expected):
    """
    Removes extra keys in 'actual' response object, that are missing
    in 'expected', including nested keys.

    :param actual: Actual candidates response
    :param expected: Expected candidates response

    :returns: actual response without extra keys
    """
    type_actual = type(actual)
    type_expected = type(expected)

    if type_actual is list and type_expected is list:
        for actual_item, expected_item in zip(actual, expected):
            remove_extra_keys(actual_item, expected_item)

    if type_actual is not dict or type_expected is not dict:
        return actual

    for key in list(actual):
        if key not in expected:
            del actual[key]
        else:
            remove_extra_keys(actual[key], expected[key])

    return actual


def sort_candidates(data):
    """
    Sorts candidates by dbid uuid in both actual and expected response objects.
    """
    if 'candidates' in data:
        data['candidates'].sort(key=lambda x: x['dbid'] + x['uuid'])
    if 'drivers' in data:
        data['drivers'].sort(key=lambda x: x['dbid'] + x['uuid'])

    return data


def normalize(actual, expected):
    """
    Normalizes actual and expected response objects such that:
        - extra keys in 'actual' are removed;
        - 'classes' lists in 'actual' and 'expected' are sorted;

    :param actual: Actual candidates response
    :param expected: Expected candidates response

    :returns: tuple (actual, expected) - normalized actual and expected
    responses
    """
    actual = sort_candidates(actual)
    expected = sort_candidates(expected)
    actual = remove_extra_keys(actual, expected)
    for data in (actual, expected):
        data = patch_classes(data)
    return actual, expected
