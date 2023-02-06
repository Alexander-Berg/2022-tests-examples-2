# -*- coding: utf-8 -*-

import unittest

from nose.tools import assert_raises
from passport.backend.core.db.faker.db import passman_recovery_key_insert
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.differ import diff
from passport.backend.core.models.account import Account
from passport.backend.core.models.passman_recovery_key import PassManRecoveryKey
from passport.backend.core.serializers.eav.passman_recovery_key import PassManRecoveryKeySerializer

from .test_query import (
    TEST_PASSMAN_KEY_ID,
    TEST_PASSMAN_RECOVERY_KEY,
    TEST_UID,
)


class TestPassManRecoveryKeySerializer(unittest.TestCase):

    def test_create(self):
        acc = Account(uid=TEST_UID).parse({'login': 'login'})
        recovery_key = PassManRecoveryKey(acc, key_id=TEST_PASSMAN_KEY_ID, recovery_key=TEST_PASSMAN_RECOVERY_KEY)

        queries = PassManRecoveryKeySerializer().serialize(None, recovery_key, diff(None, recovery_key))
        eq_eav_queries(
            queries,
            [
                passman_recovery_key_insert().values([
                    {
                        'uid': TEST_UID,
                        'key_id': TEST_PASSMAN_KEY_ID,
                        'recovery_key': TEST_PASSMAN_RECOVERY_KEY,
                    },
                ]),
            ],
        )

    def test_delete_forbidden(self):
        acc = Account(uid=TEST_UID).parse({'login': 'login'})
        recovery_key = PassManRecoveryKey(acc, key_id=TEST_PASSMAN_KEY_ID, recovery_key=TEST_PASSMAN_RECOVERY_KEY)

        with assert_raises(ValueError):
            PassManRecoveryKeySerializer().serialize(recovery_key, None, diff(recovery_key, None))

    def test_change_forbidden(self):
        acc = Account(uid=TEST_UID).parse({'login': 'login'})
        recovery_key = PassManRecoveryKey(acc, key_id=TEST_PASSMAN_KEY_ID, recovery_key=TEST_PASSMAN_RECOVERY_KEY)
        s1 = recovery_key.snapshot()

        recovery_key.key_id = '123'

        with assert_raises(ValueError):
            PassManRecoveryKeySerializer().serialize(s1, recovery_key, diff(s1, recovery_key))
