import pickle


class DumpError(ValueError):
    """DumpError"""


class LoadError(ValueError):
    """DumpError"""


def dumps(data):
    try:
        return pickle.dumps(data)
    except Exception as exc:
        raise DumpError(str(exc))


def loads(data):
    try:
        return pickle.loads(data)
    except Exception as exc:
        raise LoadError(str(exc))
