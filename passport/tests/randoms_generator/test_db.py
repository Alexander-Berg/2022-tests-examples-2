# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)

from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.dbscripts.randoms_generator.db import (
    CleanTableQuery,
    GetKeyspacesQuery,
    InsertKeyQuery,
    keyspaces_table,
    lrandoms_table,
)
from passport.backend.dbscripts.test.base_phone_harvester import TestCase
from sqlalchemy import select


class TestGetKeyspacesQuery(TestCase):
    def test_ok(self):
        eq_eav_queries(
            [GetKeyspacesQuery()],
            [
                select([keyspaces_table.c.domainsuff, keyspaces_table.c.tablename]),
            ],
        )


class TestInsertKeyQuery(TestCase):
    def test_ok(self):
        eq_eav_queries(
            [InsertKeyQuery('lrandoms', 'key', timedelta(days=10))],
            [
                lrandoms_table.insert().values(
                    keybody='key',
                    start=DatetimeNow(),
                    valid=DatetimeNow(timestamp=datetime.now() + timedelta(days=10)),
                ),
            ],
        )


class TestCleanTableQuery(TestCase):
    def test_ok(self):
        eq_eav_queries(
            [CleanTableQuery('lrandoms')],
            [
                lrandoms_table.delete().where(lrandoms_table.c.valid < DatetimeNow()),
            ],
        )
