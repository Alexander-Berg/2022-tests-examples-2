import yaml

if hasattr(yaml, 'CLoader'):
    _Loader = yaml.CLoader  # type: ignore
else:
    _Loader = yaml.Loader  # type: ignore


def load_file(path, encoding='utf-8'):
    with open(path, 'r', encoding=encoding) as fp:
        return yaml.load(fp, Loader=_Loader)


def load(file):
    return yaml.load(file, Loader=_Loader)
