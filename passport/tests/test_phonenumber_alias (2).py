# -*- coding: utf-8 -*-

from nose_parameterized import parameterized
from passport.backend.core.db.faker.db import (
    aliases_insert,
    attribute_table_insert_on_duplicate_update_key as at_insert_odk,
    insert_ignore_into_removed_aliases,
)
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import (
    aliases_table as alt,
    attributes_table as at,
)
from passport.backend.core.differ import diff
from passport.backend.core.eav_type_mapping import (
    ALIAS_NAME_TO_TYPE as ALT,
    ATTRIBUTE_NAME_TO_TYPE as AT,
)
from passport.backend.core.models.account import Account
from passport.backend.core.models.alias import PhonenumberAlias
from passport.backend.core.serializers.eav.alias import PhonenumberAliasEavSerializer
from passport.backend.core.test.consts import (
    TEST_PHONE_NUMBER1,
    TEST_PHONE_NUMBER2,
    TEST_UID,
)
from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.core.undefined import Undefined
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import and_


class _PhonenumberAliasTestCase(PassportTestCase):
    def setUp(self):
        super(_PhonenumberAliasTestCase, self).setUp()
        self._account = Account(uid=TEST_UID)

    def _insert_phonenumber_alias_query(self, number):
        return aliases_insert().values(
            uid=TEST_UID,
            type=ALT['phonenumber'],
            value=number.digital.encode('utf8'),
            surrogate_type=str(ALT['phonenumber']).encode('utf8'),
        )

    def _insert_enable_search_attribute_query(self):
        return at_insert_odk().values([
            {
                'uid': TEST_UID,
                'type': AT['account.enable_search_by_phone_alias'],
                'value': b'1',
            },
        ])

    def _insert_phonenumber_alias_to_removed_aliases_query(self):
        return insert_ignore_into_removed_aliases(
            select([alt.c.uid, alt.c.type, alt.c.value])
            .where(
                and_(
                    alt.c.uid == TEST_UID,
                    alt.c.type.in_([ALT['phonenumber']]),
                ),
            ),
        )

    def _update_phonenumber_alias_query(self, number):
        return alt.update().values(value=number.digital.encode('utf8')).where(
            and_(
                alt.c.uid == TEST_UID,
                alt.c.type == ALT['phonenumber'],
                alt.c.surrogate_type == str(ALT['phonenumber']).encode('utf-8'),
            ),
        )

    def _remove_phonenumber_alias_query(self):
        return alt.delete().where(
            and_(
                alt.c.uid == TEST_UID,
                alt.c.type.in_([ALT['phonenumber']]),
            ),
        )

    def _remove_enable_search_attribute_query(self):
        return at.delete().where(
            and_(
                at.c.uid == TEST_UID,
                at.c.type.in_([AT['account.enable_search_by_phone_alias']]),
            ),
        )


class TestCreatePhonenumberAlias(_PhonenumberAliasTestCase):
    def test_empty(self):
        alias = PhonenumberAlias(self._account)

        queries = PhonenumberAliasEavSerializer().serialize(None, alias, diff(None, alias))
        eq_eav_queries(queries, [])

    def test_phonenumber_alias(self):
        alias = PhonenumberAlias(self._account, number=TEST_PHONE_NUMBER1)

        queries = PhonenumberAliasEavSerializer().serialize(None, alias, diff(None, alias))
        eq_eav_queries(
            queries,
            [
                self._insert_phonenumber_alias_query(TEST_PHONE_NUMBER1),
            ],
        )

    def test_enable_search_turned_on(self):
        alias = PhonenumberAlias(
            self._account,
            number=TEST_PHONE_NUMBER1,
            enable_search=True,
        )

        queries = PhonenumberAliasEavSerializer().serialize(None, alias, diff(None, alias))

        eq_eav_queries(
            queries,
            [
                self._insert_enable_search_attribute_query(),
                self._insert_phonenumber_alias_query(TEST_PHONE_NUMBER1),
            ],
        )

    def test_enable_search_turned_off(self):
        alias = PhonenumberAlias(
            self._account,
            number=TEST_PHONE_NUMBER1,
            enable_search=False,
        )

        queries = PhonenumberAliasEavSerializer().serialize(None, alias, diff(None, alias))

        eq_eav_queries(
            queries,
            [
                self._remove_enable_search_attribute_query(),
                self._insert_phonenumber_alias_query(TEST_PHONE_NUMBER1),
            ],
        )

    def test_enable_search_undefined(self):
        alias = PhonenumberAlias(self._account, number=TEST_PHONE_NUMBER1)

        queries = PhonenumberAliasEavSerializer().serialize(None, alias, diff(None, alias))

        eq_eav_queries(
            queries,
            [
                self._insert_phonenumber_alias_query(TEST_PHONE_NUMBER1),
            ],
        )


class TestChangePhonenumberAlias(_PhonenumberAliasTestCase):
    def test_phone_number_unchanged(self):
        alias = PhonenumberAlias(self._account, number=TEST_PHONE_NUMBER1)

        s1 = alias.snapshot()

        queries = PhonenumberAliasEavSerializer().serialize(s1, alias, diff(s1, alias))
        eq_eav_queries(queries, [])

    def test_update_phone_number(self):
        alias = PhonenumberAlias(self._account, number=TEST_PHONE_NUMBER1)

        s1 = alias.snapshot()

        alias.number = TEST_PHONE_NUMBER2

        queries = PhonenumberAliasEavSerializer().serialize(s1, alias, diff(s1, alias))

        eq_eav_queries(
            queries,
            [
                self._insert_phonenumber_alias_to_removed_aliases_query(),
                self._update_phonenumber_alias_query(TEST_PHONE_NUMBER2),
            ],
        )

    @parameterized.expand([
        (Undefined, Undefined),
        (False, False),
        (True, True),
    ])
    def test_enable_search_attribute_unchanged(self, old, new):
        alias = PhonenumberAlias(
            self._account,
            number=TEST_PHONE_NUMBER1,
            enable_search=old,
        )

        s1 = alias.snapshot()

        alias.enable_search = new

        queries = PhonenumberAliasEavSerializer().serialize(s1, alias, diff(s1, alias))
        eq_eav_queries(queries, [])

    @parameterized.expand([
        (Undefined, True),
        (False, True),
    ])
    def test_turn_on_enable_search_attribute(self, old, new):
        alias = PhonenumberAlias(
            self._account,
            number=TEST_PHONE_NUMBER1,
            enable_search=old,
        )

        s1 = alias.snapshot()

        alias.enable_search = new

        queries = PhonenumberAliasEavSerializer().serialize(s1, alias, diff(s1, alias))
        eq_eav_queries(
            queries,
            [
                self._insert_enable_search_attribute_query(),
            ],
        )

    @parameterized.expand([
        (True, False),
        (Undefined, False),
    ])
    def test_turn_off_enable_search_attribute(self, old, new):
        alias = PhonenumberAlias(
            self._account,
            number=TEST_PHONE_NUMBER1,
            enable_search=old,
        )

        s1 = alias.snapshot()

        alias.enable_search = new

        queries = PhonenumberAliasEavSerializer().serialize(s1, alias, diff(s1, alias))
        eq_eav_queries(
            queries,
            [
                self._remove_enable_search_attribute_query(),
            ],
        )


class TestDeletePhonenumberAlias(_PhonenumberAliasTestCase):
    def test_delete(self):
        alias = PhonenumberAlias(self._account, number=TEST_PHONE_NUMBER1)

        queries = PhonenumberAliasEavSerializer().serialize(alias, None, diff(alias, None))
        eq_eav_queries(
            queries,
            [
                self._insert_phonenumber_alias_to_removed_aliases_query(),
                self._remove_phonenumber_alias_query(),
            ],
        )

    def test_enable_search_turned_on(self):
        alias = PhonenumberAlias(self._account, number=TEST_PHONE_NUMBER1, enable_search=True)

        queries = PhonenumberAliasEavSerializer().serialize(alias, None, diff(alias, None))
        eq_eav_queries(
            queries,
            [
                self._insert_phonenumber_alias_to_removed_aliases_query(),
                self._remove_phonenumber_alias_query(),
                self._remove_enable_search_attribute_query(),
            ],
        )

    def test_enable_search_turned_off(self):
        alias = PhonenumberAlias(self._account, number=TEST_PHONE_NUMBER1, enable_search=False)

        queries = PhonenumberAliasEavSerializer().serialize(alias, None, diff(alias, None))
        eq_eav_queries(
            queries,
            [
                self._insert_phonenumber_alias_to_removed_aliases_query(),
                self._remove_phonenumber_alias_query(),
            ],
        )

    def test_enable_search_undefined(self):
        alias = PhonenumberAlias(self._account, number=TEST_PHONE_NUMBER1)

        queries = PhonenumberAliasEavSerializer().serialize(alias, None, diff(alias, None))
        eq_eav_queries(
            queries,
            [
                self._insert_phonenumber_alias_to_removed_aliases_query(),
                self._remove_phonenumber_alias_query(),
            ],
        )
