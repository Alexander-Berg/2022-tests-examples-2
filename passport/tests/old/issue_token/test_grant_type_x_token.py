# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
from time import time

from django.conf import settings
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox import BLACKBOX_OAUTH_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_oauth_response
from passport.backend.core.builders.money_api import PAYMENT_AUTH_SUCCEEDED_STATUS
from passport.backend.core.builders.money_api.faker import (
    money_payment_api_auth_context_response,
    money_payment_api_error_response,
    TEST_AUTH_CONTEXT_ID,
    TEST_REDIRECT_URI as TEST_PAYMENT_AUTH_URL,
)
from passport.backend.oauth.api.api.old.error_descriptions import TOKEN_EXPIRED
from passport.backend.oauth.api.tests.old.issue_token.base import (
    BaseIssueTokenTestCase,
    CommonIssueTokenTests,
    TEST_IP,
)
from passport.backend.oauth.core.db.eav import UPDATE
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.token import (
    issue_token,
    Token,
    TOKEN_TYPE_STATELESS,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_ANOTHER_UID,
    TEST_LOGIN,
    TEST_LOGIN_ID,
    TEST_UID,
)
from passport.backend.oauth.core.test.db_utils import model_to_bb_response
from passport.backend.oauth.core.test.fake_configs import mock_scope_grant
from passport.backend.oauth.core.test.utils import assert_params_in_tskv_log_entry


TEST_PAYMENT_AUTH_RETPATH = 'deeplink://payment_auth_passed'


class TestIssueTokenByXToken(BaseIssueTokenTestCase, CommonIssueTokenTests):
    grant_type = 'x-token'

    def setUp(self):
        super(TestIssueTokenByXToken, self).setUp()
        self.x_token = issue_token(
            uid=self.uid,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='iFridge',
            scopes=[Scope.by_keyword('test:xtoken')],
        )
        self.statbox_handle_mock.reset_mock()
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=self.uid,
                aliases={'portal': TEST_LOGIN},
                oauth_token_info={
                    'token_attributes': model_to_bb_response(self.x_token),
                },
                login_id=TEST_LOGIN_ID,
            ),
        )

    def credentials(self):
        return {
            'access_token': self.x_token.access_token,
        }

    def assert_blackbox_ok(self):
        super(TestIssueTokenByXToken, self).assert_blackbox_ok()
        self.fake_blackbox.requests[0].assert_query_contains({
            'method': 'oauth',
            'format': 'json',
            'aliases': 'all',
            'oauth_token': self.x_token.access_token,
            'oauth_token_attributes': 'all',
            'oauth_client_attributes': 'all',
            'userip': TEST_IP,
        })

    def assert_statbox_ok(self):
        assert_params_in_tskv_log_entry(
            self.statbox_handle_mock,
            dict(x_token_id=str(self.x_token.id)),
        )

    def specific_antifraud_values(self):
        return {
            'login_id': TEST_LOGIN_ID,
            'previous_login_id': TEST_LOGIN_ID,
            'token_id': '2',
        }

    def device_info(self):
        return {
            'uuid': '550e8400-e29b-41d4-a716-446655440000',
            'deviceid': 'xxxxxx',
            'app_id': 'com.yandex.maps',
            'app_platform': 'android',
            'manufacturer': 'htc',
            'model': 'wildfire',
            'app_version': '0.0.1',
            'am_version': '0.0.2',
            'ifv': 'not_ios',
            'device_name': 'Vasya Poupkin\'s phone',
        }

    def specific_statbox_values(self):
        return dict(
            self.device_info(),
            **{
                'model_name': 'wildfire',
                'device_id': 'xxxxxx',
            }
        )

    def test_stateless_token_ok(self):
        super(TestIssueTokenByXToken, self).test_stateless_token_ok()
        self.fake_blackbox.get_requests_by_method('create_oauth_token')[0].assert_query_contains({
            'xtoken_id': str(self.x_token.id),
            'xtoken_shard': '1',
        })

    def test_limited_by_karma(self):
        # тест переопределен из базового класса, т.к. требуется особенный мок
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=self.uid,
                aliases={'portal': TEST_LOGIN},
                oauth_token_info={
                    'token_attributes': model_to_bb_response(self.x_token),
                },
                login_id=TEST_LOGIN_ID,
                karma=1100,
            ),
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='forbidden account type')

    def test_is_child_error(self):
        # тест переопределен из базового класса, т.к. требуется особенный мок
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=self.uid,
                aliases={'portal': TEST_LOGIN},
                attributes={
                    'account.is_child': '1',
                },
                oauth_token_info={
                    'token_attributes': model_to_bb_response(self.x_token),
                },
                login_id=TEST_LOGIN_ID,
            ),
        )
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='forbidden account type')

    def test_x_token_id_stored_for_normal_x_token(self):
        rv = self.make_request()
        self.assert_token_response_ok(rv)
        token = Token.by_access_token(rv['access_token'])
        eq_(token.x_token_id, self.x_token.id)

    def test_x_token_id_not_stored_for_stateless_x_token(self):
        stateless_x_token = issue_token(
            uid=self.uid,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='iFridge',
            scopes=[Scope.by_keyword('test:xtoken')],
            token_type=TOKEN_TYPE_STATELESS,
        )
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=self.uid,
                aliases={'portal': TEST_LOGIN},
                oauth_token_info={
                    'token_attributes': model_to_bb_response(stateless_x_token),
                },
                login_id=TEST_LOGIN_ID,
            ),
        )
        rv = self.make_request()
        self.assert_token_response_ok(rv)
        token = Token.by_access_token(rv['access_token'])
        ok_(not token.x_token_id)

    def test_login_id_stored(self):
        rv = self.make_request()
        self.assert_token_response_ok(rv)
        token = Token.by_access_token(rv['access_token'])
        eq_(token.login_id, TEST_LOGIN_ID)

    def test_no_reuse_for_glogouted(self):
        token = issue_token(uid=self.uid, client=self.test_client, grant_type=self.grant_type, env=self.env)
        with UPDATE(token):
            token.issued = datetime.now() - timedelta(seconds=10)
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=self.uid,
                attributes={settings.BB_ATTR_GLOGOUT: time() + 10},
                aliases={'portal': TEST_LOGIN},
                oauth_token_info={
                    'token_attributes': model_to_bb_response(self.x_token),
                },
                login_id=TEST_LOGIN_ID,
            ),
        )
        rv = self.make_request()
        self.assert_token_response_ok(rv)
        ok_(rv['access_token'] != token.access_token)

    def test_token_invalid(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(status=BLACKBOX_OAUTH_INVALID_STATUS, error=TOKEN_EXPIRED),
        )
        rv = self.make_request(expected_status=400, access_token='foobar', **self.device_info())
        self.assert_error(rv, error='invalid_grant', error_description=TOKEN_EXPIRED)
        self.check_statbox(
            status='error',
            reason='x_token.invalid',
            bb_status=BLACKBOX_OAUTH_INVALID_STATUS,
            bb_error=TOKEN_EXPIRED,
            **self.specific_statbox_values()
        )

    def test_token_empty(self):
        rv = self.make_request(access_token='', expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='expired_token')

    def test_token_placeholder(self):
        rv = self.make_request(access_token='-', expected_status=400)
        self.assert_error(rv, error='invalid_grant', error_description='expired_token')

    def test_no_xtoken_grant(self):
        self.x_token.set_scopes([Scope.by_keyword('test:foo')])
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=self.uid,
                oauth_token_info={
                    'token_attributes': model_to_bb_response(self.x_token),
                },
                login_id=TEST_LOGIN_ID,
            ),
        )

        rv = self.make_request(expected_status=400, **self.device_info())
        self.assert_error(rv, error='invalid_grant', error_description='No xtoken_grant_scope')
        self.check_statbox(
            uid=str(TEST_UID),
            status='error',
            reason='x_token.scope_missing',
            actual_scopes='test:foo',
            x_token_id=str(self.x_token.id),
            **self.specific_statbox_values()
        )

    def test_device_id_discrepancy(self):
        rv = self.make_request(device_id='other_id', passport_track_id='1111')
        self.assert_token_response_ok(rv)
        self.check_statbox_entry(
            dict(
                self.base_statbox_values(),
                action='device_id_verification',
                status='warning',
                uid=str(TEST_UID),
                device_id='other_id',
                x_token_device_id='iFridge',
                x_token_id=str(self.x_token.id),
            ),
            entry_index=-2,
        )
        token = Token.by_access_token(rv['access_token'])
        self.assert_credentials_log_ok(device_id='other_id', login='test', token_id=str(token.id), track_id='1111')

    def test_account_type_forbidden__handicapped_account(self):
        for alias_type, alias in (
            ('phonish', 'phne-123'),
            ('mailish', 'admin@gmail.com'),
        ):
            self.fake_blackbox.set_response_value(
                'oauth',
                blackbox_oauth_response(
                    uid=self.uid,
                    aliases={alias_type: alias},
                    oauth_token_info={
                        'token_attributes': model_to_bb_response(self.x_token),
                    },
                    login_id=TEST_LOGIN_ID,
                ),
            )
            rv = self.make_request(expected_status=400, **self.device_info())
            self.assert_error(rv, error='invalid_grant', error_description='forbidden account type')
            self.check_statbox_last_entry(
                uid=str(TEST_UID),
                status='error',
                reason='account_type.forbidden',
                account_type=alias_type,
                x_token_id=str(self.x_token.id),
                **self.specific_statbox_values()
            )

    def test_account_type_allowed(self):
        for alias_type, alias in (
            ('phonish', 'phne-123'),
            ('mailish', 'admin@gmail.com'),
        ):
            self.fake_grants.set_data({
                'grant_type:x-token/%s' % alias_type: mock_scope_grant(
                    grant_types=['x-token'],
                    client_ids=[self.test_client.display_id],
                ),
            })
            self.fake_blackbox.set_response_value(
                'oauth',
                blackbox_oauth_response(
                    uid=self.uid,
                    aliases={alias_type: alias},
                    oauth_token_info={
                        'token_attributes': model_to_bb_response(self.x_token),
                    },
                    login_id=TEST_LOGIN_ID,
                ),
            )
            rv = self.make_request()
            self.assert_token_response_ok(rv)

    def test_ok_with_payment_auth(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('money:all')])

        rv = self.make_request(expected_status=400, payment_auth_retpath=TEST_PAYMENT_AUTH_RETPATH)
        self.assert_error(
            rv,
            error='payment_auth_pending',
            error_description='Payment auth required',
            payment_auth_context_id=TEST_AUTH_CONTEXT_ID,
            payment_auth_url=TEST_PAYMENT_AUTH_URL,
            payment_auth_app_ids=['money.app.1', 'money.app.2'],
        )

        self.fake_money_api.set_response_value(
            'check_auth_context',
            money_payment_api_auth_context_response(
                status=PAYMENT_AUTH_SUCCEEDED_STATUS,
                uid=TEST_UID,
                client_id=self.test_client.display_id,
                scopes=self.test_client.scopes,
            ),
        )
        rv = self.make_request(payment_auth_context_id=TEST_AUTH_CONTEXT_ID)
        self.assert_token_response_ok(rv)

    def test_payment_auth_retpath_missing(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('money:all')])

        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_request', error_description='payment_auth_retpath not in POST')

    def test_payment_auth_not_passed(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('money:all')])

        self.fake_money_api.set_response_value(
            'check_auth_context',
            money_payment_api_auth_context_response(
                status='Pending',
                uid=TEST_UID,
                client_id=self.test_client.display_id,
                scopes=self.test_client.scopes,
            ),
        )
        rv = self.make_request(expected_status=400, payment_auth_context_id=TEST_AUTH_CONTEXT_ID)
        self.assert_error(rv, error='payment_auth_pending', error_description='Payment auth not passed')

    def test_payment_auth_passed_for_other_uid(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('money:all')])

        self.fake_money_api.set_response_value(
            'check_auth_context',
            money_payment_api_auth_context_response(
                status=PAYMENT_AUTH_SUCCEEDED_STATUS,
                uid=TEST_ANOTHER_UID,
                client_id=self.test_client.display_id,
                scopes=self.test_client.scopes,
            ),
        )
        rv = self.make_request(expected_status=400, payment_auth_context_id=TEST_AUTH_CONTEXT_ID)
        self.assert_error(rv, error='payment_auth_pending', error_description='Payment auth not passed')

    def test_money_api_failed(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('money:all')])

        self.fake_money_api.set_response_value(
            'create_auth_context',
            money_payment_api_error_response(),
            status=500,
        )
        rv = self.make_request(decode_response=False, expected_status=503, payment_auth_retpath=TEST_PAYMENT_AUTH_RETPATH)
        eq_(rv, 'Service temporarily unavailable')
