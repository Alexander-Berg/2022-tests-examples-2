# -*- coding: utf-8 -*-
from datetime import datetime
from unittest import TestCase

from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.db.faker.db import (
    aliases_insert,
    attribute_table_insert,
    attribute_table_insert_on_duplicate_append_key,
    attribute_table_insert_on_duplicate_increment_key,
    attribute_table_insert_on_duplicate_update_if_value_equals,
    attribute_table_insert_on_duplicate_update_key,
    insert_ignore_into_removed_aliases,
    passman_recovery_key_insert,
    yakey_backup_insert,
    yakey_backup_update,
)
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.query import DbQuery
from passport.backend.core.db.schemas import (
    aliases_table,
    attributes_table,
    passman_recovery_keys_table,
    password_history_eav_table,
    pddsuid_table,
    pdduid_table,
    removed_aliases_table,
    suid_table,
    totp_secret_id_table,
    uid_table,
    yakey_backups_table,
)
from passport.backend.core.db.utils import with_ignore_prefix
from passport.backend.core.models.domain import Domain
from passport.backend.core.serializers.eav.query import (
    DeleteAliasWithValueQuery,
    EavDeleteAliasQuery,
    EavDeleteAllEmailsQuery,
    EavDeleteAttributeQuery,
    EavDeleteEmailBindingQuery,
    EavDeleteEmailQuery,
    EavDeleteSuidQuery,
    EavInsertAliasQuery,
    EavInsertAttributeQuery,
    EavInsertAttributeWithOnDuplicateKeyAppendQuery,
    EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery,
    EavInsertAttributeWithOnDuplicateKeyIncrementQuery,
    EavInsertAttributeWithOnDuplicateKeyUpdateQuery,
    EavInsertEmailBindingQuery,
    EavInsertPasswordHistoryQuery,
    EavInsertSuidQuery,
    EavSuidIncrementQuery,
    EavSuidQuery,
    EavTotpSecretIdIncrementQuery,
    EavUidIncrementQuery,
    EavUpdateAliasQuery,
    InsertAliasesWithValueIntoRemovedAliasesQuery,
    InsertAllPddAliasesFromAccountIntoRemovedAliasesQuery,
    MassInsertAliasesIntoRemovedAliasesQuery,
    PassManDeleteAllRecoveryKeysQuery,
    PassManInsertRecoveryKeyQuery,
    SUID_TABLES,
    YaKeyBackupCreateQuery,
    YaKeyBackupDeleteQuery,
    YaKeyBackupUpdateQuery,
)
from passport.backend.core.serializers.query import (
    GenericQuery,
    GenericUpdateQuery,
)
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from sqlalchemy.schema import (
    Column,
    MetaData,
    Table,
)
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import (
    and_,
    or_,
    text,
)
from sqlalchemy.types import (
    Integer,
    VARBINARY,
)


TEST_UID = 1
TEST_UID2 = 2
TEST_ADDRESS = 'test@test.ru'
TEST_EMAIL_ID = 1
TEST_BOUND_AT = datetime(2016, 5, 16, 12, 1, 0)

TEST_PHONE_NUMBER_DIGITAL = 79090000001
TEST_OTHER_PHONE_NUMBER_DIGITAL = 79090000002
TEST_BACKUP_1 = 'abc123-x'
TEST_BACKUP_2 = 'abc123-y'
TEST_PREVIOUS_UPDATE = datetime(2016, 1, 2)
TEST_DEVICE_NAME = 'device'

TEST_CYRILLIC_DOMAIN_IDNA = u'окна.рф'.encode('idna').decode('utf8')
TEST_CYRILLIC_DOMAIN = u'окна.рф'
TEST_LATIN_DOMAIN = 'dom.ru'

TEST_PASSMAN_KEY_ID = b'\xd1\x8a' * 16
TEST_PASSMAN_KEY_ID_2 = b'\xd1\x8b' * 16
TEST_PASSMAN_RECOVERY_KEY = b'\xd1\x8c' * 16


class TestInsertEmailBindingQuery(TestCase):

    def setUp(self):
        self.query = EavInsertEmailBindingQuery(
            TEST_UID,
            TEST_ADDRESS,
            TEST_EMAIL_ID,
            TEST_BOUND_AT,
        )

    def test_query_params(self):
        eq_(
            self.query.query_params(),
            [
                TEST_ADDRESS,
                TEST_EMAIL_ID,
                TEST_BOUND_AT,
            ],
        )

    def test_repr(self):
        eq_(
            repr(self.query),
            "<EavInsertEmailBindingQuery: uid: %d | params: [%r, %r, %r]>" % (
                TEST_UID,
                TEST_ADDRESS,
                TEST_EMAIL_ID,
                TEST_BOUND_AT,
            ),
        )


class TestDeleteEmailBindingQuery(TestCase):

    def setUp(self):
        self.query = EavDeleteEmailBindingQuery(
            TEST_UID,
            TEST_EMAIL_ID,
        )

    def test_query_params(self):
        eq_(
            self.query.query_params(),
            [
                TEST_EMAIL_ID,
            ],
        )

    def test_repr(self):
        eq_(
            repr(self.query),
            "<EavDeleteEmailBindingQuery: uid: %d | params: [%r]>" % (
                TEST_UID,
                TEST_EMAIL_ID,
            ),
        )


class TestDeleteEmailQuery(TestCase):

    def setUp(self):
        self.query = EavDeleteEmailQuery(
            TEST_UID,
            TEST_EMAIL_ID,
        )

    def test_query_params(self):
        eq_(
            self.query.query_params(),
            [
                TEST_EMAIL_ID,
            ],
        )

    def test_repr(self):
        eq_(
            repr(self.query),
            "<EavDeleteEmailQuery: uid: %d | params: [%r]>" % (
                TEST_UID,
                TEST_EMAIL_ID,
            ),
        )


class TestDeleteAllEmailsQuery(TestCase):

    def setUp(self):
        self.query = EavDeleteAllEmailsQuery(TEST_UID)

    def test_query_params(self):
        eq_(
            self.query.query_params(),
            [],
        )

    def test_repr(self):
        eq_(
            repr(self.query),
            "<EavDeleteAllEmailsQuery: uid: %d | params: []>" % TEST_UID,
        )


class TestEavAttributeQuery(TestCase):
    def test_insert_to_odk_update_query(self):
        uid = 123
        types_values = [(1, u'значение1'), (3, u'значение2')]
        q = EavInsertAttributeWithOnDuplicateKeyUpdateQuery(uid, types_values)
        eq_eav_queries(
            [q],
            [
                attribute_table_insert_on_duplicate_update_key().values(
                    [
                        {
                            'uid': uid,
                            'type': eav_type,
                            'value': value.encode('utf-8'),
                        } for eav_type, value in types_values
                    ],
                ),
            ],
        )

    def test_insert_to_odk_update_if_equals_query__ok(self):
        uid, expected, new_value = 123, 'expected', u'значение1'
        types_values = [(13, (expected, new_value))]
        q = EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery(uid, types_values)
        eq_eav_queries(
            [q],
            [
                attribute_table_insert_on_duplicate_update_if_value_equals(expected).values(
                    [
                        {
                            'uid': uid,
                            'type': 13,
                            'value': new_value.encode('utf-8'),
                        },
                    ],
                ),
            ],
        )

    @raises(ValueError)
    def test_insert_to_odk_update_if_equals_query__too_many_values__error(self):
        types_values = [
            (13, ('expected', 'new_value')),
            (14, ('old-value', 'new-value')),
        ]
        q = EavInsertAttributeWithOnDuplicateKeyIfValueEqualsUpdateQuery(123, types_values)
        q.to_query()

    def test_insert_to_odk_append_query(self):
        uid = 123
        types_values = [(1, u'значение1'), (3, u'значение2')]
        q = EavInsertAttributeWithOnDuplicateKeyAppendQuery(uid, types_values)
        eq_eav_queries(
            [q],
            [
                attribute_table_insert_on_duplicate_append_key().values(
                    [
                        {
                            'uid': uid,
                            'type': eav_type,
                            'value': value.encode('utf-8'),
                        } for eav_type, value in types_values
                    ],
                ),
            ],
        )

    def test_insert_to_odk_increment_query(self):
        uid = 123
        types_values = [(1, '11'), (3, 0)]
        q = EavInsertAttributeWithOnDuplicateKeyIncrementQuery(uid, types_values)
        eq_eav_queries(
            [q],
            [
                attribute_table_insert_on_duplicate_increment_key().values(
                    [
                        {
                            'uid': uid,
                            'type': eav_type,
                            'value': str(value).encode('utf8'),
                        } for eav_type, value in types_values
                    ],
                ),
            ],
        )

    def test_join_insert_odk_query(self):
        uid = 123
        q1 = EavInsertAttributeWithOnDuplicateKeyUpdateQuery(uid, [(1, 2), (3, 4)])
        q2 = EavInsertAttributeWithOnDuplicateKeyUpdateQuery(uid, [(5, 6), (7, 8)])
        q3 = q1 + q2
        eq_(q3.uid, 123)
        eq_(q3.types_values, [(1, 2), (3, 4), (5, 6), (7, 8)])

    def test_insert_to_query(self):
        uid = 123
        types_values = [(1, u'значение1'), (3, u'значение2')]
        q = EavInsertAttributeQuery(uid, types_values)
        eq_eav_queries(
            [q],
            [
                attribute_table_insert().values(
                    [
                        {
                            'uid': uid,
                            'type': eav_type,
                            'value': value.encode('utf-8'),
                        } for eav_type, value in types_values
                    ],
                ),
            ],
        )

    def test_join_insert_query(self):
        uid = 123
        q1 = EavInsertAttributeQuery(uid, [(1, 2), (3, 4)])
        q2 = EavInsertAttributeQuery(uid, [(5, 6), (7, 8)])
        q3 = q1 + q2
        eq_(q3.uid, 123)
        eq_(q3.types_values, [(1, 2), (3, 4), (5, 6), (7, 8)])

    def test_delete_to_query(self):
        uid = 123
        types = [1, 2, 3]
        q = EavDeleteAttributeQuery(uid, types)
        eq_eav_queries(
            [q],
            [
                attributes_table.delete().where(
                    and_(attributes_table.c.uid == uid, attributes_table.c.type.in_(types))),
            ],
        )

    def test_join_delete_query(self):
        uid = 123
        q1 = EavDeleteAttributeQuery(uid, [1, 2, 3])
        q2 = EavDeleteAttributeQuery(uid, [4, 5, 6])
        q3 = q1 + q2
        eq_eav_queries(
            [q3],
            [
                attributes_table.delete().where(
                    and_(attributes_table.c.uid == uid, attributes_table.c.type.in_([1, 2, 3, 4, 5, 6]))),
            ],
        )

    @raises(TypeError)
    def test_join_not_same_type(self):
        q1 = EavInsertAttributeQuery(1, [])
        q2 = EavInsertAttributeWithOnDuplicateKeyUpdateQuery(1, [])
        q1 + q2

    @raises(ValueError)
    def test_join_odk_query_with_different_uid(self):
        q1 = EavInsertAttributeWithOnDuplicateKeyUpdateQuery(1, [])
        q2 = EavInsertAttributeWithOnDuplicateKeyUpdateQuery(2, [])
        q1 + q2

    @raises(ValueError)
    def test_join_query_with_different_uid(self):
        q1 = EavInsertAttributeQuery(1, [])
        q2 = EavInsertAttributeQuery(2, [])
        q1 + q2

    def test_eq(self):
        for value in [1, '', None, DbQuery()]:
            for cls in [EavInsertAttributeQuery, EavInsertAttributeWithOnDuplicateKeyUpdateQuery, EavDeleteAttributeQuery]:
                eq_(cls(1, []) == value, False)

        eq_(EavInsertAttributeQuery(1, [(1, 2)]), EavInsertAttributeQuery(1, [(1, 2)]))
        eq_(
            EavInsertAttributeWithOnDuplicateKeyUpdateQuery(1, [(1, 2)]),
            EavInsertAttributeWithOnDuplicateKeyUpdateQuery(1, [(1, 2)]),
        )
        eq_(EavDeleteAttributeQuery(1, [1, 2]), EavDeleteAttributeQuery(1, [1, 2]))
        ok_(EavInsertAttributeWithOnDuplicateKeyUpdateQuery(1, []) != EavInsertAttributeQuery(1, []))

    def test_repr(self):
        eq_(repr(EavInsertAttributeQuery(1, [(1, 2)])),
            "<EavInsertAttributeQuery: uid: 1 | params: [(1, 2)]>")
        eq_(repr(EavDeleteAttributeQuery(1, [1])),
            "<EavDeleteAttributeQuery: uid: 1 | params: [1]>")


class TestEavPasswordHistoryQuery(TestCase):
    def test_insert_to_query(self):
        uid = 123
        history = [
            (datetime.fromtimestamp(1), '11', 1),
            (datetime.fromtimestamp(2), '22', 2),
        ]
        q = EavInsertPasswordHistoryQuery(uid, history)

        eq_eav_queries(
            [q],
            [
                password_history_eav_table.insert().values(
                    [
                        {
                            'uid': uid,
                            'ts': datetime.fromtimestamp(i),
                            'encrypted_password': str(i).encode('utf8') * 2,
                            'reason': i,
                        }
                        for i in [1, 2]
                    ],
                ),
            ],
        )

    def test_join_insert_query(self):
        uid = 123
        dt1 = datetime.fromtimestamp(1)
        dt2 = datetime.fromtimestamp(2)
        q1 = EavInsertPasswordHistoryQuery(uid, [(dt1, '11', 1)])
        q2 = EavInsertPasswordHistoryQuery(uid, [(dt2, '22', 2)])
        q3 = q1 + q2
        eq_(q3.uid, 123)
        eq_(q3.password_history, [(dt1, '11', 1), (dt2, '22', 2)])
        eq_eav_queries(
            [q3],
            [
                password_history_eav_table.insert().values(
                    [
                        {'uid': 123, 'ts': dt1, 'encrypted_password': b'11', 'reason': 1},
                        {'uid': 123, 'ts': dt2, 'encrypted_password': b'22', 'reason': 2},
                    ],
                ),
            ],
        )

    @raises(TypeError)
    def test_join_not_same_type(self):
        q1 = EavInsertPasswordHistoryQuery(1, [])
        q2 = DbQuery()
        q1 + q2

    @raises(ValueError)
    def test_join_query_with_different_uid(self):
        q1 = EavInsertPasswordHistoryQuery(1, [])
        q2 = EavInsertPasswordHistoryQuery(2, [])
        q1 + q2

    def test_eq(self):
        for value in [1, '', None, DbQuery()]:
            for cls in [EavInsertPasswordHistoryQuery]:
                eq_(cls(1, []) == value, False)

        dt = dt = datetime.fromtimestamp(1)
        eq_(EavInsertPasswordHistoryQuery(1, [(dt, '1')]), EavInsertPasswordHistoryQuery(1, [(dt, '1')]))
        ok_(EavInsertPasswordHistoryQuery(1, [(dt, '1')]) != EavInsertPasswordHistoryQuery(1, [(dt, '2')]))

    def test_repr(self):
        dt = datetime.fromtimestamp(1)
        eq_(
            repr(EavInsertPasswordHistoryQuery(1, [(dt, '1')])),
            "<EavInsertPasswordHistoryQuery: uid: 1 | params: [(%s, '1')]>" % repr(dt),
        )


class TestEavSuidQuery(TestCase):
    def setUp(self):
        self.uid = 1
        self.sid = 2
        self.suid = 100

    def test_get_table(self):
        for sid, table in SUID_TABLES.items():
            eq_(EavSuidQuery(self.uid, sid).get_table(), table)

    def test_insert_to_query(self):
        q = EavInsertSuidQuery(self.uid, self.sid, self.suid)
        eq_eav_queries(
            [q],
            [
                SUID_TABLES[self.sid].insert().values({'suid': self.suid, 'uid': self.uid}),
            ],
        )

    def test_delete_to_query(self):
        q = EavDeleteSuidQuery(self.uid, self.sid)
        table = SUID_TABLES[self.sid]
        eq_eav_queries(
            [q],
            [
                table.delete().where(table.c.uid == self.uid),
            ],
        )

    def test_eq(self):
        delete_query = EavDeleteSuidQuery(self.uid, self.sid)
        insert_query = EavInsertSuidQuery(self.uid, self.sid, self.suid)

        eq_(delete_query == DbQuery(), False)
        eq_(insert_query == DbQuery(), False)
        eq_(insert_query == delete_query, False)

        eq_(EavInsertSuidQuery(self.uid, self.sid, self.suid + 1) == insert_query, False)
        eq_(EavDeleteSuidQuery(self.uid, self.sid + 1) == delete_query, False)

        eq_(EavInsertSuidQuery(self.uid, self.sid, self.suid), insert_query)
        eq_(EavDeleteSuidQuery(self.uid, self.sid), delete_query)

    def test_repr(self):
        eq_(repr(EavInsertSuidQuery(self.uid, self.sid, self.suid)),
            '<EavInsertSuidQuery: uid: 1 | sid: 2 | suid: 100>')
        eq_(repr(EavDeleteSuidQuery(self.uid, self.sid)),
            '<EavDeleteSuidQuery: uid: 1 | sid: 2>')


class TestEavAliasQuery(TestCase):
    def test_insert_to_query(self):
        q = EavInsertAliasQuery(123, [(2, 'somevalue', 2)])
        eq_eav_queries(
            [q],
            [
                aliases_insert().values(
                    {
                        'uid': 123,
                        'type': 2,
                        'value': b'somevalue',
                        'surrogate_type': b'2',
                    },
                ),
            ],
        )

    def test_delete_to_query(self):
        q = EavDeleteAliasQuery(123, [2, 4, 5])
        eq_eav_queries(
            [q],
            [
                aliases_table.delete().where(
                    and_(aliases_table.c.uid == 123, aliases_table.c.type.in_([2, 4, 5]))),
            ],
        )

    def test_delete_with_value_to_query_1(self):
        q = DeleteAliasWithValueQuery(123, [(1, 'value')])
        eq_eav_queries(
            [q],
            [
                aliases_table.delete().where(
                    and_(aliases_table.c.uid == 123, aliases_table.c.type == 1, aliases_table.c.value == b'value')),
            ],
        )

    def test_delete_with_value_to_query_2(self):
        q = DeleteAliasWithValueQuery(123, [(1, 'value1'), (2, 'value2')])
        eq_eav_queries(
            [q],
            [
                aliases_table.delete().where(
                    and_(
                        aliases_table.c.uid == 123,
                        or_(
                            and_(aliases_table.c.type == 1, aliases_table.c.value == b'value1'),
                            and_(aliases_table.c.type == 2, aliases_table.c.value == b'value2'),
                        ),
                    ),
                ),
            ],
        )

    def test_eq(self):
        for value in [1, '', None, DbQuery()]:
            for cls in [EavInsertAliasQuery, EavDeleteAliasQuery, DeleteAliasWithValueQuery]:
                eq_(cls(1, []) == value, False)

        eq_(EavInsertAliasQuery(1, [(2, 'somevalue')]), EavInsertAliasQuery(1, [(2, 'somevalue')]))
        eq_(EavDeleteAliasQuery(123, [2, 4, 5]), EavDeleteAliasQuery(123, [2, 4, 5]))
        eq_(DeleteAliasWithValueQuery(123, [(1, 'value1'), (2, 'value2')]),
            DeleteAliasWithValueQuery(123, [(1, 'value1'), (2, 'value2')]))

    def test_repr(self):
        eq_(
            repr(EavInsertAliasQuery(123, [(2, 'somevalue')])),
            "<EavInsertAliasQuery: uid: 123 | types_values: [(2, 'somevalue')]>",
        )
        eq_(
            repr(EavUpdateAliasQuery(123, 2, 'somevalue', 2)),
            "<EavUpdateAliasQuery: uid: 123 | types_values: (2, 'somevalue', 2)>",
        )
        eq_(
            repr(EavDeleteAliasQuery(123, [2, 4, 5])),
            '<EavDeleteAliasQuery: uid: 123 | types: [2, 4, 5]>',
        )
        eq_(
            repr(DeleteAliasWithValueQuery(123, [(1, 'value')])),
            "<DeleteAliasWithValueQuery: uid: 123 | types_values: [(1, 'value')]>",
        )


class TestInsertAliasesWithValueIntoRemovedAliasesQuery(TestCase):
    def test_insert_query(self):
        test_data = [
            (7, 'login1'),
            (7, 'login2'),
            (8, 'login1'),
        ]
        q = InsertAliasesWithValueIntoRemovedAliasesQuery(
            123,
            test_data,
        )
        expected_query = with_ignore_prefix(
            removed_aliases_table.insert().values([
                {
                    'type': alias_type,
                    'value': value.encode('utf8'),
                    'uid': 123,
                }
                for alias_type, value
                in test_data
            ]),
        )
        eq_eav_queries([q], [expected_query])

    def test_join_insert_query(self):
        q1 = InsertAliasesWithValueIntoRemovedAliasesQuery(123, [(7, 'value')])
        q2 = InsertAliasesWithValueIntoRemovedAliasesQuery(123, [(8, 'value1')])
        q3 = q1 + q2
        eq_(q3.uid, 123)
        eq_(
            q3.types_values,
            [
                (7, 'value'),
                (8, 'value1'),
            ],
        )

    def test_repr(self):
        eq_(
            repr(InsertAliasesWithValueIntoRemovedAliasesQuery(123, [(7, 'value'), (8, 'value1')])),
            "<InsertAliasesWithValueIntoRemovedAliasesQuery: uid: 123 | types_values: [(7, 'value'), (8, 'value1')]>",
        )


class TestInsertAllPddAliasesFromAccountIntoRemovedAliasesQuery(TestCase):
    def domain_data(self, domain):
        return {
            'hosted_domains': [
                {
                    'born_date': '2010-10-12 15:03:24',
                    'default_uid': '0',
                    'admin': '1',
                    'domid': '1',
                    'options': '{}',
                    'slaves': '',
                    'master_domain': '',
                    'mx': '0',
                    'domain': domain,
                    'ena': '1',
                },
            ],
        }

    def test_insert_to_query(self):
        for test_domain in (
            TEST_LATIN_DOMAIN,
            TEST_CYRILLIC_DOMAIN,
            TEST_CYRILLIC_DOMAIN_IDNA,
        ):
            q = InsertAllPddAliasesFromAccountIntoRemovedAliasesQuery(
                TEST_UID,
                Domain().parse(self.domain_data(test_domain)),
            )
            expected_query = insert_ignore_into_removed_aliases(
                select(
                    [
                        aliases_table.c.uid,
                        aliases_table.c.type,
                        text('''concat('%s', SUBSTR(aliases.value, LOCATE('/', aliases.value)))''' % (
                            test_domain.encode('idna').decode('utf8'),
                        )),
                    ],
                ).where(
                    and_(
                        aliases_table.c.uid == 1,
                        aliases_table.c.type.in_([7, 8]),
                    ),
                ),
            )
            eq_eav_queries([q], [expected_query])

    def test_join_insert_query(self):
        uid = TEST_UID
        q1 = InsertAllPddAliasesFromAccountIntoRemovedAliasesQuery(uid, Domain().parse(self.domain_data(TEST_CYRILLIC_DOMAIN)))
        q2 = InsertAllPddAliasesFromAccountIntoRemovedAliasesQuery(uid, Domain().parse(self.domain_data(TEST_LATIN_DOMAIN)))
        q3 = q1 + q2
        eq_(q3.uid, TEST_UID)
        eq_(q3.domain, [TEST_CYRILLIC_DOMAIN, TEST_LATIN_DOMAIN])


class TestInsertAliasIntoRemovedAliasesQuery(TestCase):
    def test_insert_to_query(self):
        q = MassInsertAliasesIntoRemovedAliasesQuery(123, [1, 2, 3, 4])
        expected_query = insert_ignore_into_removed_aliases(
            select([aliases_table.c.uid, aliases_table.c.type, aliases_table.c.value]).where(
                and_(
                    aliases_table.c.uid == 123,
                    aliases_table.c.type.in_([1, 2, 3, 4]),
                )
            )
        )
        eq_eav_queries([q], [expected_query])

    def test_join_insert_query(self):
        uid = 123
        q1 = MassInsertAliasesIntoRemovedAliasesQuery(uid, [1, 2, 3])
        q2 = MassInsertAliasesIntoRemovedAliasesQuery(uid, [4, 5])
        q3 = q1 + q2
        eq_(q3.uid, 123)
        eq_(q3.types, [1, 2, 3, 4, 5])

    @raises(TypeError)
    def test_join_not_same_type(self):
        q1 = MassInsertAliasesIntoRemovedAliasesQuery(1, [])
        q2 = DbQuery()
        q1 + q2

    @raises(ValueError)
    def test_join_query_with_different_uid(self):
        q1 = MassInsertAliasesIntoRemovedAliasesQuery(1, [])
        q2 = MassInsertAliasesIntoRemovedAliasesQuery(2, [])
        q1 + q2

    def test_eq(self):
        for value in [1, '', None, DbQuery()]:
            eq_(MassInsertAliasesIntoRemovedAliasesQuery(1, []) == value, False)

        eq_(MassInsertAliasesIntoRemovedAliasesQuery(1, [1, 2]), MassInsertAliasesIntoRemovedAliasesQuery(1, [1, 2]))
        ok_(MassInsertAliasesIntoRemovedAliasesQuery(1, [1, 2]) != MassInsertAliasesIntoRemovedAliasesQuery(1, [1, 2, 3]))

    def test_repr(self):
        eq_(repr(MassInsertAliasesIntoRemovedAliasesQuery(123, [1, 2, 3])),
            "<MassInsertAliasesIntoRemovedAliasesQuery: uid: 123 | types: [1, 2, 3]>")


class TestEavUidIncrementQuery(TestCase):
    def test_to_query(self):
        q = EavUidIncrementQuery(False)
        expected_query = uid_table.insert().values({'id': None})
        eq_eav_queries([q], [expected_query])

    def test_pdd_to_query(self):
        q = EavUidIncrementQuery(True)
        expected_query = pdduid_table.insert().values({'id': None})
        eq_eav_queries([q], [expected_query])

    @raises(TypeError)
    def test_not_joinable(self):
        q1 = EavUidIncrementQuery(False)
        q2 = EavUidIncrementQuery(False)
        q1 + q2

    def test_repr(self):
        eq_(repr(EavUidIncrementQuery(False)),
            "<EavUidIncrementQuery: is_pdd: False | table: uid>")

    def test_pdd_repr(self):
        eq_(repr(EavUidIncrementQuery(True)),
            "<EavUidIncrementQuery: is_pdd: True | table: pdduid>")


class TestEavSuidIncrementQuery(TestCase):
    def test_to_query(self):
        q = EavSuidIncrementQuery(False)
        expected_query = suid_table.insert().values({'id': None})
        eq_eav_queries([q], [expected_query])

    def test_pdd_to_query(self):
        q = EavSuidIncrementQuery(True)
        expected_query = pddsuid_table.insert().values({'id': None})
        eq_eav_queries([q], [expected_query])

    @raises(TypeError)
    def test_not_joinable(self):
        q1 = EavSuidIncrementQuery(False)
        q2 = EavSuidIncrementQuery(False)
        q1 + q2

    def test_repr(self):
        eq_(repr(EavSuidIncrementQuery(False)),
            "<EavSuidIncrementQuery: is_pdd: False | table: suid>")

    def test_pdd_repr(self):
        eq_(repr(EavSuidIncrementQuery(True)),
            "<EavSuidIncrementQuery: is_pdd: True | table: pddsuid>")


class TestEavTotpSecretIdIncrementQuery(TestCase):
    def test_to_query(self):
        q = EavTotpSecretIdIncrementQuery()
        expected_query = totp_secret_id_table.insert().values({'id': None})
        eq_eav_queries([q], [expected_query])

    @raises(TypeError)
    def test_not_joinable(self):
        q1 = EavTotpSecretIdIncrementQuery()
        q2 = EavTotpSecretIdIncrementQuery()
        q1 + q2

    def test_repr(self):
        eq_(
            repr(EavTotpSecretIdIncrementQuery()),
            '<EavTotpSecretIdIncrementQuery: table: totp_secret_id>',
        )


class TestGenericQueries(TestCase):

    def setUp(self):
        super(TestGenericQueries, self).setUp()
        self.metadata = MetaData()
        self.table = Table(
            'test_table',
            self.metadata,
            Column('test_name', VARBINARY(length=255), nullable=False),
        )

    @raises(RuntimeError)
    def test_generic_no_table_specified(self):
        q = GenericQuery(None, {})
        q.get_pk_field()

    @raises(RuntimeError)
    def test_generic_no_pk_in_table(self):
        q = GenericQuery(self.table, {})
        q.get_pk_field()

    def test_update_generic_case(self):
        pk_table = Table(
            'test_table',
            MetaData(),
            Column('id', Integer, primary_key=True),
            Column('test_name', VARBINARY(length=255), nullable=False),
        )
        q = GenericUpdateQuery(
            pk_table,
            1,
            {
                'test_name': 'new_name',
            },
        )
        eq_eav_queries(
            [q],
            [
                pk_table.update().values(test_name=b'new_name').where(
                    pk_table.c.id == 1,
                )
            ],
        )

    def test_update_filter_by(self):
        """
        Проверяем, что GenericUpdateQuery можно указать специализированный
        запрос и это будет отражено в запросе к БД.
        """
        q = GenericUpdateQuery(
            self.table,
            1,
            {
                'test_name': 'new_name',
            },
            filter_by=(self.table.c.test_name == b'hello, world'),
        )
        eq_eav_queries(
            [q],
            [
                self.table.update().values(test_name=b'new_name').where(
                    self.table.c.test_name == b'hello, world'
                )
            ],
        )


class TestYaKeyBackupCreateQuery(TestCase):
    def test_to_query(self):
        q = YaKeyBackupCreateQuery(
            TEST_PHONE_NUMBER_DIGITAL,
            TEST_BACKUP_1,
            DatetimeNow(),
            TEST_DEVICE_NAME,
        )
        eq_eav_queries(
            [q],
            [
                yakey_backup_insert().values(
                    [
                        {
                            'phone_number': TEST_PHONE_NUMBER_DIGITAL,
                            'backup': TEST_BACKUP_1.encode('utf8'),
                            'device_name': TEST_DEVICE_NAME,
                            'updated': DatetimeNow(),
                        },
                    ],
                ),
            ],
        )

    @raises(TypeError)
    def test_can_not_be_joined(self):
        q1 = YaKeyBackupCreateQuery(TEST_PHONE_NUMBER_DIGITAL, TEST_BACKUP_1, DatetimeNow(), None)
        q2 = YaKeyBackupCreateQuery(TEST_PHONE_NUMBER_DIGITAL, TEST_BACKUP_2, DatetimeNow(), None)
        q1 + q2


class TestYaKeyBackupUpdateQuery(TestCase):
    def test_to_query(self):
        q = YaKeyBackupUpdateQuery(
            TEST_PHONE_NUMBER_DIGITAL,
            TEST_BACKUP_2,
            DatetimeNow(),
            previous_update=TEST_PREVIOUS_UPDATE,
            device_name=TEST_DEVICE_NAME,
        )
        eq_eav_queries(
            [q],
            [
                yakey_backup_update(TEST_PREVIOUS_UPDATE).values(
                    [
                        {
                            'phone_number': TEST_PHONE_NUMBER_DIGITAL,
                            'backup': TEST_BACKUP_2.encode('utf8'),
                            'device_name': TEST_DEVICE_NAME,
                            'updated': DatetimeNow(),
                        },
                    ],
                ),
            ],
        )

    @raises(TypeError)
    def test_can_not_be_joined(self):
        q1 = YaKeyBackupUpdateQuery(
            TEST_PHONE_NUMBER_DIGITAL,
            TEST_BACKUP_1,
            DatetimeNow(),
            TEST_PREVIOUS_UPDATE,
            None,
        )
        q2 = YaKeyBackupUpdateQuery(
            TEST_PHONE_NUMBER_DIGITAL,
            TEST_BACKUP_2,
            DatetimeNow(),
            TEST_PREVIOUS_UPDATE,
            None,
        )
        q1 + q2


class TestYaKeyBackupDeleteQuery(TestCase):
    def test_to_query(self):
        q = YaKeyBackupDeleteQuery(TEST_PHONE_NUMBER_DIGITAL)
        eq_eav_queries(
            [q],
            [
                yakey_backups_table.delete().where(
                    yakey_backups_table.c.phone_number == TEST_PHONE_NUMBER_DIGITAL,
                ),
            ],
        )

    @raises(TypeError)
    def test_can_not_be_joined(self):
        q1 = YaKeyBackupDeleteQuery(TEST_PHONE_NUMBER_DIGITAL)
        q2 = YaKeyBackupDeleteQuery(TEST_OTHER_PHONE_NUMBER_DIGITAL)
        q1 + q2


class TestPassManInsertRecoveryKeyQuery(TestCase):
    def test_to_query(self):
        q = PassManInsertRecoveryKeyQuery(
            TEST_UID,
            TEST_PASSMAN_KEY_ID,
            TEST_PASSMAN_RECOVERY_KEY,
        )
        eq_eav_queries(
            [q],
            [
                passman_recovery_key_insert().values(
                    [
                        {
                            'uid': TEST_UID,
                            'key_id': TEST_PASSMAN_KEY_ID,
                            'recovery_key': TEST_PASSMAN_RECOVERY_KEY,
                        },
                    ],
                ),
            ],
        )

    @raises(TypeError)
    def test_can_not_be_joined(self):
        q1 = PassManInsertRecoveryKeyQuery(
            TEST_UID,
            TEST_PASSMAN_KEY_ID,
            TEST_PASSMAN_RECOVERY_KEY,
        )
        q2 = PassManInsertRecoveryKeyQuery(
            TEST_UID,
            TEST_PASSMAN_KEY_ID_2,
            TEST_PASSMAN_RECOVERY_KEY,
        )
        q1 + q2


class TestPassManDeleteAllRecoveryKeysQuery(TestCase):
    def test_to_query(self):
        q = PassManDeleteAllRecoveryKeysQuery(
            TEST_UID,
        )
        eq_eav_queries(
            [q],
            [
                passman_recovery_keys_table.delete().where(
                    passman_recovery_keys_table.c.uid == TEST_UID,
                ),
            ],
        )
