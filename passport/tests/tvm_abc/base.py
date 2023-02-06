# -*- coding: utf-8 -*-
from django.conf import settings
from django.test.utils import override_settings
from passport.backend.core.builders.abc import ABCTemporaryError
from passport.backend.core.builders.abc.faker import (
    abc_cursor_paginated_response,
    abc_service_member,
)
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_OAUTH_INVALID_STATUS,
    BLACKBOX_SESSIONID_INVALID_STATUS,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_invalid_user_ticket,
    fake_user_ticket,
)
from passport.backend.oauth.core.db.eav import CREATE
from passport.backend.oauth.core.test.base_test_data import (
    TEST_ABC_SERVICE_ID,
    TEST_CIPHER_KEYS,
    TEST_LOGIN,
    TEST_OTHER_LOGIN,
    TEST_OTHER_UID,
    TEST_UID,
)
from passport.backend.oauth.core.test.framework.testcases.bundle_api_testcase import BundleApiTestCase
from passport.backend.oauth.tvm_api.tests.base import (
    TEST_ABC_REQUEST_ID,
    TEST_ROBOT_UID,
)
from passport.backend.oauth.tvm_api.tests.base.vault_test import (
    TEST_VAULT_SECRET_UUID_1,
    TEST_VAULT_VERSION_UUID_1,
)
from passport.backend.oauth.tvm_api.tvm_api.db.tvm_client import TVMClient


def abc_get_service_members_response(uid=TEST_UID, service_id=TEST_ABC_SERVICE_ID, role_codes=('tvm_manager',)):
    return abc_cursor_paginated_response([
        abc_service_member(
            uid=uid,
            service_id=service_id,
            role_code=role_code,
        )
        for role_code in role_codes
    ])


@override_settings(
    ATTRIBUTE_CIPHER_KEYS=TEST_CIPHER_KEYS,
    ABC_ROBOT_UID=TEST_ROBOT_UID,
    STAFF_URL='api.staff.yandex.net',
    STAFF_TIMEOUT=1.0,
    STAFF_RETRIES=1,
    ABC_URL='api.abc.yandex.net',
    ABC_TIMEOUT=1.0,
    ABC_RETRIES=1,
    DISABLE_CHECK_SECRET_SAVED_TO_VAULT=False,
)
class BaseTvmAbcTestcase(BundleApiTestCase):
    maxDiff = None

    def setUp(self):
        super(BaseTvmAbcTestcase, self).setUp()

        self.fake_abc.set_response_value(
            'get_service_members',
            abc_get_service_members_response(),
        )

        with CREATE(TVMClient.create(
            creator_uid=TEST_UID,
            name='Test Client',
        )) as client:
            client.abc_service_id = TEST_ABC_SERVICE_ID
            client.abc_request_id = TEST_ABC_REQUEST_ID
            client.vault_secret_uuid = TEST_VAULT_SECRET_UUID_1
            client.vault_version_uuid = TEST_VAULT_VERSION_UUID_1
            self.test_client = client

    def default_params(self):
        return {
            'consumer': 'dev',
        }


class BaseTvmAbcTestcaseWithCookieOrToken(BaseTvmAbcTestcase):
    def setUp(self):
        super(BaseTvmAbcTestcaseWithCookieOrToken, self).setUp()

        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(uid=TEST_UID, login=TEST_LOGIN),
                **(dict(uid=TEST_OTHER_UID, login=TEST_OTHER_LOGIN))
            ),
        )
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                scope=settings.ABC_SCOPE_KEYWORD,
            ),
        )

    def default_params(self):
        return dict(
            super(BaseTvmAbcTestcaseWithCookieOrToken, self).default_params(),
            uid=TEST_UID,
        )

    def default_headers(self):
        return dict(
            super(BaseTvmAbcTestcaseWithCookieOrToken, self).default_headers(),
            HTTP_HOST='oauth-internal.yandex.ru',
            HTTP_YA_CLIENT_COOKIE='Session_id=foo;',
        )


class BaseTvmAbcTestcaseWithUserTicket(BaseTvmAbcTestcase):
    def setUp(self):
        super(BaseTvmAbcTestcaseWithUserTicket, self).setUp()

        self.fake_tvm_ticket_checker.set_check_user_ticket_side_effect([
            fake_user_ticket(default_uid=TEST_UID, scopes=[settings.SESSIONID_SCOPE]),
        ])

    def default_headers(self):
        return dict(
            super(BaseTvmAbcTestcaseWithUserTicket, self).default_headers(),
            HTTP_X_YA_USER_TICKET='foo',
        )


class CommonUserAuthTests(object):
    def test_no_creds(self):
        rv = self.make_request(headers={'HTTP_HOST': 'oauth.yandex.ru'})
        self.assert_status_error(rv, ['sessionid.empty'])

    def test_session_cookie_invalid(self):
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['sessionid.invalid'])

    def test_user_not_in_cookie(self):
        rv = self.make_request(uid=43)
        self.assert_status_error(rv, ['sessionid.no_uid'])

    def test_user_session_invalid(self):
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(default_user_status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['sessionid.invalid'])

    def test_auth_header_malformed(self):
        rv = self.make_request(headers={'HTTP_YA_CONSUMER_AUTHORIZATION': 'foo'})
        self.assert_status_error(rv, ['authorization.invalid'])

    def test_token_invalid(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(status=BLACKBOX_OAUTH_INVALID_STATUS),
        )
        rv = self.make_request(headers={'HTTP_YA_CONSUMER_AUTHORIZATION': 'OAuth token'})
        self.assert_status_error(rv, ['oauth_token.invalid'])

    def test_token_without_scope(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(scope='test:foo'),
        )
        rv = self.make_request(headers={'HTTP_YA_CONSUMER_AUTHORIZATION': 'OAuth token'})
        self.assert_status_error(rv, ['oauth_token.invalid'])


class CommonRobotAuthTests(object):
    def test_no_token(self):
        rv = self.make_request(headers={'HTTP_HOST': 'oauth.yandex.ru'})
        self.assert_status_error(rv, ['authorization.invalid'])

    def test_auth_header_malformed(self):
        rv = self.make_request(headers={'HTTP_HOST': 'oauth.yandex.ru', 'HTTP_YA_CONSUMER_AUTHORIZATION': 'foo'})
        self.assert_status_error(rv, ['authorization.invalid'])

    def test_token_invalid(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(status=BLACKBOX_OAUTH_INVALID_STATUS),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['oauth_token.invalid'])

    def test_unknown_uid_in_token(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(uid=43),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['oauth_token.invalid'])


class CommonUserTicketTests(object):
    def test_no_creds(self):
        # Убедимся, что на куки или токен не смотрим
        rv = self.make_request(headers={
            'HTTP_HOST': 'oauth.yandex.ru',
            'HTTP_COOKIE': 'Session_id=foo',
            'HTTP_AUTHORIZATION': 'OAuth bar',
        })
        self.assert_status_error(rv, ['user_ticket.empty'])

    def test_user_ticket_invalid(self):
        self.fake_tvm_ticket_checker.set_check_user_ticket_side_effect([
            fake_invalid_user_ticket(),
        ])
        rv = self.make_request()
        self.assert_status_error(rv, ['user_ticket.invalid'])

    def test_user_ticket_without_scope(self):
        self.fake_tvm_ticket_checker.set_check_user_ticket_side_effect([
            fake_user_ticket(default_uid=TEST_UID, scopes=['foo:bar']),
        ])
        rv = self.make_request()
        self.assert_status_error(rv, ['user_ticket.invalid'])


class CommonRoleTests(object):
    def test_multiple_roles_ok(self):
        self.fake_abc.set_response_value(
            'get_service_members',
            abc_get_service_members_response(role_codes=['dishwasher', 'tvm_manager']),
        )
        if hasattr(self, 'vault_mock'):
            with self.vault_mock() as vault:
                self.register_default_mocks(vault)
                rv = self.make_request()
        else:
            rv = self.make_request()

        self.assert_status_ok(rv)

    def test_role_missing(self):
        self.fake_abc.set_response_value(
            'get_service_members',
            abc_get_service_members_response(role_codes=['copypaster']),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['abc_team.member_required'])

    def test_abc_temporary_error(self):
        self.fake_abc.set_response_side_effect(
            'get_service_members',
            ABCTemporaryError(),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['backend.failed'])
