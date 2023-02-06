# -*- coding: utf-8 -*-
from datetime import timedelta

from nose.tools import eq_
from passport.backend.core.db.faker.db_utils import (
    compile_query_with_dialect,
    eq_eav_queries,
)
from passport.backend.core.db.schemas import yakey_backups_table
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.dbscripts.test.base_phone_harvester import TestCase
from passport.backend.dbscripts.test.consts import (
    TEST_PHONE_NUMBER1,
    TEST_PHONE_NUMBER2,
)
from passport.backend.dbscripts.yakey_backups_cleaner.db import YakeyBackupsCleanupQuery
from sqlalchemy.sql.expression import and_


class TestYakeyBackupsCleanupQuery(TestCase):
    def test_ok(self):
        eq_eav_queries(
            [YakeyBackupsCleanupQuery(offset=timedelta(seconds=100))],
            [
                yakey_backups_table.delete().where(
                    yakey_backups_table.c.updated <= DatetimeNow() - timedelta(seconds=100),
                ),
            ],
        )

    def test_default_offset(self):
        eq_eav_queries(
            [YakeyBackupsCleanupQuery()],
            [
                yakey_backups_table.delete().where(
                    yakey_backups_table.c.updated <= DatetimeNow() - timedelta(days=365),
                ),
            ],
        )

    def test_with_phone_numbers(self):
        phone_numbers = [int(TEST_PHONE_NUMBER1.digital), int(TEST_PHONE_NUMBER2.digital)]

        query = YakeyBackupsCleanupQuery(
            offset=timedelta(seconds=100),
            phone_numbers=phone_numbers,
        ).to_query()

        eq_(
            [str(compile_query_with_dialect(query))],
            [
                str(compile_query_with_dialect(
                    yakey_backups_table.delete().where(
                        and_(
                            yakey_backups_table.c.updated <= DatetimeNow() - timedelta(seconds=100),
                            yakey_backups_table.c.phone_number.in_(phone_numbers),
                        ),
                    ),
                )),
            ],
        )
