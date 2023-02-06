import json
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
    return definitions_mod.ExampleObject(
        sample_string='ss',
        sample_integer=4,
        sample_number=1.2,
        sample_boolean=True,
    )


def test_simple(example_object):
    assert example_object.sample_integer == 4
    assert example_object.optional_integer == 3


def test_repr(example_object):
    # TODO pkostikov: not very beautiful repr
    assert example_object.to_json_string() == repr(example_object)


def test_json_converters(example_object, definitions_mod):
    obj = example_object

    json_str = obj.to_json_string()
    obj_dict = json.loads(json_str)
    assert obj_dict['sample_string'] == 'ss'

    restored_obj = definitions_mod.ExampleObject.from_json_string(json_str)

    for attr in (
            'sample_string',
            'sample_integer',
            'sample_number',
            'sample_boolean',
    ):
        assert getattr(obj, attr) == getattr(restored_obj, attr)

    assert restored_obj.to_json_string() == obj.to_json_string()
    assert restored_obj.serialize() == obj.serialize()
    assert restored_obj == obj


def test_json_loaders(definitions_mod):
    json_str = """{
        "sample_string": "ss",
        "sample_integer": 3,
        "sample_number": 1.2,
        "sample_boolean": true
    }
    """

    obj = definitions_mod.ExampleObject.from_json_string(json_str)
    assert obj.sample_string == 'ss'
    assert obj.sample_integer == 3
    assert obj.optional_integer == 3


def test_default_required(definitions_mod):
    with pytest.raises(TypeError):
        definitions_mod.DefaultRequired()

    obj_no_spec = definitions_mod.DefaultRequired(required_no_default='xx')
    assert obj_no_spec.required_no_default == 'xx'
    assert obj_no_spec.optional_no_default is None
    assert obj_no_spec.optional_default == 'abc'

    obj_spec = definitions_mod.DefaultRequired(
        required_no_default='xx',
        optional_no_default='yy',
        optional_default='zz',
    )
    assert obj_spec.required_no_default == 'xx'
    assert obj_spec.optional_no_default == 'yy'
    assert obj_spec.optional_default == 'zz'


def test_default_required_parse_serialize(definitions_mod):
    no_spec_dict = {'required_no_default': 'xx'}
    obj_no_spec = definitions_mod.DefaultRequired.deserialize(no_spec_dict)
    assert obj_no_spec.required_no_default == 'xx'
    assert obj_no_spec.optional_no_default is None
    assert obj_no_spec.optional_default == 'abc'
    assert obj_no_spec.serialize() == {
        'required_no_default': 'xx',
        'optional_default': 'abc',
    }

    spec_dict = {
        'required_no_default': 'xx',
        'optional_no_default': 'yy',
        'optional_default': 'zz',
    }
    obj_spec = definitions_mod.DefaultRequired.deserialize(spec_dict)
    assert obj_spec.required_no_default == 'xx'
    assert obj_spec.optional_no_default == 'yy'
    assert obj_spec.optional_default == 'zz'
    assert obj_spec.serialize() == {
        'required_no_default': 'xx',
        'optional_no_default': 'yy',
        'optional_default': 'zz',
    }


def test_nested(definitions_mod):
    obj = definitions_mod.Nested.deserialize(
        {'nested': {'str': 'qwerty'}, 'req_arr': [{'opt_int': 3}, {}]},
    )
    assert obj.req_arr[0].opt_int == 3


def test_default_required_vector(definitions_mod):
    with pytest.raises(TypeError):
        definitions_mod.DefaultRequiredVector()

    obj_no_spec = definitions_mod.DefaultRequiredVector(
        required_no_default=[1, 2],
    )
    assert obj_no_spec.required_no_default == [1, 2]
    assert obj_no_spec.optional_no_default is None
    assert obj_no_spec.optional_default == []

    obj_spec = definitions_mod.DefaultRequiredVector(
        required_no_default=[1, 2],
        optional_no_default=[3, 4],
        optional_default=[5, 6],
    )
    assert obj_spec.required_no_default == [1, 2]
    assert obj_spec.optional_no_default == [3, 4]
    assert obj_spec.optional_default == [5, 6]


def test_default_required_vector_parse_serialize(definitions_mod):
    no_spec_dict = {'required_no_default': [1, 2]}
    obj_no_spec = definitions_mod.DefaultRequiredVector.deserialize(
        no_spec_dict,
    )
    assert obj_no_spec.required_no_default == [1, 2]
    assert obj_no_spec.optional_no_default is None
    assert obj_no_spec.optional_default == []
    assert obj_no_spec.serialize() == {
        'required_no_default': [1, 2],
        'optional_default': [],
    }

    spec_dict = {
        'required_no_default': [1, 2],
        'optional_no_default': [3, 4],
        'optional_default': [5, 6],
    }
    obj_spec = definitions_mod.DefaultRequiredVector.deserialize(spec_dict)
    assert obj_spec.required_no_default == [1, 2]
    assert obj_spec.optional_no_default == [3, 4]
    assert obj_spec.optional_default == [5, 6]
    assert obj_spec.serialize() == {
        'required_no_default': [1, 2],
        'optional_no_default': [3, 4],
        'optional_default': [5, 6],
    }


def test_deep_nested(definitions_mod):
    data = {'level_one': {'level_two': {'level_three': [[], [{'i': 3}]]}}}
    obj = definitions_mod.DeepNested.deserialize(data)

    assert obj.serialize() == data
    assert obj.level_one.level_two.level_three[1][0].i == 3


def test_special_characters(definitions_mod):
    obj = definitions_mod.SpecialCharacters()
    assert obj.quote == 'a\\b\'c'
    assert obj.double_quotes == 'a\\b"c'
