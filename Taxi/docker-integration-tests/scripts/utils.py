import yaml

DEFAULT_PY3_IMAGE = 'registry.yandex.net/taxi/taxi-integration-xenial-base'
DEFAULT_DEPSPY3_PATH = '/usr/lib/yandex/taxi-py3-2/'


def load_yaml(yaml_path):
    with open(yaml_path, 'r') as fp:
        return yaml.load(fp, getattr(yaml, 'CLoader', yaml.Loader))
