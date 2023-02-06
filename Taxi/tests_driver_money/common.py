def are_equal_json(json1, json2) -> bool:
    if (json1 is None) != (json2 is None):
        return False

    if type(json1) is not type(json2):
        return False

    # neither list nor dict
    if not isinstance(json1, (list, dict)):
        return json1 == json2

    # list or dict
    if len(json1) != len(json2):
        return False

    # list - check as set
    if isinstance(json1, list):
        for item1 in json1:
            if not any([are_equal_json(item1, item2) for item2 in json2]):
                return False

        return True

    # dict
    for key, value in json1.items():
        if not are_equal_json(value, json2.get(key)):
            return False

    return True
