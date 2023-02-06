# coding: utf8
from sibilla import utils


def test_intersection():
    def _t(needle, hashstack):
        assert utils.contains(needle, hashstack)

    _t('', '')
    _t({}, {'a': 'b'})
    _t([{}], [{}])
    _t({'a': 1, 'b': 2}, {'b': 2, 'a': 1})
    _t(['a'], ['b', 'c', 'a', 'd'])
    _t([{'a': 1}], [{'a': 1, 'b': 1}, {'a': 1, 'b': 1}, {'a': 1, 'b': 1}])
