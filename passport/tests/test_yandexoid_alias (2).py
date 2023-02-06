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
from passport.backend.core.models.alias import YandexoidAlias
from passport.backend.core.serializers.eav.alias import YandexoidAliasEavSerializer
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import and_


class TestCreateYandexoidAlias(unittest.TestCase):
    def test_empty(self):
        acc = Account(uid=123)
        alias = YandexoidAlias(acc)

        queries = YandexoidAliasEavSerializer().serialize(None, alias, diff(None, alias))
        eq_eav_queries(queries, [])

    def test_yandexoid_alias(self):
        acc = Account(uid=123)
        alias = YandexoidAlias(acc, login='L-o.gin.login')

        queries = YandexoidAliasEavSerializer().serialize(None, alias, diff(None, alias))

        eq_eav_queries(queries, [
            aliases_insert().values(
                uid=123,
                type=ALT['yandexoid'],
                value=b'l-o.gin.login',
                surrogate_type=str(ALT['yandexoid']).encode('utf8'),
            ),
        ])


class TestChangeYandexoidAlias(unittest.TestCase):
    def test_unchanged(self):
        acc = Account(uid=123)
        alias = YandexoidAlias(acc, login='login')

        s1 = alias.snapshot()

        queries = YandexoidAliasEavSerializer().serialize(s1, alias, diff(s1, alias))
        eq_eav_queries(queries, [])

    @raises(ValueError)
    def test_update_yandexoid(self):
        acc = Account(uid=123)
        alias = YandexoidAlias(acc, login='login')

        s1 = alias.snapshot()

        alias = YandexoidAlias(acc, login='login2')
        list(YandexoidAliasEavSerializer().serialize(s1, alias, diff(s1, alias)))


class TestDeleteYandexoidAlias(unittest.TestCase):
    def test_delete(self):
        acc = Account(uid=123)
        alias = YandexoidAlias(acc, login='login')

        s1 = alias.snapshot()

        queries = YandexoidAliasEavSerializer().serialize(s1, None, diff(s1, None))

        eq_eav_queries(queries, [
            insert_ignore_into_removed_aliases(
                select([alt.c.uid, alt.c.type, alt.c.value]).where(
                    and_(alt.c.uid == 123, alt.c.type.in_([ALT['yandexoid']]))
                ),
            ),
            alt.delete().where(
                and_(alt.c.uid == 123, alt.c.type.in_([ALT['yandexoid']])),
            ),
        ])
