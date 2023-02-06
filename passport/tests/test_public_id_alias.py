# -*- coding: utf-8 -*-
import unittest

from passport.backend.core.db.faker.db import insert_ignore_into_removed_aliases
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import (
    aliases_table as at,
    removed_aliases_table as rat,
)
from passport.backend.core.db.utils import with_ignore_prefix
from passport.backend.core.differ import diff
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ALT
from passport.backend.core.models.account import Account
from passport.backend.core.models.alias import PublicIdAlias
from passport.backend.core.serializers.eav.alias import PublicIdAliasEavSerializer
from passport.backend.core.test.consts import TEST_UID
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import and_


class TestCreatePublicIdAlias(unittest.TestCase):
    def test_empty(self):
        acc = Account(uid=TEST_UID)
        alias = PublicIdAlias(acc)

        queries = PublicIdAliasEavSerializer().serialize(None, alias, diff(None, alias))
        eq_eav_queries(queries, [])

    def test_create(self):
        acc = Account(uid=TEST_UID)
        alias = PublicIdAlias(acc, alias='public_id-1')

        queries = PublicIdAliasEavSerializer().serialize(None, alias, diff(None, alias))

        eq_eav_queries(queries, [
            at.insert().values(
                uid=TEST_UID,
                type=ALT['public_id'],
                value=b'public_id-1',
                surrogate_type=str(ALT['public_id']).encode('utf8'),
            ),
        ])


class TestChangePublicIdAlias(unittest.TestCase):
    def test_unchanged(self):
        acc = Account(uid=TEST_UID)
        alias = PublicIdAlias(acc, alias='public_id-1')

        s1 = alias.snapshot()

        queries = PublicIdAliasEavSerializer().serialize(s1, alias, diff(s1, alias))
        eq_eav_queries(queries, [])

    def test_update(self):
        acc = Account(uid=TEST_UID)
        alias = PublicIdAlias(acc, alias='public_id-1')

        s1 = alias.snapshot()
        alias = PublicIdAlias(acc, alias='public_id-2')

        queries = PublicIdAliasEavSerializer().serialize(s1, alias, diff(s1, alias))
        eq_eav_queries(queries, [
            insert_ignore_into_removed_aliases(
                select([at.c.uid, at.c.type, at.c.value]).where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type.in_([ALT['public_id']]),
                    ),
                ),
            ),
            at.update().values(value=b'public_id-2').where(
                and_(
                    at.c.uid == TEST_UID,
                    at.c.type == ALT['public_id'],
                    at.c.surrogate_type == str(ALT['public_id']).encode('utf-8'),
                ),
            ),
        ])


class TestDeletePublicIdAlias(unittest.TestCase):
    def test_delete(self):
        acc = Account(uid=TEST_UID)
        alias = PublicIdAlias(acc, alias='public_id-1')

        s1 = alias.snapshot()

        list(PublicIdAliasEavSerializer().serialize(s1, None, diff(s1, None)))


class TestOldPublicIds(unittest.TestCase):
    def setUp(self):
        self.acc = Account(uid=TEST_UID)
        self.acc.public_id_alias = PublicIdAlias(self.acc, alias='public_id-1').parse({
            'aliases': {
                str(ALT['old_public_id']): [],
            },
        })

    def test_add_old_public_ids(self):
        s1 = self.acc.public_id_alias.snapshot()
        self.acc.public_id_alias.add_old_public_id('test1')
        self.acc.public_id_alias.add_old_public_id('TesT2')

        queries = PublicIdAliasEavSerializer().serialize(
            s1,
            self.acc.public_id_alias,
            diff(s1, self.acc.public_id_alias),
        )

        eq_eav_queries(
            queries,
            [
                at.insert().values(
                    uid=TEST_UID,
                    type=ALT['old_public_id'],
                    value=b'test1',
                    surrogate_type=b'20-test1',
                ),
                at.insert().values(
                    uid=TEST_UID,
                    type=ALT['old_public_id'],
                    value=b'test2',
                    surrogate_type=b'20-test2',
                ),
            ],
        )

    def test_no_operations_needed(self):
        s1 = self.acc.public_id_alias.snapshot()

        self.acc.public_id_alias.add_old_public_id('test1')
        self.acc.public_id_alias.remove_old_public_id('test1')

        queries = PublicIdAliasEavSerializer().serialize(
            s1,
            self.acc.public_id_alias,
            diff(s1, self.acc.public_id_alias),
        )
        eq_eav_queries(
            queries,
            [],
        )

    def test_remove_old_public_id(self):
        self.acc.public_id_alias.add_old_public_id('test1')
        self.acc.public_id_alias.add_old_public_id('test2')

        s1 = self.acc.public_id_alias.snapshot()
        self.acc.public_id_alias.remove_old_public_id('test2')

        queries = PublicIdAliasEavSerializer().serialize(
            s1,
            self.acc.public_id_alias,
            diff(s1, self.acc.public_id_alias),
        )
        eq_eav_queries(
            queries,
            [
                with_ignore_prefix(
                    rat.insert().values(
                        uid=TEST_UID,
                        type=ALT['old_public_id'],
                        value=b'test2',
                    ),
                ),
                at.delete().where(
                    and_(
                        at.c.uid == TEST_UID,
                        at.c.type == ALT['old_public_id'],
                        at.c.value == b'test2',
                    ),
                ),
            ],
        )
