# -*- coding: utf-8 -*-
from datetime import datetime
from unittest import TestCase

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.logging_utils.loggers.tskv import (
    BaseLogEntry,
    JsonLogEntry,
    TskvLogEntry,
)
import six


class TestBaseLogEntry(TestCase):
    def test_escape(self):
        test_map = [
            ('foo\tbar', u'foo\\tbar'),
            ('foo\nbar', u'foo\\nbar'),
            ('foo\rbar', u'foo\\rbar'),
            ('foo\0bar', u'foo\\0bar'),
            ('foo\\bar', u'foo\\\\bar'),
            (123, u'123'),
            (u'фуу', u'фуу'),
        ]
        for actual, expected in test_map:
            eq_(BaseLogEntry.escape_value(actual), expected)

    def test_eq(self):
        expected_statbox = BaseLogEntry()
        expected_statbox.params = {'a': 1, 'b': 1}
        eq_(BaseLogEntry(**{'a': 1, 'b': 1}), expected_statbox)

    def test_not_eq(self):
        ok_(BaseLogEntry(**{'a': 1, 'b': 1}) != BaseLogEntry())
        ok_(BaseLogEntry(**{'a': 1, 'b': 1}) != 10)


class TestTskvLogEntry(TestCase):
    def test_format(self):
        test_map = [
            ({'foo': 'bar'}, u'tskv\tfoo=bar'),
            ({'foo': 'bar', 'foo2': 'bar2'}, u'tskv\tfoo=bar\tfoo2=bar2'),
            ({'foo': '', 'bar': 'bar'}, u'tskv\tbar=bar\tfoo='),
            ({}, u'tskv'),
            ({'foo': None}, u'tskv'),
        ]
        for actual, expected in test_map:
            eq_(six.text_type(TskvLogEntry(**actual)), expected)
            if six.PY2:
                eq_(six.binary_type(TskvLogEntry(**actual)), expected.encode('utf-8'))

    def test_unicode_key_and_value(self):
        eq_(six.text_type(TskvLogEntry(**{u'foo': u'йцук'})), u'tskv\tfoo=йцук')
        if six.PY2:
            eq_(six.binary_type(TskvLogEntry(**{u'foo': u'йцук'})), u'tskv\tfoo=йцук'.encode('utf-8'))

    def test_str_key_and_unicode_value(self):
        eq_(six.text_type(TskvLogEntry(**{'foo': u'йцук'})), u'tskv\tfoo=йцук')
        if six.PY2:
            eq_(six.binary_type(TskvLogEntry(**{'foo': u'йцук'})), u'tskv\tfoo=йцук'.encode('utf-8'))

    def test_unicode_key_and_str_value(self):
        eq_(six.text_type(TskvLogEntry(**{u'foo': 'йцук'})), u'tskv\tfoo=йцук')
        if six.PY2:
            eq_(six.binary_type(TskvLogEntry(**{u'foo': 'йцук'})), u'tskv\tfoo=йцук'.encode('utf-8'))

    def test_str_key_and_value(self):
        eq_(six.text_type(TskvLogEntry(**{'foo': 'йцук'})), u'tskv\tfoo=йцук')
        if six.PY2:
            eq_(six.binary_type(TskvLogEntry(**{'foo': 'йцук'})), u'tskv\tfoo=йцук'.encode('utf-8'))

    def test_not_utf_8_str_value(self):
        eq_(six.text_type(TskvLogEntry(**{'foo': b'\xe9\x98\x00'})), u'tskv\tfoo=\ufffd\\0')
        if six.PY2:
            eq_(six.binary_type(TskvLogEntry(**{'foo': b'\xe9\x98\x00'})), u'tskv\tfoo=\ufffd\\0'.encode('utf-8'))

    def test_datetime_value(self):
        now = datetime.now()
        eq_(
            six.text_type(TskvLogEntry(**{'my_datetime': now})),
            u'tskv\tmy_datetime=%s' % now.strftime('%Y-%m-%d %H:%M:%S'),
        )

    def test_truncate_str_value(self):
        eq_(six.text_type(TskvLogEntry(**{'foo': 'a' * 1001})), u'tskv\tfoo=%s' % ('a' * 1000))
        if six.PY2:
            eq_(six.binary_type(TskvLogEntry(**{'foo': 'a' * 1001})), six.binary_type('tskv\tfoo=%s' % ('a' * 1000)))


class TestJsonLogEntry(TestCase):
    def test_format(self):
        test_map = [
            ({'foo': 'bar'}, u'{"foo": "bar"}'),
            ({'foo': 'bar', 'foo2': 'bar2'}, u'{"foo": "bar", "foo2": "bar2"}'),
            ({'foo': ''}, u'{"foo": ""}'),
            ({}, u'{}'),
            ({'foo': None}, u'{}'),
        ]
        for actual, expected in test_map:
            eq_(six.text_type(JsonLogEntry(**actual)), expected)
            if six.PY2:
                eq_(six.binary_type(JsonLogEntry(**actual)), expected.encode('utf-8'))

    def test_unicode_key_and_value(self):
        eq_(six.text_type(JsonLogEntry(**{u'foo': u'йцук'})), u'{"foo": "йцук"}')
        if six.PY2:
            eq_(six.binary_type(JsonLogEntry(**{u'foo': u'йцук'})), u'{"foo": "йцук"}'.encode('utf-8'))

    def test_str_key_and_unicode_value(self):
        eq_(six.text_type(JsonLogEntry(**{'foo': u'йцук'})), u'{"foo": "йцук"}')
        if six.PY2:
            eq_(six.binary_type(JsonLogEntry(**{'foo': u'йцук'})), u'{"foo": "йцук"}'.encode('utf-8'))

    def test_unicode_key_and_str_value(self):
        eq_(six.text_type(JsonLogEntry(**{u'foo': 'йцук'})), u'{"foo": "йцук"}')
        if six.PY2:
            eq_(six.binary_type(JsonLogEntry(**{u'foo': 'йцук'})), u'{"foo": "йцук"}'.encode('utf-8'))

    def test_str_key_and_value(self):
        eq_(six.text_type(JsonLogEntry(**{'foo': 'йцук'})), u'{"foo": "йцук"}')
        if six.PY2:
            eq_(six.binary_type(JsonLogEntry(**{'foo': 'йцук'})), u'{"foo": "йцук"}'.encode('utf-8'))

    def test_not_utf_8_str_value(self):
        eq_(six.text_type(JsonLogEntry(**{'foo': b'\xe9\x98\x00'})), u'{"foo": "\ufffd\\u0000"}')
        if six.PY2:
            eq_(six.binary_type(JsonLogEntry(**{'foo': b'\xe9\x98\x00'})), u'{"foo": "\ufffd\\u0000"}'.encode('utf-8'))

    def test_datetime_value(self):
        now = datetime.now()
        eq_(
            six.text_type(JsonLogEntry(**{'my_datetime': now})),
            u'{"my_datetime": "%s"}' % now.strftime('%Y-%m-%d %H:%M:%S'),
        )

    def test_truncate_str_value(self):
        eq_(six.text_type(JsonLogEntry(**{'foo': 'a' * 1001})), u'{"foo": "%s"}' % ('a' * 1000))
        if six.PY2:
            eq_(six.binary_type(JsonLogEntry(**{'foo': 'a' * 1001})), six.binary_type('{"foo": "%s"}' % ('a' * 1000)))

    def test_bool_value(self):
        eq_(six.text_type(JsonLogEntry(**{u'foo': True})), u'{"foo": true}')
        if six.PY2:
            eq_(six.binary_type(JsonLogEntry(**{u'foo': True})), u'{"foo": true}'.encode('utf-8'))
