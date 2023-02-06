# -*- coding: utf-8 -*-
import unittest

from nose.tools import raises
from passport.backend.core.db.faker.db import (
    aliases_insert,
    insert_ignore_into_removed_aliases,
)
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import aliases_table as alt
from passport.backend.core.differ import diff
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ALT
from passport.backend.core.models.account import Account
from passport.backend.core.models.alias import MailishAlias
from passport.backend.core.serializers.eav.alias import MailishAliasEavSerializer
from passport.backend.core.test.consts import TEST_UID
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import and_


class TestCreateMailishAlias(unittest.TestCase):
    def test_empty(self):
        acc = Account(uid=TEST_UID)
        alias = MailishAlias(acc)

        queries = MailishAliasEavSerializer().serialize(None, alias, diff(None, alias))
        eq_eav_queries(queries, [])

    def test_create(self):
        acc = Account(uid=TEST_UID)
        alias = MailishAlias(acc, mailish_id='Test-Id')

        queries = MailishAliasEavSerializer().serialize(None, alias, diff(None, alias))

        eq_eav_queries(queries, [
            aliases_insert().values(
                uid=TEST_UID,
                type=ALT['mailish'],
                value=b'test-id',
                surrogate_type=str(ALT['mailish']).encode('utf8'),
            ),
        ])


class TestChangeMailishAlias(unittest.TestCase):
    def test_unchanged(self):
        acc = Account(uid=TEST_UID)
        alias = MailishAlias(acc, mailish_id='Test-Id')

        s1 = alias.snapshot()

        queries = MailishAliasEavSerializer().serialize(s1, alias, diff(s1, alias))
        eq_eav_queries(queries, [])

    def test_update(self):
        acc = Account(uid=TEST_UID)
        alias = MailishAlias(acc, mailish_id='Test-Id')

        s1 = alias.snapshot()

        alias = MailishAlias(acc, mailish_id='Test-Another-Id')

        queries = MailishAliasEavSerializer().serialize(s1, alias, diff(s1, alias))
        eq_eav_queries(queries, [
            insert_ignore_into_removed_aliases(
                select([alt.c.uid, alt.c.type, alt.c.value]).where(
                    and_(
                        alt.c.uid == TEST_UID,
                        alt.c.type.in_([ALT['mailish']]),
                    ),
                ),
            ),
            alt.update().values(value=b'test-another-id').where(
                and_(
                    alt.c.uid == TEST_UID,
                    alt.c.type == ALT['mailish'],
                    alt.c.surrogate_type == str(ALT['mailish']).encode('utf-8'),
                ),
            ),
        ])


class TestDeleteMailishAlias(unittest.TestCase):
    @raises(ValueError)
    def test_delete(self):
        acc = Account(uid=TEST_UID)
        alias = MailishAlias(acc, mailish_id='Test-Id')

        s1 = alias.snapshot()

        list(MailishAliasEavSerializer().serialize(s1, None, diff(s1, None)))
