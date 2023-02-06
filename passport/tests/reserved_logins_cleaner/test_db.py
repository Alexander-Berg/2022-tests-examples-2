# -*- coding: utf-8 -*-
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import reserved_logins_table
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.dbscripts.reserved_logins_cleaner.db import ReservedLoginsCleanupQuery
from passport.backend.dbscripts.test.base_phone_harvester import TestCase


class TestReservedLoginsCleanupQuery(TestCase):
    def test_ok(self):
        eq_eav_queries(
            [ReservedLoginsCleanupQuery()],
            [
                reserved_logins_table.delete().where(
                    reserved_logins_table.c.free_ts < DatetimeNow(),
                ),
            ],
        )
