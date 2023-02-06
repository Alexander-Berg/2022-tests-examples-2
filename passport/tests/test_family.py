# -*- coding: utf-8 -*-
import unittest
import uuid

from nose.tools import (
    eq_,
    ok_,
    raises,
)
from nose_parameterized import parameterized
from passport.backend.core.models.family import (
    FamilyInfo,
    FamilyInvite,
    FamilyMember,
)
from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.utils.common import merge_dicts


TEST_CONTACT = 'test@test.com'
TEST_FAMILY_ID1 = 'f1'
TEST_FAMILY_ID2 = 'f2'
TEST_INVITE_ID = '8d5c8fd6-88e8-4e20-bf80-b64f8421e834'
TEST_TIMESTAMP = 1584453663.879545
TEST_USER_ID1 = 71
TEST_USER_ID2 = 72
TEST_KIDDISH_ID1 = 82


def get_family_info(
    family_id=TEST_FAMILY_ID1,
    admin_uid=TEST_USER_ID1,
    users=None,
    places=None,
    kid_uids=None,
):
    if users is None:
        users = [TEST_USER_ID1, TEST_USER_ID2]
    if places is None:
        places = range(len(users))
    assert len(users) == len(places)
    adults = {int(u): {'uid': u, 'place': p} for u, p in zip(users, places)}

    if kid_uids is None:
        kid_uids = list()
    kid_first_place_offset = 100
    kid_places = range(kid_first_place_offset, kid_first_place_offset + len(kid_uids))
    kids = {int(u): {'uid': u, 'place': p, 'is_kid': True} for u, p in zip(kid_uids, kid_places)}

    return {
        'family_id': family_id,
        'admin_uid': admin_uid,
        'users': merge_dicts(adults, kids),
    }


class TestFamilyInfoModel(PassportTestCase):
    def test_parse_basic(self):
        family_info = FamilyInfo().parse(get_family_info(kid_uids=[TEST_KIDDISH_ID1]))

        eq_(family_info.family_id, TEST_FAMILY_ID1)
        eq_(family_info.admin_uid, TEST_USER_ID1)

        family_member1 = FamilyMember().parse({
            'uid': TEST_USER_ID1,
            'place': 0,
        })
        family_member1.parent = family_info
        family_member2 = FamilyMember().parse({
            'uid': TEST_USER_ID2,
            'place': 1,
        })
        family_member2.parent = family_info
        eq_(
            family_info.members,
            {
                TEST_USER_ID1: family_member1,
                TEST_USER_ID2: family_member2,
            },
        )

        family_kid1 = FamilyMember().parse({
            'uid': TEST_KIDDISH_ID1,
            'place': 100,
        })
        family_kid1.parent = family_info
        eq_(family_info.kids.members, {TEST_KIDDISH_ID1: family_kid1})

    def test_parse_int(self):
        family_info = FamilyInfo().parse(get_family_info(1))

        eq_(family_info.family_id, TEST_FAMILY_ID1)

    @raises(ValueError)
    def test_parse_wrong(self):
        FamilyInfo().parse(get_family_info('e123'))


class TestFamilyInviteModel(unittest.TestCase):
    def test_parse_basic(self):
        family_invite = FamilyInvite().parse({
            'family_id': TEST_FAMILY_ID1,
            'invite_id': TEST_INVITE_ID,
            'issuer_uid': TEST_USER_ID1,
            'create_time': int(TEST_TIMESTAMP),
            'send_method': FamilyInvite.SEND_METHOD_SMS,
            'contact': TEST_CONTACT,
        })
        eq_(family_invite.family_id, TEST_FAMILY_ID1)
        eq_(family_invite.invite_id, TEST_INVITE_ID)
        eq_(family_invite.issuer_uid, TEST_USER_ID1)
        eq_(family_invite.create_time, int(TEST_TIMESTAMP))
        eq_(family_invite.send_method, FamilyInvite.SEND_METHOD_SMS)
        eq_(family_invite.contact, TEST_CONTACT)

    def test_parse_different_types(self):
        family_invite = FamilyInvite().parse({
            'family_id': 1,
            'invite_id': str(uuid.UUID(TEST_INVITE_ID, version=4)),
            'issuer_uid': TEST_USER_ID1,
            'create_time': TEST_TIMESTAMP,
            'send_method': FamilyInvite.SEND_METHOD_SMS,
            'contact': TEST_CONTACT,
        })
        eq_(family_invite.family_id, TEST_FAMILY_ID1)
        eq_(family_invite.invite_id, str(TEST_INVITE_ID))
        eq_(family_invite.issuer_uid, TEST_USER_ID1)
        eq_(family_invite.create_time, int(TEST_TIMESTAMP))
        eq_(family_invite.send_method, FamilyInvite.SEND_METHOD_SMS)
        eq_(family_invite.contact, TEST_CONTACT)

    def test_generate(self):
        family_invite = FamilyInvite.generate(
            TEST_FAMILY_ID1,
            FamilyInvite.SEND_METHOD_SMS,
            TEST_CONTACT,
            TEST_USER_ID1,
            TEST_TIMESTAMP,
        )
        eq_(family_invite.family_id, TEST_FAMILY_ID1)
        eq_(family_invite.issuer_uid, TEST_USER_ID1)
        ok_(family_invite.create_time, TEST_TIMESTAMP)
        eq_(str(uuid.UUID(family_invite.invite_id, version=4)), family_invite.invite_id)
        eq_(family_invite.send_method, FamilyInvite.SEND_METHOD_SMS)
        eq_(family_invite.contact, TEST_CONTACT)


class TestFamilyInfoAdmin(unittest.TestCase):
    def test_family_is_uid_admin_int(self):
        family_info = FamilyInfo().parse(
            get_family_info(users=[TEST_USER_ID1]))
        ok_(family_info.is_uid_admin(TEST_USER_ID1))

    def test_family_not_is_uid_admin_int(self):
        family_info = FamilyInfo().parse(
            get_family_info(users=[TEST_USER_ID1]))
        ok_(not family_info.is_uid_admin(TEST_USER_ID2))

    def test_family_is_uid_admin_str(self):
        family_info = FamilyInfo().parse(
            get_family_info(users=[TEST_USER_ID1]))
        ok_(family_info.is_uid_admin(str(TEST_USER_ID1)))

    def test_family_not_is_uid_admin_str(self):
        family_info = FamilyInfo().parse(
            get_family_info(users=[TEST_USER_ID1]))
        ok_(not family_info.is_uid_admin(str(TEST_USER_ID2)))


class TestFamilyInfoAdults(unittest.TestCase):
    def test_family_info_contains_member(self):
        family_info = FamilyInfo().parse(get_family_info())
        family_member = FamilyMember().parse({
            'family_id': TEST_FAMILY_ID1,
            'uid': TEST_USER_ID2,
            'place': 0,
        })

        ok_(family_member in family_info)

    def test_family_info_does_not_contain_member(self):
        family_info = FamilyInfo().parse(
            get_family_info(users=[TEST_USER_ID1]))
        family_member = FamilyMember().parse({
            'family_id': TEST_FAMILY_ID2,
            'uid': TEST_USER_ID2,
            'place': 0,
        })

        ok_(family_member not in family_info)

    def test_family_info_contains_int(self):
        family_info = FamilyInfo().parse(get_family_info())

        ok_(TEST_USER_ID1 in family_info)

    def test_family_info_does_not_contain_int(self):
        family_info = FamilyInfo().parse(
            get_family_info(users=[TEST_USER_ID1]))

        ok_(TEST_USER_ID2 not in family_info)

    def test_family_info_contains_str(self):
        family_info = FamilyInfo().parse(get_family_info())

        ok_(str(TEST_USER_ID1) in family_info)

    def test_family_info_does_not_contain_str(self):
        family_info = FamilyInfo().parse(
            get_family_info(users=[TEST_USER_ID1]))

        ok_(str(TEST_USER_ID2) not in family_info)

    def test_family_add_member_uid(self):
        family_info = FamilyInfo().parse(
            get_family_info(users=[TEST_USER_ID1]))
        family_info.add_member_uid(TEST_USER_ID2, 0)
        eq_(family_info.members[TEST_USER_ID2].uid, TEST_USER_ID2)

    @raises(KeyError)
    def test_family_remove_member_uid(self):
        family_info = FamilyInfo().parse(
            get_family_info(users=[TEST_USER_ID1, TEST_USER_ID2]))
        family_info.remove_member_uid(TEST_USER_ID2)
        str(family_info.members[TEST_USER_ID2])

    @raises(ValueError)
    def test_family_add_existing_member_uid(self):
        family_info = FamilyInfo().parse(
            get_family_info(users=[TEST_USER_ID1]))
        family_info.add_member_uid(TEST_USER_ID1, 0)

    @raises(ValueError)
    def test_family_remove_non_existing_member_uid(self):
        family_info = FamilyInfo().parse(
            get_family_info(users=[TEST_USER_ID1]))
        family_info.remove_member_uid(TEST_USER_ID2)

    @parameterized.expand(
        [
            ([], [], 0),
            ([TEST_USER_ID1], [0], 1),
            ([TEST_USER_ID1], [4], 0),
            ([TEST_USER_ID1, TEST_USER_ID2], [0, 1], 2),
            ([TEST_USER_ID1, TEST_USER_ID2], [0, 2], 1),
            ([TEST_USER_ID1, TEST_USER_ID2], [1, 2], 0),
            ([TEST_USER_ID1, TEST_USER_ID2, TEST_USER_ID2 + 1], [0, 2, 4], 1),
            ([TEST_USER_ID1, TEST_USER_ID2, TEST_USER_ID2 + 1], [0, 1, 2], 3),
            ([TEST_USER_ID1, TEST_USER_ID2, TEST_USER_ID2 + 1, TEST_USER_ID2 + 2], [0, 1, 2, 3], None),
            ([TEST_USER_ID1, TEST_USER_ID2, TEST_USER_ID2 + 1, TEST_USER_ID2 + 2], [0, 1, 2, 4], None),
            ([TEST_USER_ID1, TEST_USER_ID2, TEST_USER_ID2 + 1, TEST_USER_ID2 + 2], [1, 2, 3, 4], None),
        ]
    )
    def test_get_first_free_place(self, users, places, expected):
        family_info = FamilyInfo().parse(
            get_family_info(users=users, places=places),
        )
        place = family_info.get_first_free_place(4)
        if expected is None:
            self.assertIsNone(place)
        else:
            eq_(place, expected)

    @parameterized.expand(
        [
            ([TEST_USER_ID1], [0], 0, TEST_USER_ID1),
            ([str(TEST_USER_ID1)], [0], 0, TEST_USER_ID1),
            ([str(TEST_USER_ID1)], [4], 4, TEST_USER_ID1),
            ([TEST_USER_ID1, TEST_USER_ID2], [0, 1], 1, TEST_USER_ID2),
            ([TEST_USER_ID1, TEST_USER_ID2], [0, 4], 4, TEST_USER_ID2),
            ([TEST_USER_ID1, TEST_USER_ID2], [4, 0], 4, TEST_USER_ID1),
            ([TEST_USER_ID1, TEST_USER_ID2, TEST_USER_ID2 + 1, TEST_USER_ID2 + 2], [0, 1, 2, 3], 3, TEST_USER_ID2 + 2),
            ([TEST_USER_ID1, TEST_USER_ID2, TEST_USER_ID2 + 1, TEST_USER_ID2 + 2], [0, 3, 1, 2], 1, TEST_USER_ID2 + 1),
            ([TEST_USER_ID1, TEST_USER_ID2, TEST_USER_ID2 + 1, TEST_USER_ID2 + 2], [0, 3, 4, 5], 3, TEST_USER_ID2),
            ([TEST_USER_ID1, TEST_USER_ID2, TEST_USER_ID2 + 1, TEST_USER_ID2 + 2], [0, 1, 2, 5], 5, TEST_USER_ID2 + 2),
            ([TEST_USER_ID1, TEST_USER_ID2, TEST_USER_ID2 + 1, TEST_USER_ID2 + 2], [0, 3, 5, 4], 3, TEST_USER_ID2),
        ]
    )
    def test_get_member_uid_by_place(self, users, places, place, expected):
        family_info = FamilyInfo().parse(
            get_family_info(users=users, places=places),
        )
        uid = family_info.get_member_uid_by_place(place)
        self.assertEqual(uid, expected)

        # Additional semi-automatic check
        for uid_auto, place_auto in zip(users, places):
            uid_got = family_info.get_member_uid_by_place(place_auto)
            self.assertEqual(uid_got, int(uid_auto), 'Wrong uid %s != %s for place %s' % (uid_got, uid_auto, place_auto))

    @parameterized.expand(
        [
            ([TEST_USER_ID1], [0], [1, 2, 3, 4]),
            ([str(TEST_USER_ID1)], [0], [1, 2, 3, 4]),
            ([str(TEST_USER_ID1)], [4], [0, 1, 2, 3]),
            ([TEST_USER_ID1, TEST_USER_ID2], [0, 1], [2, 3, 4, 5]),
            ([TEST_USER_ID1, TEST_USER_ID2], [0, 4], [1, 2, 3, 5]),
            ([TEST_USER_ID1, TEST_USER_ID2], [4, 0], [1, 2, 3, 5]),
            ([TEST_USER_ID1, TEST_USER_ID2, TEST_USER_ID2 + 1, TEST_USER_ID2 + 2], [0, 1, 2, 3], [4, 6]),
            ([TEST_USER_ID1, TEST_USER_ID2, TEST_USER_ID2 + 1, TEST_USER_ID2 + 2], [0, 3, 1, 2], [4, 6]),
            ([TEST_USER_ID1, TEST_USER_ID2, TEST_USER_ID2 + 1, TEST_USER_ID2 + 2], [0, 3, 4, 5], [1, 2, 6]),
            ([TEST_USER_ID1, TEST_USER_ID2, TEST_USER_ID2 + 1, TEST_USER_ID2 + 2], [0, 1, 2, 5], [3, 4, 6]),
            ([TEST_USER_ID1, TEST_USER_ID2, TEST_USER_ID2 + 1, TEST_USER_ID2 + 2], [0, 3, 5, 4], [1, 2, 6]),
        ]
    )
    def test_get_member_uid_by_place_error(self, users, places, try_places):
        family_info = FamilyInfo().parse(
            get_family_info(users=users, places=places),
        )
        for place in try_places:
            res = family_info.get_member_uid_by_place(place)
            self.assertIsNone(res, msg='Returned %s, not None, for place %s' % (res, place))


class TestFamilyInfoKids(unittest.TestCase):
    def setUp(self):
        super(TestFamilyInfoKids, self).setUp()
        self.family_info = FamilyInfo().parse(dict(users=dict()))

    def test_family_add_member_uid(self):
        member = FamilyMember(uid=TEST_KIDDISH_ID1, place=100)
        self.family_info.kids.add_member_uid(member.uid, member.place)

        self.assertEqual(self.family_info.kids.members, {member.uid: member})

    def test_family_remove_member_uid(self):
        member = FamilyMember(uid=TEST_KIDDISH_ID1, place=100)
        self.family_info.kids.add_member_uid(member.uid, member.place)

        self.family_info.kids.remove_member_uid(TEST_KIDDISH_ID1)

        self.assertEqual(self.family_info.kids.members, dict())

    def test_family_info_contains_member(self):
        member = FamilyMember(uid=TEST_KIDDISH_ID1, place=100)
        self.family_info.kids.add_member_uid(member.uid, member.place)

        ok_(member in self.family_info.kids)

    def test_family_info_does_not_contain_member(self):
        member1 = FamilyMember(uid=TEST_KIDDISH_ID1, place=100)
        self.family_info.kids.add_member_uid(member1.uid, member1.place)

        member2 = FamilyMember(uid=TEST_USER_ID1, place=100)
        ok_(member2 not in self.family_info.kids)

    def test_family_info_contains_int(self):
        self.family_info.kids.add_member_uid(uid=TEST_KIDDISH_ID1, place=100)

        ok_(TEST_KIDDISH_ID1 in self.family_info.kids)

    def test_family_info_does_not_contain_int(self):
        self.family_info.kids.add_member_uid(uid=TEST_KIDDISH_ID1, place=100)

        ok_(TEST_USER_ID1 not in self.family_info.kids)

    def test_family_info_contains_str(self):
        self.family_info.kids.add_member_uid(uid=TEST_KIDDISH_ID1, place=100)

        ok_(str(TEST_KIDDISH_ID1) in self.family_info.kids)

    @raises(ValueError)
    def test_family_add_existing_member_uid(self):
        self.family_info.kids.add_member_uid(uid=TEST_KIDDISH_ID1, place=100)
        self.family_info.kids.add_member_uid(uid=TEST_KIDDISH_ID1, place=101)

    @raises(ValueError)
    def test_family_remove_non_existing_member_uid(self):
        self.family_info.kids.remove_member_uid(uid=TEST_KIDDISH_ID1)

    @parameterized.expand(
        [
            ([], [], 100),
            ([TEST_USER_ID1], [100], 101),
            ([TEST_USER_ID1], [104], 100),
            ([TEST_USER_ID1, TEST_USER_ID2], [100, 101], 102),
            ([TEST_USER_ID1, TEST_USER_ID2], [100, 102], 101),
            ([TEST_USER_ID1, TEST_USER_ID2], [101, 102], 100),
            ([TEST_USER_ID1, TEST_USER_ID2, TEST_USER_ID2 + 1], [100, 102, 104], None),
            ([TEST_USER_ID1, TEST_USER_ID2, TEST_USER_ID2 + 1], [100, 101, 102], None),
        ],
    )
    def test_get_first_free_place(self, kid_uids, places, expected):
        for uid, place in zip(kid_uids, places):
            self.family_info.kids.add_member_uid(uid=uid, place=place)

        place = self.family_info.kids.get_first_free_place(3)

        if expected is None:
            self.assertIsNone(place)
        else:
            eq_(place, expected)

    @parameterized.expand(
        [
            ([TEST_USER_ID1], [100], 100, TEST_USER_ID1),
            ([TEST_USER_ID1, TEST_USER_ID2], [100, 102], 100, TEST_USER_ID1),
            ([TEST_USER_ID1, TEST_USER_ID2], [100, 102], 102, TEST_USER_ID2),
        ],
    )
    def test_get_member_uid_by_place(self, kid_uids, places, place, expected):
        for uid, other_place in zip(kid_uids, places):
            self.family_info.kids.add_member_uid(uid=uid, place=other_place)

        uid = self.family_info.kids.get_member_uid_by_place(place)

        self.assertEqual(uid, expected)

        # Additional semi-automatic check
        for uid_auto, place_auto in zip(kid_uids, places):
            uid_got = self.family_info.kids.get_member_uid_by_place(place_auto)
            self.assertEqual(uid_got, int(uid_auto), 'Wrong uid %s != %s for place %s' % (uid_got, uid_auto, place_auto))

    @parameterized.expand(
        [
            ([TEST_USER_ID1, TEST_USER_ID2], [100, 102], [101]),
            ([TEST_USER_ID1, TEST_USER_ID2], [101, 103], [100, 102, 104]),
        ],
    )
    def test_get_member_uid_by_place_error(self, kid_uids, places, try_places):
        for uid, place in zip(kid_uids, places):
            self.family_info.kids.add_member_uid(uid=uid, place=place)

        for place in try_places:
            res = self.family_info.kids.get_member_uid_by_place(place)
            self.assertIsNone(res, msg='Returned %s, not None, for place %s' % (res, place))
