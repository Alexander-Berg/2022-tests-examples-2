# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core import validators


TEST_SCHEMA = {
    'type': 'object',
    'properties': {
        'prop1': {'type': 'string'},
        'prop2': {'type': 'number'},
        'prop3': {'type': 'array', 'items': {'type': 'integer'}},
    },
}


class TestJSONValidator(unittest.TestCase):
    def setUp(self):
        self.v = validators.JSONValidator()
        self.schema_v = validators.JSONValidator(schema=TEST_SCHEMA)

    @raises(validators.Invalid)
    def test_invalid_json(self):
        self.v.to_python(u'[1, "2ф", 3g]')

    def test_valid_json(self):
        eq_(
            self.v.to_python(u'[1, "2ф", 3]'),
            [1, u'2ф', 3],
        )

    def test_valid_json_with_schema(self):
        eq_(
            self.schema_v.to_python(u'{"prop1":"фыва","prop2":1.2,"prop3":[10],"extra":0}'),
            {'prop1': u'фыва', 'prop2': 1.2, 'prop3': [10], 'extra': 0},
        )

    @raises(validators.Invalid)
    def test_invalid_json_with_schema(self):
        self.schema_v.to_python(u'{"prop1":"фыва","prop2":1.2,"prop3":[10.1],"extra":0}')
