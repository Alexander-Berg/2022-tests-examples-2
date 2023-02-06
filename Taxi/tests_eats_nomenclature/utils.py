import pytest


def remove_public_id(response_json):
    """
    Remove public_id from categories and items objects,
    checks one's existance
    """
    for category in response_json['categories']:
        assert category.pop('public_id', None) is not None
        for item in category['items']:
            assert item.pop('public_id', None) is not None
    return response_json


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
