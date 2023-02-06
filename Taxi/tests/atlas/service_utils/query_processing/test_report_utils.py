import pytest

import atlas.service_utils.query_processing.report_utils as ru


def test_extended_quadkeys_normal():
    quadkeys = ['10', '12']
    expected = {'100', '101', '102', '103', '120', '121', '122', '123'}
    assert expected == set(ru.extended_quadkeys(quadkeys, 3))


def test_extended_quadkeys_empty_extention():
    quadkeys = ['10', '12']
    expected = {'10', '12'}
    assert expected == set(ru.extended_quadkeys(quadkeys, 2))


def test_shrink_quadkeys():
    quadkeys = ['100', '101', '102', '103', '210', '211', '212', '213']
    expected = {'10', '21'}
    assert expected == set(ru.shrink_quadkeys(quadkeys, 2))

    quadkeys = ['100', '200']
    with pytest.raises(KeyError):
        ru.shrink_quadkeys(quadkeys, 2)
