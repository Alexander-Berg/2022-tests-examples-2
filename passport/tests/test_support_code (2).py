# -*- coding: utf-8 -*-

from datetime import datetime
import json

import mock
from nose_parameterized import parameterized
from passport.backend.core.crypto.signing import (
    SigningRegistry,
    VersionNotFoundSigningError,
)
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.models.support_code import SupportCode
from passport.backend.core.serializers.ydb.public import to_ydb_rows
from passport.backend.core.serializers.ydb.support_code import (
    hash_support_code_value,
    SupportCodeRow,
    SupportCodeSerializerConfiguration,
)
from passport.backend.core.test.consts import (
    TEST_UID1,
    TEST_UID2,
)
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.core.ydb.exceptions import YdbTemporaryError
from passport.backend.core.ydb.faker.stubs import FakeResultSet
from passport.backend.core.ydb.faker.ydb import FakeYdb
from passport.backend.core.ydb.processors.support_code import (
    delete_support_codes_expired_before_timestamp,
    DeleteSupportCodesExpiredBeforeTimestampYdbQuery,
    find_support_code,
    FindSupportCodeYdbQuery,
    insert_support_code,
    InsertSupportCodeYdbQuery,
    SupportCodeExistsError,
)
import passport.backend.core.ydb_client as ydb
from passport.backend.utils.time import datetime_to_integer_unixtime


TEST_CODE1 = 'code1'
TEST_CODE2 = 'code2'
TEST_TIMESTAMP1 = datetime(2001, 1, 2, 23, 29, 59)
TEST_TIMESTAMP2 = datetime(2007, 5, 10, 7, 3, 14)
TEST_SECRET_ID1 = b'1'
TEST_SECRET_ID2 = b'2'
TEST_SECRET_ID3 = b'3'


class BaseSupportCodeTestCase(PassportTestCase):
    def setUp(self):
        super(BaseSupportCodeTestCase, self).setUp()

        self.fake_ydb = FakeYdb()

        fake_signing = mock.patch(
            'passport.backend.core.crypto.signing.urandom',
            return_value=b'',
        )

        self.__patches = [
            self.fake_ydb,
            fake_signing
        ]

        for patch in self.__patches:
            patch.start()

        self.signing_registry = SigningRegistry()
        self.signing_registry.add_from_dict(
            {
                'default_version_id': TEST_SECRET_ID2,
                'versions': [
                    {
                        'id':   TEST_SECRET_ID1,
                        'algorithm': 'SHA256',
                        'salt_length': 32,
                        'secret': b'secret1'
                    },
                    {
                        'id':   TEST_SECRET_ID2,
                        'algorithm': 'SHA256',
                        'salt_length': 32,
                        'secret': b'secret2'
                    },
                ],
            },
        )
        LazyLoader.register('YandexAndYandexTeamSigningRegistry', lambda: self.signing_registry)

    def tearDown(self):
        del self.signing_registry
        for patch in reversed(self.__patches):
            patch.stop()
        del self.__patches
        del self.fake_ydb
        super(BaseSupportCodeTestCase, self).tearDown()

    def build_support_code(
        self,
        uid=TEST_UID1,
        value=TEST_CODE1,
        expires_at=TEST_TIMESTAMP1,
    ):
        return SupportCode(
            uid=uid,
            value=value,
            expires_at=expires_at,
        )

    def build_cur_support_code_row(self, support_code=None):
        secret = self.signing_registry.get(TEST_SECRET_ID2)
        return self.build_support_code_row(secret, support_code)

    def build_old_support_code_row(self, support_code=None):
        secret = self.signing_registry.get(TEST_SECRET_ID1)
        return self.build_support_code_row(secret, support_code)

    def build_support_code_row(self, secret, support_code=None):
        if not support_code:
            support_code = self.build_support_code()
        row = SupportCodeRow.from_support_code(support_code, secret)
        value = json.dumps(
            dict(
                uid=support_code.uid,
                signature=row.signature,
            ),
        )
        return dict(
            code_hash=row.code_hash,
            expires_at=datetime_to_integer_unixtime(support_code.expires_at),
            value=value
        )

    def build_support_code_serializer_configuration(self):
        return SupportCodeSerializerConfiguration(
            signing_registry=self.signing_registry,
            old_secret=self.signing_registry.get(TEST_SECRET_ID1),
            cur_secret=self.signing_registry.get(TEST_SECRET_ID2),
        )

    def support_code_to_ydb_rows(self, support_code):
        return to_ydb_rows(support_code, self.build_support_code_serializer_configuration())

    def build_old_code_hash(self, support_code=None):
        secret = self.signing_registry.get(TEST_SECRET_ID1)
        return self.build_code_hash(secret, support_code)

    def build_cur_code_hash(self, support_code=None):
        secret = self.signing_registry.get(TEST_SECRET_ID2)
        return self.build_code_hash(secret, support_code)

    def build_code_hash(self, secret, support_code=None):
        if not support_code:
            support_code = self.build_support_code()
        return hash_support_code_value(support_code.value, secret)


@with_settings_hosts(
    YDB_SUPPORT_CODE_DATABASE='/support_code',
    YDB_SUPPORT_CODE_ENABLED=True,
    YDB_RETRIES=2,
)
class TestInsertSupportCode(BaseSupportCodeTestCase):
    @parameterized.expand(
        [
            (dict(uid=TEST_UID1),),
            (dict(uid=TEST_UID2),),
            (dict(value=TEST_CODE1),),
            (dict(value=TEST_CODE2),),
            (dict(expires_at=TEST_TIMESTAMP1),),
            (dict(expires_at=TEST_TIMESTAMP2),),
        ],
    )
    def test_support_code(self, kwargs):
        support_code = self.build_support_code(**kwargs)
        self.fake_ydb.set_execute_return_value([])

        insert_support_code(support_code)

        self.fake_ydb.assert_queries_executed(
            [
                InsertSupportCodeYdbQuery(
                    self.build_old_support_code_row(support_code),
                    self.build_cur_support_code_row(support_code),
                ),
            ],
        )

    def test_other_secret(self):
        self.fake_ydb.set_execute_return_value([])
        self.signing_registry.add_from_dict(
            {
                'default_version_id': TEST_SECRET_ID3,
                'versions': [
                    {
                        'id':   TEST_SECRET_ID3,
                        'algorithm': 'SHA256',
                        'salt_length': 32,
                        'secret': b'secret3'
                    },
                ],
            },
        )

        insert_support_code(self.build_support_code())

        self.fake_ydb.assert_queries_executed(
            [
                InsertSupportCodeYdbQuery(
                    self.build_support_code_row(self.signing_registry.get(TEST_SECRET_ID2)),
                    self.build_support_code_row(self.signing_registry.get(TEST_SECRET_ID3)),
                ),
            ],
        )

    def test_no_old_secret(self):
        self.signing_registry.set_default_version_id(TEST_SECRET_ID1)

        support_code = self.build_support_code()

        with self.assertRaises(VersionNotFoundSigningError):
            insert_support_code(support_code)

        self.fake_ydb.assert_queries_executed([])

    def test_ydb_timeout(self):
        self.fake_ydb.set_execute_side_effect(ydb.Timeout('timeout'))

        support_code = self.build_support_code()

        with self.assertRaises(YdbTemporaryError):
            insert_support_code(support_code)

        self.fake_ydb.assert_queries_executed(
            [
                InsertSupportCodeYdbQuery(
                    self.build_old_support_code_row(support_code),
                    self.build_cur_support_code_row(support_code),
                ),
            ],
        )

    def test_ydb_integrity_error(self):
        self.fake_ydb.set_execute_side_effect(ydb.PreconditionFailed('integrity_error'))

        support_code = self.build_support_code()

        with self.assertRaises(SupportCodeExistsError):
            insert_support_code(support_code)

        self.fake_ydb.assert_queries_executed(
            [
                InsertSupportCodeYdbQuery(
                    self.build_old_support_code_row(support_code),
                    self.build_cur_support_code_row(support_code),
                ),
            ],
        )


@with_settings_hosts(
    YDB_SUPPORT_CODE_DATABASE='/support_code',
    YDB_SUPPORT_CODE_ENABLED=True,
    YDB_RETRIES=2,
)
class TestFindSupportCode(BaseSupportCodeTestCase):
    @parameterized.expand(
        [
            (TEST_CODE1,),
            (TEST_CODE2,),
        ],
    )
    def test_code(self, code):
        old_support_code = self.build_support_code(value=code)
        self.fake_ydb.set_execute_side_effect(
            [
                [FakeResultSet(self.support_code_to_ydb_rows(old_support_code))],
            ],
        )

        new_support_code = find_support_code(code)

        self.assertEqual(new_support_code, old_support_code)
        self.fake_ydb.assert_queries_executed(
            [
                FindSupportCodeYdbQuery(
                    self.build_cur_code_hash(old_support_code),
                    self.build_old_code_hash(old_support_code),
                ),
            ],
        )

    def test_other_secret(self):
        self.signing_registry.add_from_dict(
            {
                'default_version_id': TEST_SECRET_ID3,
                'versions': [
                    {
                        'id':   TEST_SECRET_ID3,
                        'algorithm': 'SHA256',
                        'salt_length': 32,
                        'secret': b'secret3'
                    },
                ],
            },
        )
        old_support_code = self.build_support_code(value=TEST_CODE1)
        self.fake_ydb.set_execute_side_effect(
            [
                [FakeResultSet(self.support_code_to_ydb_rows(old_support_code))],
            ],
        )

        new_support_code = find_support_code(TEST_CODE1)

        self.assertEqual(new_support_code, old_support_code)
        self.fake_ydb.assert_queries_executed(
            [
                FindSupportCodeYdbQuery(
                    self.build_code_hash(self.signing_registry.get(TEST_SECRET_ID3), old_support_code),
                    self.build_code_hash(self.signing_registry.get(TEST_SECRET_ID2), old_support_code),
                ),
            ],
        )

    def test_unknown_secret(self):
        old_support_code = self.build_support_code(value=TEST_CODE1)
        self.fake_ydb.set_execute_side_effect(
            [
                [FakeResultSet(self.support_code_to_ydb_rows(old_support_code))],
            ],
        )
        self.signing_registry.add_from_dict(
            {
                'default_version_id': TEST_SECRET_ID3,
                'versions': [
                    {
                        'id':   TEST_SECRET_ID3,
                        'algorithm': 'SHA256',
                        'salt_length': 32,
                        'secret': b'secret3'
                    },
                ],
            },
        )
        self.signing_registry.remove(TEST_SECRET_ID1)

        new_support_code = find_support_code(TEST_CODE1)

        assert new_support_code is None

    def test_ydb_timeout(self):
        self.fake_ydb.set_execute_side_effect(ydb.Timeout('timeout'))

        old_support_code = self.build_support_code(value=TEST_CODE1)

        with self.assertRaises(YdbTemporaryError):
            find_support_code(TEST_CODE1)

        self.fake_ydb.assert_queries_executed(
            [
                FindSupportCodeYdbQuery(
                    self.build_cur_code_hash(old_support_code),
                    self.build_old_code_hash(old_support_code),
                ),
            ],
        )

    def test_not_found(self):
        self.fake_ydb.set_execute_side_effect([[FakeResultSet([])]])
        support_code = find_support_code(TEST_CODE1)
        assert support_code is None

    def test_single_row(self):
        old_support_code = self.build_support_code(value=TEST_CODE1)

        self.fake_ydb.set_execute_side_effect(
            [
                [FakeResultSet(self.support_code_to_ydb_rows(old_support_code)[:1])],
            ],
        )

        new_support_code = find_support_code(TEST_CODE1)

        assert new_support_code is None

    def test_invalid_signature(self):
        old_support_code = self.build_support_code(value=TEST_CODE1)
        self.fake_ydb.set_execute_side_effect(
            [
                [FakeResultSet(self.support_code_to_ydb_rows(old_support_code))],
            ],
        )
        self.signing_registry.add_from_dict(
            {
                'versions': [
                    {
                        'id':   TEST_SECRET_ID1,
                        'algorithm': 'SHA256',
                        'salt_length': 32,
                        'secret': b'newsecret'
                    },
                ],
            },
        )

        new_support_code = find_support_code(TEST_CODE1)

        assert new_support_code is None

    def test_uids_mismatch(self):
        support_code1 = self.build_support_code(value=TEST_CODE1, uid=TEST_UID1)
        support_code2 = self.build_support_code(value=TEST_CODE1, uid=TEST_UID2)
        row1 = self.support_code_to_ydb_rows(support_code1)[0]
        row2 = self.support_code_to_ydb_rows(support_code2)[1]
        self.fake_ydb.set_execute_side_effect(
            [
                [FakeResultSet([row1, row2])],
            ],
        )

        new_support_code = find_support_code(TEST_CODE1)

        assert new_support_code is None

    def test_expires_at_mismatch(self):
        self.fake_ydb.set_execute_return_value([])
        support_code1 = self.build_support_code(value=TEST_CODE1, expires_at=TEST_TIMESTAMP1)
        support_code2 = self.build_support_code(value=TEST_CODE1, expires_at=TEST_TIMESTAMP2)
        row1 = self.support_code_to_ydb_rows(support_code1)[0]
        row2 = self.support_code_to_ydb_rows(support_code2)[1]
        self.fake_ydb.set_execute_side_effect(
            [
                [FakeResultSet([row1, row2])],
            ],
        )

        new_support_code = find_support_code(TEST_CODE1)

        assert new_support_code is None


@with_settings_hosts(
    YDB_SUPPORT_CODE_DATABASE='/support_code',
    YDB_SUPPORT_CODE_ENABLED=True,
    YDB_RETRIES=2,
)
class TestDeleteSupportCodesExpiredBeforeTimestamp(BaseSupportCodeTestCase):
    @parameterized.expand(
        [
            (TEST_TIMESTAMP1,),
            (TEST_TIMESTAMP2,),
        ],
    )
    def test_timestamp(self, timestamp):
        self.fake_ydb.set_execute_return_value([])
        delete_support_codes_expired_before_timestamp(timestamp)

        self.fake_ydb.assert_queries_executed(
            [
                DeleteSupportCodesExpiredBeforeTimestampYdbQuery(
                    datetime_to_integer_unixtime(timestamp),
                ),
            ],
        )

    def test_ydb_timeout(self):
        self.fake_ydb.set_execute_side_effect(ydb.Timeout('timeout'))

        with self.assertRaises(YdbTemporaryError):
            delete_support_codes_expired_before_timestamp(TEST_TIMESTAMP1)

        self.fake_ydb.assert_queries_executed(
            [
                DeleteSupportCodesExpiredBeforeTimestampYdbQuery(
                    datetime_to_integer_unixtime(TEST_TIMESTAMP1),
                ),
            ],
        )
