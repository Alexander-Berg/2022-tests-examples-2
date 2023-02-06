import pytest

from taxi_exp.lib.meta_merge import dicts_recursive_merge


def _gen_deep_dict(count):
    result = {'a': {}}
    _inner_result = result['a']
    for _ in range(count - 1):
        _inner_result['a'] = {}
        _inner_result = _inner_result['a']
    return result, ['.'.join('a' * count)]


@pytest.mark.parametrize(
    'dictionary,result',
    [
        ({}, []),
        ({'a': None}, ['a']),
        (
            {
                'a': {
                    'c': 1,
                    'd': 3,
                    'e': [[], 1, 2, 3, {'k': 'l', 'jk': {'kl': 45}, 'o': {}}],
                    'p': [],
                },
                'b': 2,
                'l': [],
                'o': {},
            },
            ['a.c', 'a.d', 'a.e', 'a.p', 'b', 'l', 'o'],
        ),
        (_gen_deep_dict(500)),
    ],
)
def test_path_generator(dictionary, result):
    assert dicts_recursive_merge.gen_paths(dictionary) == result
