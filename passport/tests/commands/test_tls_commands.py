# coding: utf-8

import base64
import hashlib
import json

import mock
from passport.backend.library.test.time_mock import TimeMock
from passport.backend.vault.api.test.base_test_case import BaseTestCase
from vault_client_cli.commands.tls import (
    TLSSecret,
    TLSSecretValueError,
    TLSTicketValueError,
)

from .base import (
    BaseCLICommandRSATestCaseMixin,
    BaseCLICommandTestCase,
)


class UrandomMock(object):
    def __init__(self):
        self.urandom_pos = 0
        self.urandom_mock = mock.patch('os.urandom', side_effect=self.urandom_gen)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        self.urandom_mock.start()

    def stop(self):
        self.urandom_mock.stop()

    def gen_bytes(self, size):
        pos = self.urandom_pos
        for i in range(size):
            yield chr(pos)
            pos += 1
            if pos > 255:
                pos = 0

    def urandom_gen(self, size):
        self.urandom_pos += 1
        if self.urandom_pos > 255:
            self.urandom_pos = 0
        return ''.join(self.gen_bytes(size))


class TestTLSClasses(BaseTestCase):
    def setUp(self):
        self.maxDiff = None

        self.time_mock = TimeMock()
        self.time_mock.start()

    def tearDown(self):
        self.time_mock.stop()

    def test_create_tls_secret(self):
        with UrandomMock():
            self.assertDictEqual(
                TLSSecret().dump(),
                {
                    '0': 'AQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8w',
                    '0.sha256': '209d209007d9a1dba629569b7ec7e452ab0652d0fe8de154328c7d1856670c49',
                    '1': 'AgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAx',
                    '1.sha256': '82a61c4f7e5aecccb9ff754bba7240e5851decf1ee8114ccf94ed5f626023617',
                    '2': 'AwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEy',
                    '2.sha256': '273c0b82e7d79f52348c3245e50fda733ffe391f08bf253e3a1a47b8a6844d3b',
                    'options': '{"count": 3, "length": 48, "suffix": "", "ttl": 28}',
                    'ts': 1445385600,
                }
            )

            self.assertDictEqual(
                TLSSecret(count=5, length=56, suffix='test.ext').dump(),
                {
                    '0.test.ext': 'BAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs=',
                    '0.test.ext.sha256': '9b39293192881a3223343006dc7bcc4f259665e530c6c3b89346eb8283b7a45b',
                    '1.test.ext': 'BQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw=',
                    '1.test.ext.sha256': '538a56fa39707eedbe69e04da33c6d9113336d63652b10412bccb73f3fb3c414',
                    '2.test.ext': 'BgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0=',
                    '2.test.ext.sha256': 'add96bae03584a31b6547886787db4f06c51b26529424ea911ee1051031a75ee',
                    '3.test.ext': 'BwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4=',
                    '3.test.ext.sha256': 'aa993d0bc96aa499228679aab24fd5e8f3395531fea1ff80e09245902a02afa4',
                    '4.test.ext': 'CAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj8=',
                    '4.test.ext.sha256': 'ab6c08b696fb3c930d88143eecb525c9249ee556443004ce8c9e0964fa0afc45',
                    'options': '{"count": 5, "length": 56, "suffix": "test.ext", "ttl": 28}',
                    'ts': 1445385600
                }
            )

    def test_rotate_tls_secret(self):
        with UrandomMock():
            tls_secret = TLSSecret()
            tls_secret_dump = tls_secret.dump()
            self.assertDictEqual(
                tls_secret_dump,
                {
                    '0': 'AQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8w',
                    '0.sha256': '209d209007d9a1dba629569b7ec7e452ab0652d0fe8de154328c7d1856670c49',
                    '1': 'AgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAx',
                    '1.sha256': '82a61c4f7e5aecccb9ff754bba7240e5851decf1ee8114ccf94ed5f626023617',
                    '2': 'AwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEy',
                    '2.sha256': '273c0b82e7d79f52348c3245e50fda733ffe391f08bf253e3a1a47b8a6844d3b',
                    'options': '{"count": 3, "length": 48, "suffix": "", "ttl": 28}',
                    'ts': 1445385600,
                }
            )

            self.time_mock.tick()
            tls_secret.rotate()

            self.assertDictEqual(
                tls_secret_dump,
                tls_secret.dump()
            )

            self.time_mock.tick(tls_secret.ttl * 3600)
            tls_secret.rotate()
            rotated_tls_secret_dump = tls_secret.dump()
            self.assertDictEqual(
                rotated_tls_secret_dump,
                {
                    '0': 'BAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIz',
                    '0.sha256': '6e4bb01621337209a12c88e2fbffa4d12187ad1cd5abb6946aced9ea6d5f53d0',
                    '1': tls_secret_dump['0'],
                    '1.sha256': tls_secret_dump['0.sha256'],
                    '2': tls_secret_dump['1'],
                    '2.sha256': tls_secret_dump['1.sha256'],
                    'options': '{"count": 3, "length": 48, "suffix": "", "ttl": 28}',
                    'ts': 1445486401,
                }
            )

            self.time_mock.tick()
            tls_secret.rotate(force=True)
            self.assertDictEqual(
                tls_secret.dump(),
                {
                    '0': 'BQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0',
                    '0.sha256': '806abfd4ceedb01590649c4d2c976d5b8104457395a63f9475edc5db946ca910',
                    '1': rotated_tls_secret_dump['0'],
                    '1.sha256': rotated_tls_secret_dump['0.sha256'],
                    '2': rotated_tls_secret_dump['1'],
                    '2.sha256': rotated_tls_secret_dump['1.sha256'],
                    'options': '{"count": 3, "length": 48, "suffix": "", "ttl": 28}',
                    'ts': 1445486402,
                }
            )

    def test_create_from_version_ok(self):
        version = {
            u'created_at': 1445385615.0,
            u'created_by': 100,
            u'creator_login': u'vault-test-100',
            u'secret_name': u'new_tls_secret',
            u'secret_uuid': u'sec-0000000000000000000001x140',
            u'value': {u'0.test': u'AQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8w',
                       u'0.test.sha256': u'209d209007d9a1dba629569b7ec7e452ab0652d0fe8de154328c7d1856670c49',
                       u'1.test': u'AgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAx',
                       u'1.test.sha256': u'82a61c4f7e5aecccb9ff754bba7240e5851decf1ee8114ccf94ed5f626023617',
                       u'2.test': u'AwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEy',
                       u'2.test.sha256': u'273c0b82e7d79f52348c3245e50fda733ffe391f08bf253e3a1a47b8a6844d3b',
                       u'3.test': u'AwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEy',
                       u'3.test.sha256': u'273c0b82e7d79f52348c3245e50fda733ffe391f08bf253e3a1a47b8a6844d3b',
                       u'options': "{\"count\": 4, \"length\": 48, \"suffix\": \"test\", \"ttl\": 28}",
                       u'ts': u'1445385615'},
            u'version': u'ver-0000000000000000000001x145'}
        tls_secret = TLSSecret.from_version(version)
        self.assertDictEqual(
            tls_secret.dump(),
            {'0.test': u'AQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8w',
             '0.test.sha256': u'209d209007d9a1dba629569b7ec7e452ab0652d0fe8de154328c7d1856670c49',
             '1.test': u'AgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAx',
             '1.test.sha256': u'82a61c4f7e5aecccb9ff754bba7240e5851decf1ee8114ccf94ed5f626023617',
             '2.test': u'AwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEy',
             '2.test.sha256': u'273c0b82e7d79f52348c3245e50fda733ffe391f08bf253e3a1a47b8a6844d3b',
             '3.test': u'AwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEy',
             '3.test.sha256': u'273c0b82e7d79f52348c3245e50fda733ffe391f08bf253e3a1a47b8a6844d3b',
             'options': '{"count": 4, "length": 48, "suffix": "test", "ttl": 28}',
             'ts': 1445385615.0}
        )

    def test_create_from_version_errors(self):
        version = {
            u'created_at': 1445385615.0,
            u'created_by': 100,
            u'creator_login': u'vault-test-100',
            u'secret_name': u'new_tls_secret',
            u'secret_uuid': u'sec-0000000000000000000001x140',
            u'value': {u'0.test': u'AQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8w',
                       u'0.test.sha256': u'209d209007d9a1dba629569b7ec7e452ab0652d0fe8de154328c7d1856670c49',
                       u'1.test': u'AgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAx',
                       u'1.test.sha256': u'82a61c4f7e5aecccb9ff754bba7240e5851decf1ee8114ccf94ed5f626023617',
                       u'2.test': u'AwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEy',
                       u'2.test.sha256': u'273c0b82e7d79f52348c3245e50fda733ffe391f08bf253e3a1a47b8a6844d3b',
                       u'3.test': u'AwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEy',
                       u'3.test.sha256': u'273c0b82e7d79f52348c3245e50fda733ffe391f08bf253e3a1a47b8a6844d3b',
                       u'options': "{\"count\": 4, \"length\": 48, \"suffix\": \"test\", \"ttl\": 28}"},
            u'version': u'ver-0000000000000000000001x145'}
        with self.assertRaises(TLSSecretValueError) as r:
            TLSSecret.from_version(version)
        self.assertEqual(
            str(r.exception),
            '"" is an invalid timestamp (ts) value',
        )

        version = {
            u'created_at': 1445385615.0,
            u'created_by': 100,
            u'creator_login': u'vault-test-100',
            u'secret_name': u'new_tls_secret',
            u'secret_uuid': u'sec-0000000000000000000001x140',
            u'value': {u'0.test': u'AQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8w',
                       u'0.test.sha256': u'209d209007d9a1dba629569b7ec7e452ab0652d0fe8de154328c7d1856670c49',
                       u'1.test': u'AgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAx',
                       u'1.test.sha256': u'82a61c4f7e5aecccb9ff754bba7240e5851decf1ee8114ccf94ed5f626023617',
                       u'2.test': u'AwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEy',
                       u'2.test.sha256': u'273c0b82e7d79f52348c3245e50fda733ffe391f08bf253e3a1a47b8a6844d3b',
                       u'3.test': u'AwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEy',
                       u'3.test.sha256': u'273c0b82e7d79f52348c3245e50fda733ffe391f08bf253e3a1a47b8a6844d3b',
                       u'options': "{\"count\": 3, \"length\": 48, \"suffix\": \"test\", \"ttl\": 28}",
                       u'ts': 1445385615.0},
            u'version': u'ver-0000000000000000000001x145'}
        with self.assertRaises(TLSSecretValueError) as r:
            TLSSecret.from_version(version)
        self.assertEqual(
            str(r.exception),
            u'The version tickets count mismatch tickets counts in options or less minimal tickets count. '
            u'(3 != 4) Minimal tickets count is 3',
        )

        version = {
            u'created_at': 1445385615.0,
            u'created_by': 100,
            u'creator_login': u'vault-test-100',
            u'secret_name': u'new_tls_secret',
            u'secret_uuid': u'sec-0000000000000000000001x140',
            u'value': {u'0.test': u'AQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8w',
                       u'0.test.sha256': u'209d209007d9a1dba629569b7ec7e452ab0652d0fe8de154328c7d1856670c49',
                       u'1.test': u'AgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAx',
                       u'1.test.sha256': u'82a61c4f7e5aecccb9ff754bba7240e5851decf1ee8114ccf94ed5f626023617',
                       u'2.test': u'AwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEy',
                       u'2.test.sha256': u'273c0b82e7d79f52348c3245e50fda733ffe391f08bf253e3a1a47b8a6844d3b',
                       u'3.test': u'AwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEy',
                       u'3.test.sha256': u'273c0b82e7d79f52348c3245e50fda733ffe391f08bf253e3a1a47b8a6844d3b',
                       u'options': "{\"count\": 4, \"length\": 48, \"suffix\": \"\", \"ttl\": 28}",
                       u'ts': 1445385615.0},
            u'version': u'ver-0000000000000000000001x145'}
        with self.assertRaises(TLSSecretValueError) as r:
            TLSSecret.from_version(version)
        self.assertEqual(
            str(r.exception),
            u'Can\'t find tickets in a version value (suffix: "")',
        )

        version = {
            u'created_at': 1445385615.0,
            u'created_by': 100,
            u'creator_login': u'vault-test-100',
            u'secret_name': u'new_tls_secret',
            u'secret_uuid': u'sec-0000000000000000000001x140',
            u'value': {u'options': "{\"count\": 4, \"length\": 48, \"suffix\": \"test\", \"ttl\": 28}",
                       u'ts': 1445385615.0},
            u'version': u'ver-0000000000000000000001x145'}
        with self.assertRaises(TLSSecretValueError) as r:
            TLSSecret.from_version(version)
        self.assertEqual(
            str(r.exception),
            u'Can\'t find tickets in a version value (suffix: "test")',
        )

        version = {
            u'created_at': 1445385615.0,
            u'created_by': 100,
            u'creator_login': u'vault-test-100',
            u'secret_name': u'new_tls_secret',
            u'secret_uuid': u'sec-0000000000000000000001x140',
            u'value': {u'0.test': base64.b64encode('1'*48),
                       u'0.test.sha256': u'209d209007d9a1dba629569b7ec7e452ab0652d0fe8de154328c7d1856670c49',
                       u'1.test': u'AgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAx',
                       u'1.test.sha256': u'82a61c4f7e5aecccb9ff754bba7240e5851decf1ee8114ccf94ed5f626023617',
                       u'2.test': u'AwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEy',
                       u'2.test.sha256': u'273c0b82e7d79f52348c3245e50fda733ffe391f08bf253e3a1a47b8a6844d3b',
                       u'3.test': u'AwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEy',
                       u'3.test.sha256': u'273c0b82e7d79f52348c3245e50fda733ffe391f08bf253e3a1a47b8a6844d3b',
                       u'options': "{\"count\": 4, \"length\": 48, \"suffix\": \"test\", \"ttl\": 28}",
                       u'ts': u'1445385615'},
            u'version': u'ver-0000000000000000000001x145'}
        with self.assertRaises(TLSTicketValueError) as r:
            TLSSecret.from_version(version)
        self.assertEqual(
            str(r.exception),
            u'Ticket error: "209d209007d9a1dba629569b7ec7e452ab0652d0fe8de154328c7d1856670c49" is an invalid '
            u'sha256 hexdigest for "MTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTEx"',
        )

        version = {
            u'created_at': 1445385615.0,
            u'created_by': 100,
            u'creator_login': u'vault-test-100',
            u'secret_name': u'new_tls_secret',
            u'secret_uuid': u'sec-0000000000000000000001x140',
            u'value': {u'0.test': base64.b64encode(b'1'*100),
                       u'0.test.sha256': hashlib.sha256(base64.b64encode(b'1'*100)).hexdigest(),
                       u'1.test': u'AgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAx',
                       u'1.test.sha256': u'82a61c4f7e5aecccb9ff754bba7240e5851decf1ee8114ccf94ed5f626023617',
                       u'2.test': u'AwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEy',
                       u'2.test.sha256': u'273c0b82e7d79f52348c3245e50fda733ffe391f08bf253e3a1a47b8a6844d3b',
                       u'3.test': u'AwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEy',
                       u'3.test.sha256': u'273c0b82e7d79f52348c3245e50fda733ffe391f08bf253e3a1a47b8a6844d3b',
                       u'options': "{\"count\": 4, \"length\": 48, \"suffix\": \"test\", \"ttl\": 28}",
                       u'ts': u'1445385615'},
            u'version': u'ver-0000000000000000000001x145'}
        with self.assertRaises(TLSTicketValueError) as r:
            TLSSecret.from_version(version)
        self.assertEqual(
            str(r.exception),
            u'An invalid ticket content length. (100 != 48, MTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTEx'
            'MTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMQ==)'
        )

    def test_create_warnings(self):
        tls_secret = TLSSecret(count=1, length=5, ttl=0)
        self.assertListEqual(
            tls_secret.warnings,
            [
                'Tickets count less then 3 (1), set to 3',
                'Ticket length less then 12 (5), set to 12',
                'TTL less then 1 (0), set to 1',
            ]
        )


class TestCreateTokenCommand(BaseCLICommandTestCase, BaseCLICommandRSATestCaseMixin):
    fill_database = False
    fill_external_data = True
    send_user_ticket = True

    def test_create_tls_ticket_secret_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                command_args = [
                    'tls', 'create',
                    'new_tls_secret',
                    '--comment', 'TLS tickets for passport.yandex-team.ru',
                    '--tags', 'passport, nginx, tls'
                ]
                result = self.runner.invoke(command_args)
                self.assertEqual(result.exit_code, 0, result.stdout)
                self.assertEqual(
                    result.stdout,
                    u'uuid: sec-0000000000000000000001x140\n'
                    u'name: new_tls_secret\n'
                    u'comment: TLS tickets for passport.yandex-team.ru\n'
                    u'tags: nginx, passport, tls\n'
                    u'\n'
                    u'creator: vault-test-100 (100)\n'
                    u'created: 2015-10-21 00:00:15\n'
                    u'updated: 2015-10-21 00:00:15\n'
                    u'\n'
                    u'versions:\n'
                    u'+--------------------------------+----------+---------------------+----------------------+\n'
                    u'| uuid                           | parent   | created             | creator              |\n'
                    u'|--------------------------------+----------+---------------------+----------------------|\n'
                    u'| ver-0000000000000000000001x145 | -        | 2015-10-21 00:00:15 | vault-test-100 (100) |\n'
                    u'+--------------------------------+----------+---------------------+----------------------+\n'
                    u'\n'
                    u'roles:\n'
                    u'owner:user:vault-test-100\n'
                    u'\n',
                )

    def test_create_tls_ticket_secret_json_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                with UrandomMock():
                    command_args = [
                        'tls', 'create',
                        'new_tls_secret',
                        '--comment', 'TLS tickets for passport.yandex-team.ru',
                        '--tags', 'passport, nginx, tls',
                        '-j',
                    ]
                    result = self.runner.invoke(command_args)
                    self.assertEqual(result.exit_code, 0, result.stdout)

                    result = json.loads(result.stdout)
                    self.assertDictEqual(
                        result,
                        {u'acl': [{u'created_at': 1445385615.0,
                                   u'created_by': 100,
                                   u'creator_login': u'vault-test-100',
                                   u'login': u'vault-test-100',
                                   u'role_slug': u'OWNER',
                                   u'uid': 100}],
                         u'comment': u'TLS tickets for passport.yandex-team.ru',
                         u'created_at': 1445385615.0,
                         u'created_by': 100,
                         u'creator_login': u'vault-test-100',
                         u'effective_role': u'OWNER',
                         u'name': u'new_tls_secret',
                         u'secret_roles': [{u'created_at': 1445385615.0,
                                            u'created_by': 100,
                                            u'creator_login': u'vault-test-100',
                                            u'login': u'vault-test-100',
                                            u'role_slug': u'OWNER',
                                            u'uid': 100}],
                         u'secret_versions': [{u'created_at': 1445385615.0,
                                               u'created_by': 100,
                                               u'creator_login': u'vault-test-100',
                                               u'keys': [u'0',
                                                         u'0.sha256',
                                                         u'1',
                                                         u'1.sha256',
                                                         u'2',
                                                         u'2.sha256',
                                                         u'options',
                                                         u'ts'],
                                               u'version': u'ver-0000000000000000000001x145'}],
                         u'tags': [u'nginx', u'passport', u'tls'],
                         u'tokens': [],
                         u'updated_at': 1445385615.0,
                         u'updated_by': 100,
                         u'uuid': u'sec-0000000000000000000001x140'}
                    )

        with self.user_permissions_and_time_mock():
            self.assertDictEqual(
                self.vault_client.get_version(result['secret_versions'][0]['version']),
                {u'created_at': 1445385615.0,
                 u'created_by': 100,
                 u'creator_login': u'vault-test-100',
                 u'secret_name': u'new_tls_secret',
                 u'secret_uuid': u'sec-0000000000000000000001x140',
                 u'value': {u'0': u'AQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8w',
                            u'0.sha256': u'209d209007d9a1dba629569b7ec7e452ab0652d0fe8de154328c7d1856670c49',
                            u'1': u'AgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAx',
                            u'1.sha256': u'82a61c4f7e5aecccb9ff754bba7240e5851decf1ee8114ccf94ed5f626023617',
                            u'2': u'AwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEy',
                            u'2.sha256': u'273c0b82e7d79f52348c3245e50fda733ffe391f08bf253e3a1a47b8a6844d3b',
                            u'options': u"{\"count\": 3, \"length\": 48, \"suffix\": \"\", \"ttl\": 28}",
                            u'ts': u'1445385615'},
                 u'version': u'ver-0000000000000000000001x145'}
            )

    def test_create_custom_tls_ticket_secret_json_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                with UrandomMock():
                    command_args = [
                        'tls', 'create',
                        'new_tls_secret',
                        '--key-suffix', 'passport.yandex.tld',
                        '--count', '5',
                        '--ttl', '28',
                        '--length', '64',
                        '-j',
                    ]
                    result = self.runner.invoke(command_args)
                    self.assertEqual(result.exit_code, 0, result.stdout)

        with self.user_permissions_and_time_mock():
            self.assertDictEqual(
                self.vault_client.get_version(json.loads(result.stdout)['uuid']),
                {u'created_at': 1445385615.0,
                 u'created_by': 100,
                 u'creator_login': u'vault-test-100',
                 u'secret_name': u'new_tls_secret',
                 u'secret_uuid': u'sec-0000000000000000000001x140',
                 u'value': {u'0.passport.yandex.tld': u'AQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/QA==',
                            u'0.passport.yandex.tld.sha256': u'99ad9425f2f8b81bd785a1f097258139571c276dc6bd49270d8df6c0892c4693',
                            u'1.passport.yandex.tld': u'AgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj9AQQ==',
                            u'1.passport.yandex.tld.sha256': u'161657a16198056fd7e474b84da2336c10bca530b85f3536f827fe4c91f9cfee',
                            u'2.passport.yandex.tld': u'AwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQg==',
                            u'2.passport.yandex.tld.sha256': u'32fa5bfb49d96c71a14160804ff1cbdfd6578777176e99c10bb8feb012d9705d',
                            u'3.passport.yandex.tld': u'BAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/QEFCQw==',
                            u'3.passport.yandex.tld.sha256': u'2998a846c573b9d4ae036a54092999330258a56c9494833d6bf2de7e1f8e2121',
                            u'4.passport.yandex.tld': u'BQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj9AQUJDRA==',
                            u'4.passport.yandex.tld.sha256': u'e73ce5165cda3795f49eb33d27bc63db34d1efebea030f656944b0533ad6c7fe',
                            u'options': u'{"count": 5, "length": 64, "suffix": "passport.yandex.tld", "ttl": 28}',
                            u'ts': u'1445385615'},
                 u'version': u'ver-0000000000000000000001x142'}
            )


class TestRotateTokenCommand(BaseCLICommandTestCase, BaseCLICommandRSATestCaseMixin):
    fill_database = False
    fill_external_data = True

    def test_rotate_tls_ticket_secret_ok(self):
        with self.rsa_permissions_and_time_mock() as tm:
            with self.uuid_mock():
                with UrandomMock():
                    tls_secret = TLSSecret()
                    secret_uuid = self.client.create_secret(
                        name='new_tls_secret',
                        value=tls_secret.dump(),
                    ).result['uuid']

                    tm.tick(28 * 3600)
                    command_args = [
                        'tls', 'rotate',
                        secret_uuid,
                    ]
                    result = self.runner.invoke(command_args)
                    self.assertEqual(result.exit_code, 0, result.stdout)
                    self.assertEqual(
                        result.stdout,
                        u'Get a secret (sec-0000000000000000000001x140)\n'
                        u'Get the last secret version\n'
                        u'Validate the last version\n'
                        u'Rotate a version if needed\n'
                        u'Store the new version\n'
                        u'Hide an old version\n'
                        u'\n'
                        u'status: Secret was rotated\n'
                        u'version: ver-0000000000000000000001x143\n'
                        u'comment: \n'
                        u'secret uuid: sec-0000000000000000000001x140\n'
                        u'secret name: new_tls_secret\n'
                        u'parent: ver-0000000000000000000001x142\n'
                        u'\n'
                        u'creator: vault-test-100 (100)\n'
                        u'created: 2015-10-22 04:00:15\n'
                        u'\n'
                        u'value:\n'
                        u'{\n'
                        u'    "0": "CgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5", \n'
                        u'    "0.sha256": "2de6e8a6cbd20a48693eccd7d08337c276bdca548ea747f6258cff7067d62910", \n'
                        u'    "1": "AQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8w", \n'
                        u'    "1.sha256": "209d209007d9a1dba629569b7ec7e452ab0652d0fe8de154328c7d1856670c49", \n'
                        u'    "2": "AgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAx", \n'
                        u'    "2.sha256": "82a61c4f7e5aecccb9ff754bba7240e5851decf1ee8114ccf94ed5f626023617", \n'
                        u'    "options": "{\\"count\\": 3, \\"length\\": 48, \\"suffix\\": \\"\\", \\"ttl\\": 28}", \n'
                        u'    "ts": "1445486415"\n'
                        u'}\n'
                    )

    def test_rotate_tls_ticket_secret_json_ok(self):
        with self.rsa_permissions_and_time_mock() as tm:
            with self.uuid_mock():
                with UrandomMock():
                    tls_secret = TLSSecret()
                    secret_uuid = self.client.create_secret(
                        name='new_tls_secret',
                        value=tls_secret.dump(),
                    ).result['uuid']

                    tm.tick(28 * 3600)
                    command_args = [
                        'tls', 'rotate',
                        secret_uuid,
                        '-j',
                    ]
                    result = self.runner.invoke(command_args)
                    self.assertEqual(result.exit_code, 0, result.stdout)
                    self.assertDictEqual(
                        json.loads(result.stdout),
                        {u'created_at': 1445486415.0,
                         u'created_by': 100,
                         u'creator_login': u'vault-test-100',
                         u'parent_version_uuid': u'ver-0000000000000000000001x142',
                         u'secret_name': u'new_tls_secret',
                         u'secret_uuid': u'sec-0000000000000000000001x140',
                         u'value': {u'0': u'CgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5',
                                    u'0.sha256': u'2de6e8a6cbd20a48693eccd7d08337c276bdca548ea747f6258cff7067d62910',
                                    u'1': tls_secret.tickets[0].value,
                                    u'1.sha256': tls_secret.tickets[0].hexdigest,
                                    u'2': tls_secret.tickets[1].value,
                                    u'2.sha256': tls_secret.tickets[1].hexdigest,
                                    u'options': u"{\"count\": 3, \"length\": 48, \"suffix\": \"\", \"ttl\": 28}",
                                    u'ts': u'1445486415'},
                         u'version': u'ver-0000000000000000000001x143'}
                    )

    def test_force_rotate_tls_ticket_secret_json_ok(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                with UrandomMock():
                    tls_secret = TLSSecret()
                    secret_uuid = self.client.create_secret(
                        name='new_tls_secret',
                        value=tls_secret.dump(),
                    ).result['uuid']

                    command_args = [
                        'tls', 'rotate',
                        secret_uuid,
                        '-j', '-f',
                    ]
                    result = self.runner.invoke(command_args)
                    self.assertEqual(result.exit_code, 0, result.stdout)
                    self.assertDictEqual(
                        json.loads(result.stdout),
                        {u'created_at': 1445385615.0,
                         u'created_by': 100,
                         u'creator_login': u'vault-test-100',
                         u'parent_version_uuid': u'ver-0000000000000000000001x142',
                         u'secret_name': u'new_tls_secret',
                         u'secret_uuid': u'sec-0000000000000000000001x140',
                         u'value': {u'0': u'CgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5',
                                    u'0.sha256': u'2de6e8a6cbd20a48693eccd7d08337c276bdca548ea747f6258cff7067d62910',
                                    u'1': tls_secret.tickets[0].value,
                                    u'1.sha256': tls_secret.tickets[0].hexdigest,
                                    u'2': tls_secret.tickets[1].value,
                                    u'2.sha256': tls_secret.tickets[1].hexdigest,
                                    u'options': u"{\"count\": 3, \"length\": 48, \"suffix\": \"\", \"ttl\": 28}",
                                    u'ts': u'1445385615'},
                         u'version': u'ver-0000000000000000000001x143'}
                    )

    def test_rotate_unexistent_secret_error(self):
        with self.rsa_permissions_and_time_mock():
            command_args = [
                'tls', 'rotate',
                'sec-0000000000000000000001x140',
                '-f',
            ]
            result = self.runner.invoke(command_args)
            self.assertEqual(result.exit_code, 3, result.stdout)
            self.assertEqual(
                result.stdout,
                u'Get a secret (sec-0000000000000000000001x140)\n'
                u'error: Requested a non-existent entity (Secret, sec-0000000000000000000001x140)\n'
            )

    def test_rotate_secret_without_version_error(self):
        with self.rsa_permissions_and_time_mock():
            with self.uuid_mock():
                with UrandomMock():
                    secret_uuid = self.client.create_secret(
                        name='new_tls_secret',
                    ).result['uuid']
                    command_args = [
                        'tls', 'rotate',
                        secret_uuid,
                        '-f',
                    ]
                    result = self.runner.invoke(command_args)
                    self.assertEqual(result.exit_code, 3, result.stdout)
                    self.assertEqual(
                        result.stdout,
                        u'Get a secret (sec-0000000000000000000001x140)\n'
                        u'Get the last secret version\n'
                        u'error: Requested a non-existent entity (SecretVersion, HEAD)\n'
                    )

    def test_rotate_secret_without_owner_permission_error(self):
        with self.user_permissions_and_time_mock(uid=100):
            tls_secret = TLSSecret()
            secret_uuid = self.client.create_secret(
                name='new_tls_secret',
                value=tls_secret.dump(),
            ).result['uuid']
            self.vault_client.add_user_role_to_secret(secret_uuid, 'OWNER', uid=102)
            self.vault_client.add_user_role_to_secret(secret_uuid, 'READER', uid=100)
            self.vault_client.delete_user_role_from_secret(secret_uuid, 'OWNER', uid=100)

        with self.rsa_permissions_and_time_mock() as tm:
            with self.uuid_mock():
                with UrandomMock():
                    tm.tick(28 * 3600)
                    command_args = [
                        'tls', 'rotate',
                        secret_uuid,
                        '-f',
                    ]
                    result = self.runner.invoke(command_args)
                    self.assertEqual(result.exit_code, 3, result.stdout)
                    self.assertEqual(
                        result.stdout,
                        u"Get a secret ({secret})\n"
                        u"error: You don't have an owner permission to the secret ({secret})\n".format(
                            secret=secret_uuid,
                        )
                    )
