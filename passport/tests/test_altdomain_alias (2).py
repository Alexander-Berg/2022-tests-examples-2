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
from passport.backend.core.models.alias import AltDomainAlias
from passport.backend.core.serializers.eav.alias import AltDomainAliasEavSerializer
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import and_


class TestCreateAltDomainAlias(unittest.TestCase):
    def test_empty(self):
        acc = Account(uid=123)
        alias = AltDomainAlias(acc)

        queries = AltDomainAliasEavSerializer().serialize(None, alias, diff(None, alias))
        eq_eav_queries(queries, [])

    def test_create(self):
        acc = Account(uid=123)
        alias = AltDomainAlias(acc, login='login.login@galatasaray.net')

        queries = AltDomainAliasEavSerializer().serialize(None, alias, diff(None, alias))
        eq_eav_queries(queries, [
            aliases_insert().values(
                uid=123,
                type=ALT['altdomain'],
                value=b'1/login-login',
                surrogate_type=str(ALT['altdomain']).encode('utf8'),
            ),
        ])

    def test_create_cyrillic(self):
        acc = Account(uid=123)
        alias = AltDomainAlias(acc, login=u'логин@kinopoisk.ru')

        queries = AltDomainAliasEavSerializer().serialize(None, alias, diff(None, alias))
        eq_eav_queries(queries, [
            aliases_insert().values(
                uid=123,
                type=ALT['altdomain'],
                value=b'2/\xd0\xbb\xd0\xbe\xd0\xb3\xd0\xb8\xd0\xbd',
                surrogate_type=str(ALT['altdomain']).encode('utf8'),
            ),
            # подписка в данном случае не создается
        ])


class TestChangeAltDomainAlias(unittest.TestCase):
    def test_unchanged(self):
        acc = Account(uid=123)
        alias = AltDomainAlias(acc, login='login@galatasaray.net')

        s1 = alias.snapshot()

        queries = AltDomainAliasEavSerializer().serialize(s1, alias, diff(s1, alias))
        eq_eav_queries(queries, [])

    @raises(ValueError)
    def test_update_login(self):
        acc = Account(uid=123)
        alias = AltDomainAlias(acc, login='login@kinopoisk.ru')

        s1 = alias.snapshot()

        alias.login = AltDomainAlias(acc, login='login2')
        list(AltDomainAliasEavSerializer().serialize(s1, alias, diff(s1, alias)))


class TestDeleteAltDomainAlias(unittest.TestCase):
    def test_delete(self):
        acc = Account(uid=123)
        alias = AltDomainAlias(acc, login='login@galatasaray.net')

        s1 = alias.snapshot()

        queries = AltDomainAliasEavSerializer().serialize(s1, None, diff(s1, None))
        eq_eav_queries(queries, [
            insert_ignore_into_removed_aliases(
                select([alt.c.uid, alt.c.type, alt.c.value]).where(
                    and_(alt.c.uid == 123, alt.c.type.in_([ALT['altdomain']]))
                )
            ),
            alt.delete().where(
                and_(
                    alt.c.uid == 123,
                    alt.c.type.in_([ALT['altdomain']]),
                ),
            ),
        ])
