import datetime as dt

import dateutil as du
import pytest


def now_with_tz():
    return dt.datetime.now().replace(tzinfo=du.tz.tzlocal())


def update_dict_by_paths(data, values):
    """
    works similar to `data.update(values)`,
    but keys in `values` are used as a `/`-separated path for `data`.
    E.g. `'key/path': 1`, will set the value of `data[key][path]` to 1
    """
    for value_path, value in values.items():
        _update_dict_value_by_path(data, value_path, value)


def _update_dict_value_by_path(data, value_path, value):
    cur_path = data
    last_path = data
    split_path = value_path.split('/')
    for i in split_path:
        if i not in cur_path:
            cur_path[i] = {}
        last_path = cur_path
        cur_path = cur_path[i]

    last_path[split_path[-1]] = value


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
