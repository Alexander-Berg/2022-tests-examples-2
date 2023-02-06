# -*- coding: utf-8 -*-

from passport.backend.api.tests.views.bundle.family.family_base import BaseFamilyInviteTestcase
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_FAMILY_INVITE_ID,
    TEST_FAMILY_INVITE_ID1,
    TEST_FAMILY_MAX_KIDS_NUMBER,
    TEST_FAMILY_MAX_SIZE,
    TEST_UID,
    TEST_UID1,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


PASSPORT_BASE_URL_TEMPLATE = 'https://0.passportdev.yandex.%(tld)s'


@with_settings_hosts(
    FAMILY_MAX_KIDS_NUMBER=TEST_FAMILY_MAX_KIDS_NUMBER,
    FAMILY_MAX_SIZE=TEST_FAMILY_MAX_SIZE,
)
class InvitesInfoTestCase(BaseFamilyInviteTestcase):
    default_url = '/1/bundle/family/invites_info/'
    consumer = 'dev'
    http_method = 'post'

    def setUp(self):
        super(InvitesInfoTestCase, self).setUp()
        self.env.grants.set_grants_return_value(
            mock_grants(grants={'family': ['invites_info']}),
        )

    def test_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**self.build_blackbox_userinfo_response(with_family=True)),
        )
        self.setup_ydb(
            self.build_ydb_invites(
                [
                    self.build_invite(invite_id=TEST_FAMILY_INVITE_ID),
                    self.build_invite(invite_id=TEST_FAMILY_INVITE_ID1),
                ],
            ),
        )
        response = self.make_request(query_args={'uid': TEST_UID})
        self.assert_ok_response(
            response,
            family_invites=[
                {'invite_id': TEST_FAMILY_INVITE_ID},
                {'invite_id': TEST_FAMILY_INVITE_ID1},
            ],
            family_settings={
                'max_capacity': TEST_FAMILY_MAX_SIZE,
                'max_kids_number': TEST_FAMILY_MAX_KIDS_NUMBER,
            },
        )
        self.assert_statbox_empty()
        self.assert_historydb_empty()

    def test_user_is_not_family_admin(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                **self.build_blackbox_userinfo_response(
                    uid=TEST_UID1,
                    with_family=True,
                )
            ),
        )
        response = self.make_request(query_args={'uid': TEST_UID1})
        self.assert_error_response(response, ['family.not_is_admin'])
        self.assert_statbox_empty()
        self.assert_historydb_empty()

    def test_user_has_no_family(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                **self.build_blackbox_userinfo_response(
                    uid=TEST_UID1,
                    with_family=False,
                )
            ),
        )
        response = self.make_request(query_args={'uid': TEST_UID1})
        self.assert_error_response(response, ['family.does_not_exist'])
        self.assert_statbox_empty()
        self.assert_historydb_empty()

    def test_user_not_found(self):
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        response = self.make_request(query_args={'uid': TEST_UID})

        self.assert_error_response(response, ['account.not_found'])
        self.assert_statbox_empty()
        self.assert_historydb_empty()
