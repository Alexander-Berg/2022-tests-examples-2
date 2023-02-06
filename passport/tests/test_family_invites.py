# -*- coding: utf-8 -*-

from passport.backend.core.models.family import FamilyInvite
from passport.backend.core.serializers.ydb.family import FamilyInviteSerializer
from passport.backend.core.test.test_utils import PassportTestCase


TEST_CONTACT = 'test@test.com'
TEST_FAMILY_ID = 'f1'
TEST_INVITE_ID = '8d5c8fd6-88e8-4e20-bf80-b64f8421e834'
TEST_TIMESTAMP = 1584453663
TEST_UID = 1


class TestFamilyInvites(PassportTestCase):
    def setUp(self):
        super(TestFamilyInvites, self).setUp()

    def get_serializer(self):
        return FamilyInviteSerializer.from_config({})

    def test_to_rows(self):
        serializer = self.get_serializer()
        invite = FamilyInvite().parse({
            'family_id': TEST_FAMILY_ID,
            'invite_id': TEST_INVITE_ID,
            'issuer_uid': TEST_UID,
            'create_time': TEST_TIMESTAMP,
            'send_method': FamilyInvite.SEND_METHOD_SMS,
            'contact': TEST_CONTACT,
        })
        rows = serializer.to_ydb_rows(invite)

        self.assertEqual(rows, [
            {
                'family_id': int(TEST_FAMILY_ID.lstrip('f')),
                'invite_id': TEST_INVITE_ID,
                'issuer_uid': TEST_UID,
                'create_time': TEST_TIMESTAMP,
                'send_method': FamilyInvite.SEND_METHOD_SMS,
                'contact': TEST_CONTACT,
            },
        ])

    def test_from_rows(self):
        serializer = self.get_serializer()
        invite = serializer.from_ydb_rows(iter([
            {
                'family_id': int(TEST_FAMILY_ID.lstrip('f')),
                'invite_id': TEST_INVITE_ID,
                'issuer_uid': TEST_UID,
                'create_time': TEST_TIMESTAMP,
                'send_method': FamilyInvite.SEND_METHOD_SMS,
                'contact': TEST_CONTACT,
            },
        ]))

        self.assertEqual(invite.family_id, TEST_FAMILY_ID)
        self.assertEqual(invite.invite_id, TEST_INVITE_ID)
        self.assertEqual(invite.issuer_uid, TEST_UID)
        self.assertEqual(invite.create_time, TEST_TIMESTAMP)
        self.assertEqual(invite.send_method, FamilyInvite.SEND_METHOD_SMS)
        self.assertEqual(invite.contact, TEST_CONTACT)
