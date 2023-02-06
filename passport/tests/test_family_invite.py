# -*- coding: utf-8 -*-
import datetime

from passport.backend.core.models.family import FamilyInvite
from passport.backend.core.test.consts import TEST_UID
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.core.ydb.declarative import (
    delete,
    insert,
    select,
)
from passport.backend.core.ydb.declarative.elements import and_
from passport.backend.core.ydb.exceptions import (
    YdbMultipleResultFound,
    YdbTemporaryError,
)
from passport.backend.core.ydb.faker.stubs import FakeResultSet
from passport.backend.core.ydb.faker.ydb import FakeYdb
from passport.backend.core.ydb.processors.family_invite import (
    delete_family_invite,
    delete_family_invites_until,
    FamilyInviteExistsError,
    find_family_invite,
    find_invites_for_family,
    insert_family_invite,
)
from passport.backend.core.ydb.schemas import family_invites_table as fit
import passport.backend.core.ydb_client as ydb


TEST_FAMILY_ID = 'f1'
TEST_INVITE_ID = '0bab73fc-f1d1-4572-91b2-a2a0af84a666'
TEST_INVITE_ID2 = '0b6066e5-a718-4314-9ec4-d87889ddbcb7'
TEST_PHONE = '+79030915478'
TEST_TIMESTAMP = 1585142726


class BaseFamilyInviteTestCase(PassportTestCase):
    def setUp(self):
        super(BaseFamilyInviteTestCase, self).setUp()

        self.fake_ydb = FakeYdb()

        self.__patches = [
            self.fake_ydb,
        ]

        for patch in self.__patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        del self.__patches
        del self.fake_ydb
        super(BaseFamilyInviteTestCase, self).tearDown()

    def build_family_invite(
        self,
        family_id=TEST_FAMILY_ID,
        issuer_uid=TEST_UID,
        invite_id=TEST_INVITE_ID,
        send_method=FamilyInvite.SEND_METHOD_SMS,
        create_time=TEST_TIMESTAMP,
        contact=TEST_PHONE,
    ):
        return FamilyInvite(
            family_id=family_id,
            invite_id=invite_id,
            issuer_uid=issuer_uid,
            send_method=send_method,
            create_time=create_time,
            contact=contact,
        )

    def build_family_invite_row(
        self,
        family_id=TEST_FAMILY_ID,
        invite_id=TEST_INVITE_ID,
        issuer_uid=TEST_UID,
        send_method=FamilyInvite.SEND_METHOD_SMS,
        create_time=TEST_TIMESTAMP,
        contact=TEST_PHONE,
    ):
        return dict(
            family_id=int(str(family_id).lstrip('f')),
            invite_id=invite_id,
            issuer_uid=issuer_uid,
            send_method=send_method,
            create_time=create_time*1000000,
            contact=contact,
        )


@with_settings_hosts(
    YDB_FAMILY_INVITE_DATABASE='/family_invites',
    YDB_FAMILY_INVITE_ENABLED=True,
    YDB_RETRIES=2,
)
class TestInsertFamilyInvite(BaseFamilyInviteTestCase):
    def build_insert_query(self, invite):
        return insert(fit, dict(
            invite_id=invite.invite_id,
            family_id=invite.family_id,
            issuer_uid=invite.issuer_uid,
            send_method=invite.send_method,
            create_time=invite.create_time,
            contact=invite.contact,
        )).compile()

    def test_insert(self):
        self.fake_ydb.set_execute_return_value([])
        invite = self.build_family_invite()
        insert_family_invite(invite)

        self.fake_ydb.assert_queries_executed(
            [
                self.build_insert_query(invite),
            ],
        )

    def test_ydb_timeout(self):
        self.fake_ydb.set_execute_side_effect(ydb.Timeout('timeout'))

        invite = self.build_family_invite()
        with self.assertRaises(YdbTemporaryError):
            insert_family_invite(invite)

        self.fake_ydb.assert_queries_executed(
            [
                self.build_insert_query(invite),
            ],
        )

    def test_ydb_integrity_error(self):
        self.fake_ydb.set_execute_side_effect(ydb.PreconditionFailed('integrity_error'))

        invite = self.build_family_invite()
        with self.assertRaises(FamilyInviteExistsError):
            insert_family_invite(invite)

        self.fake_ydb.assert_queries_executed(
            [
                self.build_insert_query(invite),
            ],
        )


@with_settings_hosts(
    YDB_FAMILY_INVITE_DATABASE='/family_invites',
    YDB_FAMILY_INVITE_ENABLED=True,
    YDB_RETRIES=2,
)
class TestFindFamilyInvite(BaseFamilyInviteTestCase):
    def build_select_query(self, invite_id):
        return select(fit, fit.c.invite_id == invite_id).compile()

    def test_find(self):
        invite = self.build_family_invite()
        self.fake_ydb.set_execute_side_effect(
            [
                [FakeResultSet(
                    [self.build_family_invite_row()],
                )],
            ],
        )

        found = find_family_invite(TEST_INVITE_ID)

        self.assertEqual(found, invite)
        self.fake_ydb.assert_queries_executed(
            [
                self.build_select_query(invite_id=TEST_INVITE_ID),
            ],
        )

    def test_not_found(self):
        self.fake_ydb.set_execute_side_effect([
            [FakeResultSet([])],
        ])

        found = find_family_invite(TEST_INVITE_ID)

        assert found is None
        self.fake_ydb.assert_queries_executed(
            [
                self.build_select_query(invite_id=TEST_INVITE_ID),
            ],
        )

    def test_ydb_timeout(self):
        self.fake_ydb.set_execute_side_effect(ydb.Timeout('timeout'))

        with self.assertRaises(YdbTemporaryError):
            find_family_invite(TEST_INVITE_ID)

        self.fake_ydb.assert_queries_executed(
            [
                self.build_select_query(invite_id=TEST_INVITE_ID),
            ],
        )

    def test_multiple_found(self):
        self.fake_ydb.set_execute_side_effect(
            [
                [FakeResultSet(
                    [
                        self.build_family_invite_row(),
                        self.build_family_invite_row(),
                    ],
                )],
            ],
        )

        with self.assertRaises(YdbMultipleResultFound):
            find_family_invite(TEST_INVITE_ID)


@with_settings_hosts(
    YDB_FAMILY_INVITE_DATABASE='/family_invites',
    YDB_FAMILY_INVITE_ENABLED=True,
    YDB_RETRIES=2,
)
class TestFindFamilyInvitesForFamily(BaseFamilyInviteTestCase):
    def build_select_query(self, family_id, exclude_invite=None):
        if exclude_invite:
            return select(
                fit,
                and_(
                    fit.c.family_id == family_id,
                    fit.c.invite_id != exclude_invite,
                ),
                optimizer_index='family_id_index',
            ).compile()
        else:
            return select(
                fit,
                fit.c.family_id == family_id,
                optimizer_index='family_id_index',
            ).compile()

    def test_find(self):
        invite = self.build_family_invite()
        invite2 = self.build_family_invite(invite_id=TEST_INVITE_ID2)
        self.fake_ydb.set_execute_side_effect(
            [
                [FakeResultSet(
                    [
                        self.build_family_invite_row(),
                        self.build_family_invite_row(invite_id=TEST_INVITE_ID2),
                    ],
                )],
            ],
        )

        result = find_invites_for_family(TEST_FAMILY_ID)

        self.assertEqual(result, [invite, invite2])
        self.fake_ydb.assert_queries_executed(
            [
                self.build_select_query(family_id=TEST_FAMILY_ID),
            ],
        )

    def test_find_exclude(self):
        invite = self.build_family_invite()
        self.fake_ydb.set_execute_side_effect(
            [
                [FakeResultSet(
                    [
                        self.build_family_invite_row(),
                    ],
                )],
            ],
        )

        result = find_invites_for_family(TEST_FAMILY_ID, exclude_invite=TEST_INVITE_ID2)

        self.assertEqual(result, [invite])
        self.fake_ydb.assert_queries_executed(
            [
                self.build_select_query(family_id=TEST_FAMILY_ID, exclude_invite=TEST_INVITE_ID2),
            ],
        )

    def test_ydb_timeout(self):
        self.fake_ydb.set_execute_side_effect(ydb.Timeout('timeout'))

        with self.assertRaises(YdbTemporaryError):
            find_invites_for_family(TEST_FAMILY_ID)

        self.fake_ydb.assert_queries_executed(
            [
                self.build_select_query(family_id=TEST_FAMILY_ID),
            ],
        )


@with_settings_hosts(
    YDB_FAMILY_INVITE_DATABASE='/family_invites',
    YDB_FAMILY_INVITE_ENABLED=True,
    YDB_RETRIES=2,
)
class TestDeleteFamilyInvite(BaseFamilyInviteTestCase):
    def build_delete_query(self, invite_id):
        return delete(fit, fit.c.invite_id == invite_id).compile()

    def test_delete(self):
        self.fake_ydb.set_execute_return_value([])
        delete_family_invite(TEST_INVITE_ID)

        self.fake_ydb.assert_queries_executed(
            [
                self.build_delete_query(TEST_INVITE_ID),
            ],
        )

    def test_ydb_timeout(self):
        self.fake_ydb.set_execute_side_effect(ydb.Timeout('timeout'))

        with self.assertRaises(YdbTemporaryError):
            delete_family_invite(TEST_INVITE_ID)

        self.fake_ydb.assert_queries_executed(
            [
                self.build_delete_query(TEST_INVITE_ID),
            ],
        )


@with_settings_hosts(
    YDB_FAMILY_INVITE_DATABASE='/family_invites',
    YDB_FAMILY_INVITE_ENABLED=True,
    YDB_RETRIES=2,
)
class TestDeleteFamilyInvitesUntil(BaseFamilyInviteTestCase):
    def build_delete_query(self, timestamp):
        return delete(fit, fit.c.create_time <= timestamp, optimizer_index='create_time_index').compile()

    def test_delete_ts(self):
        self.fake_ydb.set_execute_return_value([])
        delete_family_invites_until(TEST_TIMESTAMP)

        self.fake_ydb.assert_queries_executed(
            [
                self.build_delete_query(TEST_TIMESTAMP),
            ],
        )

    def test_delete_datetime(self):
        self.fake_ydb.set_execute_return_value([])
        datetime_ts = datetime.datetime.fromtimestamp(TEST_TIMESTAMP)
        delete_family_invites_until(datetime_ts)

        self.fake_ydb.assert_queries_executed(
            [
                self.build_delete_query(TEST_TIMESTAMP),
            ],
        )
