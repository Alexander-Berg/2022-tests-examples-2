# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from nose.tools import eq_
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import (
    extended_attributes_table as ext_attr_t,
    phone_bindings_table as ph_b_t,
    phone_operations_table as p_op_t,
)
from passport.backend.core.eav_type_mapping import EXTENDED_ATTRIBUTES_PHONE_TYPE
from passport.backend.core.serializers.eav.query import EavPhoneIdIncrementQuery
from passport.backend.dbscripts.phone_harvester.db import (
    EavDeleteAllPhoneBindingsQuery,
    EavDeleteAllPhoneExtendedAttributesQuery,
    EavDeleteAllPhoneOperationsQuery,
    execute_in_transaction,
)
from passport.backend.dbscripts.test.base_phone_harvester import TestCase
from passport.backend.dbscripts.test.consts import TEST_UID1
from sqlalchemy.sql.expression import and_


class TestEavDeleteAllPhoneExtendedAttributesQuery(TestCase):
    def test_ok(self):
        eq_eav_queries(
            [EavDeleteAllPhoneExtendedAttributesQuery(TEST_UID1)],
            [
                ext_attr_t.delete().where(
                    and_(
                        ext_attr_t.c.uid == TEST_UID1,
                        ext_attr_t.c.entity_type == EXTENDED_ATTRIBUTES_PHONE_TYPE,
                    ),
                ),
            ],
        )


class TestEavDeleteAllPhoneBindingsQuery(TestCase):
    def test_ok(self):
        eq_eav_queries(
            [EavDeleteAllPhoneBindingsQuery(TEST_UID1)],
            [ph_b_t.delete().where(ph_b_t.c.uid == TEST_UID1)],
        )


class TestEavDeleteAllPhoneOperationsQuery(TestCase):
    def test_ok(self):
        eq_eav_queries(
            [EavDeleteAllPhoneOperationsQuery(TEST_UID1)],
            [p_op_t.delete().where(p_op_t.c.uid == TEST_UID1)],
        )


class TestExecuteInTransaction(TestCase):
    def test_no_queries(self):
        execute_in_transaction([])

        eq_(self._db_faker.query_count('passportdbcentral'), 0)
        eq_(self._db_faker.query_count('passportdbshard1'), 0)

    def test_many_queries(self):
        execute_in_transaction([
            EavDeleteAllPhoneOperationsQuery(TEST_UID1),
            EavDeleteAllPhoneOperationsQuery(TEST_UID1),
            EavPhoneIdIncrementQuery(is_pdd=False),
        ])

        eq_(self._db_faker.query_count('passportdbcentral'), 1)
        eq_(self._db_faker.query_count('passportdbshard1'), 2)

        self._db_faker.assert_executed_queries_equal(
            [
                'BEGIN',
                EavDeleteAllPhoneOperationsQuery(TEST_UID1),
                EavDeleteAllPhoneOperationsQuery(TEST_UID1),
                'COMMIT',
            ],
            db='passportdbshard1',
        )
        self._db_faker.assert_executed_queries_equal(
            [
                'BEGIN',
                EavPhoneIdIncrementQuery(is_pdd=False),
                'COMMIT',
            ],
            db='passportdbcentral',
        )
