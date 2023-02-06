# -*- coding: utf-8 -*-
import unittest

from nose.tools import raises
from passport.backend.core.db.faker.db import aliases_insert
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.differ import diff
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ALT
from passport.backend.core.models.account import Account
from passport.backend.core.models.alias import PortalAlias
from passport.backend.core.serializers.eav.alias import PortalAliasEavSerializer


class TestCreatePortalAlias(unittest.TestCase):
    def test_empty(self):
        acc = Account(uid=123)
        alias = PortalAlias(acc)

        queries = PortalAliasEavSerializer().serialize(None, alias, diff(None, alias))
        eq_eav_queries(queries, [])

    def test_create(self):
        acc = Account(uid=123)
        alias = PortalAlias(acc, login='Test.Login')

        queries = PortalAliasEavSerializer().serialize(None, alias, diff(None, alias))

        eq_eav_queries(queries, [
            aliases_insert().values(
                uid=123,
                type=ALT['portal'],
                value=b'test-login',
                surrogate_type=str(ALT['portal']).encode('utf8'),
            ),
        ])


class TestChangePortalAlias(unittest.TestCase):
    def test_unchanged(self):
        acc = Account(uid=123)
        alias = PortalAlias(acc, login='Test.Login')

        s1 = alias.snapshot()

        queries = PortalAliasEavSerializer().serialize(s1, alias, diff(s1, alias))
        eq_eav_queries(queries, [])

    @raises(ValueError)
    def test_update(self):
        acc = Account(uid=123)
        alias = PortalAlias(acc, login='Test.Login')

        s1 = alias.snapshot()

        alias = PortalAlias(acc, login='Test.Another.Login')
        list(PortalAliasEavSerializer().serialize(s1, alias, diff(s1, alias)))


class TestDeletePortalAlias(unittest.TestCase):
    @raises(ValueError)
    def test_delete(self):
        acc = Account(uid=123)
        alias = PortalAlias(acc, login='Test.Login')

        s1 = alias.snapshot()

        list(PortalAliasEavSerializer().serialize(s1, None, diff(s1, None)))
