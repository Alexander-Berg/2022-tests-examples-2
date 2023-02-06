# -*- coding: utf-8 -*-

from passport.backend.api.tests.views.bundle.family.family_base import BaseFamilyInviteTestcase
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_EMAIL,
    TEST_FAMILY_ID,
    TEST_FAMILY_INVITE_ID,
    TEST_HOST,
    TEST_TIMESTAMP,
    TEST_UID,
    TEST_USER_AGENT,
    TEST_USER_COOKIE,
    TEST_USER_IP,
)
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.test.test_utils.mock_objects import mock_grants


PASSPORT_BASE_URL_TEMPLATE = 'https://0.passportdev.yandex.%(tld)s'


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    PASSPORT_BASE_URL_TEMPLATE=PASSPORT_BASE_URL_TEMPLATE,
)
class InviteInfoTestCase(BaseFamilyInviteTestcase):
    default_url = '/1/bundle/family/invite_info/'
    consumer = 'dev'
    http_method = 'post'
    http_headers = dict(
        host=TEST_HOST,
        user_agent=TEST_USER_AGENT,
        cookie=TEST_USER_COOKIE,
        user_ip=TEST_USER_IP,
    )

    def setUp(self):
        super(InviteInfoTestCase, self).setUp()
        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'family': ['invite_info'],
                },
            ),
        )

    def test_invite_info(self):
        self.setup_ydb(
            self.build_ydb_invite(),
        )
        resp = self.make_request(query_args={'invite_id': TEST_FAMILY_INVITE_ID})
        self.assert_ok_response(
            resp,
            invite_id=TEST_FAMILY_INVITE_ID,
            family_id=TEST_FAMILY_ID,
            issuer_uid=TEST_UID,
            send_method='email',
            contact=TEST_EMAIL,
            create_time=int(TEST_TIMESTAMP),
        )
        self.assert_historydb_empty()
        self.assert_statbox_empty()
        self.assert_ydb_exec(self.build_ydb_select())

    def test_invite_not_found(self):
        self.setup_ydb(
            self.build_ydb_empty(),
        )
        resp = self.make_request(query_args={'invite_id': TEST_FAMILY_INVITE_ID})
        self.assert_error_response(resp, ['family.invalid_invite'])
        self.assert_historydb_empty()
        self.assert_statbox_empty()
        self.assert_ydb_exec(self.build_ydb_select())
