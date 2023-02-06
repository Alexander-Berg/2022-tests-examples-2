# -*- coding: utf-8 -*-

from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.frodo import Frodo
from passport.backend.core.builders.frodo.faker import (
    EmptyFrodoParams,
    FakeFrodo,
    frodo_check_response,
)
from passport.backend.core.test.test_utils import with_settings
from six import iteritems


@with_settings(FRODO_URL='http://localhost/')
class FakeFrodoTestCase(TestCase):
    def setUp(self):
        self.fake_frodo = FakeFrodo()
        self.fake_frodo.start()

    def tearDown(self):
        self.fake_frodo.stop()
        del self.fake_frodo

    def test_set_response_value(self):
        ok_(not self.fake_frodo._mock.request.called)
        self.fake_frodo.set_response_value(u'confirm', u'')
        eq_(Frodo().confirm({'u1': 85, 'u2': 75}), True)
        ok_(self.fake_frodo._mock.request.called)

    def test_set_response_side_effect(self):
        ok_(not self.fake_frodo._mock.request.called)
        self.fake_frodo.set_response_side_effect(u'confirm', ValueError)
        with assert_raises(ValueError):
            Frodo().confirm({'u1': 85, 'u2': 75})
        ok_(self.fake_frodo._mock.request.called)

    def test_getattr(self):
        eq_(self.fake_frodo._mock.foo, self.fake_frodo.foo)


@with_settings(FRODO_URL='http://localhost/')
class EmptyFrodoParamsTestCase(TestCase):
    filled_fields = [
        'so_codes',
        'captchareq',
        'step1time', 'step2time',
        'utime', 'time',
        'hinta', 'hintaex', 'hintq', 'hintqex',
        'v2_account_timezone',
        'lang', 'v2_account_language',
        'xcountry', 'v2_account_country',
        'v2_has_cookie_l',
        'v2_has_cookie_my',
        'v2_has_cookie_yandex_login',
        'v2_has_cookie_yp',
        'v2_has_cookie_ys',
        'valkey',
        'v2_phone_bindings_count',
    ]
    fields_count = 101

    def test_all_empty(self):
        empty_frodo_params = EmptyFrodoParams()
        eq_(len(empty_frodo_params.keys()), self.fields_count)
        for key, item in iteritems(empty_frodo_params):
            if key not in self.filled_fields:
                eq_(item, '')

    def test_init_field(self):
        empty_frodo_params = EmptyFrodoParams(key='value')
        eq_(len(empty_frodo_params.keys()), self.fields_count + 1)
        for key, value in iteritems(empty_frodo_params):
            if key == 'key':
                eq_(value, 'value')
            elif key not in self.filled_fields:
                eq_(value, '')


class TestFrodoCheckResponse(TestCase):
    def test_default(self):
        eq_(frodo_check_response(), '<spamlist></spamlist>')
