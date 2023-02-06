# -*- coding: utf-8 -*-
from copy import deepcopy

from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_BLACKBOX_RESPONSE_ACCOUNT_DATA,
    TEST_BLACKBOX_RESPONSE_ACCOUNT_OTHER_FAMILY_INFO,
    TEST_BLACKBOX_RESPONSE_ACCOUNT_OWN_FAMILY_INFO,
    TEST_EMAIL,
    TEST_FAMILY_ID,
    TEST_FAMILY_ID1,
    TEST_FAMILY_INVITE_ID,
    TEST_HOST,
    TEST_TIMESTAMP,
    TEST_UID,
    TEST_UID1,
    TEST_UID4,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_family_info_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.db.schemas import (
    attributes_table as at,
    family_info_table as fit,
    family_members_table as fmt,
    uid_table,
)
from passport.backend.core.models.family import FamilyInvite
from passport.backend.core.serializers.ydb.public import to_ydb_rows
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.ydb.declarative import (
    delete,
    insert,
    select,
)
from passport.backend.core.ydb.declarative.elements import and_
from passport.backend.core.ydb.faker.stubs import (
    FakeResultSet,
    FakeYdbCommit,
)
from passport.backend.core.ydb.schemas import family_invites_table as fivt
from passport.backend.utils.common import merge_dicts


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
)
class BaseFamilyTestcase(BaseBundleTestViews):
    http_method = 'post'
    http_headers = dict(
        host=TEST_HOST,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_USER_COOKIE,
        user_ip=TEST_USER_IP,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.setup_statbox_templates()

    def setup_bb_family_response(
        self,
        family_id=TEST_FAMILY_ID,
        admin_uid=TEST_UID,
        family_members=None,
        exists=True,
        kid_uids=None,
    ):
        family_members = family_members or [TEST_UID, TEST_UID1]
        family_info = blackbox_family_info_response(
            admin_uid=admin_uid,
            exists=exists,
            family_id=family_id,
            kid_uids=kid_uids,
            uids=family_members,
            with_members_info=True,
        )
        self.env.blackbox.set_blackbox_response_value(
            'family_info',
            family_info
        )

    def build_blackbox_family_admin_response(
        self,
        display_name=None,
        has_family=True,
        own_family=True,
        is_child=False,
        can_manage_children=False
    ):
        if has_family:
            if own_family:
                acc_family_info = TEST_BLACKBOX_RESPONSE_ACCOUNT_OWN_FAMILY_INFO
            else:
                acc_family_info = TEST_BLACKBOX_RESPONSE_ACCOUNT_OTHER_FAMILY_INFO
        else:
            acc_family_info = {}
        blackbox_data = deepcopy(TEST_BLACKBOX_RESPONSE_ACCOUNT_DATA)
        if display_name is not None:
            blackbox_data['display_name'] = display_name
        if is_child:
            blackbox_data.setdefault('attributes', {})['account.is_child'] = '1'
        if can_manage_children:
            blackbox_data.setdefault('attributes', {})['account.can_manage_children'] = '1'
        return dict(
            family_info=acc_family_info,
            **blackbox_data
        )

    def setup_bb_response(
        self,
        has_family=True,
        own_family=True,
        is_child=False,
        family_members=None,
        different_family_id_info=False,
        display_name=None,
        can_manage_children=False,
        secure_phone=None,
    ):
        family_admin_response = self.build_blackbox_family_admin_response(
            display_name=display_name,
            has_family=has_family,
            own_family=own_family,
            is_child=is_child,
            can_manage_children=can_manage_children,
        )
        secure_phone = secure_phone if secure_phone is not None else dict()
        sessionid_data = blackbox_sessionid_multi_response(**merge_dicts(family_admin_response, secure_phone))
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            sessionid_data,
        )
        if has_family:
            if family_members is None:
                family_members = [TEST_UID if own_family else TEST_UID1]
            if different_family_id_info:
                family_id = TEST_FAMILY_ID1
            else:
                family_id = family_admin_response['family_info']['family_id']
            self.setup_bb_family_response(
                admin_uid=family_admin_response['family_info']['admin_uid'],
                family_id=family_id,
                family_members=family_members,
                kid_uids=[TEST_UID4],
            )

    def build_blackbox_userinfo_response(self, with_family, uid=TEST_UID, is_child=False,
                                         family_admin_uid=TEST_UID, family_id=TEST_FAMILY_ID):
        additional_fields = {}
        if with_family:
            additional_fields['family_info'] = {
                'family_id': family_id,
                'admin_uid': family_admin_uid,
            }
        if is_child:
            additional_fields['attributes'] = {'account.is_child': '1'}
        return dict(
            uid=uid,
            **additional_fields
        )

    def build_blackbox_other_userinfo_response(self, with_family, family_id=TEST_FAMILY_ID, is_child=False):
        return self.build_blackbox_userinfo_response(
            with_family=with_family,
            uid=TEST_UID1,
            is_child=is_child,
            family_id=family_id,
        )

    def set_other_userinfo_bb_response(self, **kwargs):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**self.build_blackbox_other_userinfo_response(**kwargs)),
        )

    def _attribute_to_db(self, uid, attributes=None, values=None):
        assert len(list(attributes)) == len(list(values))
        with self.env.db.no_recording():
            for a, v in zip(attributes, values):
                self.env.db.insert(
                    at.name,
                    'passportdbshard1',
                    uid=uid,
                    type=a,
                    value=v,
                )
    def _members_uid_to_db(self, uids=None):
        uids = uids if uids is not None else []
        for uid in uids:
            self.env.db.insert(
                uid_table.name,
                'passportdbcentral',
                id=uid,
            )

    def _family_to_db(self, family_id, admin_uid, uids=None, places=None):
        if uids is None:
            uids = []
        if places is None:
            places = range(len(uids))
        assert len(list(places)) == len(list(uids))
        family_id = int(str(family_id).lstrip('f'))
        with self.env.db.no_recording():
            self.env.db.insert(
                fit.name,
                'passportdbcentral',
                admin_uid=int(admin_uid),
                family_id=family_id,
                meta='',
            )
            for uid, place in zip(uids, places):
                self.env.db.insert(
                    fmt.name,
                    'passportdbcentral',
                    family_id=family_id,
                    uid=uid,
                    place=place,
                )

    @staticmethod
    def base_historydb_events(uid):
        return [
            {
                'name': 'consumer',
                'value': 'dev',
                'uid': str(uid),
            },
            {
                'name': 'user_agent',
                'value': 'curl',
                'uid': str(uid),
            },
        ]

    def tearDown(self):
        self.env.stop()
        del self.env

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'family_info_modification',
            consumer='dev',
            event='family_info_modification',
            ip='1.2.3.4',
            user_agent='curl',
        )
        self.env.family_logger.bind_entry(
            'family_info_modification',
            consumer='dev',
            event='family_info_modification',
            ip='1.2.3.4',
            user_agent='curl',
        )
        self.env.statbox.bind_entry(
            'account_modification',
            consumer='dev',
            ip='1.2.3.4',
            user_agent='curl',
        )

    def assert_statboxes(self, entries):

        basic_entries = []
        family_entries = []
        for entry in entries:
            basic_entries.append(self.env.statbox.entry(entry[0], **entry[1]))
            if entry[0] != 'check_cookies':
                family_entries.append(self.env.family_logger.entry(entry[0], **entry[1]))
        self.env.statbox.assert_equals(basic_entries)
        self.env.family_logger.assert_equals(family_entries)

    def assert_statbox_check_cookies(self):
        self.env.statbox.assert_equals([self.env.statbox.entry('check_cookies')])

    def assert_statbox_empty(self):
        self.env.statbox.assert_equals([])
        self.env.family_logger.assert_equals([])

    def assert_historydb_empty(self):
        self.assert_events_are_logged(
            self.env.handle_mock,
            [],
        )


class BaseFamilyInviteTestcase(BaseFamilyTestcase):
    def setUp(self):
        super(BaseFamilyInviteTestcase, self).setUp()

    def build_invite(
        self,
        invite_id=TEST_FAMILY_INVITE_ID,
        family_id=TEST_FAMILY_ID,
        issuer_uid=TEST_UID,
        send_method=FamilyInvite.SEND_METHOD_EMAIL,
        contact=TEST_EMAIL,
        create_time=TEST_TIMESTAMP,
    ):
        return FamilyInvite().parse({
            'family_id': family_id,
            'invite_id': invite_id,
            'issuer_uid': issuer_uid,
            'send_method': send_method,
            'contact': contact,
            'create_time': create_time,
        })

    def setup_ydb(self, response):
        self.env.fake_ydb.set_execute_side_effect(response)

    def build_ydb_invite(
        self,
        invite_id=TEST_FAMILY_INVITE_ID,
        family_id=TEST_FAMILY_ID,
        issuer_uid=TEST_UID,
        send_method=FamilyInvite.SEND_METHOD_EMAIL,
        contact=TEST_EMAIL,
        create_time=TEST_TIMESTAMP*1000000,
        number=1,
    ):
        return [
            [
                FakeResultSet(
                    to_ydb_rows(
                        self.build_invite(
                            invite_id=invite_id,
                            issuer_uid=issuer_uid,
                            family_id=family_id,
                            send_method=send_method,
                            contact=contact,
                            create_time=create_time,
                        ),
                        None,
                    ) * number,
                )
            ]
        ]

    def build_ydb_invites(
        self,
        invites,
    ):
        return [
            [FakeResultSet(to_ydb_rows(invite, None)[0] for invite in invites)]
        ]

    def build_ydb_empty(self, with_rowset=True, n=1):
        if with_rowset:
            return [[FakeResultSet([])]] * n
        else:
            return [[]]

    def build_ydb_select(self):
        return [
            select(fivt, fivt.c.invite_id == TEST_FAMILY_INVITE_ID).compile(),
            FakeYdbCommit,
        ]

    def build_ydb_find(self, exclude_invite=None):
        if exclude_invite:
            query = select(
                fivt,
                and_(
                    fivt.c.family_id == TEST_FAMILY_ID,
                    fivt.c.invite_id != TEST_FAMILY_INVITE_ID,
                ),
                optimizer_index='family_id_index',
            )
        else:
            query = select(
                fivt,
                fivt.c.family_id == TEST_FAMILY_ID,
                optimizer_index='family_id_index',
            )
        return [query.compile(), FakeYdbCommit]

    def build_ydb_delete(self):
        return [
            delete(
                fivt,
                fivt.c.invite_id == TEST_FAMILY_INVITE_ID,
            ).compile(),
            FakeYdbCommit,
        ]

    def build_ydb_delete_all(self):
        return [
            delete(
                fivt,
                fivt.c.family_id == TEST_FAMILY_ID,
                optimizer_index='family_id_index',
            ).compile(),
            FakeYdbCommit,
        ]

    def build_ydb_insert(self, invite):
        return [
            insert(fivt, dict(
                invite_id=invite.invite_id,
                family_id=invite.family_id,
                issuer_uid=invite.issuer_uid,
                send_method=invite.send_method,
                create_time=invite.create_time,
                contact=invite.contact,
            )).compile(),
            FakeYdbCommit,
        ]

    def assert_ydb_exec(self, queries):
        self.env.fake_ydb.assert_queries_executed(queries)
