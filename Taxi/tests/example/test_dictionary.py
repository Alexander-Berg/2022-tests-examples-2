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
def example_object(definitions_mod):
    return definitions_mod.ExampleUnorderedMap(
        key_value_collection=dict({'key1': 10, 'key2': 20}),
    )


@pytest.fixture
def object_data():
    return {'key_value_collection': dict({'key1': 10, 'key2': 20})}


def test_dictionary_deserialization(object_data, definitions_mod):
    obj = definitions_mod.ExampleUnorderedMap.deserialize(object_data)
    assert obj.key_value_collection['key1'] == 10
    assert obj.key_value_collection['key2'] == 20
    assert obj.serialize() == object_data


def test_dictionary_json_deserialization(definitions_mod):
    json_str = '{"key_value_collection": {"key1": 10, "key2": 20}}'
    obj = definitions_mod.ExampleUnorderedMap.from_json_string(json_str)
    assert obj.key_value_collection['key1'] == 10
    assert obj.key_value_collection['key2'] == 20


def test_dictionary_json_serialization(example_object, definitions_mod):
    json_str = example_object.to_json_string()
    obj = definitions_mod.ExampleUnorderedMap.from_json_string(json_str)
    assert example_object == obj
