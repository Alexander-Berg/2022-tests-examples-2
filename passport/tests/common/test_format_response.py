# -*- coding: utf-8 -*-
import json
import unittest

from nose.tools import eq_
from passport.backend.adm_api.common.format_response import (
    format_error,
    format_errors,
    JsonLoggedResponse,
)
from passport.backend.adm_api.test.utils import with_settings_hosts
from passport.backend.adm_api.test.views import ViewsTestEnvironment
from passport.backend.core.validators.validators import Invalid


@with_settings_hosts()
class LoggedJsonResponseTestCase(unittest.TestCase):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_original_response_not_changed(self):
        kwargs = {
            'sensitive_fields': ['baz', 'foo.bar'],
            'baz': 'original-secret',
            'foo': {
                'bar': 'nested-secret',
            }
        }

        with self.env.client.application.test_request_context():
            resp = JsonLoggedResponse(**kwargs)

            logdata = json.loads(resp.logdata())
            eq_(logdata['baz'], '*****')
            eq_(logdata['foo']['bar'], '*****')

            eq_(resp.dict_['baz'], 'original-secret')
            eq_(resp.dict_['foo']['bar'], 'nested-secret')


class TestFormatError(unittest.TestCase):
    def test_format_error(self):
        eq_(format_error('code', 'msg', 'field'), {'code': 'code', 'message': 'msg', 'field': 'field'})

    def test_format_error_lower_code(self):
        eq_(format_error('cOdE', 'msg', 'field'), {'code': 'code', 'message': 'msg', 'field': 'field'})

    def test_format_error_no_field(self):
        eq_(format_error('cOdE', 'msg'), {'code': 'code', 'message': 'msg', 'field': None})


class TestFormatErrors(unittest.TestCase):
    def test_simple_error(self):
        error = Invalid(('code', 'msg'), None, None)
        eq_(format_errors(error), [{'code': 'code', 'message': 'msg', 'field': None}])

    def test_error_list(self):
        error = Invalid(('code', 'msg'), None, None, error_list=[
            Invalid(('code1', 'msg'), None, None),
            Invalid(('code2', 'msg'), None, None),
        ])
        eq_(
            format_errors(error),
            [
                {'code': 'code1', 'message': 'msg', 'field': None},
                {'code': 'code2', 'message': 'msg', 'field': None},
            ],
        )

    def test_error_dict(self):
        error = Invalid(('code', 'msg'), None, None, error_dict={
            'field1': Invalid(('code1', 'msg'), None, None),
            'field2': Invalid(('code2', 'msg'), None, None),
        })
        actual_errors = format_errors(error)
        expected_errors = [
            {'code': 'code1', 'message': 'msg', 'field': 'field1'},
            {'code': 'code2', 'message': 'msg', 'field': 'field2'},
        ]
        assert actual_errors == expected_errors
