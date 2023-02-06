# -*- coding: utf-8 -*-

import unittest

from passport.backend.core.db.faker.db import attribute_table_insert_on_duplicate_update_key as at_insert_odk
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import attributes_table as at
from passport.backend.core.differ import diff
from passport.backend.core.eav_type_mapping import ATTRIBUTE_NAME_TO_TYPE as AT
from passport.backend.core.models.account import Account
from passport.backend.core.models.rfc_totp_secret import RfcTotpSecret
from passport.backend.core.serializers.eav.rfc_totp_secret import RfcTotpSecretEavSerializer
from passport.backend.core.types.rfc_totp_secret import RfcTotpSecretType
from sqlalchemy.sql.expression import and_


TEST_SECRET = b'\x0c\x40\x03\x04\x41\x05'
TEST_ENCRYPTED_SECRET = b'1:DEADBEEF'


class TestCreateRfcTotpSecret(unittest.TestCase):
    def test_empty(self):
        acc = Account(uid=123)
        secret = RfcTotpSecret(acc)

        queries = RfcTotpSecretEavSerializer().serialize(None, secret, diff(None, secret))
        eq_eav_queries(queries, [])

    def test_create(self):
        acc = Account(uid=123).parse({'login': 'login'})
        secret = RfcTotpSecret(acc)
        secret.set(RfcTotpSecretType(TEST_SECRET))

        queries = list(RfcTotpSecretEavSerializer().serialize(None, secret, diff(None, secret)))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['account.rfc_totp.secret'], 'value': TEST_ENCRYPTED_SECRET},
                ]),
            ],
        )

    def test_all_fields(self):
        acc = Account(uid=123)
        secret = RfcTotpSecret(acc)
        secret.set(RfcTotpSecretType(TEST_SECRET))
        secret.check_time = 111

        queries = list(RfcTotpSecretEavSerializer().serialize(None, secret, diff(None, secret)))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['account.rfc_totp.secret'], 'value': TEST_ENCRYPTED_SECRET},
                    {'uid': 123, 'type': AT['account.rfc_totp.check_time'], 'value': b'111'},
                ]),
            ],
        )


class TestChangeRfcTotpSecret(unittest.TestCase):
    def test_unchanged(self):
        acc = Account(uid=123)
        secret = RfcTotpSecret(acc)

        s1 = secret.snapshot()
        queries = RfcTotpSecretEavSerializer().serialize(s1, secret, diff(s1, secret))
        eq_eav_queries(queries, [])

    def test_change_all_fields(self):
        acc = Account(uid=123).parse({'login': 'login'})
        secret = RfcTotpSecret(acc)

        secret.set(RfcTotpSecretType(b'foo'))
        secret.check_time = 1

        s1 = secret.snapshot()

        secret.totp_secret = RfcTotpSecretType(TEST_SECRET)
        secret.check_time = 111

        queries = list(RfcTotpSecretEavSerializer().serialize(s1, secret, diff(s1, secret)))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['account.rfc_totp.secret'], 'value': TEST_ENCRYPTED_SECRET},
                    {'uid': 123, 'type': AT['account.rfc_totp.check_time'], 'value': b'111'},
                ]),
            ],
        )

    def test_delete(self):
        acc = Account(uid=123)
        secret = RfcTotpSecret(acc, totp_secret=TEST_SECRET)

        s1 = secret.snapshot()
        queries = RfcTotpSecretEavSerializer().serialize(s1, None, diff(s1, None))

        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == 123,
                        at.c.type.in_(
                            sorted([
                                AT['account.rfc_totp.secret'],
                                AT['account.rfc_totp.check_time'],
                            ]),
                        ),
                    ),
                ),
            ],
        )
