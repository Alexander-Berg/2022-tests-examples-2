import pytest

from taxi_pyml.codegen.serialization import ValidationError

from taxi_pyml.example import objects as py_objects


@pytest.mark.parametrize(
    ('data', 'cls', 'error'),
    [
        pytest.param(
            {'i': 234, 'unexpected_field': 'value'},
            py_objects.Dummy,
            ValidationError,
            id='additional_properties',
        ),
        pytest.param(
            {'i': [234, 567]},
            py_objects.Dummy,
            ValidationError,
            id='array_instead_of_int',
        ),
        pytest.param(
            {'i': 'abba'},
            py_objects.Dummy,
            ValidationError,
            id='string_instead_of_int',
        ),
        pytest.param(
            {'i': {'some_field': 'some_value'}},
            py_objects.Dummy,
            ValidationError,
            id='object_instead_of_int',
        ),
        pytest.param(
            {}, py_objects.Dummy, KeyError, id='required_value_is_missing',
        ),
        pytest.param(234, py_objects.Dummy, ValidationError, id='not_a_dict'),
        pytest.param(
            {'nested': 'value', 'req_array': []},
            py_objects.Nested,
            ValidationError,
            id='value_instead_of_object',
        ),
    ],
)
def test_validation(data, cls, error):
    with pytest.raises(error):
        cls.deserialize(data)
