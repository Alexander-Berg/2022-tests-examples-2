# запускать из /uservices командой
# python -m util.schemas_merger.tests.test_schemas_merger

import copy

import pytest

from util.schemas_merger import schemas_merger as sm


_SCHEMA_TEMPLATE = {
    'type': 'object',
    'additionalProperties': False,
    'required': [],
    'properties': {},
}

_ARRAY_PROPERTY = {
    'type': 'array',
    'description': 'some_description',
    'x-taxi-cpp-type': 'std::unordered_set',
    'items': {'type': 'string'},
}

_STRING_PROPERTY = {
    'type': 'string',
    'description': 'some_description',
    'example': 'example',
    'default': 'str',
}

_OBJECT_PROPERTY = {
    'type': 'object',
    'additionalProperties': False,
    'required': [],
    'properties': {
        'sub_object': {
            'type': 'object',
            'additionalProperties': False,
            'required': ['first_sub_sub_object'],
            'properties': {
                'sub_sub_object': {
                    'type': 'object',
                    'additionalProperties': False,
                    'required': [],
                    'properties': {
                        'sub_sub_sub_object': {
                            'type': 'object',
                            'additionalProperties': False,
                            'required': ['str1'],
                            'properties': {'str1': _STRING_PROPERTY},
                        },
                    },
                },
                'string_property': _STRING_PROPERTY,
            },
        },
        'boolean_property': {'type': 'boolean', 'default': True},
    },
}

_PROP = 'properties'
_AP = 'additionalProperties'
_OP = 'object_property'
_SP = 'string_property'
_REASON = 'x-taxi-additional-properties-true-reason'


def test_simple_merge():
    first_schema = copy.deepcopy(_SCHEMA_TEMPLATE)
    first_schema[_PROP][_SP] = _STRING_PROPERTY
    first_schema[_PROP]['array_property'] = _ARRAY_PROPERTY
    first_schema['required'].append('array_property')
    second_schema = copy.deepcopy(_SCHEMA_TEMPLATE)
    second_schema[_PROP][_SP] = _STRING_PROPERTY
    first_schema['required'].append(_SP)

    common_schema = sm.merge_schemas(
        {'second': second_schema, 'first': first_schema},
    )
    assert len(common_schema['required']) == 2
    assert len(common_schema[_PROP]) == 2


def test_nested_merge():
    first_schema = copy.deepcopy(_SCHEMA_TEMPLATE)
    first_schema[_PROP][_OP] = copy.deepcopy(_OBJECT_PROPERTY)
    second_schema = copy.deepcopy(_SCHEMA_TEMPLATE)
    second_object_property = {
        'type': 'object',
        'additionalProperties': False,
        'required': [],
        'properties': {
            'sub_object': {
                'type': 'object',
                'additionalProperties': False,
                'required': ['second_sub_sub_object'],
                'properties': {
                    'sub_sub_object': {
                        'type': 'object',
                        'additionalProperties': False,
                        'required': [],
                        'properties': {
                            'sub_sub_sub_object': {
                                'type': 'object',
                                'additionalProperties': False,
                                'required': ['str2'],
                                'properties': {'str2': _STRING_PROPERTY},
                            },
                        },
                    },
                },
            },
        },
    }
    second_schema[_PROP][_OP] = second_object_property

    common_schema = sm.merge_schemas(
        {'first': first_schema, 'second': second_schema},
    )
    temp0 = common_schema[_PROP][_OP][_PROP]
    assert len(temp0) == 2
    assert len(temp0['sub_object']['required']) == 2
    temp2 = temp0['sub_object'][_PROP]['sub_sub_object'][_PROP][
        'sub_sub_sub_object'
    ]
    assert len(temp2['required']) == 2
    assert len(temp2[_PROP]) == 2


def test_conflict_in_add_properties_first():
    first_schema = copy.deepcopy(_SCHEMA_TEMPLATE)
    first_schema[_PROP][_OP] = copy.deepcopy(_OBJECT_PROPERTY)
    second_schema = copy.deepcopy(_SCHEMA_TEMPLATE)
    second_object_property = {
        'type': 'object',
        'additionalProperties': True,
        _REASON: 'true reason',
        'required': [],
        'properties': {
            'boolean_property': {'type': 'boolean', 'default': True},
            'second_property': {'type': 'integer', 'default': 10},
        },
    }
    second_schema[_PROP][_OP] = second_object_property

    common_schema = sm.merge_schemas(
        {'first': first_schema, 'second': second_schema},
    )
    temp = common_schema[_PROP][_OP]
    assert len(temp[_PROP]) == 3
    assert _REASON in temp


def test_conflict_in_add_properties_second():
    first_schema = copy.deepcopy(_SCHEMA_TEMPLATE)
    first_schema[_PROP][_OP] = copy.deepcopy(_OBJECT_PROPERTY)
    first_schema[_PROP][_OP][_PROP]['sub_object'][_PROP]['sub_sub_object'][
        _PROP
    ]['sub_sub_sub_object'][_AP] = True
    second_schema = copy.deepcopy(_SCHEMA_TEMPLATE)
    second_object_property = {
        'type': 'object',
        'additionalProperties': False,
        _REASON: 'Various types of requirements',
        'required': [],
        'properties': {
            'sub_object': {
                'type': 'object',
                'additionalProperties': False,
                'required': ['second_sub_sub_object'],
                'properties': {
                    'sub_sub_object': {
                        'type': 'object',
                        'additionalProperties': False,
                        'required': [],
                        'properties': {
                            'sub_sub_sub_object': {
                                'type': 'object',
                                'additionalProperties': {
                                    'type': 'array',
                                    'items': {'type': 'keyword'},
                                },
                                'required': ['str2'],
                                'properties': {'str2': _STRING_PROPERTY},
                            },
                        },
                    },
                },
            },
        },
    }
    second_schema[_PROP][_OP] = second_object_property
    with pytest.raises(ValueError, match=r'.*keyword.*'):
        sm.merge_schemas({'first': first_schema, 'second': second_schema})


def test_conflict_in_add_properties_third():
    first_schema = copy.deepcopy(_SCHEMA_TEMPLATE)
    first_schema[_PROP][_OP] = copy.deepcopy(_OBJECT_PROPERTY)
    first_schema[_PROP][_OP][_PROP]['sub_object'][_PROP]['sub_sub_object'][
        _PROP
    ]['sub_sub_sub_object'][_AP] = (
        {'type': 'array', 'items': {'type': 'keyword2'}}
    )
    second_schema = copy.deepcopy(_SCHEMA_TEMPLATE)
    second_object_property = {
        'type': 'object',
        'additionalProperties': False,
        _REASON: 'Various types of requirements',
        'required': [],
        'properties': {
            'sub_object': {
                'type': 'object',
                'additionalProperties': False,
                'required': ['second_sub_sub_object'],
                'properties': {
                    'sub_sub_object': {
                        'type': 'object',
                        'additionalProperties': False,
                        'required': [],
                        'properties': {
                            'sub_sub_sub_object': {
                                'type': 'object',
                                'additionalProperties': {
                                    'type': 'array',
                                    'items': {'type': 'keyword'},
                                },
                                'required': ['str2'],
                                'properties': {'str2': _STRING_PROPERTY},
                            },
                        },
                    },
                },
            },
        },
    }
    second_schema[_PROP][_OP] = second_object_property
    with pytest.raises(ValueError, match=r'.*keyword2.*'):
        sm.merge_schemas({'first': first_schema, 'second': second_schema})


def test_non_object_merge():
    first_schema = copy.deepcopy(_SCHEMA_TEMPLATE)
    first_string_property = copy.deepcopy(_STRING_PROPERTY)
    del first_string_property['default']
    first_schema[_PROP][_SP] = first_string_property

    second_schema = copy.deepcopy(_SCHEMA_TEMPLATE)
    second_object_property = copy.deepcopy(_STRING_PROPERTY)
    second_schema[_PROP][_SP] = second_object_property
    common_schema = sm.merge_schemas(
        {'second': second_schema, 'first': first_schema},
    )
    assert not common_schema[_PROP][_SP].get('default')


def test_conflict_in_fields():
    first_schema = copy.deepcopy(_SCHEMA_TEMPLATE)
    first_array_property = copy.deepcopy(_ARRAY_PROPERTY)
    first_array_property['items']['type'] = 'integer'
    first_schema[_PROP]['array_prop'] = first_array_property

    second_schema = copy.deepcopy(_SCHEMA_TEMPLATE)
    second_object_property = copy.deepcopy(_ARRAY_PROPERTY)
    second_schema[_PROP]['array_prop'] = second_object_property
    with pytest.raises(ValueError, match=r'.*items.*'):
        sm.merge_schemas({'first': first_schema, 'second': second_schema})


def test_expand_required():
    first_schema = copy.deepcopy(_SCHEMA_TEMPLATE)
    first_schema[_PROP][_OP] = {
        'type': 'object',
        'additionalProperties': False,
        'properties': {'str1': _STRING_PROPERTY},
    }
    second_schema = copy.deepcopy(_SCHEMA_TEMPLATE)
    second_schema[_PROP][_OP] = {
        'type': 'object',
        'additionalProperties': False,
        'properties': {'str2': _STRING_PROPERTY},
    }

    common_schema = sm.merge_schemas(
        {'second': second_schema, 'first': first_schema},
    )
    assert not common_schema[_PROP][_OP].get('required')

    first_schema[_PROP][_OP]['required'] = ['str1']
    second_schema[_PROP][_OP]['required'] = ['str2']
    common_schema = sm.merge_schemas(
        {'second': second_schema, 'first': first_schema},
    )
    assert common_schema[_PROP][_OP]['required'] == ['str1', 'str2']


def test_one_of():
    first_schema = copy.deepcopy(_SCHEMA_TEMPLATE)
    second_schema = copy.deepcopy(_SCHEMA_TEMPLATE)
    first_schema[_PROP]['prop_with_one_of'] = {
        'description': 'some text',
        'oneOf': [
            {'type': 'array', 'items': {'type': 'integer', 'example': 5}},
            {'type': 'integer', 'description': 'some text'},
            {'type': 'boolean'},
            {
                'type': 'object',
                _AP: 'false',
                'required': ['first', 'second'],
                'properties': {
                    'second': {'type': 'boolean', 'description': 'text'},
                    'first': {'type': 'string'},
                },
            },
        ],
    }
    second_schema[_PROP]['prop_with_one_of'] = {
        'description': 'another text',
        'oneOf': [
            {'type': 'array', 'items': {'type': 'integer', 'example': 5}},
            {'type': 'integer', 'description': 'some text'},
            {'type': 'boolean'},
            {
                'type': 'object',
                _AP: 'false',
                'required': ['first', 'second'],
                'properties': {
                    'second': {'type': 'boolean', 'description': 'text'},
                    'first': {'type': 'string'},
                },
            },
        ],
    }
    common_schema = sm.merge_schemas(
        {'second': second_schema, 'first': first_schema},
    )
    temp = common_schema[_PROP]['prop_with_one_of']
    assert len(temp) == 2
    assert len(temp['oneOf']) == 4


def test_all():
    test_simple_merge()
    test_nested_merge()
    test_conflict_in_add_properties_first()
    test_conflict_in_add_properties_second()
    test_conflict_in_add_properties_third()
    test_non_object_merge()
    test_conflict_in_fields()
    test_expand_required()
    test_one_of()


test_all()
