# -*- coding: utf-8 -*-
from django.urls import reverse_lazy
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.logging_utils.helpers import mask_sessionid
from passport.backend.oauth.api.api.iface.utils import (
    client_to_response,
    scopes_to_response,
)
from passport.backend.oauth.api.tests.iface.views.base import (
    BaseIfaceApiTestCase,
    CommonCookieTests,
    CommonTokenTests,
    TEST_DEVICE_ID,
    TEST_DEVICE_NAME,
)
from passport.backend.oauth.core.db.client import ApprovalStatus
from passport.backend.oauth.core.db.eav import (
    DELETE,
    UPDATE,
)
from passport.backend.oauth.core.db.request import (
    CodeStrength,
    CodeType,
    create_request,
    Request,
)
from passport.backend.oauth.core.db.token import issue_token
from passport.backend.oauth.core.test.base_test_data import (
    TEST_AVATAR_ID,
    TEST_DISPLAY_NAME,
    TEST_GRANT_TYPE,
    TEST_LOGIN,
    TEST_NORMALIZED_LOGIN,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.oauth.core.test.fake_configs import (
    mock_grants,
    mock_scope_grant,
)


class TestDeviceAuthorize(BaseIfaceApiTestCase, CommonCookieTests, CommonTokenTests):
    http_method = 'POST'
    url_submit = reverse_lazy('iface_device_authorize_submit')
    url_commit = reverse_lazy('iface_device_authorize_commit')

    default_url = url_submit

    def setUp(self):
        super(TestDeviceAuthorize, self).setUp()
        self.setup_blackbox_response()
        self.token_request = create_request(
            client=self.test_client,
            is_token_response=False,
            make_code=True,
            code_strength=CodeStrength.Medium,
            code_type=CodeType.Unique,
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
        )

    def default_params(self):
        return {
            'consumer': 'oauth_frontend',
            'uid': TEST_UID,
            'language': 'ru',
            'code': self.token_request.code,
        }

    def test_ok_with_unique_code(self):
        rv = self.make_request(url=self.url_submit)
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])
        eq_(rv['already_granted_scopes'], {})
        eq_(
            rv['requested_scopes'],
            scopes_to_response(self.test_client.scopes),
        )
        eq_(
            rv['account'],
            {
                'uid': TEST_UID,
                'login': TEST_NORMALIZED_LOGIN,
                'display_login': TEST_LOGIN,
                'display_name': TEST_DISPLAY_NAME['name'],
                'default_avatar_id': TEST_AVATAR_ID,
                'is_avatar_empty': False,
            },
        )
        eq_(
            rv['client'],
            client_to_response(self.test_client),
        )
        eq_(rv['device_name'], TEST_DEVICE_NAME)

        request = Request.by_id(self.token_request.id)
        ok_(request is not None)
        ok_(not request.is_accepted)
        ok_(not request.uid)
        eq_(request.code_type, CodeType.Unique)

        rv = self.make_request(url=self.url_commit)
        self.assert_status_ok(rv)
        eq_(
            rv['client'],
            client_to_response(self.test_client),
        )
        eq_(rv['device_name'], TEST_DEVICE_NAME)

        accepted_request = Request.by_id(request.id)
        ok_(accepted_request.is_accepted)
        eq_(accepted_request.uid, TEST_UID)

        self.check_statbox_entries([
            {
                'mode': 'check_cookies',
                'host': 'oauth-internal.yandex.ru',
                'consumer': 'oauth_frontend',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
            {
                'mode': 'check_cookies',
                'host': 'oauth-internal.yandex.ru',
                'consumer': 'oauth_frontend',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
            {
                'mode': 'accept_device_code',
                'status': 'ok',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'token_request_id': request.display_id,
                'user_ip': TEST_USER_IP,
                'user_agent': 'curl',
                'yandexuid': 'yu',
            },
        ])

    def test_ok_with_client_bound_code(self):
        token_request = create_request(
            client=self.test_client,
            is_token_response=False,
            make_code=True,
            code_strength=CodeStrength.BelowMedium,
            code_type=CodeType.ClientBound,
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
        )
        code = token_request.code

        rv = self.make_request(url=self.url_submit, code=code, client_id=self.test_client.display_id)
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])
        eq_(rv['already_granted_scopes'], {})
        eq_(
            rv['requested_scopes'],
            scopes_to_response(self.test_client.scopes),
        )
        eq_(
            rv['account'],
            {
                'uid': TEST_UID,
                'login': TEST_NORMALIZED_LOGIN,
                'display_login': TEST_LOGIN,
                'display_name': TEST_DISPLAY_NAME['name'],
                'default_avatar_id': TEST_AVATAR_ID,
                'is_avatar_empty': False,
            },
        )
        eq_(
            rv['client'],
            client_to_response(self.test_client),
        )
        eq_(rv['device_name'], TEST_DEVICE_NAME)

        request = Request.by_id(token_request.id)
        ok_(request is not None)
        ok_(not request.is_accepted)
        ok_(not request.uid)
        eq_(request.code, code)
        eq_(request.code_type, CodeType.ClientBound)

        rv = self.make_request(url=self.url_commit, code=code, client_id=self.test_client.display_id)
        self.assert_status_ok(rv)
        eq_(
            rv['client'],
            client_to_response(self.test_client),
        )
        eq_(rv['device_name'], TEST_DEVICE_NAME)

        accepted_request = Request.by_id(request.id)
        ok_(accepted_request.is_accepted)
        eq_(accepted_request.uid, TEST_UID)

        self.check_statbox_entries([
            {
                'mode': 'check_cookies',
                'host': 'oauth-internal.yandex.ru',
                'consumer': 'oauth_frontend',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
            {
                'mode': 'check_cookies',
                'host': 'oauth-internal.yandex.ru',
                'consumer': 'oauth_frontend',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
            {
                'mode': 'accept_device_code',
                'status': 'ok',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'token_request_id': request.display_id,
                'user_ip': TEST_USER_IP,
                'user_agent': 'curl',
                'yandexuid': 'yu',
            },
        ])

    def test_yandex_code_with_crc(self):
        with UPDATE(self.test_client):
            self.test_client.is_yandex = True

        token_request = create_request(
            client=self.test_client,
            is_token_response=False,
            make_code=True,
            code_strength=CodeStrength.BelowMediumWithCRC,
            code_type=CodeType.ClientBound,
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
        )
        code = token_request.code

        rv = self.make_request(url=self.url_submit, code=code, client_id=self.test_client.display_id)
        self.assert_status_ok(rv)
        ok_(not rv['require_user_confirm'])
        eq_(rv['already_granted_scopes'], {})
        eq_(
            rv['requested_scopes'],
            scopes_to_response(self.test_client.scopes),
        )

        rv = self.make_request(url=self.url_commit, code=code, client_id=self.test_client.display_id)
        self.assert_status_ok(rv)

    def test_scopes_already_granted(self):
        """Запрашиваются ранее выданные права"""
        issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
            device_id=TEST_DEVICE_ID,
        )
        rv = self.make_request(url=self.url_submit)
        self.assert_status_ok(rv)
        ok_(rv['require_user_confirm'])
        eq_(
            rv['requested_scopes'],
            scopes_to_response([]),
        )
        eq_(
            rv['already_granted_scopes'],
            scopes_to_response(self.test_client.scopes),
        )

        rv = self.make_request(url=self.url_commit)
        self.assert_status_ok(rv)

    def test_params_missing(self):
        rv = self.make_request(url=self.url_submit, exclude=['code'])
        self.assert_status_error(rv, ['code.missing'])

        rv = self.make_request(url=self.url_commit, exclude=['code'])
        self.assert_status_error(rv, ['code.missing'])

    def test_scope_grants_missing(self):
        self.fake_grants.set_data({
            'oauth_frontend': mock_grants(grants={'iface_api': ['*']}),
            'test:foo': mock_scope_grant(grant_types=['password']),
        })
        rv = self.make_request(url=self.url_submit)
        self.assert_status_error(rv, ['access.denied'])
        self.check_statbox_entries([
            {
                'mode': 'check_cookies',
                'host': 'oauth-internal.yandex.ru',
                'consumer': 'oauth_frontend',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
            {
                'mode': 'issue_token',
                'grant_type': 'device_code',
                'status': 'error',
                'reason': 'limited_by.grant_type',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'user_ip': TEST_USER_IP,
            },
        ])

    def test_bad_karma(self):
        self.setup_blackbox_response(karma=1100)
        rv = self.make_request(url=self.url_submit)
        self.assert_status_error(rv, ['access.denied'])
        self.check_statbox_entries([
            {
                'mode': 'check_cookies',
                'host': 'oauth-internal.yandex.ru',
                'consumer': 'oauth_frontend',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
            {
                'mode': 'issue_token',
                'grant_type': 'device_code',
                'status': 'error',
                'reason': 'limited_by.karma',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'user_ip': TEST_USER_IP,
            },
        ])

    def test_bad_karma_but_yandex_client_on_submit(self):
        with UPDATE(self.test_client) as client:
            client.is_yandex = True

        self.setup_blackbox_response(karma=1100)
        rv = self.make_request(url=self.url_submit)
        self.assert_status_ok(rv)

    def test_is_child(self):
        self.setup_blackbox_response(is_child=True)
        rv = self.make_request(url=self.url_submit)
        self.assert_status_error(rv, ['account.is_child'])
        ok_('request_id' not in rv)
        self.check_statbox_entries([
            {
                'mode': 'check_cookies',
                'host': 'oauth-internal.yandex.ru',
                'consumer': 'oauth_frontend',
                'have_sessguard': '0',
                'sessionid': mask_sessionid('foo'),
            },
            {
                'mode': 'issue_token',
                'grant_type': 'device_code',
                'status': 'error',
                'reason': 'limited_by.account_type',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'user_ip': TEST_USER_IP,
            },
        ])

    def test_is_child_but_client_is_yandex(self):
        with UPDATE(self.test_client) as client:
            client.is_yandex = True

        self.setup_blackbox_response(is_child=True)
        rv = self.make_request(url=self.url_submit)
        self.assert_status_ok(rv)

    def test_code_invalid(self):
        rv = self.make_request(url=self.url_submit, code='a')
        self.assert_status_error(rv, ['request.not_found'])

        rv = self.make_request(url=self.url_commit, code='a')
        self.assert_status_error(rv, ['request.not_found'])

    def test_code_not_found(self):
        rv = self.make_request(url=self.url_submit, code='a' * 8)
        self.assert_status_error(rv, ['request.not_found'])

        rv = self.make_request(url=self.url_commit, code='a' * 8)
        self.assert_status_error(rv, ['request.not_found'])

    def test_submit_client_not_found(self):
        rv = self.make_request(url=self.url_submit, client_id='a' * 32)
        self.assert_status_error(rv, ['request.not_found'])

    def test_commit_client_deleted(self):
        rv = self.make_request(url=self.url_submit)
        self.assert_status_ok(rv)

        request = Request.by_id(self.token_request.id)
        ok_(request is not None)

        with DELETE(self.test_client):
            pass
        rv = self.make_request(url=self.url_commit)
        self.assert_status_error(rv, ['request.not_found'])

    def test_client_blocked(self):
        with UPDATE(self.test_client) as client:
            client.block()
        rv = self.make_request(url=self.url_submit)
        self.assert_status_error(rv, ['client.blocked'])

    def test_authorize_client_waiting_for_approval(self):
        with UPDATE(self.test_client) as client:
            client.approval_status = ApprovalStatus.Pending
        rv = self.make_request(url=self.url_submit)
        self.assert_status_error(rv, ['client.approval_pending'])

    def test_client_approval_rejected(self):
        with UPDATE(self.test_client) as client:
            client.approval_status = ApprovalStatus.Rejected
        rv = self.make_request(url=self.url_submit)
        self.assert_status_error(rv, ['client.approval_rejected'])
