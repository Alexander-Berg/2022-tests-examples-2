# -*- coding: utf-8 -*-
from datetime import datetime
import unittest

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.eav_type_mapping import (
    ALLOW_ZERO_VALUE_ATTRS as AZV,
    ATTRIBUTE_NAME_TO_TYPE as AT,
)
from passport.backend.core.serializers.eav.base import (
    EavAttributeMap,
    EavSerializer,
)
from passport.backend.core.serializers.eav.exceptions import EavDeletePDDAliasWithoutValueError
from passport.backend.core.serializers.eav.query import (
    EavDeleteAttributeQuery,
    EavInsertAttributeWithOnDuplicateKeyUpdateQuery,
    EavInsertPasswordHistoryQuery,
)


class TestEavSerializer(unittest.TestCase):
    def setUp(self):
        self.es = EavSerializer()

    def test_is_writeable_attr(self):
        eav_type = AT['person.gender']
        eq_(self.es.is_writable_attr(eav_type, 0), False)
        eq_(self.es.is_writable_attr(eav_type, ''), False)
        eq_(self.es.is_writable_attr(eav_type, None), False)
        eq_(self.es.is_writable_attr(eav_type, 'm'), True)

    def test_is_writable_attr_allow_zero_attrs(self):
        for eav_type in AZV:
            eq_(self.es.is_writable_attr(eav_type, 0), True)
            eq_(self.es.is_writable_attr(eav_type, ''), False)
            eq_(self.es.is_writable_attr(eav_type, None), False)
            eq_(self.es.is_writable_attr(eav_type, 123), True)

    def test_set_attr_params(self):
        eq_(self.es.set_attr_params('person.firstname', 'bla'),
            (AT['person.firstname'], 'bla'))
        eq_(self.es.set_attr_params('person.firstname', ''), None)

    def test_insert_attrs_query(self):
        eavquery = self.es.insert_attrs_query(1, [(1, 2)])
        eq_(eavquery.uid, 1)
        eq_(eavquery.types_values, [(1, 2)])
        eq_(eavquery.query_params(), [(1, 2)])

    def test_delete_attrs_query(self):
        eavquery = self.es.delete_attrs_query(1, [2])
        eq_(eavquery.uid, 1)
        eq_(eavquery.types, [2])
        eq_(eavquery.query_params(), [2])

    def test_build_set_attrs_with_cleaned_values(self):
        queries = self.es.build_set_attrs_with_cleaned_values(1, {
            'person.gender': 'm',
            'person.firstname': 'firstname',
            'person.language': None,
        })
        eq_(
            queries,
            [
                EavInsertAttributeWithOnDuplicateKeyUpdateQuery(
                    1,
                    [
                        (AT['person.gender'], 'm'),
                        (AT['person.firstname'], 'firstname'),
                    ],
                ),
            ],
        )

    def test_build_delete_attrs_by_names(self):
        query = self.es.build_delete_attrs_by_names(1, ['person.gender', 'person.firstname'])
        eq_(query, EavDeleteAttributeQuery(1, [AT['person.gender'], AT['person.firstname']]))

    def test_build_insert_suid_query(self):
        query = self.es.build_insert_suid_query(1, 2, 3)
        eq_(query.uid, 1)
        eq_(query.sid, 2)
        eq_(query.suid, 3)

    def test_build_delete_suid_query(self):
        query = self.es.build_delete_suid_query(1, 2)
        eq_(query.uid, 1)
        eq_(query.sid, 2)

    def test_build_insert_alias_query(self):
        query = self.es.build_insert_alias_query(1, 'portal', 'value')
        eq_(query.uid, 1)
        eq_(query.types_values, [(1, 'value', 1)])

    def test_build_delete_alias_query(self):
        query = self.es.build_delete_alias_query(1, 'portal')
        eq_(query.uid, 1)
        eq_(query.types, [1])

    @raises(EavDeletePDDAliasWithoutValueError)
    def test_build_delete_alias_query_pddalias(self):
        self.es.build_delete_alias_query(1, 'pddalias')

    def test_build_delete_alias_with_value_query(self):
        query = self.es.build_delete_alias_with_value_query(1, 'portal', 'value')
        eq_(query.uid, 1)
        eq_(query.types_values, [(1, 'value')])

    def test_build_delete_fields_query(self):
        eav_mapper = {
            'firstname': EavAttributeMap('person.firstname', lambda x: x),
            'lastname': EavAttributeMap('person.lastname', lambda x: x),
        }
        query = self.es.build_delete_fields_query(eav_mapper, 123)
        eq_(query.uid, 123)
        eq_(sorted(query.types), [27, 28])

    def test_build_delete_fields_query_empty_mapper(self):
        eav_mapper = {}
        query = self.es.build_delete_fields_query(eav_mapper, 123)
        eq_(query, None)

    def test_build_insert_password_history_query(self):
        dt = datetime.now()
        query = self.es.build_insert_password_history(1, dt, 'password', 1)
        eq_(type(query), EavInsertPasswordHistoryQuery)
        eq_(query.uid, 1)
        eq_(query.password_history, [(dt, 'password', 1)])
