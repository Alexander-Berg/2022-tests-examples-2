import pytest

import atlas_backend.utils.common as common


@pytest.mark.parametrize(
    'value,expected',
    [
        ({'a': 1}, {'a': 1}),
        ({'a': 1, 'b': 2}, {'a': 1, 'b': 2}),
        ({'a': 1, 'b': {'c': 2, 'd': 5}}, {'a': 1, 'b.c': 2, 'b.d': 5}),
        (
            {'a': 1, 'b': {'c': {'e': [1, 2, 3]}, 'd': 5}},
            {'a': 1, 'b.c.e': [1, 2, 3], 'b.d': 5},
        ),
        ({'a': {'b': {'c': {'d': {'e': 1}}}}}, {'a.b.c.d.e': 1}),
        ({'a': '1'}, {'a': '1'}),
        (
            {
                'a': {'b': '1', 'c': '2'},
                'b': {'d': {'c': '5', 'f': '100'}, 'a': {'e': '2', 'f': '5'}},
            },
            {
                'a.b': '1',
                'a.c': '2',
                'b.d.c': '5',
                'b.d.f': '100',
                'b.a.e': '2',
                'b.a.f': '5',
            },
        ),
    ],
)
def test_flatten_nested_dicts(value, expected):
    result = common.flatten_nested_dicts(value)
    assert result == expected


def test_flatten_nested_dicts_dot_names_collision():
    dct = {'a.b': {'c': 1}, 'a': {'b': {'c': 2}}}
    with pytest.raises(RuntimeError):
        common.flatten_nested_dicts(dct)
