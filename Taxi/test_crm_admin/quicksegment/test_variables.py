# pylint: disable=invalid-name,redefined-outer-name

import json

import pytest
import yaml

from crm_admin.quicksegment import variables


@pytest.fixture
def params():
    return variables.Variables({'a': 1, 'b': {'c': 2}, 'd': {'e': {'f': 3}}})


@pytest.mark.parametrize('var, value', [('a', 1), ('b.c', 2), ('d.e.f', 3)])
def test_get(params, var, value):
    assert params.get(var) == value


@pytest.mark.parametrize('var', ['x', 'b.c.x'])
def test_get_missing_value(params, var):
    with pytest.raises(KeyError):
        params.get(var)


@pytest.mark.parametrize(
    'var, default, value', [('b.c', 123, 2), ('x.y', 123, 123)],
)
def test_get_default(params, var, default, value):
    assert params.get_def(var, default) == value


def test_read_yaml(params, tmpdir):
    path = tmpdir / 'params.yaml'
    with open(path, 'wt') as f:
        yaml.dump(params.asdict(), f)

    vs = variables.Variables.read_yaml(path)
    assert vs.asdict() == params.asdict()


def test_read_json(params, tmpdir):
    path = tmpdir / 'params.json'
    with open(path, 'wt') as f:
        json.dump(params.asdict(), f)

    vs = variables.Variables.read_json(path)
    assert vs.asdict() == params.asdict()


def test_empty():
    vs = variables.Variables(None)
    assert vs.asdict() == {}


def test_get_multivalue_group():
    vs = variables.Variables({'g1': [{'val': 1}], 'g2': {'val': 2}})
    assert vs.get_multivalue_group('g1') == [{'val': 1}]

    with pytest.raises(KeyError):
        # not a multivalue group
        vs.get_multivalue_group('g2')

    with pytest.raises(KeyError):
        # missing key
        vs.get_multivalue_group('g3')
