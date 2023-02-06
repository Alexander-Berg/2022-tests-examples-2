# -*- coding: utf-8 -*-

import mock
from nose_parameterized import parameterized
from passport.backend.core.crypto.signing import SigningRegistry
from passport.backend.core.models.support_code import SupportCode
from passport.backend.core.serializers.ydb.support_code import (
    hash_support_code_value,
    SupportCodeRow,
)
from passport.backend.core.test.consts import TEST_UID1
from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.utils.time import unixtime_to_datetime


TEST_CODE1 = '123456'
TEST_SECRET_ID1 = b'1'
TEST_SECRET_ID2 = b'2'
TEST_UNIXTIME = 1425200524
TEST_DATETIME = unixtime_to_datetime(TEST_UNIXTIME)


class TestSupportCode(PassportTestCase):
    def setUp(self):
        super(TestSupportCode, self).setUp()
        fake_signing = mock.patch(
            'passport.backend.core.crypto.signing.urandom',
            return_value=b'',
        )
        self.__patches = [fake_signing]
        for patch in self.__patches:
            patch.start()

        self.setup_signing_registry()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        del self.__patches
        super(TestSupportCode, self).tearDown()

    def setup_signing_registry(self):
        self.signing_registry = SigningRegistry()
        self.signing_registry.add_from_dict(
            dict(
                versions=[
                    dict(
                        id=TEST_SECRET_ID1,
                        algorithm='SHA256',
                        salt_length=8,
                        secret=b'secret1'
                    ),
                    dict(
                        id=TEST_SECRET_ID2,
                        algorithm='SHA256',
                        salt_length=8,
                        secret=b'secret2'
                    ),
                ],
            ),
        )

    def build_support_code(self, uid=TEST_UID1, expires_at=TEST_DATETIME):
        return SupportCode(
            uid=uid,
            expires_at=expires_at,
            value=TEST_CODE1,
        )

    def test_from_support_code(self):
        support_code = self.build_support_code(uid=TEST_UID1, expires_at=TEST_DATETIME)
        secret = self.signing_registry.get(TEST_SECRET_ID1)
        row = SupportCodeRow.from_support_code(support_code, secret)

        self.assertEqual(row.uid, TEST_UID1)
        self.assertEqual(row.expires_at, TEST_DATETIME)

    @parameterized.expand(
        [
            (TEST_SECRET_ID1, b'5Z4Zm9s9BSsf/AxTUTr/b+OmZ0xMfg2mB6twQHVL/Gsx'),
            (TEST_SECRET_ID2, b'noBPmRZjw28y7iPrXsDiGfZ7rn5DxmHUs45Q26Vvnuoy'),
        ],
    )
    def test_secret_affects_code_hash(self, secret_id, code_hash):
        secret = self.signing_registry.get(secret_id)
        self.assertEqual(
            hash_support_code_value(TEST_CODE1, secret),
            code_hash,
        )

    @parameterized.expand(
        [
            (TEST_SECRET_ID1, 'MS4xMC58Xg8iHiDZFvv0dofIM6aOCvcjcZEB8k1f0ZQ278OYlA=='),
            (TEST_SECRET_ID2, 'MS4yMC6b6zhn4kFsf70Q1NLfE4RHR8D/KsI2+AtKeAwwWwaTDw=='),
        ],
    )
    def test_secret_affects_signature(self, secret_id, signature):
        support_code = self.build_support_code()
        support_code = SupportCodeRow(
            uid=support_code.uid,
            expires_at=support_code.expires_at,
            code_hash='',
            signature=None,
        )
        secret = self.signing_registry.get(secret_id)
        support_code.sign(secret)

        self.assertEqual(support_code.signature, signature)
