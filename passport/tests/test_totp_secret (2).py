# -*- coding: utf-8 -*-

import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.db.faker.db import (
    attribute_table_insert_on_duplicate_increment_key as at_increment_odk,
    attribute_table_insert_on_duplicate_update_key as at_insert_odk,
    totp_secret_id_table_insert,
)
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import attributes_table as at
from passport.backend.core.differ import diff
from passport.backend.core.eav_type_mapping import ATTRIBUTE_NAME_TO_TYPE as AT
from passport.backend.core.models.account import Account
from passport.backend.core.models.totp_secret import (
    TotpSecret,
    TotpSecretAutoId,
)
from passport.backend.core.serializers.eav.totp_secret import (
    totp_secret_processor,
    TotpSecretAutoIdEavSerializer,
    TotpSecretEavSerializer,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.types.totp_secret import TotpSecretType
from sqlalchemy.sql.expression import and_


class TestCreateTotpSecret(unittest.TestCase):
    def test_empty(self):
        acc = Account(uid=123)
        secret = TotpSecret(acc)

        queries = TotpSecretEavSerializer().serialize(None, secret, diff(None, secret))
        eq_eav_queries(queries, [])

    def test_create(self):
        acc = Account(uid=123).parse({'login': 'login'})
        secret = TotpSecret(acc)
        secret.set(TotpSecretType('secret'))

        queries = list(TotpSecretEavSerializer().serialize(None, secret, diff(None, secret)))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['account.totp.secret'], 'value': b'secret'},
                    {'uid': 123, 'type': AT['account.totp.update_datetime'], 'value': TimeNow()},
                ]),
            ],
        )

    def test_all_fields(self):
        acc = Account(uid=123)
        secret = TotpSecret(acc)
        secret.set(TotpSecretType('secret'))
        secret.check_time = 111
        secret.failed_pin_checks_count = 1
        secret.yakey_device_ids = ['d1', 'd2']

        queries = list(TotpSecretEavSerializer().serialize(None, secret, diff(None, secret)))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['account.totp.secret'], 'value': b'secret'},
                    {'uid': 123, 'type': AT['account.totp.update_datetime'], 'value': TimeNow()},
                    {'uid': 123, 'type': AT['account.totp.check_time'], 'value': b'111'},
                    {'uid': 123, 'type': AT['account.totp.failed_pin_checks_count'], 'value': b'1'},
                    {'uid': 123, 'type': AT['account.totp.yakey_device_ids'], 'value': b'd1,d2'},
                ]),
            ],
        )


class TestChangeTotpSecret(unittest.TestCase):
    def test_unchanged(self):
        acc = Account(uid=123)
        secret = TotpSecret(acc)

        s1 = secret.snapshot()
        queries = TotpSecretEavSerializer().serialize(s1, secret, diff(s1, secret))
        eq_eav_queries(queries, [])

    def test_change_all_fields(self):
        acc = Account(uid=123).parse({'login': 'login'})
        secret = TotpSecret(acc)

        secret.set(TotpSecretType('secret'))
        secret.check_time = 1
        secret.failed_pin_checks_count = 1
        secret.yakey_device_ids = ['d1', 'd2']

        s1 = secret.snapshot()

        secret.totp_secret = TotpSecretType('new_secret')
        secret.check_time = 111
        secret.failed_pin_checks_count = 2
        secret.yakey_device_ids = ['d2', 'd3']

        queries = list(TotpSecretEavSerializer().serialize(s1, secret, diff(s1, secret)))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['account.totp.secret'], 'value': b'new_secret'},
                    {'uid': 123, 'type': AT['account.totp.check_time'], 'value': b'111'},
                    {'uid': 123, 'type': AT['account.totp.yakey_device_ids'], 'value': b'd2,d3'},
                ]),
                at_increment_odk().values([
                    {'uid': 123, 'type': AT['account.totp.failed_pin_checks_count'], 'value': b'2'},
                ]),
            ],
        )

    def test_update_failed_pin_checks_count_set_initial_value(self):
        acc = Account(uid=123)
        secret = TotpSecret(acc)

        secret.set(TotpSecretType('secret'))

        s1 = secret.snapshot()

        secret.failed_pin_checks_count = 1

        queries = list(TotpSecretEavSerializer().serialize(s1, secret, diff(s1, secret)))

        eq_eav_queries(queries, [
            at_insert_odk().values([{
                'uid': 123, 'type': AT['account.totp.failed_pin_checks_count'], 'value': b'1',
            }]),
        ])

    def test_update_failed_pin_checks_count_increment_value(self):
        acc = Account(uid=123)
        secret = TotpSecret(acc)

        secret.set(TotpSecretType('secret'))
        secret.failed_pin_checks_count = 2

        s1 = secret.snapshot()

        secret.failed_pin_checks_count = 3

        queries = list(TotpSecretEavSerializer().serialize(s1, secret, diff(s1, secret)))

        eq_eav_queries(queries, [
            at_increment_odk().values([{
                'uid': 123, 'type': AT['account.totp.failed_pin_checks_count'], 'value': b'3',
            }]),
        ])

    def test_update_failed_pin_checks_count_no_increment(self):
        acc = Account(uid=123)
        secret = TotpSecret(acc)

        secret.set(TotpSecretType('secret'))
        secret.failed_pin_checks_count = 2

        s1 = secret.snapshot()

        secret.failed_pin_checks_count = 4

        queries = list(TotpSecretEavSerializer().serialize(s1, secret, diff(s1, secret)))

        eq_eav_queries(queries, [
            at_insert_odk().values([{
                'uid': 123, 'type': AT['account.totp.failed_pin_checks_count'], 'value': b'4',
            }]),
        ])

    def test_account_delete_failed_pin_checks_count(self):
        acc = Account(uid=123).parse({'totp.failed_pin_checks_count': 10})
        secret = TotpSecret(acc)

        s1 = secret.snapshot()
        secret.failed_pin_checks_count = None

        queries = list(TotpSecretEavSerializer().serialize(s1, secret, diff(s1, secret)))
        eq_eav_queries(queries, [
            at.delete().where(
                and_(
                    at.c.uid == 123,
                    at.c.type.in_([AT['account.totp.failed_pin_checks_count']]),
                ),
            ),
        ])

        # проверим, что установка в 0 так же стирает атрибут
        # кажется нас устраивает такое поведение для счетчика
        secret.failed_pin_checks_count = 5
        s1 = secret.snapshot()
        secret.failed_pin_checks_count = 0

        queries = list(TotpSecretEavSerializer().serialize(s1, secret, diff(s1, secret)))
        eq_eav_queries(queries, [
            at.delete().where(
                and_(
                    at.c.uid == 123,
                    at.c.type.in_([AT['account.totp.failed_pin_checks_count']]),
                ),
            ),
        ])

    def test_delete(self):
        acc = Account(uid=123)
        secret = TotpSecret(acc, totp_secret='secret')

        s1 = secret.snapshot()
        queries = TotpSecretEavSerializer().serialize(s1, None, diff(s1, None))

        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == 123,
                        at.c.type.in_(
                            sorted([
                                AT['account.totp.secret'],
                                AT['account.totp.check_time'],
                                AT['account.totp.update_datetime'],
                                AT['account.totp.failed_pin_checks_count'],
                                AT['account.totp.yakey_device_ids'],
                            ]),
                        ),
                    ),
                ),
            ],
        )


class TestTotpSecretProcessor(unittest.TestCase):
    def test(self):
        secret = mock.Mock()
        secret.encrypted_pin_and_secret = '123'
        eq_(totp_secret_processor(secret), '123')


class TestTotpSecretAutoId(unittest.TestCase):
    def test_create(self):
        auto_id = TotpSecretAutoId()

        queries = TotpSecretAutoIdEavSerializer().serialize(None, auto_id, diff(None, auto_id))
        eq_eav_queries(
            queries,
            [
                totp_secret_id_table_insert(),
            ],
            inserted_keys=[1],
        )

    def test_change(self):
        auto_id = TotpSecretAutoId()
        with assert_raises(ValueError):
            TotpSecretAutoIdEavSerializer().serialize(auto_id, auto_id, diff(auto_id, auto_id))

    def test_delete(self):
        auto_id = TotpSecretAutoId()
        with assert_raises(ValueError):
            TotpSecretAutoIdEavSerializer().serialize(auto_id, None, diff(auto_id, None))
