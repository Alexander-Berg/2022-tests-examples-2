# -*- coding: utf-8 -*-
from unittest import TestCase

import mock
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.query import DbTransactionContainer
from passport.backend.core.differ import diff
from passport.backend.core.differ.types import (
    Diff,
    EmptyDiff,
)
from passport.backend.core.models.base import Model
from passport.backend.core.models.base.fields import Field
from passport.backend.core.serializers.base import (
    AliasSerializer,
    DirectSerializer,
    serialize,
)
from passport.backend.core.serializers.logs.base import (
    ADDED,
    AttributeOfListItemSerializerRule,
    CHANGED,
    DELETED,
)
from passport.backend.core.undefined import Undefined
from sqlalchemy.schema import (
    Column,
    MetaData,
    Table,
)
from sqlalchemy.types import (
    Integer,
    VARBINARY,
)


def test_serialize_none_snapshots():
    eq_(list(serialize(None, None, {}, {})), [])


class TestAliasSerializer(TestCase):
    @raises(NotImplementedError)
    def test_create(self):
        AliasSerializer().create({})

    @raises(NotImplementedError)
    def test_change(self):
        AliasSerializer().change(None, None, None)

    @raises(NotImplementedError)
    def test_delete(self):
        AliasSerializer().delete(None)

    def test_serialize(self):
        create_mock = mock.Mock(return_value=['create'])
        change_mock = mock.Mock(return_value=['change'])
        delete_mock = mock.Mock(return_value=['delete'])
        with mock.patch.object(AliasSerializer, 'create', create_mock), \
                mock.patch.object(AliasSerializer, 'change', change_mock), \
                mock.patch.object(AliasSerializer, 'delete', delete_mock):
            s = AliasSerializer()
            eq_(s.serialize(None, None, EmptyDiff), [])

            diff = Diff({1: 'added'}, {}, {})
            eq_(s.serialize(None, object(), diff), ['create'])

            # Удаление объекта
            diff = Diff({}, {}, {})
            eq_(s.serialize(object(), None, diff), ['delete'])

            # Объекты есть, но diff пустой
            diff = Diff({}, {}, {})
            eq_(s.serialize(object(), object(), diff), [])

            # Изменение объекта
            diff = Diff({}, {1: 'changed'}, {})
            eq_(s.serialize(object(), object(), diff), ['change'])


class TestDirectSerializer(TestCase):
    def setUp(self):
        self.metadata = MetaData()
        self.table = Table(
            'test_table',
            self.metadata,
            Column('test_id', Integer, primary_key=True),
            Column('test_name', VARBINARY(length=255), nullable=False),
            Column('nonmappedfield', VARBINARY(length=255), nullable=False),
        )
        self.model = type(
            'TestModel',
            (Model,),
            {
                'test_id': Field('test_id'),
                'name': Field('name'),
                'nonmappedfield': Field('nonmappedfield'),
            }
        )
        self.model_data = {
            'name': 'Hello, world!',
            'nonmappedfield': 'World? Hello?',
        }

        self.serializer = DirectSerializer()
        self.serializer.table = self.table
        self.serializer.model = self.model
        self.serializer.id_field_name = 'test_id'
        self.serializer.field_mapping = {
            'name': 'test_name',
        }

    def test_no_action_required(self):
        """
        Если в объекте ничего не поменялось с точки зрения
        сериализатор, то не должно быть и сгенерировано никаких
        запросов.
        """
        queries = self.serializer.serialize(
            None,
            None,
            diff(None, None),
        )
        eq_eav_queries(queries, [])

        m = self.model().parse(self.model_data)
        s1 = m.snapshot()

        queries = self.serializer.serialize(
            s1,
            m,
            diff(s1, m),
        )
        eq_eav_queries(queries, [])

    def test_insert_with_undefined_pk(self):
        """
        Проверяем, что если мы не зададим значение первичного ключа явно, то
        сериализатор его сформирует, запишет в базу и выставит на модель.
        """

        m = self.model().parse(self.model_data)
        ok_(m.test_id is Undefined)
        queries = self.serializer.serialize(
            None,
            m,
            diff(None, m),
        )

        eq_eav_queries(
            queries,
            [
                'BEGIN',
                self.table.insert().values(
                    test_name=b'Hello, world!',
                    nonmappedfield=b'World? Hello?',
                ),
                'COMMIT',
            ],
            inserted_keys=[1],
        )
        eq_(m.test_id, 1)

    def test_insert_with_specified_pk(self):
        """
        Проверяем, что если мы явно зададим значение первичного ключа, то
        сериализатор запишет и его в базу.
        """

        self.model_data['test_id'] = 1
        m = self.model().parse(self.model_data)
        queries = self.serializer.serialize(
            None,
            m,
            diff(None, m),
        )

        eq_eav_queries(
            queries,
            [
                'BEGIN',
                self.table.insert().values(
                    test_id=1,
                    test_name=b'Hello, world!',
                    nonmappedfield=b'World? Hello?',
                ),
                'COMMIT',
            ],
            inserted_keys=[1],
        )

    def test_change(self):
        m = self.model().parse(self.model_data)
        m.test_id = 1
        s1 = m.snapshot()
        m.name = 'Another world.'

        queries = self.serializer.serialize(
            s1,
            m,
            diff(s1, m),
        )

        # Проверяем, что был сформирован запрос на помещение в базу
        # и имена полей оттранслированы (name -> test_name)
        eq_eav_queries(
            queries,
            [
                'BEGIN',
                self.table.update().values(
                    test_name=b'Another world.',
                ).where(self.table.c.test_id == 1),
                'COMMIT',
            ]
        )

    def test_delete(self):
        m = self.model().parse(self.model_data)
        m.test_id = 1
        queries = self.serializer.serialize(
            m,
            None,
            diff(m, None),
        )

        # Проверяем, что был сформирован запрос на помещение в базу
        # и имена полей оттранслированы (name -> test_name)
        eq_eav_queries(
            queries,
            [
                'BEGIN',
                self.table.delete().where(self.table.c.test_id == 1),
                'COMMIT',
            ]
        )

    @raises(ValueError)
    def test_empty_queries_failsafe(self):
        self.serializer.create = lambda old, new, diff: []
        m = self.model().parse(self.model_data)
        for query in self.serializer.serialize(
            None,
            m,
            diff(None, m),
        ):
            if isinstance(query, DbTransactionContainer):
                list(query.get_queries())


class TestAttributeOfListItemSerializerRule(TestCase):
    def test_add_attribute(self):
        rule = AttributeOfListItemSerializerRule(
            'foo.bar',
            operations=[ADDED],
        )
        old = {'foo': {}}
        new = {'foo': {'bar': 'spam'}}

        ok_(rule.is_applicable(old, new, diff(old, new)))

    def test_change_attribute(self):
        rule = AttributeOfListItemSerializerRule(
            'foo.bar',
            operations=[CHANGED],
        )
        old = {'foo': {'bar': 'spam'}}
        new = {'foo': {'bar': 'doh'}}

        ok_(rule.is_applicable(old, new, diff(old, new)))

    def test_delete_attribute(self):
        rule = AttributeOfListItemSerializerRule(
            'foo.bar',
            operations=[DELETED],
        )
        old = {'foo': {'bar': 'spam'}}
        new = {'foo': {}}

        ok_(rule.is_applicable(old, new, diff(old, new)))

    def test_delete_list_item__serialized(self):
        rule = AttributeOfListItemSerializerRule(
            'foo.bar',
            operations=[DELETED],
        )
        old = {'foo': {'bar': 'spam'}}
        new = {}

        ok_(rule.is_applicable(old, new, diff(old, new)))

    def test_delete_list_item__not_serialized(self):
        rule = AttributeOfListItemSerializerRule(
            'foo.bar',
            operations=[],
        )
        old = {'foo': {'bar': 'spam'}}
        new = {}

        ok_(not rule.is_applicable(old, new, diff(old, new)))

    def test_no_changes(self):
        rule = AttributeOfListItemSerializerRule(
            'foo.bar',
            operations=[ADDED, CHANGED, DELETED],
        )
        old = new = {'foo': {'bar': 'spam'}}

        ok_(not rule.is_applicable(old, new, diff(old, new)))
