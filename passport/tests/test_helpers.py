# -*- coding: utf-8 -*-
from copy import deepcopy
import json
from unittest import TestCase

import mock
from nose.tools import eq_
from passport.backend.core.logging_utils.helpers import (
    encode_header,
    mask_sensitive_fields,
    trim_message,
)


class TestEncodeHeader(TestCase):
    def test_error(self):
        smart_text_mock = mock.Mock()
        smart_text_mock.side_effect = UnicodeDecodeError('utf8', b'', 0, 0, '')
        with mock.patch('passport.backend.utils.string.smart_text', smart_text_mock):
            eq_(
                encode_header('name', 'value'),
                'Unable to encode header: \'utf8\' codec can\'t decode bytes in position 0--1: ',
            )


class TestTrimMessage(TestCase):
    def test_trim_message_short(self):
        eq_(trim_message('foo\nbar'), 'foo\\nbar')

    def test_trim_message_long(self):
        actual = 'foo\nbar' * 200
        expected = '%s ... (%d total symbols)' % (actual[:512].replace('\n', '\\n'), len(actual))
        eq_(trim_message(actual), expected)


class TestLogs(TestCase):
    MASK = '*****'

    def test_not_a_dict(self):
        data = '<?xml version="1.0" encoding="utf-8"?><error code="500">Server error</error>'
        masked = mask_sensitive_fields(data)
        eq_(masked, data)

    def test_empty(self):
        data = {}
        masked = mask_sensitive_fields(data)
        eq_(masked, {})

    def test_default_fields(self):
        data = {
            'passwd': 'password',
            'passwd2': 'password2',
            'password': 'password',
            'sessionid': 'session-id',
            'client_secret': 'client_secret',
            'not_senstitive': 'value',
            'totp': 'totp',
        }
        masked = mask_sensitive_fields(data)
        eq_(
            masked,
            {
                'passwd': self.MASK,
                'passwd2': self.MASK,
                'password': self.MASK,
                'sessionid': self.MASK,
                'client_secret': self.MASK,
                'totp': self.MASK,
                'not_senstitive': 'value',
            },
        )

    def test_mask_is_case_insensitive(self):
        # Маскироваться должны поля без учета регистра,
        # даже если под фильтр попадают 2 и более полей
        data = {
            'sslSession': {
                'value': 'session',
                'Value': 'session',
                'VALUE': 'session',
                'data': 'data',
            },
            'oAuth_client_secret': 'aaa',
            'codE': 'aaa',
            'CODE': 'supersecretcode',
        }
        original_data = deepcopy(data)

        masked = mask_sensitive_fields(
            data,
            [
                'sslsession.value',
                'oauth_client_secret',
                'code',
            ],
        )
        eq_(
            masked,
            {
                'sslSession': {
                    'value': self.MASK,
                    'Value': self.MASK,
                    'VALUE': self.MASK,
                    'data': 'data',
                },
                'oAuth_client_secret': self.MASK,
                'codE': self.MASK,
                'CODE': self.MASK,
            },
        )

        # Оригинальные данные не изменились после вызова
        eq_(data, original_data)

    def test_mask_sessionid(self):
        sessionid = '|'.join(
            [
                '3:1527501084.5.0.1516175546025:_iRXE8MLBF0MBAAAuAYCKg:39.1',
                '1120000000001516.0.2',
                'lrandoms.random_n.signature',
            ],
        )
        masked_sessionid = '|'.join(
            [
                '3:1527501084.5.0.1516175546025:_iRXE8MLBF0MBAAAuAYCKg:39.1',
                '1120000000001516.0.2',
                'lrandoms.random_n.' + self.MASK,
            ],
        )
        data = {
            'sessionid': sessionid,
            'sslsessionid': sessionid,
        }
        masked = mask_sensitive_fields(data)
        eq_(
            masked,
            {
                'sessionid': masked_sessionid,
                'sslsessionid': masked_sessionid,
            },
        )

    def test_mask_sessguard(self):
        sessguard = '1.1567684262.1567684262896:CAgICA:7f..1:318216.1000:4192.4RGabH7s.JZBG_yVFXXi0KyJAhef_NOn4JHc'
        masked_sessguard = '1.1567684262.1567684262896:CAgICA:7f..1:318216.1000:4192.4RGabH7s.%s' % self.MASK
        eq_(
            mask_sensitive_fields({'sessguard': sessguard}),
            {
                'sessguard': masked_sessguard,
            },
        )

    def test_mask_service_guard_container(self):
        service_guard_container = '1.zLeEcUEF/4l7ng728NRv/AmJqdg2kTqkLqxhcgQMDAI=.JZBG_yVFXXi0KyJAhef_NOn4JHc'
        masked_service_guard_container = '1.zLeEcUEF/4l7ng728NRv/AmJqdg2kTqkLqxhcgQMDAI=.%s' % self.MASK
        eq_(
            mask_sensitive_fields({'service_guard_container': service_guard_container}),
            {
                'service_guard_container': masked_service_guard_container,
            },
        )

    def test_mask_oauth(self):
        token = 'AQAAAACy1C6ZAAAM8vUoTJzWrULOgXiy_AYj5x0'
        masked_token = 'AQAAAACy1C6ZAAAM8vUo*******************'
        data = {
            'oauth_token': token,
            'access_token': token,
            'x_token': token,
            'token': token,
        }
        masked = mask_sensitive_fields(data)
        eq_(
            masked,
            {
                'oauth_token': masked_token,
                'access_token': masked_token,
                'x_token': masked_token,
                'token': masked_token,
            },
        )

    def test_mask_tvm_tickets(self):
        data = {
            'X-Ya-Service-Ticket': '3:serv:public:SECRET',
            'X-Ya-User-Ticket': '3:user:public:SECRET',
        }
        masked = mask_sensitive_fields(data)
        eq_(
            masked,
            {
                'X-Ya-Service-Ticket': '3:serv:public:',
                'X-Ya-User-Ticket': '3:user:public:',
            },
        )

    def test_basic(self):
        data = {
            'passwd': 'password',
            'passwd2': 'password2',
            'password': 'password',
            'sessionid': 'session-id',
            'client_secret': 'client_secret',
            'oauth': {
                'access_token': 'access_token',
            },
            'session': {
                'value': 'session',
                'data': 'data',
            },
            'sslsession': {
                'value': 'session',
                'data': 'data',
            },
            'cookies': ['name=value'],
            'not_senstitive': 'value',
            'signed_value': 'crypt.sign',
            'oauth_client_secret': 'aaa',
            'code': 'aaa',
            'authorization_code': 'aaa',
            'support_code': 'aaa',
        }
        original_data = deepcopy(data)

        masked = mask_sensitive_fields(
            data,
            [
                'passwd',
                'passwd2',
                'password',
                'sessionid',
                'client_secret',
                'oauth.access_token',
                'session.value',
                'sslsession.value',
                'cookies',
                'signed_value',
                'oauth_client_secret',
                'code',
                'authorization_code',
                'support_code',
            ],
        )
        eq_(
            masked,
            {
                'passwd': self.MASK,
                'passwd2': self.MASK,
                'password': self.MASK,
                'sessionid': self.MASK,
                'client_secret': self.MASK,
                'oauth': {
                    'access_token': self.MASK,
                },
                'session': {
                    'value': self.MASK,
                    'data': 'data',
                },
                'sslsession': {
                    'value': self.MASK,
                    'data': 'data',
                },
                'cookies': ['name=' + self.MASK],
                'not_senstitive': 'value',
                'signed_value': 'crypt.*****',
                'oauth_client_secret': self.MASK,
                'code': self.MASK,
                'authorization_code': self.MASK,
                'support_code': self.MASK,
            },
        )

        # Оригинальные данные не изменились после вызова
        eq_(data, original_data)

    def test_replace_non_leaf(self):
        data = {
            'sessionid': {
                'data': 'value',
            },
            'field': {
                'subfield': 'value',
            },
        }
        masked = mask_sensitive_fields(data, ['sessionid', 'field.subfield.foo'])
        eq_(masked, dict(data, sessionid=self.MASK))

    def test_lists(self):
        data = {
            u'fruits': [
                {u'name': u'apple', u'color': u'red'},
                {u'name': u'grape', u'color': u'green'},
            ],
        }
        original_data = deepcopy(data)

        masked = mask_sensitive_fields(data, [u'fruits[].color'])
        eq_(
            masked,
            {
                u'fruits': [
                    {u'name': u'apple', u'color': self.MASK},
                    {u'name': u'grape', u'color': self.MASK},
                ],
            },
        )

        # Оригинальные данные не изменились после вызова
        eq_(data, original_data)

        eq_(
            mask_sensitive_fields(data, [u'fruits']),
            {u'fruits': self.MASK},
        )

    def test_nested_lists(self):
        nested_data = {
            'a': [
                {'b': [{'c1': '1'}, {'c2': '2'}]},
                {'b': [{'c1': '3'}, {'c2': '4'}]},
            ],
        }

        eq_(
            mask_sensitive_fields(nested_data, ['a[].b[].c1']),
            {
                'a': [
                    {'b': [{'c1': self.MASK}, {'c2': '2'}]},
                    {'b': [{'c1': self.MASK}, {'c2': '4'}]},
                ],
            },
        )

        eq_(
            mask_sensitive_fields(
                nested_data,
                ['a[].b[].c1', 'a[].b[].c2'],
            ),
            {
                'a': [
                    {'b': [{'c1': self.MASK}, {'c2': self.MASK}]},
                    {'b': [{'c1': self.MASK}, {'c2': self.MASK}]},
                ],
            },
        )

    def test_empty_path(self):
        data = {
            u'fruits': [
                {u'name': u'apple', u'color': u'red'},
                {u'name': u'grape', u'color': u'green'},
            ],
        }

        masked = mask_sensitive_fields(data, [''])
        eq_(data, masked)

    def test_invalid_data(self):
        eq_(
            mask_sensitive_fields({u'b': u'a'}, ['a[].b']),
            {u'b': u'a'},
        )

    def test_json_data_sensitive_fields(self):
        orig_json_data = {
            'passwords': 'xyz',
            'question_answer': {
                'question': 'q',
                'answer': 'a',
                'question_id': 10,
            },
            'phone_numbers': [
                '+79123456789',
                '89123456780',
                '+1912345678111',
            ],
            'contact_reason': 'contact reason',
        }
        masked_data = mask_sensitive_fields(dict(json_data=json.dumps(orig_json_data)))
        eq_(
            masked_data,
            {
                'json_data': {
                    'passwords': self.MASK,
                    'question_answer': {
                        'question': 'q',
                        'answer': self.MASK,
                        'question_id': 10,
                    },
                    'contact_reason': 'contact reason',
                    'phone_numbers': self.MASK,
                },
            },
        )

    def test_invalid_json_data(self):
        eq_(
            mask_sensitive_fields(dict(json_data='{"a":{}')),
            dict(json_data='{"a":{}'),
        )

    def test_signed_value_mask_all(self):
        eq_(
            mask_sensitive_fields(data={'signed_value': 'sign'}),
            dict(signed_value='*****'),
        )

    def test_mask_cookies(self):
        assert mask_sensitive_fields(
            {
                'cookies': [
                    'x=a',
                    'x=a ',
                    'x=a,',
                    'x=a;',
                    'xy=a==b;',
                    'x=a; Domain=.yandex.ru; Expires=Tue, 10 Jan 2000 12:34:56 GMT; Path=/',
                ],
            }
        ) == {
            'cookies': [
                'x=*****',
                'x=***** ',
                'x=*****,',
                'x=*****;',
                'xy=*****;',
                'x=*****; Domain=.yandex.ru; Expires=Tue, 10 Jan 2000 12:34:56 GMT; Path=/',
            ],
        }

        assert mask_sensitive_fields({'cookies': 'hello'}) == {'cookies': '*****'}
