# -*- coding: utf-8 -*-
from datetime import timedelta
import unittest

from passport.backend.core.db.faker.db import attribute_table_insert_on_duplicate_update_key as at_insert_odk
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import attributes_table as at
from passport.backend.core.differ import diff
from passport.backend.core.eav_type_mapping import ATTRIBUTE_NAME_TO_TYPE as AT
from passport.backend.core.models.account import Account
from passport.backend.core.models.takeout import Takeout
from passport.backend.core.serializers.eav.takeout import TakeoutEavSerializer
from passport.backend.utils.time import unixtime_to_datetime
from sqlalchemy.sql.expression import and_


TEST_UNIXTIME = 42
TEST_DATETIME = unixtime_to_datetime(42)


class TestCreateTakeout(unittest.TestCase):
    def test_empty(self):
        acc = Account(uid=123)
        takeout = Takeout(acc)

        queries = TakeoutEavSerializer().serialize(None, takeout, diff(None, takeout))
        eq_eav_queries(queries, [])

    def test_create(self):
        acc = Account(uid=123).parse({'login': 'login'})
        takeout = Takeout(acc)
        takeout.extract_in_progress_since = TEST_DATETIME
        takeout.archive_s3_key = 'key'
        takeout.archive_password = 'password'
        takeout.archive_created_at = TEST_DATETIME
        takeout.fail_extract_at = TEST_DATETIME

        queries = list(TakeoutEavSerializer().serialize(None, takeout, diff(None, takeout)))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['takeout.extract_in_progress_since'], 'value': str(TEST_UNIXTIME).encode('utf8')},
                    {'uid': 123, 'type': AT['takeout.archive_s3_key'], 'value': b'key'},
                    {'uid': 123, 'type': AT['takeout.archive_password'], 'value': b'password'},
                    {'uid': 123, 'type': AT['takeout.archive_created_at'], 'value': str(TEST_UNIXTIME).encode('utf8')},
                    {'uid': 123, 'type': AT['takeout.fail_extract_at'], 'value': str(TEST_UNIXTIME).encode('utf8')},
                ]),
            ],
        )


class TestChangeTakeout(unittest.TestCase):
    def test_unchanged(self):
        acc = Account(uid=123)
        takeout = Takeout(acc)

        s1 = takeout.snapshot()
        queries = TakeoutEavSerializer().serialize(s1, takeout, diff(s1, takeout))
        eq_eav_queries(queries, [])

    def test_change_all_fields(self):
        acc = Account(uid=123).parse({'login': 'login'})
        takeout = Takeout(acc)

        takeout.extract_in_progress_since = None
        takeout.archive_s3_key = 'key'
        takeout.archive_password = 'password'
        takeout.archive_created_at = TEST_DATETIME
        takeout.fail_extract_at = TEST_DATETIME

        s1 = takeout.snapshot()

        takeout.extract_in_progress_since = TEST_DATETIME
        takeout.archive_s3_key = '-'
        takeout.archive_password = '-'
        takeout.archive_created_at = TEST_DATETIME + timedelta(seconds=1)
        takeout.fail_extract_at = TEST_DATETIME + timedelta(seconds=1)

        queries = list(TakeoutEavSerializer().serialize(s1, takeout, diff(s1, takeout)))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': 123, 'type': AT['takeout.extract_in_progress_since'], 'value': str(TEST_UNIXTIME).encode('utf8')},
                    {'uid': 123, 'type': AT['takeout.archive_s3_key'], 'value': b'-'},
                    {'uid': 123, 'type': AT['takeout.archive_password'], 'value': b'-'},
                    {'uid': 123, 'type': AT['takeout.archive_created_at'], 'value': str(TEST_UNIXTIME + 1).encode('utf8')},
                    {'uid': 123, 'type': AT['takeout.fail_extract_at'], 'value': str(TEST_UNIXTIME + 1).encode('utf8')},
                ]),
            ],
        )


class TestDeleteTakeout(unittest.TestCase):
    def test_delete(self):
        acc = Account(uid=123)
        takeout = Takeout(acc)
        takeout.extract_in_progress_since = TEST_DATETIME

        s1 = takeout.snapshot()
        queries = TakeoutEavSerializer().serialize(s1, None, diff(s1, None))

        eq_eav_queries(
            queries,
            [
                at.delete().where(
                    and_(
                        at.c.uid == 123,
                        at.c.type.in_(
                            sorted([
                                AT['takeout.fail_extract_at'],
                                AT['takeout.extract_in_progress_since'],
                                AT['takeout.archive_s3_key'],
                                AT['takeout.archive_password'],
                                AT['takeout.archive_created_at'],
                                AT['takeout.subscription'],
                                AT['takeout.delete.subscription'],
                            ]),
                        ),
                    ),
                ),
            ],
        )
