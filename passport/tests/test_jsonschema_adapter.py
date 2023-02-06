# -*- coding: utf-8 -*-

from collections import OrderedDict
import unittest

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core import validators
from passport.backend.core.validators.jsonschema_adapter import (
    JsonSchema,
    validate_jsonschema_form,
)


class JsonSchemaAdapterTestCase(unittest.TestCase):

    def test_schema_sorting_for_object(self):
        """Обеспечиваем правильный порядок валидаторов в схеме для объекта"""
        schema = OrderedDict([
            ('$schema', 'http://json-schema.org/schema#'),
            ('additionalProperties', False),
            ('properties', {'elem': {'type': 'string'}}),
            ('required', ['elem']),
            ('type', 'object'),
        ])

        eq_(
            list(JsonSchema(schema).schema.items()),
            [
                ('type', 'object'),
                ('required', ['elem']),
                ('properties', {'elem': {'type': 'string'}}),
                ('$schema', 'http://json-schema.org/schema#'),
                ('additionalProperties', False),
            ],
        )

    def test_schema_sorting_nested_for_items(self):
        """Обеспечиваем правильный порядок валидаторов в схеме для вложенного списка"""
        subschema = OrderedDict([
            ('uniqueItems', True),
            ('items', {'type': 'string'}),
            ('type', 'array'),
        ])
        schema = OrderedDict([
            ('$schema', 'http://json-schema.org/schema#'),
            ('additionalProperties', False),
            ('properties', {'elem': subschema}),
            ('required', ['elem']),
            ('type', 'object'),
        ])

        subschema_sorted = OrderedDict([
            ('type', 'array'),
            ('items', {'type': 'string'}),
            ('uniqueItems', True),
        ])
        eq_(
            JsonSchema(schema).schema,
            OrderedDict([
                ('type', 'object'),
                ('required', ['elem']),
                ('properties', {'elem': subschema_sorted}),
                ('$schema', 'http://json-schema.org/schema#'),
                ('additionalProperties', False),
            ]),
        )

    def test_validation_with_unsorted_schema_raises_error(self):
        schema = {
            '$schema': 'http://json-schema.org/schema#',
            'type': 'object',
        }

        assert_raises(TypeError, validate_jsonschema_form, schema, {})

    def test_extended_properties_validation_error(self):
        schema = JsonSchema({
            '$schema': 'http://json-schema.org/schema#',
            'type': 'object',
            'required': ['elem', 'field'],
            'properties': {
                'elem': validators.SimpleEmailValidator(),
                'field': {'type': 'string'},
            },
            'additionalProperties': False,
        })

        errors = validate_jsonschema_form(schema, {'elem': 'not_a_valid_email@'})

        eq_(errors, ['elem.invalid', 'field.empty'])

    def test_extended_properties_nested_validation_error(self):
        schema = JsonSchema({
            '$schema': 'http://json-schema.org/schema#',
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'elem': validators.Birthday(),
                },
            },
        })

        errors = validate_jsonschema_form(schema, [{'elem': '2010-10-10'}, {}, {'elem': 'birthday'}, []])

        eq_(errors, ['elem.invalid', 'invalid'])

    def test_extended_items_validation_error(self):
        schema = JsonSchema({
            '$schema': 'http://json-schema.org/schema#',
            'type': 'object',
            'properties': {
                'custom_list': {
                    'type': 'array',
                    'items': validators.Service(),
                },
                'list': {
                    'type': 'array',
                    'items': [
                        {'type': 'string'},
                        {'type': 'integer'},
                    ],
                },
            },
        })

        errors = validate_jsonschema_form(
            schema,
            {
                'custom_list': ['1', 'money'],
                'list': ['a', 'b'],
            },
        )

        eq_(errors, ['custom_list.invalid', 'list.invalid'])

    def test_extended_items_unique_items(self):
        schema = JsonSchema({
            '$schema': 'http://json-schema.org/schema#',
            'type': 'array',
            'items': validators.String(strip=True),
            'uniqueItems': True,
        })

        errors = validate_jsonschema_form(schema, {})
        eq_(errors, ['invalid'])

        errors = validate_jsonschema_form(schema, ['123', '234', '  123 ', '  1 2 3'])
        eq_(errors, ['duplicate'])

    def test_extended_required(self):
        schema = JsonSchema({
            '$schema': 'http://json-schema.org/schema#',
            'type': 'object',
            'properties': {
                'prop1': {'type': 'string'},
                'prop2': {'type': 'integer'},
            },
            'required': ['prop1'],
        })

        errors = validate_jsonschema_form(schema, [])
        eq_(errors, ['invalid'])

        errors = validate_jsonschema_form(schema, {'prop2': 10})
        eq_(errors, ['prop1.empty'])
