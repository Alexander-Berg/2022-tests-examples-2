# 'x.y.z' -> ['x', 'y', 'z']
def _mkpath(string):
    path = []
    for key in string.split('.'):
        if key != '':
            path.append(key)
    return path


def _match(path1, path2):
    if len(path1) != len(path2):
        return False
    for key1, key2 in zip(path1, path2):
        if key1 == '*' or key2 == '*':
            continue
        if key1 != key2:
            return False
    return True


def _query(json, path):
    try:
        for key in path:
            if json is None:
                break
            if isinstance(json, list):
                if key == '*':
                    key = 0
                else:
                    key = int(key)
                json = json[key]
            elif isinstance(json, dict):
                if key == '*':
                    key = next(iter(json))
                json = json[key]
            else:
                json = None
    except (ValueError, IndexError, StopIteration, KeyError):
        json = None
    return json


def mutate(json, pattern, mutator):
    pattern = _mkpath(pattern)

    def walk(json, path):
        if isinstance(json, list):
            temp = list()
            for idx, value in enumerate(json):
                temp.append(walk(value, path + [str(idx)]))
            json = temp
        elif isinstance(json, dict):
            temp = dict()
            for key, value in json.items():
                temp[key] = walk(value, path + [key])
            json = temp
        if _match(path, pattern):
            json = mutator(json)
        return json

    return walk(json, [])


def sort(json, pattern, *, key=''):
    key = _mkpath(key)

    def mutator(json):
        return sorted(json, key=lambda x: _query(x, key))

    return mutate(json, pattern, mutator)
