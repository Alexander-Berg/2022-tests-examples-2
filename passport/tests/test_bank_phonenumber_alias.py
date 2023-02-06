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
from passport.backend.core.models.alias import BankPhoneNumberAlias
from passport.backend.core.serializers.eav.alias import BankPhoneNumberAliasEavSerializer
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import and_


class TestCreateBankPhoneNumberAlias(unittest.TestCase):
    def test_empty(self):
        acc = Account(uid=123)
        alias = BankPhoneNumberAlias(acc)

        queries = BankPhoneNumberAliasEavSerializer().serialize(None, alias, diff(None, alias))
        eq_eav_queries(queries, [])

    def test_create(self):
        acc = Account(uid=123)
        alias = BankPhoneNumberAlias(acc, alias='79161234567')

        queries = BankPhoneNumberAliasEavSerializer().serialize(None, alias, diff(None, alias))
        eq_eav_queries(queries, [
            aliases_insert().values(
                uid=123,
                type=ALT['bank_phonenumber'],
                value=b'79161234567',
                surrogate_type=str(ALT['bank_phonenumber']).encode('utf8'),
            ),
        ])


class TestChangeBankPhoneNumberAlias(unittest.TestCase):
    def test_unchanged(self):
        acc = Account(uid=123)
        alias = BankPhoneNumberAlias(acc, alias='79161234567')

        s1 = alias.snapshot()

        queries = BankPhoneNumberAliasEavSerializer().serialize(s1, alias, diff(s1, alias))
        eq_eav_queries(queries, [])

    @raises(ValueError)
    def test_update_alias(self):
        acc = Account(uid=123)
        alias = BankPhoneNumberAlias(acc, alias='79161234567')
        s1 = alias.snapshot()

        alias.alias = BankPhoneNumberAlias(acc, alias='79261234567')
        list(BankPhoneNumberAliasEavSerializer().serialize(s1, alias, diff(s1, alias)))


class TestDeleteBankPhoneNumberAlias(unittest.TestCase):
    def test_delete(self):
        acc = Account(uid=123)
        alias = BankPhoneNumberAlias(acc, alias='+79161234567')

        s1 = alias.snapshot()

        queries = BankPhoneNumberAliasEavSerializer().serialize(s1, None, diff(s1, None))
        eq_eav_queries(queries, [
            insert_ignore_into_removed_aliases(
                select([alt.c.uid, alt.c.type, alt.c.value]).where(
                    and_(alt.c.uid == 123, alt.c.type.in_([ALT['bank_phonenumber']]))
                )
            ),
            alt.delete().where(
                and_(
                    alt.c.uid == 123,
                    alt.c.type.in_([ALT['bank_phonenumber']]),
                ),
            ),
        ])
