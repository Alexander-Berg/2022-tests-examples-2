# -*- coding: utf-8 -*-
from django.conf import settings
from django.urls import reverse_lazy
import mock
from nose.tools import (
    assert_almost_equal,
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox import (
    BLACKBOX_SESSIONID_INVALID_STATUS,
    BlackboxInvalidParamsError,
    BlackboxTemporaryError,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_sessionid_multi_append_user,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.logging_utils.helpers import mask_sessionid
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import fake_user_ticket
from passport.backend.oauth.core.db.errors import VerificationCodeCollisionError
from passport.backend.oauth.core.db.request import (
    CodeChallengeMethod,
    CodeStrength,
    Request,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_OTHER_UID,
    TEST_UID,
)
from passport.backend.oauth.core.test.fake_configs import mock_grants
from passport.backend.oauth.core.test.framework.testcases.bundle_api_testcase import BundleApiTestCase


TIME_DELTA = 5


class TestIssueAuthorizationCode(BundleApiTestCase):
    default_url = reverse_lazy('api_issue_authorization_code')
    http_method = 'POST'

    def setUp(self):
        super(TestIssueAuthorizationCode, self).setUp()
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

    def default_params(self):
        return {
            'consumer': 'dev',
            'uid': TEST_UID,
            'client_id': self.test_client.display_id,
            'client_secret': self.test_client.secret,
            'ttl': 1050,
            'code_strength': 'medium',
        }

    def default_headers(self):
        headers = super(TestIssueAuthorizationCode, self).default_headers()
        headers.update({
            'HTTP_HOST': 'oauth-internal.yandex.ru',
            'HTTP_YA_CLIENT_COOKIE': 'Session_id=foo;',
        })
        return headers

    def check_statbox(
        self,
        request_id,
        code_strength,
        require_activation=True,
        code_challenge_method=None,
        with_check_cookies_mode=False,
    ):
        entries = []
        if with_check_cookies_mode:
            entries.append(
                {
                    'mode': 'check_cookies',
                    'host': 'oauth-internal.yandex.ru',
                    'consumer': 'dev',
                    'have_sessguard': '0',
                    'sessionid': mask_sessionid('foo'),
                },
            )

        issue_code_mode_entry = {
            'mode': 'issue_code',
            'status': 'ok',
            'uid': str(TEST_UID),
            'client_id': self.test_client.display_id,
            'token_request_id': request_id,
            'code_strength': code_strength,
            'scopes': 'test:foo,test:bar',
            'require_activation': str(int(require_activation)),
        }
        if code_challenge_method is not None:
            issue_code_mode_entry.update(code_challenge_method=code_challenge_method)

        entries.append(issue_code_mode_entry)

        self.check_statbox_entries(entries)

    def test_ok(self):
        rv = self.make_request()
        self.assert_status_ok(rv)
        assert_almost_equal(rv['expires_in'], 1050, delta=TIME_DELTA)

        request = Request.by_verification_code(self.test_client.id, rv['code'])
        ok_(request is not None)
        eq_(request.code_strength, CodeStrength.Medium)
        eq_(request.scopes, self.test_client.scopes)
        assert_almost_equal(request.ttl, rv['expires_in'], delta=TIME_DELTA)
        ok_(not request.device_id)
        ok_(not request.device_name)

        self.check_statbox(request_id=request.display_id, code_strength='medium', with_check_cookies_mode=True)

    def test_ok_with_xtoken(self):
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(scope='test:xtoken'),
        )

        rv = self.make_request(headers={'HTTP_AUTHORIZATION': 'OAuth foo'})
        self.assert_status_ok(rv)

        request = Request.by_verification_code(self.test_client.id, rv['code'])
        eq_(request.code_strength, CodeStrength.Medium)
        self.check_statbox(request_id=request.display_id, code_strength='medium')

    def test_not_xtoken_error(self):
        self.fake_blackbox.set_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(scope='test:foo'),
        )

        rv = self.make_request(headers={'HTTP_AUTHORIZATION': 'OAuth foo'})
        self.assert_status_error(rv, ['oauth_token.invalid'])

    def test_ok_with_user_ticket(self):
        self.fake_tvm_ticket_checker.set_check_user_ticket_side_effect([
            fake_user_ticket(default_uid=TEST_UID, scopes=[settings.SESSIONID_SCOPE]),
        ])

        rv = self.make_request(headers={'HTTP_X_YA_USER_TICKET': 'foo'})
        self.assert_status_ok(rv)

    def test_ok_by_uid(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(),
        )

        rv = self.make_request(
            by_uid=True,
            uid=TEST_UID,
            code_challenge='a' * 43,
            code_challenge_method='S256',
        )
        self.assert_status_ok(rv)

        request = Request.by_verification_code(self.test_client.id, rv['code'])
        eq_(request.code_strength, CodeStrength.Medium)
        eq_(request.code_challenge, 'a' * 43)
        eq_(request.code_challenge_method, CodeChallengeMethod.S256)
        self.check_statbox(
            request_id=request.display_id,
            code_strength='medium',
            code_challenge_method='S256',
        )

    def test_by_uid_no_grants(self):
        self.fake_grants.set_data({
            'dev': mock_grants(grants={'api': ['issue_authorization_code']}),
        })
        rv = self.make_request(
            by_uid=True,
            uid=TEST_UID,
            code_challenge='a' * 43,
            code_challenge_method='S256',
        )
        self.assert_status_error(rv, ['grants.missing'])

    def test_by_uid_user_not_found(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        rv = self.make_request(
            by_uid=True,
            uid=TEST_UID,
            code_challenge='a' * 43,
            code_challenge_method='S256',
        )
        self.assert_status_error(rv, ['user.not_found'])

    def test_ok_with_device_info(self):
        rv = self.make_request(code_strength='long', device_id='deviceid', device_name='name')
        self.assert_status_ok(rv)
        assert_almost_equal(rv['expires_in'], 1050, delta=TIME_DELTA)

        request = Request.by_verification_code(self.test_client.id, rv['code'])
        ok_(request is not None)
        eq_(request.code_strength, CodeStrength.Long)
        eq_(request.scopes, self.test_client.scopes)
        assert_almost_equal(request.ttl, rv['expires_in'], delta=TIME_DELTA)
        eq_(request.device_id, 'deviceid')
        eq_(request.device_name, 'name')
        ok_(request.needs_activation)

        self.check_statbox(request_id=request.display_id, code_strength='long', with_check_cookies_mode=True)

    def test_ok_without_activation(self):
        rv = self.make_request(require_activation='false')
        self.assert_status_ok(rv)

        request = Request.by_verification_code(self.test_client.id, rv['code'])
        ok_(request is not None)
        ok_(not request.needs_activation)

        self.check_statbox(
            request_id=request.display_id,
            code_strength='medium',
            require_activation=False,
            with_check_cookies_mode=True,
        )

    def test_client_not_found(self):
        rv = self.make_request(client_id='a' * 32)
        self.assert_status_error(rv, ['client.not_found'])

    def test_client_secret_not_matched(self):
        rv = self.make_request(client_secret='a' * 32)
        self.assert_status_error(rv, ['client_secret.not_matched'])

    def test_no_session_cookie(self):
        rv = self.make_request(headers=super(TestIssueAuthorizationCode, self).default_headers())
        self.assert_status_error(rv, ['sessionid.empty'])

    def test_blackbox_invalid_params(self):
        self.fake_blackbox.set_response_side_effect(
            'sessionid',
            BlackboxInvalidParamsError,
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['blackbox.invalid_params'])

    def test_blackbox_failed(self):
        self.fake_blackbox.set_response_side_effect(
            'sessionid',
            BlackboxTemporaryError,
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['backend.failed'])

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

    def test_verification_code_collizion_error(self):
        with mock.patch(
            'passport.backend.oauth.api.api.external.views.create_request',
            mock.Mock(side_effect=VerificationCodeCollisionError),
        ):
            rv = self.make_request()
            self.assert_status_error(rv, ['backend.failed'])
