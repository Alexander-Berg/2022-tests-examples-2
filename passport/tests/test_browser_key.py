# -*- coding: utf-8 -*-
import unittest

from passport.backend.core.db.faker.db import (
    attribute_table_insert_on_duplicate_append_key as at_insert_odk_append,
    attribute_table_insert_on_duplicate_update_key as at_insert_odk_update,
)
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import attributes_table as at
from passport.backend.core.differ import diff
from passport.backend.core.eav_type_mapping import ATTRIBUTE_NAME_TO_TYPE as AT
from passport.backend.core.models.account import Account
from passport.backend.core.models.browser_key import BrowserKey
from passport.backend.core.serializers.eav.browser_key import BrowserKeyEavSerializer
from sqlalchemy.sql.expression import and_


class TestCreateBrowserKey(unittest.TestCase):
    def test_empty(self):
        acc = Account(uid=123)
        key = BrowserKey(acc)

        queries = BrowserKeyEavSerializer().serialize(None, key, diff(None, key))
        eq_eav_queries(queries, [])

    def test_create(self):
        acc = Account(uid=123).parse({'login': 'login'})
        key = BrowserKey(acc)
        key.set('key')

        queries = list(BrowserKeyEavSerializer().serialize(None, key, diff(None, key)))

        eq_eav_queries(
            queries,
            [
                at_insert_odk_update().values([
                    {'uid': 123, 'type': AT['account.browser_key'], 'value': b'key'},
                ]),
            ],
        )


class TestChangeBrowserKey(unittest.TestCase):
    def test_unchanged(self):
        acc = Account(uid=123)
        key = BrowserKey(acc)

        s1 = key.snapshot()
        queries = BrowserKeyEavSerializer().serialize(s1, key, diff(s1, key))
        eq_eav_queries(queries, [])

    def test_change(self):
        acc = Account(uid=123).parse({'login': 'login'})
        key = BrowserKey(acc)
        key.set('key')

        s1 = key.snapshot()

        key.set('new_key')

        queries = list(BrowserKeyEavSerializer().serialize(s1, key, diff(s1, key)))

        eq_eav_queries(
            queries,
            [
                at_insert_odk_update().values([
                    {'uid': 123, 'type': AT['account.browser_key'], 'value': b'new_key'},
                ]),
            ],
        )

    def test_append(self):
        acc = Account(uid=123).parse({'login': 'login'})
        key = BrowserKey(acc)
        key.set('key')

        s1 = key.snapshot()

        key.append('new_key')

        queries = list(BrowserKeyEavSerializer().serialize(s1, key, diff(s1, key)))

        eq_eav_queries(
            queries,
            [
                at_insert_odk_append().values([
                    {'uid': 123, 'type': AT['account.browser_key'], 'value': b'new_key'},
                ]),
            ],
        )


class TestDeleteBrowserKey(unittest.TestCase):
    def test_delete(self):
        acc = Account(uid=123)
        key = BrowserKey(acc)
        key.set('key')

        s1 = key.snapshot()
        queries = BrowserKeyEavSerializer().serialize(s1, None, diff(s1, None))

        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == 123,
                        at.c.type.in_(
                            [
                                AT['account.browser_key'],
                            ],
                        ),
                    ),
                ),
            ],
        )
