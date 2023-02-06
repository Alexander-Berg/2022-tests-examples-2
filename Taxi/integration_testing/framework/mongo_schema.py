import os

import yaml


# pylint: disable=invalid-name
YAML_LOADER = getattr(yaml, 'CLoader', yaml.Loader)

# pylint: disable=invalid-name
YAML_EXT = '.yaml'


class MongoSchema:
    def __init__(self, directory):
        self._loaded = {}
        self._paths = _get_paths(directory)

    def __getitem__(self, name):
        if name not in self._paths:
            raise KeyError('Missing schema file for collection %s' % (name,))
        if name not in self._loaded:
            with open(self._paths[name]) as file:
                self._loaded[name] = yaml.load(file, YAML_LOADER)
        return self._loaded[name]

    def __iter__(self):
        return iter(self._paths)

    def __len__(self):
        return len(self._paths)

    def __contains__(self, item):
        return item in self._paths

    def items(self):
        for name in self._paths:
            value = self.__getitem__(name)
            yield (name, value)


def _get_paths(directory):
    result = {}
    for relative_path in os.listdir(directory):
        collection, ext = os.path.splitext(relative_path)
        if ext != YAML_EXT or not collection or collection.startswith('.'):
            continue
        result[collection] = os.path.join(directory, relative_path)
    return result
