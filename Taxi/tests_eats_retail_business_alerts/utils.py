import datetime as dt
from typing import List

import dateutil as du
import pytest


def now_with_tz():
    return dt.datetime.now().replace(tzinfo=du.tz.tzlocal())


def gen_bool_params(name, id_name=None):
    id_name = id_name or name
    return {
        'argnames': name,
        'argvalues': [
            pytest.param(True, id=f'{id_name}(+)'),
            pytest.param(False, id=f'{id_name}(-)'),
        ],
    }


def gen_list_params(name, values, id_name=None):
    id_name = id_name or name
    return {
        'argnames': name,
        'argvalues': [pytest.param(i, id=f'{id_name}({i})') for i in values],
    }


def recursive_dict(x):
    result_dict = {}
    for key, value in x.__dict__.items():
        if isinstance(value, List):
            result_dict[key] = [recursive_dict(i) for i in sorted(value)]
        elif '__dict__' in dir(value):
            result_dict[key] = recursive_dict(value)
        else:
            result_dict[key] = value
    return result_dict
