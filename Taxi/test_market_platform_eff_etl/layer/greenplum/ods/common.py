def get_value_by_path(obj: dict, path: str):
    parts = path.split('.')
    tmp = obj
    for i in parts:
        if i in tmp:
            tmp = tmp[i]
        else:
            return None
    return tmp


def execute_extractors(obj, extractors: dict) -> dict:
    res = {}
    for (key, value) in extractors.items():
        if isinstance(value, str):
            res[key] = get_value_by_path(obj, value)
        elif callable(value):
            res[key] = value(obj)
        else:
            raise NotImplementedError()
    return res
