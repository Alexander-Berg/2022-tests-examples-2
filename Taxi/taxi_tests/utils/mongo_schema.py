import collections.abc
import glob
import os
import typing

from taxi_tests.utils import yaml_util


class MongoSchema(collections.abc.Mapping):
    def __init__(self, directory):
        self._loaded = {}
        self._paths = _get_paths(directory)

    def __getitem__(self, name):
        if name not in self._paths:
            raise KeyError(f'Missing schema file for collection {name}')
        if name not in self._loaded:
            self._loaded[name] = yaml_util.load_file(self._paths[name])
        return self._loaded[name]

    def __iter__(self):
        return iter(self._paths)

    def __len__(self) -> int:
        return len(self._paths)


def _get_paths(directory) -> typing.Dict[str, str]:
    result = {}
    for path in glob.glob(os.path.join(directory, '*.yaml')):
        collection, _ = os.path.splitext(os.path.basename(path))
        result[collection] = path
    return result
