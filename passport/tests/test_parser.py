# -*- coding: utf-8 -*-
import unittest

from passport.backend.core.crypto.faker import FakeKeyStorage
from passport.backend.core.historydb.crypto import encrypt
from passport.backend.library.historydbloader.historydb.exceptions import BadLogLineError
from passport.backend.library.historydbloader.historydb.parser import (
    AuthChallengeEntryParser,
    AuthEntryParser,
    CSVEntryParser,
    EventEntryParser,
    JSONEntryParser,
    LoyaltyEntryParser,
    MailUserJournalEntryParser,
    OAuthEntryParser,
    RestoreEntryParser,
    TSKVEntryParser,
    YasmsPrivateEntryParser,
)
import six
from six import StringIO


class BaseTestClass(unittest.TestCase):
    def setUp(self):
        self.fake_key_storage = FakeKeyStorage(1, b'1' * 24)
        self.fake_key_storage.start()

    def tearDown(self):
        self.fake_key_storage.stop()
        del self.fake_key_storage


class TestCSVEntryParser(BaseTestClass):
    def setUp(self):
        super(TestCSVEntryParser, self).setUp()
        self.parser = CSVEntryParser()
        self.parser.FIELDS = ['a', 'b', 'c']
        self.parser.FIELDS_PROCESSORS = {
            'a': lambda value: value.upper() if value else None,
            'b': lambda value: None if value == 'bad_b_value' else value,
        }
        self.parser.FIELDS_NAMES_MAPPER = {
            'c': 'ccc',
        }
        self.parser.REQUIRED_FIELDS = ['b']

    def test_process_line(self):
        entry = self.parser.process_line(['a_value', 'b_value', 'c_value'])
        self.assertEqual(
            entry,
            {
                'a': 'A_VALUE',
                'b': 'b_value',
                'ccc': 'c_value',
            },
        )

    def test_process_line_ignore_none(self):
        entry = self.parser.process_line(['', 'b_value', 'c_value'])
        self.assertEqual(
            entry,
            {
                'b': 'b_value',
                'ccc': 'c_value',
            },
        )

    def test_process_line_missing_required_fields(self):
        with self.assertRaises(BadLogLineError):
            self.parser.process_line(['a_value', 'bad_b_value', 'c_value'])

    def test_parse(self):
        fileobj = StringIO('a_value b_value c_value\naa_value bb_value cc_value')
        self.assertEqual(
            list(self.parser.parse(fileobj)),
            [
                {'a': 'A_VALUE', 'b': 'b_value', 'ccc': 'c_value'},
                {'a': 'AA_VALUE', 'b': 'bb_value', 'ccc': 'cc_value'},
            ],
        )

    def test_parse_ignore_bad_csv_line(self):
        fileobj = StringIO('a_value b_value c_value\na_value b_value c_\0value\naa_value bb_value cc_value')
        self.assertEqual(
            list(self.parser.parse(fileobj)),
            [
                {'a': 'A_VALUE', 'b': 'b_value', 'ccc': 'c_value'},
                {'a': 'AA_VALUE', 'b': 'bb_value', 'ccc': 'cc_value'},
            ],
        )

    def test_parse_disable_ignore_bad_csv_line(self):
        with self.assertRaises(BadLogLineError):
            fileobj = StringIO('a_value b_bad_value c_value\na_value b_value c_\0value\naa_value bb_value cc_value')
            list(self.parser.parse(fileobj, ignore_errors=False)),

    def test_parse_ignore_bad_line_content(self):
        fileobj = StringIO('a_value bad_b_value c_value\na_value b_value c_value')
        self.assertEqual(
            list(self.parser.parse(fileobj)),
            [
                {'a': 'A_VALUE', 'b': 'b_value', 'ccc': 'c_value'},
            ],
        )

    def test_parse_disable_ignore_bad_line_content(self):
        with self.assertRaises(BadLogLineError):
            fileobj = StringIO('a_value bad_b_value c_value\na_value b_value c_value')
            self.assertEqual(
                list(self.parser.parse(fileobj, ignore_errors=False)),
                [
                    {'a': 'A_VALUE', 'b': 'b_value', 'ccc': 'c_value'},
                ],
            )

    def test_parse_bad_values_count(self):
        with self.assertRaises(BadLogLineError):
            fileobj = StringIO('a_value bad_b_value c_value d_value\na_value b_value c_value')
            self.assertEqual(
                list(self.parser.parse(fileobj, ignore_errors=False)),
                [
                    {'a': 'A_VALUE', 'b': 'b_value', 'ccc': 'c_value'},
                ],
            )


class TestAuthEntryParser(BaseTestClass):
    parser = AuthEntryParser()

    def test_parse(self):
        fileobj = StringIO(
            '1 1970-01-01T05:01:30.000000+04 95 bb 55555554 login@ya.ru 2 imap successful '
            'whitelisted 99.88.77.66 3.2.1.1 - - - -\n'
            '1 1970-01-01T01:01:35.000001+00 43 passport 55555554 login - web '
            'ses_create is_secure=1;captcha_passed=1;ttl=5 11.222.1.22 - '
            '70779056991379999840 https://passport.yandex.com/passport?mode=simplereg&from=mail ya.ru '
            '`Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:23.0) Gecko/20100101 Firefox/23.0`',
        )
        self.assertEqual(
            list(self.parser.parse(fileobj)),
            [
                {
                    'version': 1,
                    'timestamp': 3690.0,
                    'host_id': int('95', 16),
                    'client_name': 'bb',
                    'uid': 55555554,
                    'login': 'login@ya.ru',
                    'sid': 2,
                    'type': 'imap',
                    'status': 'successful',
                    'comment': 'whitelisted',
                    'user_ip': '99.88.77.66',
                    'proxy_ip': '3.2.1.1',
                },
                {
                    'version': 1,
                    'timestamp': 3695.000001,
                    'host_id': 67,
                    'client_name': 'passport',
                    'uid': 55555554,
                    'login': 'login',
                    'type': 'web',
                    'status': 'ses_create',
                    'comment': 'is_secure=1;captcha_passed=1;ttl=5',
                    'user_ip': '11.222.1.22',
                    'yandexuid': '70779056991379999840',
                    'referer': 'https://passport.yandex.com/passport?mode=simplereg&from=mail',
                    'retpath': 'ya.ru',
                    'useragent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:23.0) Gecko/20100101 Firefox/23.0',
                },
            ],
        )

    def test_required_fields(self):
        fileobjs = [
            # rfctime
            StringIO('1 - 95 bb 55555554 login@ya.ru 2 imap successful whitelisted 99.88.77.66 - - - - -'),
            # host_id
            StringIO(
                '1 1970-01-01T05:01:30.000000+04 - bb 55555554 login@ya.ru 2 imap '
                'successful whitelisted 99.88.77.66 - - - - -\n',
            ),
            # status
            StringIO(
                '1 1970-01-01T05:01:30.000000+04 95 bb 55555554 login@ya.ru 2 '
                'imap - whitelisted 99.88.77.66 - - - - -\n',
            ),
        ]
        for fileobj in fileobjs:
            with self.assertRaises(BadLogLineError):
                list(self.parser.parse(fileobj, ignore_errors=False))

        fileobj = StringIO('''- 1970-01-01T05:01:30.000000+04 95 - - - - - successful - - - - - - -\n''')
        self.assertEqual(
            list(self.parser.parse(fileobj, ignore_errors=False)),
            [
                {
                    'status': 'successful',
                    'timestamp': 3690.0,
                    'host_id': 149,
                },
            ],
        )


class TestEventEntryParser(BaseTestClass):
    parser = EventEntryParser()

    def test_parse(self):
        fileobj = StringIO(
            '1 1970-01-01T05:01:27.697373+04 43 passport 123456789 info.hinta '
            'Ответ 211.212.213.214 33.33.44.55 123142415 avmm OK\n'
            '2 1970-01-01T05:02:37.645978+04 43 passport 987654321 '
            'sid.add 2 111.112.113.114 33.33.44.55 10080006331300000 dyor Тест'
        )

        self.assertEqual(
            list(self.parser.parse(fileobj)),
            [
                {
                    'version': 1,
                    'timestamp': 3687.697373,
                    'host_id': 67,
                    'client_name': 'passport',
                    'uid': 123456789,
                    'name': 'info.hinta',
                    'value': 'Ответ',
                    'user_ip': '211.212.213.214',
                    'proxy_ip': '33.33.44.55',
                    'yandexuid': '123142415',
                    'admin': 'avmm',
                    'comment': 'OK',
                },
                {
                    'uid': 987654321,
                    'timestamp': 3757.645978,
                    'client_name': 'passport',
                    'value': '2',
                    'user_ip': '111.112.113.114',
                    'proxy_ip': '33.33.44.55',
                    'version': 2,
                    'host_id': 67,
                    'yandexuid': '10080006331300000',
                    'name': 'sid.add',
                    'admin': 'dyor',
                    'comment': 'Тест',
                },
            ],
        )

    def test_parse_encrypted_values(self):
        encrypted_value = encrypt(u'значение')
        if six.PY3:
            encrypted_value = encrypted_value.decode()
        fileobj = StringIO(
            '2 1970-01-01T05:02:37.645978+04 7F passport 11807491 info.password %s 1.2.3.4 - - - -\n' % encrypted_value +
            '2 1970-01-01T05:02:37.645978+04 7F passport 11807491 info.hinta %s 1.2.3.4 - - - -\n' % encrypted_value +
            '2 1970-01-01T05:02:37.645978+04 7F passport 11807491 info.hintq question 1.2.3.4 - - - -\n' +
            '2 1970-01-01T05:02:38.645978+04 7F passport 11807491 info.password - 1.2.3.4 - - - -\n'
        )

        self.assertEqual(
            list(self.parser.parse(fileobj)),
            [
                {
                    'uid': 11807491,
                    'timestamp': 3757.645978,
                    'client_name': 'passport',
                    'value': u'значение'.encode('utf-8'),
                    'user_ip': '1.2.3.4',
                    'version': 2,
                    'host_id': 127,
                    'name': 'info.password',
                },
                {
                    'uid': 11807491,
                    'timestamp': 3757.645978,
                    'client_name': 'passport',
                    'value': u'значение'.encode('utf-8'),
                    'user_ip': '1.2.3.4',
                    'version': 2,
                    'host_id': 127,
                    'name': 'info.hinta',
                },
                {
                    'uid': 11807491,
                    'timestamp': 3757.645978,
                    'client_name': 'passport',
                    'value': 'question',
                    'user_ip': '1.2.3.4',
                    'version': 2,
                    'host_id': 127,
                    'name': 'info.hintq',
                },
                {
                    'uid': 11807491,
                    'timestamp': 3758.645978,
                    'client_name': 'passport',
                    'user_ip': '1.2.3.4',
                    'version': 2,
                    'host_id': 127,
                    'name': 'info.password',
                },
            ],
        )

    def test_required_fields(self):
        fileobjs = [
            StringIO('1 - 43 passport 123456789 info.hinta Ответ '
                     '211.212.213.214 33.33.44.55 123142415 avmm OK\n'),
            StringIO('1 1970-01-01T05:01:27.697373+04 43 passport - '
                     'info.hinta Ответ 211.212.213.214 33.33.44.55 123142415 avmm OK\n'),
            StringIO('1 1970-01-01T05:01:27.697373+04 43 passport '
                     '123456789 - Ответ 211.212.213.214 33.33.44.55 123142415 avmm OK\n'),
        ]
        for fileobj in fileobjs:
            with self.assertRaises(BadLogLineError):
                list(self.parser.parse(fileobj, ignore_errors=False))

        fileobj = StringIO('- 1970-01-01T05:01:27.697373+04 null - 123456789 info.hinta - - - - - -\n')
        self.assertEqual(
            list(self.parser.parse(fileobj, ignore_errors=False)),
            [
                {
                    'timestamp': 3687.697373,
                    'uid': 123456789,
                    'name': 'info.hinta',
                },
            ],
        )


class TestLoyaltyEntryParser(BaseTestClass):
    parser = LoyaltyEntryParser()

    def test_parse(self):
        fileobj = StringIO('''1 3600.55 email arhibot@yandex-team.ru 127.0.0.1 maps report `{"foo": "bar"}`\n'''
                           '''1 3600.66 uid 123 127.0.0.1 maps `report problem` `{"foo": "bar"}`\n''')
        self.assertEqual(
            list(self.parser.parse(fileobj)),
            [
                {
                    'version': 1,
                    'timestamp': 3600.55,
                    'user_id_type': 'email',
                    'user_id': 'arhibot@yandex-team.ru',
                    'user_ip': '127.0.0.1',
                    'domain': 'maps',
                    'name': 'report',
                    'meta': {'foo': 'bar'},
                },
                {
                    'version': 1,
                    'timestamp': 3600.66,
                    'user_id_type': 'uid',
                    'user_id': '123',
                    'user_ip': '127.0.0.1',
                    'domain': 'maps',
                    'name': 'report problem',
                    'meta': {'foo': 'bar'},
                },
            ],
        )

    def test_required_fields(self):
        fileobjs = [
            # timestamp
            StringIO('''1 - email arhibot@yandex-team.ru 127.0.0.1 maps report `{"foo": "bar"}`'''),
            # user_id_type
            StringIO('''1 3600.55 - arhibot@yandex-team.ru 127.0.0.1 maps report `{"foo": "bar"}`'''),
            # user_id
            StringIO('''1 3600.55 email - 127.0.0.1 maps report `{"foo": "bar"}`'''),
            # user_ip
            StringIO('''1 3600.55 email arhibot@yandex-team.ru - maps report `{"foo": "bar"}`\n'''),
            # domain
            StringIO('''1 3600.55 email arhibot@yandex-team.ru 127.0.0.1 - report `{"foo": "bar"}`'''),
            # name
            StringIO('''1 3600.55 email arhibot@yandex-team.ru 127.0.0.1 maps - `{"foo": "bar"}`'''),
        ]
        for fileobj in fileobjs:
            with self.assertRaises(BadLogLineError):
                list(self.parser.parse(fileobj, ignore_errors=False))

        fileobj = StringIO('''- 3600.55 email arhibot@yandex-team.ru 127.0.0.1 maps report -''')
        self.assertEqual(
            list(self.parser.parse(fileobj, ignore_errors=False)),
            [
                {
                    'timestamp': 3600.55,
                    'user_id_type': 'email',
                    'user_id': 'arhibot@yandex-team.ru',
                    'user_ip': '127.0.0.1',
                    'domain': 'maps',
                    'name': 'report',
                },
            ],
        )


class TestRestoreEntryParser(BaseTestClass):
    parser = RestoreEntryParser()

    def test_parse_version_1(self):
        fileobj = StringIO('1 restore_semi_auto_request 2014-08-18T17:51:23.528194+04 3000453634 '
                           '7F,2709,1408369883.53,3000453634,ea50c89be1b74f7fea59100aee858d907f `{"social_accounts": '
                           '{"entered": ["http://vk.com/id123123123"], "factor_absence": 0, "profiles": [], '
                           '"api_status": true}}`')
        self.assertEqual(
            list(self.parser.parse(fileobj)),
            [
                {
                    'version': 1,
                    'action': 'restore_semi_auto_request',
                    'timestamp': 1408369883.528194,
                    'uid': 3000453634,
                    'restore_id': '7F,2709,1408369883.53,3000453634,ea50c89be1b74f7fea59100aee858d907f',
                    'data_json': {"social_accounts": {"entered": ["http://vk.com/id123123123"],
                                                      "factor_absence": 0, "profiles": [], "api_status": True}},
                },
            ],
        )

    def test_parse_version_1_cyrillic(self):
        fileobj = StringIO('1 restore_semi_auto_request 2014-08-18T17:51:23.528194+04 '
                           '3000453634 7F,2709,1408369883.53,3000453634,ea50c89be1b74f7fea59100aee858d907f '
                           '`{"a": "\\u043f\\u0440\\u0438\\u0432\\u0435\\u0442``"}`')
        self.assertEqual(
            list(self.parser.parse(fileobj)),
            [
                {
                    'version': 1,
                    'action': 'restore_semi_auto_request',
                    'uid': 3000453634,
                    'timestamp': 1408369883.528194,
                    'restore_id': '7F,2709,1408369883.53,3000453634,ea50c89be1b74f7fea59100aee858d907f',
                    'data_json': {'a': u'привет`'},
                },
            ],
        )

    def test_parse_version_2(self):
        encrypted_value = encrypt('{"a":"b"}')
        if six.PY3:
            encrypted_value = encrypted_value.decode()
        fileobj = StringIO(
            '2 restore_semi_auto_request 2014-08-18T17:51:23.528194+04 '
            '3000453634 7F,2709,1408369883.53,3000453634,ea50c89be1b74f7fea59100aee858d907f %s' % encrypted_value,
        )
        self.assertEqual(
            list(self.parser.parse(fileobj)),
            [
                {
                    'version': 2,
                    'action': 'restore_semi_auto_request',
                    'uid': 3000453634,
                    'timestamp': 1408369883.528194,
                    'restore_id': '7F,2709,1408369883.53,3000453634,ea50c89be1b74f7fea59100aee858d907f',
                    'data_json': {u'a': u'b'},
                },
            ],
        )

    def test_required_fields(self):
        '''1 action 12345 2014-08-18T17:51:23.528194+04 restore-id `{"foo": "bar"}`'''
        fileobjs = [
            # version
            StringIO('''- action 12345 2014-08-18T17:51:23.528194+04 restore-id `{"foo": "bar"}`'''),
            # action
            StringIO('''1 - 12345 2014-08-18T17:51:23.528194+04 restore-id `{"foo": "bar"}`'''),
            # uid
            StringIO('''1 action - 2014-08-18T17:51:23.528194+04 restore-id `{"foo": "bar"}`'''),
            # timestamp
            StringIO('''1 action 12345 - restore-id `{"foo": "bar"}`'''),
            # restore_id
            StringIO('''1 action 12345 2014-08-18T17:51:23.528194+04 - `{"foo": "bar"}`'''),
            # data_json
            StringIO('''1 action 12345 2014-08-18T17:51:23.528194+04 restore-id -'''),
        ]
        for fileobj in fileobjs:
            with self.assertRaises(BadLogLineError):
                list(self.parser.parse(fileobj, ignore_errors=False))


class TestAuthChallengeEntryParser(BaseTestClass):
    parser = AuthChallengeEntryParser()

    def test_parse(self):
        fileobj = StringIO('1 2014-08-18T17:51:23.528194+04 updated 82879256 531a61de-9a85-11e5-bd44-002590ed3092 '
                           'CAEQoJeGswUaBkFTNjY5NyCVASiXpAEwAzjXAUCcl4azBUoQUxph3pqFEeW9RAAlkO0wkg== '
                           '`{"ip": "178.124.31.4", "yandexuid": "768858301449233308", "user_agent_info": '
                           '{"OSFamily": "Windows", "BrowserEngine": "Gecko", "isBrowser": true, '
                           '"BrowserVersion": "31.0", "OSName": "Windows 8.1", "BrowserName": "Firefox", '
                           '"BrowserEngineVersion": "31.0", "x64": true, "OSVersion": "6.3"}}`')
        self.assertEqual(
            list(self.parser.parse(fileobj)),
            [
                {
                    'version': 1,
                    'timestamp': 1408369883.528194,
                    'action': 'updated',
                    'uid': 82879256,
                    'env_profile_id': '531a61de-9a85-11e5-bd44-002590ed3092',
                    'env_profile_pb2_base64':
                        'CAEQoJeGswUaBkFTNjY5NyCVASiXpAEwAzjXAUCcl4azBUoQUxph3pqFEeW9RAAlkO0wkg==',
                    'env_json': {
                        'ip': '178.124.31.4',
                        'yandexuid': '768858301449233308',
                        'user_agent_info': {
                            'OSFamily': 'Windows',
                            'BrowserEngine': 'Gecko',
                            'isBrowser': True,
                            'BrowserVersion': '31.0',
                            'OSName': 'Windows 8.1',
                            'BrowserName': 'Firefox',
                            'BrowserEngineVersion': '31.0',
                            'x64': True,
                            'OSVersion': '6.3',
                        },
                    },
                },
            ],
        )

    def test_required_fields(self):
        list(
            self.parser.parse(StringIO('1 2015-12-04T15:48:32.023639+03 updated '
                                       '82879256 531a61de-9a85-11e5-bd44-002590ed3092 base64 `{}`')),
        )
        fileobjs = [
            # version
            StringIO('- 2015-12-04T15:48:32.023639+03 updated 82879256 '
                     '531a61de-9a85-11e5-bd44-002590ed3092 base64 `{}`'),
            # timestamp
            StringIO('1 - updated 82879256 531a61de-9a85-11e5-bd44-002590ed3092 base64 `{}`'),
            # action
            StringIO('1 2015-12-04T15:48:32.023639+03 - 82879256 '
                     '531a61de-9a85-11e5-bd44-002590ed3092 base64 `{}`'),
            # uid
            StringIO('1 2015-12-04T15:48:32.023639+03 updated - 531a61de-9a85-11e5-bd44-002590ed3092 base64 `{}`'),
            # env_profile_id
            StringIO('1 2015-12-04T15:48:32.023639+03 updated 82879256 - base64 `{}`'),
            # env_json
            StringIO('1 2015-12-04T15:48:32.023639+03 updated '
                     '82879256 531a61de-9a85-11e5-bd44-002590ed3092 base64 -'),
        ]
        for fileobj in fileobjs:
            with self.assertRaises(BadLogLineError):
                list(self.parser.parse(fileobj, ignore_errors=False))

    def test_parse_with_comment(self):
        fileobj = StringIO('1 2014-08-18T17:51:23.528194+04 updated 82879256 '
                           '531a61de-9a85-11e5-bd44-002590ed3092 '
                           'CAEQoJeGswUaBkFTNjY5NyCVASiXpAEwAzjXAUCcl4azBUoQUxph3pqFEeW9RAAlkO0wkg== '
                           '`{"ip": "178.124.31.4", "yandexuid": "768858301449233308", "user_agent_info": '
                           '{"OSFamily": "Windows", "BrowserEngine": "Gecko", "isBrowser": true, '
                           '"BrowserVersion": "31.0", "OSName": "Windows 8.1", "BrowserName": '
                           '"Firefox", "BrowserEngineVersion": "31.0", "x64": true, "OSVersion": "6.3"}}` env=rc')
        self.assertEqual(
            list(self.parser.parse(fileobj)),
            [
                {
                    'version': 1,
                    'timestamp': 1408369883.528194,
                    'action': 'updated',
                    'uid': 82879256,
                    'env_profile_id': '531a61de-9a85-11e5-bd44-002590ed3092',
                    'env_profile_pb2_base64':
                        'CAEQoJeGswUaBkFTNjY5NyCVASiXpAEwAzjXAUCcl4azBUoQUxph3pqFEeW9RAAlkO0wkg==',
                    'env_json': {
                        'ip': '178.124.31.4',
                        'yandexuid': '768858301449233308',
                        'user_agent_info': {
                            'OSFamily': 'Windows',
                            'BrowserEngine': 'Gecko',
                            'isBrowser': True,
                            'BrowserVersion': '31.0',
                            'OSName': 'Windows 8.1',
                            'BrowserName': 'Firefox',
                            'BrowserEngineVersion': '31.0',
                            'x64': True,
                            'OSVersion': '6.3',
                        },
                    },
                    'comment': 'env=rc',
                },
            ],
        )


class TestTSKVParser(BaseTestClass):
    def setUp(self):
        super(TestTSKVParser, self).setUp()
        self.parser = TSKVEntryParser()
        self.parser.FIELDS = ['a', 'b', 'c']
        self.parser.FIELDS_PROCESSORS = {
            'a': lambda value: value.upper() if value else None,
            'b': lambda value: None if value == 'bad_b_value' else value,
        }
        self.parser.FIELDS_NAMES_MAPPER = {
            'c': 'ccc',
        }
        self.parser.REQUIRED_FIELDS = ['b']

    def test_process_line_valid(self):
        line = "a=a_value\tb=b_value\tc=c_value"
        entry = self.parser.process_line(line)
        self.assertEqual(
            entry,
            {
                'a': 'A_VALUE',
                'b': 'b_value',
                'ccc': 'c_value',
            }
        )

    def test_process_line_russian_symbols_valid(self):
        line = "a=a_value\tb=значение Б\tc=c_value"
        entry = self.parser.process_line(line)
        self.assertEqual(
            entry,
            {
                'a': 'A_VALUE',
                'b': 'значение Б',
                'ccc': 'c_value',
            }
        )

    def test_process_line_with_spaces_valid(self):
        line = "a=a value\tb=b value\tc=c value"
        entry = self.parser.process_line(line)
        self.assertEqual(
            entry,
            {
                'a': 'A VALUE',
                'b': 'b value',
                'ccc': 'c value',
            }
        )

    def test_process_line_all_fields(self):
        self.parser.FIELDS = []
        line = "a=a_value\tb=b_value\tc=c_value\td=d_value"
        entry = self.parser.process_line(line)
        self.assertEqual(
            entry,
            {
                'a': 'A_VALUE',
                'b': 'b_value',
                'ccc': 'c_value',
                'd': 'd_value'
            }
        )

    def test_process_line_with_tskv_at_beginning(self):
        self.parser = TSKVEntryParser(tskv_prefix=True)
        line = "tskv\ta=a_value\tb=b_value\tc=c_value"
        entry = self.parser.process_line(line)
        self.assertEqual(
            entry,
            {
                'a': 'a_value',
                'b': 'b_value',
                'c': 'c_value',
            }
        )

    def test_process_line_ignore_none(self):
        line = "a=\tb=b_value\tc=c_value"
        entry = self.parser.process_line(line)
        self.assertEqual(
            entry,
            {
                'b': 'b_value',
                'ccc': 'c_value',
            },
        )

    def test_process_line_missing_required_fields(self):
        with self.assertRaises(BadLogLineError):
            line = "a=a_value\tb=bad_b_value\tc=c_value"
            self.parser.process_line(line)

    def test_parse(self):
        fileobj = StringIO('a=a_value\tb=b_value\tc=c_value\n'
                           'a=aa_value\tb=bb_value\tc=cc_value\n')
        self.assertEqual(
            list(self.parser.parse(fileobj)),
            [
                {'a': 'A_VALUE', 'b': 'b_value', 'ccc': 'c_value'},
                {'a': 'AA_VALUE', 'b': 'bb_value', 'ccc': 'cc_value'},
            ],
        )

    def test_parse_ignore_bad_tskv_line_1(self):
        fileobj = StringIO('a=a_value\tb=b_value\tc=c_value\n'
                           'a=aa_value b=bb_value\tc=cc_value\n'
                           'a=aaa_value\tb=bbb_value\tc=ccc_value\n')
        self.assertEqual(
            list(self.parser.parse(fileobj)),
            [
                {'a': 'A_VALUE', 'b': 'b_value', 'ccc': 'c_value'},
                {'a': 'AAA_VALUE', 'b': 'bbb_value', 'ccc': 'ccc_value'},
            ],
        )

    def test_parse_ignore_bad_tskv_line_2(self):
        fileobj = StringIO('a=a_value\tb=b_value\tc=c_value\n'
                           'a=aa_value\tb\tc=cc_value\n'
                           'a=aaa_value\tb=bbb_value\tc=ccc_value\n')
        self.assertEqual(
            list(self.parser.parse(fileobj)),
            [
                {'a': 'A_VALUE', 'b': 'b_value', 'ccc': 'c_value'},
                {'a': 'AAA_VALUE', 'b': 'bbb_value', 'ccc': 'ccc_value'},
            ],
        )

    def test_parse_disable_ignore_bad_csv_line(self):
        with self.assertRaises(BadLogLineError):
            fileobj = StringIO('a=a_value\tb=b_value\tc=c_value\n'
                               'a=aa_value b=bb_value\tc=cc_value\n'
                               'a=aaa_value\tb=bbb_value\tc=ccc_value\n')
            list(self.parser.parse(fileobj, ignore_errors=False))

    def test_parse_ignore_bad_line_content(self):
        fileobj = StringIO('a=a_value\tb=bad_b_value\tc=c_value\n'
                           'a=a_value\tb=b_value\tc=c_value')
        self.assertEqual(
            list(self.parser.parse(fileobj)),
            [
                {'a': 'A_VALUE', 'b': 'b_value', 'ccc': 'c_value'},
            ],
        )

    def test_parse_disable_ignore_bad_line_content(self):
        with self.assertRaises(BadLogLineError):
            fileobj = StringIO('a=a_value\tb=bad_b_value\tc=c_value\n'
                               'a=a_value\tb=b_value\tc=c_value')
            self.assertEqual(
                list(self.parser.parse(fileobj, ignore_errors=False)),
                [
                    {'a': 'A_VALUE', 'b': 'b_value', 'ccc': 'c_value'},
                ],
            )

    def test_parse_with_empty_line(self):
        fileobj = StringIO('\n'
                           '\n'
                           'a=a_value\tb=b_value\tc=c_value')
        self.assertEqual(
            list(self.parser.parse(fileobj, ignore_errors=False)),
            [
                {'a': 'A_VALUE', 'b': 'b_value', 'ccc': 'c_value'},
            ],
        )

    def test_parse_not_line_parts(self):
        with self.assertRaises(BadLogLineError):
            self.parser = TSKVEntryParser(tskv_prefix=True)
            fileobj = StringIO('tskv\n')
            list(self.parser.parse(fileobj, ignore_errors=False))


class TestOAuthParser(BaseTestClass):
    parser = OAuthEntryParser()

    def test_parse(self):
        fileobj = StringIO(
            'v=1\ttimestamp=1411518666.641738\tnew_scopes=login:birthday,'
            'login:email,login:info\taction=change\told_scopes=login:birthday,'
            'login:email,login:info\ttarget=client\tclient_id=932c1723e17844f0a7bfb4119505b8de\t'
            'old_callback=https://www.grandrio.com/en/social/login/ya\t'
            'new_callback=https://www.grandrio.com/{en|ru}/social/login/ya\n'
            'v=1\ttimestamp=1411514215.374172\taction=delete\tscopes=metrika:read\t'
            'target=client\tclient_id=13da17ca4db24e0b82e30575119115d3\n'
            'v=1\tscopes=fotki:delete,fotki:read,fotki:update,fotki:write\t'
            'consumer_ip=::ffff:94.73.222.51\ttarget=token\ttimestamp=1447707609.463135\t'
            'user_ip=::ffff:94.73.222.51\thas_alias=0\t'
            'user_agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/42.0.2311.90 Safari/537.36\tclient_id=c3f3f5892ec446cb855d49d26c3b5e7e\t'
            'action=create\ttoken_id=127867211\tgrant_type=password\tuid=311746834\n'
        )
        self.assertEqual(
            list(self.parser.parse(fileobj, ignore_errors=False)),
            [
                {
                    'version': 1,
                    'timestamp': 1411518666.641738,
                    'action': 'change',
                    'target': 'client',
                    'new_scopes': 'login:birthday,login:email,login:info',
                    'old_scopes': 'login:birthday,login:email,login:info',
                    'client_id': '932c1723e17844f0a7bfb4119505b8de',
                    'old_callback': 'https://www.grandrio.com/en/social/login/ya',
                    'new_callback': 'https://www.grandrio.com/{en|ru}/social/login/ya'
                },
                {
                    'version': 1,
                    'timestamp': 1411514215.374172,
                    'action': 'delete',
                    'target': 'client',
                    'scopes': 'metrika:read',
                    'client_id': '13da17ca4db24e0b82e30575119115d3'
                },
                {
                    'scopes': 'fotki:delete,fotki:read,fotki:update,fotki:write',
                    'grant_type': 'password',
                    'target': 'token',
                    'timestamp': 1447707609.463135,
                    'user_ip': '::ffff:94.73.222.51',
                    'version': 1,
                    'has_alias': '0',
                    'useragent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) '
                                 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36',
                    'client_id': 'c3f3f5892ec446cb855d49d26c3b5e7e',
                    'action': 'create',
                    'token_id': '127867211',
                    'consumer_ip': '::ffff:94.73.222.51',
                    'uid': 311746834,
                },
            ],
        )

    def test_parse_required_fields(self):
        fileobjs = [
            # version
            StringIO('timestamp=1411518666.641738\tnew_scopes=login:birthday,'
                     'login:email,login:info\taction=change\told_scopes=login:birthday,'
                     'login:email,login:info\ttarget=client\tclient_id=932c1723e17844f0a7bfb4119505b8de\t'
                     'old_callback=https://www.grandrio.com/en/social/login/ya\t'
                     'new_callback=https://www.grandrio.com/{en|ru}/social/login/ya'),
            # timestamp
            StringIO('v=1\tnew_scopes=login:birthday,login:email,login:info\taction=change\t'
                     'old_scopes=login:birthday,login:email,login:info\ttarget=client\t'
                     'client_id=932c1723e17844f0a7bfb4119505b8de\t'
                     'old_callback=https://www.grandrio.com/en/social/login/ya\t'
                     'new_callback=https://www.grandrio.com/{en|ru}/social/login/ya'),
            # action
            StringIO('v=1\ttimestamp=1411518666.641738\tnew_scopes=login:birthday,login:email,login:info\t'
                     'old_scopes=login:birthday,login:email,login:info\ttarget=client\t'
                     'client_id=932c1723e17844f0a7bfb4119505b8de\t'
                     'old_callback=https://www.grandrio.com/en/social/login/ya\t'
                     'new_callback=https://www.grandrio.com/{en|ru}/social/login/ya'),
            # target
            StringIO('v=1\ttimestamp=1411518666.641738\tnew_scopes=login:birthday,login:email,login:info\t'
                     'action=change\told_scopes=login:birthday,login:email,login:info\t'
                     'client_id=932c1723e17844f0a7bfb4119505b8de\t'
                     'old_callback=https://www.grandrio.com/en/social/login/ya\t'
                     'new_callback=https://www.grandrio.com/{en|ru}/social/login/ya')
        ]
        for fileobj in fileobjs:
            with self.assertRaises(BadLogLineError):
                list(self.parser.parse(fileobj, ignore_errors=False))


class TestMailUserJournalParser(BaseTestClass):
    parser = MailUserJournalEntryParser()

    def test_parse(self):
        fileobj = StringIO(
            'tskv\tv=1\tdate=1411518666641\tuid=123\ta=aaa\tb=\tc=ccc\n'
            'tskv\tv=1\tdate=1411518666641\tuid=123\ta=aaaa\tb=\tc=cccc\n'
            'tskv\ttableName=users_history\tuid=00000000003000366738\tdate=1414666476065\tip=37.9.101.92\tmodule=wmi\t'
            'target=account\toperation=authorization\taffected=0\thidden=0\tregionId=9999\t'
            'operationSystem.name=Windows 7\toperationSystem.version=6.1\t'
            'browser.name=YandexBrowser\tbrowser.version=14.8.1985.12084\t'
            'yandexuidCookie=7207633351394011299\tconnectionId=2c84bc9e7c2bd478f3fa82de5f1bd0be\t'
            'sessionInfo=1414422061000 2a02:6b8:0:107:d913:a2d5:d0c7:6cb2 7e\tdeviceType=desktop\t'
            'internetProvider=AS13238\t\n'
        )
        self.assertEqual(
            list(self.parser.parse(fileobj, ignore_errors=False)),
            [
                {
                    'version': 1,
                    'date': 1411518666641,
                    'uid': 123,
                    'a': 'aaa',
                    'b': '',
                    'c': 'ccc',
                },
                {
                    'version': 1,
                    'date': 1411518666641,
                    'uid': 123,
                    'a': 'aaaa',
                    'b': '',
                    'c': 'cccc',
                },
                {
                    'connectionId': '2c84bc9e7c2bd478f3fa82de5f1bd0be',
                    'affected': '0',
                    'uid': 3000366738,
                    'sessionInfo': '1414422061000 2a02:6b8:0:107:d913:a2d5:d0c7:6cb2 7e',
                    'ip': '37.9.101.92',
                    'regionId': '9999',
                    'tableName': 'users_history',
                    'module': 'wmi',
                    'operationSystem.version': '6.1',
                    'internetProvider': 'AS13238',
                    'deviceType': 'desktop',
                    'browser.version': '14.8.1985.12084',
                    'yandexuidCookie': '7207633351394011299',
                    'operationSystem.name': 'Windows 7',
                    'date': 1414666476065,
                    'operation': 'authorization',
                    'browser.name': 'YandexBrowser',
                    'hidden': '0',
                    'target': 'account',
                },
            ],
        )

    def test_parse_required_fields(self):
        fileobjs = [
            # date
            StringIO('tskv\tv=1\tuid=123\ta=aaa\tb=\tc=ccc\n'),
            # uid
            StringIO('tskv\tv=1\tdate=1411518666641\ta=aaa\tb=\tc=ccc\n'),
        ]
        for fileobj in fileobjs:
            with self.assertRaises(BadLogLineError):
                list(self.parser.parse(fileobj, ignore_errors=False))


class TestYasmsPrivateParser(BaseTestClass):
    parser = YasmsPrivateEntryParser()

    def test_parse(self):
        fileobj = StringIO(
            'tskv\ttskv_format=yasms-log\tunixtime=1416482491\t'
            'unixtimef=1416482491.877\tsms=1\taction=enqueued\t'
            'global_smsid=2127000000940195\tlocal_smsid=940195\t'
            'host_id=7F\tsender=yasms\trule=validate\tgate=9\t'
            'chars=55\tsegments=1\tencoding=utf16\tmasked_number=+7909684****\t'
            'uid=4000188396\tidentity=confirmation.add.new\tnumber=+79096841646\t'
            'text=Ваш код подтверждения: 5894. Наберите его в поле ввода.\n'
            'tskv\ttskv_format=yasms-log\tunixtime=1416482491\tunixtimef=1416482491.912\t'
            'sms=1\taction=senttosmsc\tglobal_smsid=2127000000940195\t'
            'local_smsid=940195\thost_id=7F\n'
            'tskv\ttskv_format=yasms-log\tunixtime=1416482492\tunixtimef=1416482492.926\t'
            'sms=1\taction=deliveredtosmsc\tglobal_smsid=2127000000940195\t'
            'local_smsid=940195\thost_id=7F\tmasked_number=+7909684****\tnumber=+79096841646\n',
        )
        self.assertEqual(
            list(self.parser.parse(fileobj, ignore_errors=False)),
            [
                {
                    'gate': '9',
                    'sender': 'yasms',
                    'encoding': 'utf16',
                    'masked_number': '+7909684****',
                    'timestamp': 1416482491.877,
                    'chars': '55',
                    'sms': '1',
                    'number': '+79096841646',
                    'rule': 'validate',
                    'uid': '4000188396',
                    'text': 'Ваш код подтверждения: 5894. Наберите его в поле ввода.',
                    'host_id': '7F',
                    'unixtime': 1416482491,
                    'action': 'enqueued',
                    'tskv_format': 'yasms-log',
                    'global_smsid': '2127000000940195',
                    'segments': '1',
                    'identity': 'confirmation.add.new',
                    'local_smsid': '940195',
                },
                {
                    'timestamp': 1416482491.912,
                    'sms': '1',
                    'host_id': '7F',
                    'unixtime': 1416482491,
                    'action': 'senttosmsc',
                    'tskv_format': 'yasms-log',
                    'global_smsid': '2127000000940195',
                    'local_smsid': '940195',
                },
                {
                    'masked_number': '+7909684****',
                    'timestamp': 1416482492.926,
                    'sms': '1',
                    'number': '+79096841646',
                    'host_id': '7F',
                    'unixtime': 1416482492,
                    'action': 'deliveredtosmsc',
                    'tskv_format': 'yasms-log',
                    'global_smsid': '2127000000940195',
                    'local_smsid': '940195',
                },
            ],
        )

    def test_parse_encrypted_text(self):
        self.maxDiff = 1000
        encrypted_text = encrypt(u'Ваш код подтверждения: 5894. Наберите его в поле ввода.')
        if six.PY3:
            encrypted_text = encrypted_text.decode('utf-8')
        fileobj = StringIO(
            'tskv\ttskv_format=yasms-log\tunixtime=1416482491\t'
            'unixtimef=1416482491.877\tsms=1\taction=enqueued\t'
            'global_smsid=2127000000940195\tlocal_smsid=940195\t'
            'host_id=7F\tsender=yasms\trule=validate\tgate=9\t'
            'chars=55\tsegments=1\tencoding=utf16\tmasked_number=+7909684****\t'
            'uid=4000188396\tidentity=confirmation.add.new\tnumber=+79096841646\t'
            'encryptedtext=%s\n' % encrypted_text,
        )
        self.assertEqual(
            list(self.parser.parse(fileobj, ignore_errors=False)),
            [
                {
                    'gate': '9',
                    'sender': 'yasms',
                    'encoding': 'utf16',
                    'masked_number': '+7909684****',
                    'timestamp': 1416482491.877,
                    'chars': '55',
                    'sms': '1',
                    'number': '+79096841646',
                    'rule': 'validate',
                    'uid': '4000188396',
                    'text': u'Ваш код подтверждения: 5894. Наберите его в поле ввода.'.encode('utf-8'),
                    'host_id': '7F',
                    'unixtime': 1416482491,
                    'action': 'enqueued',
                    'tskv_format': 'yasms-log',
                    'global_smsid': '2127000000940195',
                    'segments': '1',
                    'identity': 'confirmation.add.new',
                    'local_smsid': '940195',
                },
            ],
        )

    def test_parse_required_fields(self):
        fileobjs = [
            # action
            StringIO('tskv\tunixtime=1\tunixtimef=2'),
            # unixtime
            StringIO('tskv\taction=a\tunixtime=1'),
            # unixtimef -> timestamp
            StringIO('tskv\taction=aunixtimef=2'),
        ]
        for fileobj in fileobjs:
            with self.assertRaises(BadLogLineError):
                list(self.parser.parse(fileobj, ignore_errors=False))


class TestJSONParser(BaseTestClass):
    def setUp(self):
        super(TestJSONParser, self).setUp()
        self.parser = JSONEntryParser()

    def test_process_line_valid(self):
        line = '{"a": "A_VALUE", "b": "значение Б", "ccc": "c_value"}'
        entry = self.parser.process_line(line)
        self.assertEqual(
            entry,
            {
                'a': 'A_VALUE',
                'b': u'значение Б',
                'ccc': 'c_value',
            }
        )

    def test_parse(self):
        fileobj = StringIO('{"a": "A_VALUE", "b": "b_value", "ccc": "c_value"}\n'
                           '{"a": "AA_VALUE", "b": "bb_value", "ccc": "cc_value"}\n')
        self.assertEqual(
            list(self.parser.parse(fileobj)),
            [
                {'a': 'A_VALUE', 'b': 'b_value', 'ccc': 'c_value'},
                {'a': 'AA_VALUE', 'b': 'bb_value', 'ccc': 'cc_value'},
            ],
        )

    def test_parse_ignore_bad_json_line_1(self):
        fileobj = StringIO('{"a": "A_VALUE", "b": "b_value", "ccc": "c_value"}\n'
                           '{"a": "AA_VALUE", "b": "bb_value", "ccc": "cc_value"\n'
                           '{"a": "AAA_VALUE", "b": "bbb_value", "ccc": "ccc_value"}\n')
        self.assertEqual(
            list(self.parser.parse(fileobj)),
            [
                {'a': 'A_VALUE', 'b': 'b_value', 'ccc': 'c_value'},
                {'a': 'AAA_VALUE', 'b': 'bbb_value', 'ccc': 'ccc_value'},
            ],
        )

    def test_parse_ignore_bad_json_line_2(self):
        fileobj = StringIO('{"a": "A_VALUE", "b": "b_value", "ccc": "c_value"}\n'
                           '{"a": "AA_VALUE", "b", "ccc": "cc_value"}\n'
                           '{"a": "AAA_VALUE", "b": "bbb_value", "ccc": "ccc_value"}\n')
        self.assertEqual(
            list(self.parser.parse(fileobj)),
            [
                {'a': 'A_VALUE', 'b': 'b_value', 'ccc': 'c_value'},
                {'a': 'AAA_VALUE', 'b': 'bbb_value', 'ccc': 'ccc_value'},
            ],
        )

    def test_parse_disable_ignore_bad_json_line(self):
        with self.assertRaises(BadLogLineError):
            fileobj = StringIO('{"a": "A_VALUE", "b": "b_value", "ccc": "c_value"}\n'
                               '{"a": "AA_VALUE", "b": "bb_value", "ccc": "cc_value"\n'
                               '{"a": "AAA_VALUE", "b": "bbb_value", "ccc": "ccc_value"}\n')
            list(self.parser.parse(fileobj, ignore_errors=False))

    def test_parse_with_empty_line(self):
        fileobj = StringIO('\n'
                           '\n'
                           '{"a": "A_VALUE", "b": "b_value", "ccc": "c_value"}\n')
        self.assertEqual(
            list(self.parser.parse(fileobj, ignore_errors=False)),
            [
                {'a': 'A_VALUE', 'b': 'b_value', 'ccc': 'c_value'},
            ],
        )
