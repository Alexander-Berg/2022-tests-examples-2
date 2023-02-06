import copy
import dataclasses
from typing import Dict

from tests_eats_retail_business_alerts import utils


class StrGenerator:
    def __init__(self, prefix='', suffix=''):
        self.cnt = 0
        self.prefix = prefix
        self.suffix = suffix

    def __iter__(self):
        return self

    def __next__(self):
        self.cnt += 1
        return f'{self.prefix}{self.cnt}{self.suffix}'


@dataclasses.dataclass
class BaseObject:
    def update(self, values: Dict):
        for key, value in values.items():
            setattr(self, key, value)

    def clone(self, reset_updated_at=False):
        new_object = copy.deepcopy(self)
        if reset_updated_at:
            new_object.reset_field_recursive('updated_at')
        return new_object

    def reset_field_recursive(self, field):
        _reset_field_recursive(self, field)

    def __eq__(self, other):
        return utils.recursive_dict(self) == utils.recursive_dict(other)


def _reset_field_recursive(data, field_name, visited_objects=None):
    visited_objects = visited_objects or []
    if data in visited_objects:
        return
    visited_objects.append(data)

    if isinstance(data, list):
        for i in data:
            _reset_field_recursive(i, field_name, visited_objects)
    elif isinstance(data, dict):
        _reset_field_recursive(
            list(data.values()), field_name, visited_objects,
        )
    elif issubclass(type(data), BaseObject):
        if hasattr(data, field_name):
            setattr(data, field_name, None)
        _reset_field_recursive(data.__dict__, field_name, visited_objects)
