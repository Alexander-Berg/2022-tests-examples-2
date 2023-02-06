import pytest

from ctaxi_pyml import example as pybind_objects
from taxi_pyml.example import objects as py_objects


pytestmark = [
    pytest.mark.parametrize(
        'definitions_mod',
        [
            pytest.param(pybind_objects, id='pybind'),
            pytest.param(py_objects, id='py'),
        ],
    ),
]


@pytest.fixture
def example_object():
    return py_objects.ExampleUnorderedSet(setitems=set([50, 40, 30, 20, 10]))


@pytest.fixture
def object_data():
    return {'setitems': [50, 40, 30, 20, 10]}


def test_set_deserialization(object_data, definitions_mod):
    obj = definitions_mod.ExampleUnorderedSet.deserialize(object_data)
    assert 10 in obj.setitems
    assert 20 in obj.setitems
    assert sorted(obj.serialize()['setitems']) == sorted(
        object_data['setitems'],
    )


def test_set_json_deserialization(definitions_mod):
    json_str = '{"setitems": [50, 40, 30, 20, 10]}'
    obj = definitions_mod.ExampleUnorderedSet.from_json_string(json_str)
    assert 10 in obj.setitems
    assert 20 in obj.setitems


def test_set_json_serialization(example_object, definitions_mod):
    json_str = example_object.to_json_string()
    obj = definitions_mod.ExampleUnorderedSet.from_json_string(json_str)
    assert example_object == obj
