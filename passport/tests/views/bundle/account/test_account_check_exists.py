# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_AUTH_HEADER,
    TEST_CITY,
    TEST_COUNTRY_CODE,
    TEST_EMAIL,
    TEST_GENDER,
    TEST_LANGUAGE,
    TEST_OAUTH_TOKEN,
    TEST_PDD_LOGIN,
    TEST_PDD_UID,
    TEST_TZ,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.api.views.bundle.account.check_exists import (
    ACCOUNT_CHECK_EXISTS_BY_EMAIL_SCOPE,
    ACCOUNT_CHECK_EXISTS_GRANT,
)
from passport.backend.core.builders.blackbox.constants import BLACKBOX_OAUTH_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_userinfo_response,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts()
class TestAccountCheckExists(BaseBundleTestViews):
    default_url = '/1/bundle/account/check_exists/?consumer=dev'
    http_query_args = dict(
        email=TEST_EMAIL,
    )
    http_headers = dict(
        user_ip=TEST_USER_IP,
        authorization=TEST_AUTH_HEADER,
    )
    http_method = 'POST'
    mocked_grants = [ACCOUNT_CHECK_EXISTS_GRANT]

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grant_list(self.mocked_grants)
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_UID

        self.token_data = {}

        self.account_data = {
            'uid': TEST_UID,
            'login': 'login',
            'firstname': 'f',
            'lastname': 'l',
            'birthdate': '1970-01-01',
            'gender': TEST_GENDER,
            'language': TEST_LANGUAGE,
            'country': TEST_COUNTRY_CODE,
            'city': TEST_CITY,
            'timezone': TEST_TZ,
        }
        self.set_blackbox_response()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def assert_blackbox_called(self, call_count=2, user_ip=TEST_USER_IP, token=TEST_OAUTH_TOKEN):
        eq_(len(self.env.blackbox.requests), call_count)
        oauth_request = self.env.blackbox.requests[0]
        oauth_request.assert_query_contains({
            'method': 'oauth',
            'oauth_token': token,
            'userip': user_ip,
        })
        if call_count > 1:
            userinfo_request = self.env.blackbox.requests[1]
            userinfo_request.assert_post_data_contains({
                'method': 'userinfo',
                'login': TEST_EMAIL,
            })

    def set_blackbox_response(self, scope=ACCOUNT_CHECK_EXISTS_BY_EMAIL_SCOPE, has_user_in_token=False):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=scope,
                has_user_in_token=has_user_in_token,
                **self.token_data
            ),
        )

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(**self.account_data),
        )

    def test_account_exists(self):
        resp = self.make_request()

        self.assert_ok_response(resp, exists=True)
        self.assert_blackbox_called()

    def test_pdd_account_not_exists(self):
        self.account_data.update(
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            aliases={'pdd': TEST_PDD_LOGIN},
        )
        self.set_blackbox_response()

        resp = self.make_request()

        self.assert_ok_response(resp, exists=False)
        self.assert_blackbox_called()

    def test_disabled_account_not_exists(self):
        self.account_data.update(
            enabled=False,
        )
        self.set_blackbox_response()

        resp = self.make_request()

        self.assert_ok_response(resp, exists=False)
        self.assert_blackbox_called()

    def test_account_not_exists(self):
        self.account_data.update(
            uid=None,
        )
        self.set_blackbox_response()

        resp = self.make_request()

        self.assert_ok_response(resp, exists=False)
        self.assert_blackbox_called()

    def test_missing_grants(self):
        self.env.grants.set_grant_list([])

        resp = self.make_request(exclude_headers=['authorization'])

        self.assert_error_response(resp, ['access.denied'], status_code=403)

    def test_missing_auth_header(self):
        resp = self.make_request(exclude_headers=['authorization'])

        self.assert_error_response(resp, ['authorization.empty'])

    def test_invalid_token(self):
        self.token_data.update(status=BLACKBOX_OAUTH_INVALID_STATUS)
        self.set_blackbox_response()

        resp = self.make_request()

        self.assert_error_response(resp, ['oauth_token.invalid'])
        self.assert_blackbox_called(call_count=1)

    def test_personalized_token(self):
        self.set_blackbox_response(has_user_in_token=True)

        resp = self.make_request()

        self.assert_error_response(resp, ['oauth_token.invalid'])
        self.assert_blackbox_called(call_count=1)

    def test_missing_scope(self):
        self.set_blackbox_response(scope='unknown-scope')

        resp = self.make_request()

        self.assert_error_response(resp, ['oauth_token.invalid'])
        self.assert_blackbox_called(call_count=1)
