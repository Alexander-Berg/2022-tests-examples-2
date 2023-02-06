# -*- coding: utf-8 -*-
from unittest import TestCase

import mock
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.perimeter_api.perimeter_api.middlewares import mask_sensitive_fields
from passport.backend.perimeter_api.perimeter_api.roles_hooks import run_pwgen


class TestUtils(TestCase):
    def test_run_pwgen_ok(self):
        process_mock = mock.Mock()
        process_mock.communicate.return_value = (b'stdout', b'stderr')
        popen_mock = mock.Mock(return_value=process_mock)
        with mock.patch('subprocess.Popen', popen_mock):
            pwd = run_pwgen('some-arg some-arg-2')

        eq_(pwd, 'stdout')
        eq_(popen_mock.call_args[0][0], ['pwgen', 'some-arg', 'some-arg-2'])

    def test_run_pwgen_failed(self):
        process_mock = mock.Mock()
        process_mock.communicate.return_value = (b'', b'stderr')
        popen_mock = mock.Mock(return_value=process_mock)
        with mock.patch('subprocess.Popen', popen_mock):
            with assert_raises(RuntimeError):
                run_pwgen('some-arg some-arg-2')

    def test_mask_sensitive_fields(self):
        for source, result in (
            ({}, {}),
            ({'context': {'foo': 'bar'}}, {'context': '***'}),
            ({'secret': 'topsecret'}, {'secret': '***'}),
            ({'not-a-secret': 'topsecret'}, {'not-a-secret': 'topsecret'}),
        ):
            eq_(mask_sensitive_fields(source), result)
