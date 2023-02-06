import pytest


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
