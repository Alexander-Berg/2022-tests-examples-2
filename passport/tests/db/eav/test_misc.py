# -*- coding: utf-8 -*-
from mock import Mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.oauth.core.db.eav.attributes import (
    deserialize_attribute,
    serialize_attribute,
    serialize_attribute_for_index,
)
from passport.backend.oauth.core.db.eav.errors import AttributeNotFoundError
from passport.backend.oauth.core.db.eav.index import Index
from passport.backend.oauth.core.db.eav.query import IncrementAutoIdQuery
from passport.backend.oauth.core.db.eav.sharder import build_range_shard_function
from passport.backend.oauth.core.db.eav.transaction import Transaction
from passport.backend.oauth.core.test.framework import BaseTestCase


class TestIndex(BaseTestCase):
    @raises(ValueError)
    def test_bad_fields(self):
        table, column1, column2 = Mock(), Mock(), Mock()
        column1.name = 'column1'
        column2.name = 'column2'
        table.columns = [column1, column2]
        Index(
            index_table=table,
            distinct_matched_key_fields=['column1', 'column2'],
            substr_matched_key_fields=['column1'],
        )


class TestQuery(BaseTestCase):
    def test_repr(self):
        eq_(
            repr(IncrementAutoIdQuery('token')),
            'INSERT INTO auto_id_token () VALUES ()  <=  {}',
        )


class TestTransaction(BaseTestCase):
    def test_repr(self):
        eq_(
            repr(Transaction()),
            '<Transaction>: 0 queries',
        )

    def test_execute_empty(self):
        ok_(Transaction().execute() is None)

    def test_add_queries_from_different_dbms(self):
        transaction = Transaction()
        query1 = Mock()
        query1.dbm = 'dbm1'
        query2 = Mock()
        query2.dbm = 'dbm2'
        transaction.add(query1)
        with assert_raises(ValueError):
            transaction.add(query2)


class TestSharder(BaseTestCase):
    def test_shard_range_function(self):
        function = build_range_shard_function([(1, 0), (2, 100)])
        eq_(function(0), 1)
        eq_(function(99), 1)
        eq_(function(100), 2)
        eq_(function(100500), 2)
        assert_raises(ValueError, function, -1)


class TestAttributes(BaseTestCase):
    @raises(AttributeNotFoundError)
    def test_serialize_bad_attr_name(self):
        serialize_attribute('token', 1, 'bad_attr', None)

    @raises(AttributeNotFoundError)
    def test_deserialize_bad_attr_type(self):
        deserialize_attribute('token', 1, 99, None)

    @raises(AttributeNotFoundError)
    def test_serialize_for_index_bad_attr_name(self):
        serialize_attribute_for_index('token', 1, 'bad_attr', None)
