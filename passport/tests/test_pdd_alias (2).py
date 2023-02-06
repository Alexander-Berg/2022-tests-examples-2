# -*- coding: utf-8 -*-
import unittest

from nose.tools import raises
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import (
    aliases_table as at,
    removed_aliases_table as rat,
)
from passport.backend.core.db.utils import with_ignore_prefix
from passport.backend.core.differ import diff
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ALT
from passport.backend.core.models.account import Account
from passport.backend.core.models.alias import PddAlias
from passport.backend.core.models.domain import Domain
from passport.backend.core.serializers.eav.alias import PddAliasEavSerializer
from sqlalchemy.sql.expression import and_


class TestCreatePddAlias(unittest.TestCase):
    def test_empty(self):
        acc = Account(uid=123)
        alias = PddAlias(acc)

        queries = PddAliasEavSerializer().serialize(None, alias, diff(None, alias))
        eq_eav_queries(queries, [])

    def test_create(self):
        acc = Account(uid=123)
        acc.domain = Domain(id=1, domain='okna.ru')
        alias = PddAlias(acc, email='Admin@okna.ru')

        queries = PddAliasEavSerializer().serialize(None, alias, diff(None, alias))

        eq_eav_queries(queries, [
            at.insert().values(
                uid=123,
                type=ALT['pdd'],
                value=b'1/admin',
                surrogate_type=str(ALT['pdd']).encode('utf8'),
            ),
        ])


class TestChangePddAlias(unittest.TestCase):
    def test_unchanged(self):
        acc = Account(uid=123)
        alias = PddAlias(acc, email='Admin@okna.ru')

        s1 = alias.snapshot()

        queries = PddAliasEavSerializer().serialize(s1, alias, diff(s1, alias))
        eq_eav_queries(queries, [])

    @raises(ValueError)
    def test_update(self):
        acc = Account(uid=123)
        alias = PddAlias(acc, email='Admin@okna.ru')

        s1 = alias.snapshot()

        alias = PddAlias(acc, email='User@okna.ru')
        list(PddAliasEavSerializer().serialize(s1, alias, diff(s1, alias)))


class TestDeletePddAlias(unittest.TestCase):
    @raises(ValueError)
    def test_delete(self):
        acc = Account(uid=123)
        alias = PddAlias(acc, email='Admin@okna.ru')

        s1 = alias.snapshot()

        list(PddAliasEavSerializer().serialize(s1, None, diff(s1, None)))


class TestPddAdditionalLogins(unittest.TestCase):
    def setUp(self):
        self.acc = Account(uid=123)
        self.acc.pdd_alias = PddAlias(self.acc, email='admin@okna.ru').parse({
            'aliases': {
                str(ALT['pddalias']): [],
            },
        })
        self.acc.domain = Domain(domain='okna.ru', id=1)

    def test_add_new_logins(self):
        s1 = self.acc.pdd_alias.snapshot()
        self.acc.pdd_alias.add_login('test1')
        self.acc.pdd_alias.add_login('TesT2')

        queries = PddAliasEavSerializer().serialize(
            s1,
            self.acc.pdd_alias,
            diff(s1, self.acc.pdd_alias),
        )

        eq_eav_queries(
            queries,
            [
                at.insert().values(
                    uid=123,
                    type=ALT['pddalias'],
                    value=b'1/test1',
                    surrogate_type=b'1/test1',
                ),
                at.insert().values(
                    uid=123,
                    type=ALT['pddalias'],
                    value=b'1/test2',
                    surrogate_type=b'1/test2',
                ),
            ],
        )

    def test_no_operations_needed(self):
        s1 = self.acc.pdd_alias.snapshot()

        self.acc.pdd_alias.add_login('test1')
        self.acc.pdd_alias.remove_login('test1')

        queries = PddAliasEavSerializer().serialize(
            s1,
            self.acc.pdd_alias,
            diff(s1, self.acc.pdd_alias),
        )
        eq_eav_queries(
            queries,
            [],
        )

    def test_remove_logins(self):
        self.acc.pdd_alias.add_login('test1')
        self.acc.pdd_alias.add_login('test2')

        s1 = self.acc.pdd_alias.snapshot()
        self.acc.pdd_alias.remove_login('TesT2')

        queries = PddAliasEavSerializer().serialize(
            s1,
            self.acc.pdd_alias,
            diff(s1, self.acc.pdd_alias),
        )
        eq_eav_queries(
            queries,
            [
                with_ignore_prefix(
                    rat.insert().values(
                        uid=123,
                        type=ALT['pddalias'],
                        value=b'okna.ru/test2',
                    ),
                ),
                at.delete().where(
                    and_(
                        at.c.uid == 123,
                        at.c.type == ALT['pddalias'],
                        at.c.value == b'1/test2',
                    ),
                ),
            ],
        )

    def test_remove_login_on_cyrillic_domain(self):
        account = Account(uid=123)
        account.pdd_alias = (
            PddAlias(account, email=u'admin@виндовс.рф')
            .parse(
                {
                    'aliases': {str(ALT['pddalias']): []},
                },
            )
        )
        account.domain = Domain(domain=u'виндовс.рф', id=1)
        account.pdd_alias.add_login('98')
        snapshot = account.pdd_alias.snapshot()
        account.pdd_alias.remove_login('98')

        queries = PddAliasEavSerializer().serialize(
            snapshot,
            account.pdd_alias,
            diff(snapshot, account.pdd_alias),
        )
        eq_eav_queries(
            queries,
            [
                with_ignore_prefix(
                    rat.insert().values(
                        uid=123,
                        type=ALT['pddalias'],
                        value=u'виндовс.рф'.encode('idna') + b'/98',
                    ),
                ),
                at.delete().where(
                    and_(
                        at.c.uid == 123,
                        at.c.type == ALT['pddalias'],
                        at.c.value == b'1/98',
                    ),
                ),
            ],
        )
