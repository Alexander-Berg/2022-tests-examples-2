# -*- coding: utf-8 -*-
import unittest

from nose.tools import eq_
from passport.backend.core.db.faker.db import FakeDB
from passport.backend.core.db.faker.db_utils import (
    compile_query_with_dialect,
    eq_eav_queries,
)
from passport.backend.core.db.schemas import (
    family_info_table as fit,
    family_members_table as fmt,
)
from passport.backend.core.differ import diff
from passport.backend.core.models.family import (
    FamilyInfo,
    FamilyMember,
    KidsCollection,
)
from passport.backend.core.serializers.family import (
    AddFamilyMemberWithCheckQuery,
    CreateFamilyQuery,
    DeleteFamilyMemberQuery,
    FamilyInfoSerializer,
)
from sqlalchemy import (
    and_,
    literal_column,
    select,
)
from sqlalchemy.dialects import mysql


TEST_FAMILY_ID1 = 71
TEST_FAMILY_ID2 = 72
TEST_UID = 11805675
TEST_UID_EXTRA = 2291676
TEST_PLACE = 3
TEST_PLACE_EXTRA = 4


def prepare_member_data(member):
    return {
        'family_id': member.parent.family_id,
        'uid': member.uid,
    }


class TestFamilySerializer(unittest.TestCase):
    def setUp(self):
        self.db = FakeDB()
        self.db.start()
        self.serializer = FamilyInfoSerializer()

    def tearDown(self):
        self.db.stop()
        del self.db

    @staticmethod
    def _get_family(without_pk=False):
        f = FamilyInfo(
            admin_uid=TEST_UID,
        )
        if not without_pk:
            f.family_id = TEST_FAMILY_ID1
        f.members = {
            TEST_UID: FamilyMember(
                uid=TEST_UID,
                parent=f,
                place=TEST_PLACE,
            ),
        }
        return f

    def _family_to_db(self, family):
        with self.db.no_recording():
            self.db.insert(
                fit.name,
                'passportdbcentral',
                admin_uid=family.admin_uid,
                family_id=family._family_id,
                meta='',
            )
            for member in family.members.values():
                self.db.insert(
                    fmt.name,
                    'passportdbcentral',
                    family_id=family._family_id,
                    uid=member.uid,
                    place=member.place,
                )

    def test_create_family_query(self):
        query = CreateFamilyQuery(TEST_UID, '').to_query()
        compiled = compile_query_with_dialect(query, mysql.dialect())
        eq_(
            str(compiled),
            'INSERT INTO family_info (admin_uid, meta) '
            'VALUES (%s, %s)',
        )
        eq_(compiled.params, {
            'admin_uid': TEST_UID,
            'meta': '',
        })

    def test_delete_member_query(self):
        query = DeleteFamilyMemberQuery(TEST_FAMILY_ID1, TEST_UID).to_query()
        compiled = compile_query_with_dialect(query, mysql.dialect())
        eq_(
            str(compiled),
            'DELETE FROM family_members WHERE '
            'family_members.family_id = %s AND family_members.uid = %s',
        )
        eq_(compiled.params, {
            'uid_1':  TEST_UID,
            'family_id_1': TEST_FAMILY_ID1,
        })

    def test_add_member_with_check_query(self):
        query = AddFamilyMemberWithCheckQuery(
            family_id=TEST_FAMILY_ID1,
            uid=TEST_UID,
            place=TEST_PLACE,
            admin_uid=TEST_UID_EXTRA,
        ).to_query()
        compiled = compile_query_with_dialect(query, mysql.dialect())
        eq_(
            str(compiled),
            'INSERT INTO family_members (family_id, uid, place) SELECT '
            'family_info.family_id, %s, %s \nFROM family_info \nWHERE '
            'family_info.family_id = %%s AND family_info.admin_uid = %%s' % (
                TEST_UID,
                TEST_PLACE,
            ),
        )
        eq_(compiled.params, {
            'admin_uid_1': TEST_UID_EXTRA,
            'family_id_1': TEST_FAMILY_ID1,
        })

    def test_no_action(self):
        family = self._get_family()
        s1 = family.snapshot()
        queries = self.serializer.serialize(
            s1,
            family,
            diff(s1, family),
        )

        eq_eav_queries(queries, [])

    def test_create_family(self):
        family = self._get_family(without_pk=True)
        queries = self.serializer.serialize(
            None,
            family,
            diff(None, family),
        )
        eq_eav_queries(  # Почему EAV? Никто не знает. Без eav не работает
            queries,
            [
                'BEGIN',
                fit.insert().values(admin_uid=TEST_UID, meta=b''),
                fmt.insert().values(family_id=TEST_FAMILY_ID2, uid=TEST_UID, place=TEST_PLACE),
                'COMMIT',
            ],
            row_count=(1, 1),
            inserted_keys=(TEST_FAMILY_ID2, 0),
        )
        eq_(family._family_id, TEST_FAMILY_ID2)

        self.db._serialize_to_eav(family)
        self.db.check_table_contents('family_info', 'passportdbcentral', [
            {
                'family_id': 1,
                'admin_uid': TEST_UID,
                'meta': '',
            },
        ])
        self.db.check_table_contents('family_members', 'passportdbcentral', [
            {
                'family_id': 1,
                'uid': TEST_UID,
                'place': TEST_PLACE,
            },
        ])
        eq_(family._family_id, 1)

    def test_delete_family(self):
        family = self._get_family()

        queries = self.serializer.serialize(
            family,
            None,
            diff(family, None),
        )

        eq_eav_queries(
            queries,
            [
                'BEGIN',
                fit.delete().where(fit.c.family_id == TEST_FAMILY_ID1),
                fmt.delete().where(fmt.c.family_id == TEST_FAMILY_ID1),
                'COMMIT',
            ],
            row_count=(1, 1),
        )

        self._family_to_db(family)
        self.db.check_table_contents('family_info', 'passportdbcentral', [
            {
                'family_id': TEST_FAMILY_ID1,
                'admin_uid': TEST_UID,
                'meta': '',
            },
        ])
        self.db.check_table_contents('family_members', 'passportdbcentral', [
            {
                'family_id': TEST_FAMILY_ID1,
                'uid': TEST_UID,
                'place': TEST_PLACE,
            },
        ])
        self.db._serialize_to_eav(None, family)
        self.db.check_table_contents('family_info', 'passportdbcentral', [])
        self.db.check_table_contents('family_members', 'passportdbcentral', [])

    def test_add_family_member(self):
        family = self._get_family()
        s1 = family.snapshot()
        family.members[TEST_UID_EXTRA] = FamilyMember(
            uid=TEST_UID_EXTRA,
            parent=family,
            place=TEST_PLACE_EXTRA,
        )

        queries = self.serializer.serialize(
            s1,
            family,
            diff(s1, family),
        )

        eq_eav_queries(
            queries,
            [
                'BEGIN',
                fmt.insert().from_select(
                    fmt.c.keys(),
                    select([
                        fit.c.family_id,
                        literal_column(str(TEST_UID_EXTRA)),
                        literal_column(str(TEST_PLACE_EXTRA)),
                    ]).where(
                        and_(
                            fit.c.family_id == TEST_FAMILY_ID1,
                            fit.c.admin_uid == TEST_UID,
                        )
                    )
                ),
                'COMMIT',
            ],
        )

        self._family_to_db(s1)
        self.db.check_table_contents('family_members', 'passportdbcentral', [
            {
                'family_id': TEST_FAMILY_ID1,
                'uid': TEST_UID,
                'place': TEST_PLACE,
            },
        ])
        self.db._serialize_to_eav(family, s1)
        self.db.check_table_contents('family_members', 'passportdbcentral', [
            {
                'family_id': TEST_FAMILY_ID1,
                'uid': TEST_UID,
                'place': TEST_PLACE,
            },
            {
                'family_id': TEST_FAMILY_ID1,
                'uid': TEST_UID_EXTRA,
                'place': TEST_PLACE_EXTRA,
            },
        ])

    def test_delete_family_member(self):
        family = self._get_family()
        s1 = family.snapshot()
        family.members[TEST_UID_EXTRA] = FamilyMember(
            uid=TEST_UID_EXTRA,
            parent=family,
            place=TEST_PLACE_EXTRA,
        )

        queries = self.serializer.serialize(
            family,
            s1,
            diff(family, s1),
        )

        eq_eav_queries(
            queries,
            [
                'BEGIN',
                fmt.delete().where(
                    and_(
                        fmt.c.family_id == TEST_FAMILY_ID1,
                        fmt.c.uid == TEST_UID_EXTRA,
                    ),
                ),
                'COMMIT',
            ],
            row_count=(1, 1),
        )

        self._family_to_db(family)
        self.db.check_table_contents('family_members', 'passportdbcentral', [
            {
                'family_id': TEST_FAMILY_ID1,
                'uid': TEST_UID,
                'place': TEST_PLACE,
            },
            {
                'family_id': TEST_FAMILY_ID1,
                'uid': TEST_UID_EXTRA,
                'place': TEST_PLACE_EXTRA,
            },
        ])
        self.db._serialize_to_eav(s1, family)
        self.db.check_table_contents('family_members', 'passportdbcentral', [
            {
                'family_id': TEST_FAMILY_ID1,
                'uid': TEST_UID,
                'place': TEST_PLACE,
            },
        ])

    def test_add_kid(self):
        info = FamilyInfo(
            admin_uid=TEST_UID,
            family_id=TEST_FAMILY_ID1,
            kids=KidsCollection(members=dict()),
        )
        old = info.snapshot()

        info.kids.add_member_uid(uid=TEST_UID_EXTRA, place=TEST_PLACE_EXTRA)

        queries = self.serializer.serialize(old, info, diff(old, info))

        eq_eav_queries(
            queries,
            [
                'BEGIN',
                fmt.insert().from_select(
                    fmt.c.keys(),
                    select([
                        fit.c.family_id,
                        literal_column(str(TEST_UID_EXTRA)),
                        literal_column(str(TEST_PLACE_EXTRA)),
                    ]).where(
                        and_(
                            fit.c.family_id == TEST_FAMILY_ID1,
                            fit.c.admin_uid == TEST_UID,
                        )
                    ),
                ),
                'COMMIT',
            ],
        )
