# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import unittest

from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.social.api.common import (
    get_timestamp,
    make_error_dict,
    required_args,
)
from passport.backend.social.common.limits import QLimits
from passport.backend.social.common.test.consts import REQUEST_ID1

from .common import TestApiAppCase


class TestMakeErrorDict(TestApiAppCase):
    def test_create_description(self):
        error_dict = make_error_dict(name='foo-empty')
        eq_(error_dict['description'], 'Parameter `foo` is required')


class TestRequiredArgs(TestApiAppCase):
    def setUp(self):
        super(TestRequiredArgs, self).setUp()

        def func(foo):
            pass
        self._func = func

    def test_required_missing(self):
        func = required_args(foo=int)(self._func)

        rv = func()

        eq_(rv.status_code, 400)
        eq_(
            json.loads(rv.data),
            {
                'error': {
                    'name': 'foo-empty',
                    'description': 'Parameter `foo` is required',
                    'request_id': REQUEST_ID1,
                },
            },
        )

    def test_invalid_value(self):
        func = required_args(foo=int)(self._func)

        with self.app.test_request_context(query_string={'foo': 'foo'}):
            rv = func()

        eq_(rv.status_code, 400)
        eq_(
            json.loads(rv.data),
            {
                'error': {
                    'name': 'foo-invalid',
                    'description': 'Parameter `foo` has bad format',
                    'request_id': REQUEST_ID1,
                },
            },
        )


class TestGetTimestamp(TestApiAppCase):
    @raises(ValueError)
    def test_invalid_value(self):
        with self.app.test_request_context(method='POST', data={'foo': 'foo'}):
            get_timestamp('foo')


class TestQLimits(unittest.TestCase):
    def test_qlimits(self):
        qlimits = QLimits()
        qlimits['key'] = 'value'

        ok_('profiles' not in qlimits)
        eq_(qlimits['missing'], 100)
        eq_(qlimits.get('missing'), 100)

        ok_('key' in qlimits)
        eq_(qlimits['key'], 'value')
        eq_(qlimits.get('key'), 'value')
