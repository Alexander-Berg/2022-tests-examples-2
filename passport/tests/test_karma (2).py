# -*- coding: utf-8 -*-
from datetime import datetime
import unittest

from nose.tools import eq_
from passport.backend.core.db.faker.db import attribute_table_insert_on_duplicate_update_key as at_insert_odk
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import attributes_table as at
from passport.backend.core.differ import diff
from passport.backend.core.eav_type_mapping import ATTRIBUTE_NAME_TO_TYPE as AT
from passport.backend.core.models.account import Account
from passport.backend.core.models.karma import Karma
from passport.backend.core.serializers.eav.karma import (
    karma_activation_datetime_processor,
    karma_value_processor,
    KarmaEavSerializer,
)
from passport.backend.core.test.time_utils.time_utils import TimeNow
from sqlalchemy.sql.expression import and_


class TestCreateKarma(unittest.TestCase):
    def test_simple(self):
        uid = 123
        acc = Account(uid=uid)
        karma = Karma(parent=acc, prefix=2, suffix=20, activation_datetime=datetime.now())

        queries = KarmaEavSerializer().serialize(None, karma, diff(None, karma))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': uid, 'type': AT['karma.activation_datetime'], 'value': TimeNow()},
                    {'uid': uid, 'type': AT['karma.value'], 'value': b'2020'},
                ]),
            ],
        )

    def test_undefined_value(self):
        uid = 123
        acc = Account(uid=uid)
        karma = Karma(parent=acc, activation_datetime=datetime.now())

        queries = KarmaEavSerializer().serialize(None, karma, diff(None, karma))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': uid, 'type': AT['karma.activation_datetime'], 'value': TimeNow()},
                ]),
            ],
        )

    def test_default_value(self):
        uid = 123
        acc = Account(uid=uid)
        karma = Karma(parent=acc, prefix=0, suffix=0, activation_datetime=datetime.now())

        queries = KarmaEavSerializer().serialize(None, karma, diff(None, karma))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': uid, 'type': AT['karma.activation_datetime'], 'value': TimeNow()},
                ]),
            ],
        )

    def test_default_activation_datetime(self):
        uid = 123
        acc = Account(uid=uid)
        karma = Karma(parent=acc, prefix=2, suffix=20, activation_datetime=datetime.fromtimestamp(0))

        queries = KarmaEavSerializer().serialize(None, karma, diff(None, karma))

        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': uid, 'type': AT['karma.value'], 'value': b'2020'},
                ]),
            ],
        )


class TestChangeKarma(unittest.TestCase):
    def test_unchanged_karma(self):
        acc = Account(uid=10)
        karma = Karma(parent=acc, prefix=2, suffix=20, activation_datetime=datetime.now())

        s1 = karma.snapshot()

        queries = KarmaEavSerializer().serialize(s1, karma, diff(s1, karma))
        eq_eav_queries(queries, [])

    def test_change_karma(self):
        uid = 123
        acc = Account(uid=123)
        karma = Karma(parent=acc, prefix=2, suffix=20, activation_datetime=datetime.now())

        s1 = karma.snapshot()
        karma.prefix = 3
        karma.suffix = 30

        queries = KarmaEavSerializer().serialize(s1, karma, diff(s1, karma))
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': uid, 'type': AT['karma.value'], 'value': b'3030'},
                ]),
            ],
        )

    def test_change_activation_datetime(self):
        uid = 123
        acc = Account(uid=123)
        karma = Karma(parent=acc, prefix=2, suffix=20, activation_datetime=datetime.fromtimestamp(500))

        s1 = karma.snapshot()
        karma.activation_datetime = datetime.now()

        queries = KarmaEavSerializer().serialize(s1, karma, diff(s1, karma))
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': uid, 'type': AT['karma.activation_datetime'], 'value': TimeNow()},
                ]),
            ],
        )

    def test_change_all_fields(self):
        uid = 123
        acc = Account(uid=123)
        karma = Karma(parent=acc, prefix=2, suffix=20, activation_datetime=datetime.fromtimestamp(500))

        s1 = karma.snapshot()
        karma.activation_datetime = datetime.now()
        karma.prefix = 3
        karma.suffix = 30

        queries = KarmaEavSerializer().serialize(s1, karma, diff(s1, karma))
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': uid, 'type': AT['karma.activation_datetime'], 'value': TimeNow()},
                    {'uid': uid, 'type': AT['karma.value'], 'value': b'3030'},
                ]),
            ],
        )

    def test_change_value_to_default(self):
        uid = 123
        acc = Account(uid=123)
        karma = Karma(parent=acc, prefix=2, suffix=20, activation_datetime=datetime.fromtimestamp(500))

        s1 = karma.snapshot()
        karma.activation_datetime = datetime.now()
        karma.prefix = 0
        karma.suffix = 0

        queries = KarmaEavSerializer().serialize(s1, karma, diff(s1, karma))
        eq_eav_queries(
            queries,
            [
                at_insert_odk().values([
                    {'uid': uid, 'type': AT['karma.activation_datetime'], 'value': TimeNow()},
                ]),
                at.delete().where(and_(at.c.uid == uid, at.c.type.in_([AT['karma.value']]))),
            ],
        )

    def test_change_all_fields_to_default(self):
        uid = 123
        acc = Account(uid=123)
        karma = Karma(parent=acc, prefix=2, suffix=20, activation_datetime=datetime.fromtimestamp(500))

        s1 = karma.snapshot()
        karma.activation_datetime = datetime.now()
        karma.prefix = 0
        karma.suffix = 0
        karma.activation_datetime = datetime.fromtimestamp(0)

        queries = KarmaEavSerializer().serialize(s1, karma, diff(s1, karma))
        eq_eav_queries(
            queries,
            [
                at.delete().where(and_(at.c.uid == uid, at.c.type.in_([
                    AT['karma.value'], AT['karma.activation_datetime']
                ]))),
            ],
        )


class TestKarmaProcessors(unittest.TestCase):
    def test_value(self):
        # accounts.karma, если > 0
        eq_(karma_value_processor(None), None)
        eq_(karma_value_processor(-1), None)
        eq_(karma_value_processor(0), None)
        eq_(karma_value_processor(123), 123)

    def test_activation_datetime(self):
        # accounts.acl_id, если != 0 и != 2
        eq_(karma_activation_datetime_processor(None), None)
        eq_(karma_activation_datetime_processor(datetime.fromtimestamp(0)), None)
        eq_(karma_activation_datetime_processor(datetime.fromtimestamp(2)), None)
        eq_(karma_activation_datetime_processor(datetime.now()), TimeNow())
