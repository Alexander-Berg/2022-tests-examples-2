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
