# -*- coding: utf-8 -*-
from django.urls import reverse_lazy
from nose.tools import eq_
from passport.backend.core.builders.blackbox import (
    BLACKBOX_SESSIONID_INVALID_STATUS,
    BlackboxInvalidParamsError,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.logging_utils.helpers import mask_sessionid
from passport.backend.oauth.core.db.eav import (
    CREATE,
    UPDATE,
)
from passport.backend.oauth.core.db.request import (
    accept_request,
    ActivationStatus,
    Request,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_OTHER_UID,
    TEST_UID,
)
from passport.backend.oauth.core.test.framework.testcases.bundle_api_testcase import BundleApiTestCase


class TestActivateAuthorizationCode(BundleApiTestCase):
    default_url = reverse_lazy('api_activate_authorization_code')
    http_method = 'POST'

    def setUp(self):
        super(TestActivateAuthorizationCode, self).setUp()
        self.default_blackbox_kwargs = {
            'uid': TEST_UID,
            'login': 'login',
        }
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_append_user(
                blackbox_sessionid_multi_response(**self.default_blackbox_kwargs),
                **(dict(self.default_blackbox_kwargs, uid=TEST_OTHER_UID))
            ),
        )
        with CREATE(Request.create(
            uid=TEST_UID,
            client=self.test_client,
            is_token_response=False,
        )) as request:
            request.activation_status = ActivationStatus.Pending
        self.request = accept_request(request)

    def default_params(self):
        return {
            'consumer': 'dev',
            'uid': TEST_UID,
            'client_id': self.test_client.display_id,
            'client_secret': self.test_client.secret,
            'code': self.request.code,
        }

    def default_headers(self):
        headers = super(TestActivateAuthorizationCode, self).default_headers()
        headers.update({
            'HTTP_HOST': 'oauth-internal.yandex.ru',
            'HTTP_YA_CLIENT_COOKIE': 'Session_id=foo;',
        })
        return headers

    def check_statbox(self, with_activate_code=False):
        entries = [
            {
                'mode': 'check_cookies',
                'host': 'oauth-internal.yandex.ru',
                'consumer': 'dev',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
        ]
        if with_activate_code:
            entries.append(
                {
                    'mode': 'activate_code',
                    'status': 'ok',
                    'uid': str(TEST_UID),
                    'client_id': self.test_client.display_id,
                    'token_request_id': self.request.display_id,
                },
            )
        self.check_statbox_entries(entries)

    def assert_statbox_empty(self):
        self.check_statbox_entries([])

    def test_ok(self):
        rv = self.make_request()
        self.assert_status_ok(rv)

        request = Request.by_id(self.request.id)
        eq_(request.activation_status, ActivationStatus.Activated)
        self.check_statbox(with_activate_code=True)

    def test_action_not_required(self):
        with UPDATE(self.request) as request:
            request.activation_status = ActivationStatus.NotRequired

        rv = self.make_request()
        self.assert_status_error(rv, ['action.not_required'])

        request = Request.by_id(self.request.id)
        eq_(request.activation_status, ActivationStatus.NotRequired)
        self.check_statbox()

    def test_code_owner_required(self):
        rv = self.make_request(uid=TEST_OTHER_UID)
        self.assert_status_error(rv, ['code.owner_required'])
        self.check_statbox()

    def test_code_not_found(self):
        rv = self.make_request(code='qwerty123')
        self.assert_status_error(rv, ['code.not_found'])
        self.check_statbox()

    def test_client_not_found(self):
        rv = self.make_request(client_id='a' * 32)
        self.assert_status_error(rv, ['client.not_found'])
        self.assert_statbox_empty()

    def test_client_secret_not_matched(self):
        rv = self.make_request(client_secret='a' * 32)
        self.assert_status_error(rv, ['client_secret.not_matched'])
        self.assert_statbox_empty()

    def test_no_session_cookie(self):
        rv = self.make_request(headers=super(TestActivateAuthorizationCode, self).default_headers())
        self.assert_status_error(rv, ['sessionid.empty'])
        self.assert_statbox_empty()

    def test_blackbox_invalid_params(self):
        self.fake_blackbox.set_response_side_effect(
            'sessionid',
            BlackboxInvalidParamsError,
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['blackbox.invalid_params'])
        self.check_statbox()

    def test_session_cookie_invalid(self):
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['sessionid.invalid'])
        self.check_statbox()

    def test_user_not_in_cookie(self):
        rv = self.make_request(uid=43)
        self.assert_status_error(rv, ['sessionid.no_uid'])
        self.check_statbox()

    def test_user_session_invalid(self):
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(default_user_status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['sessionid.invalid'])
        self.check_statbox()
