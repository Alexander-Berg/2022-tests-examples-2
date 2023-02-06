# -*- coding: utf-8 -*-
from base64 import b64encode
import json

from nose.tools import (
    eq_,
    istest,
    nottest,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.account.secrets.browser_key import (
    BROWSER_KEY_GRANT,
    BROWSER_KEY_OAUTH_SCOPE,
)
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_userinfo_response,
)
from passport.backend.core.eav_type_mapping import ATTRIBUTE_NAME_TO_TYPE
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    check_url_contains_params,
    with_settings_hosts,
)


TEST_LOGIN = 'login'
TEST_UID = 1
TEST_TOKEN = '123456'
TEST_AUTHORIZATION_HEADER = 'OAuth %s' % TEST_TOKEN
TEST_BROWSER_KEY = 'key'
TEST_BROWSER_KEY_2 = 'key2'
TEST_USER_IP = '8.8.8.8'


@nottest
@with_settings_hosts(
    BLACKBOX_URL='localhost',
    BLACKBOX_ATTRIBUTES=['account.browser_key'],
)
class TestSecretsBrowserKeyBase(BaseBundleTestViews):

    http_headers = dict(
        user_ip=TEST_USER_IP,
        authorization=TEST_AUTHORIZATION_HEADER,
    )

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.set_grants()
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env

    def set_grants(self):
        prefix, suffix = BROWSER_KEY_GRANT.split('.')
        self.env.grants.set_grants_return_value(mock_grants(
            grants={prefix: [suffix]},
        ))

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='account_secrets_browser_key',
            ip=TEST_USER_IP,
        )
        self.env.statbox.bind_entry(
            'completed',
            uid=str(TEST_UID),
        )
        self.env.statbox.bind_entry(
            'error',
            status='error',
        )

    def check_db_ok(self, centraldb_query_count=0, sharddb_query_count=0,
                    browser_key=None):

        eq_(self.env.db.query_count('passportdbcentral'), centraldb_query_count)
        eq_(self.env.db.query_count('passportdbshard1'), sharddb_query_count)

        if browser_key is not None:
            self.env.db.check(
                'attributes',
                'account.browser_key',
                browser_key,
                uid=TEST_UID,
                db='passportdbshard1',
            )
        else:
            self.env.db.check_missing(
                'attributes',
                'account.browser_key',
                uid=TEST_UID,
                db='passportdbshard1',
            )

    def check_events_ok(self):
        expected_log_entries = {
            'action': 'browser_key',
            'consumer': 'dev',
        }
        self.assert_events_are_logged(self.env.handle_mock, expected_log_entries)

    def check_events_empty(self):
        self.assert_events_are_empty(self.env.handle_mock)

    def assert_statbox_clean(self):
        self.env.statbox.assert_has_written([])

    def assert_error_recorded_to_statbox(self, reason, **kwargs):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'error',
                reason=reason,
                **kwargs
            ),
        ])

    def assert_events_recorded_to_statbox(self, action):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'completed',
                action=action,
            ),
        ])

    def assert_blackbox_called(self, call_count=1, user_ip=TEST_USER_IP, token=TEST_TOKEN):
        eq_(self.env.blackbox._mock.blackbox_oauth_response.call_count, call_count)
        for i in range(call_count):
            oauth_url = self.env.blackbox._mock.request.call_args_list[i][0][1]
            check_url_contains_params(
                oauth_url,
                {
                    'method': 'oauth',
                    'oauth_token': token,
                    'userip': user_ip,
                    'attributes': str(ATTRIBUTE_NAME_TO_TYPE['account.browser_key']),
                },
            )

    def test_no_authorization_fails(self):
        resp = self.make_request(exclude_headers=['authorization'])
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['authorization.empty'])
        self.check_db_ok()
        self.check_events_empty()
        self.assert_statbox_clean()

    def test_bad_authorization_fails(self):
        resp = self.make_request(headers=dict(authorization='not-oauth'))
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['authorization.invalid'])
        self.check_db_ok()
        self.check_events_empty()
        self.assert_statbox_clean()
        self.assert_blackbox_called(call_count=0)

    def test_blackbox_temporary_error_fails(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'oauth',
            blackbox.BlackboxTemporaryError,
        )
        resp = self.make_request()
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['backend.blackbox_failed'])
        self.check_db_ok()
        self.check_events_empty()
        self.assert_statbox_clean()
        self.assert_blackbox_called(call_count=2)

    def test_account_disabled_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(status=blackbox.BLACKBOX_OAUTH_DISABLED_STATUS),
        )

        resp = self.make_request()
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['account.disabled'])
        self.check_db_ok()
        self.check_events_empty()
        self.assert_error_recorded_to_statbox(reason='invalid_token', bb_status=blackbox.BLACKBOX_OAUTH_DISABLED_STATUS)
        self.assert_blackbox_called()

    def test_blackbox_status_invalid_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(status=blackbox.BLACKBOX_OAUTH_INVALID_STATUS),
        )

        resp = self.make_request()
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['oauth_token.invalid'])
        self.check_db_ok()
        self.check_events_empty()
        self.assert_error_recorded_to_statbox(reason='invalid_token', bb_status=blackbox.BLACKBOX_OAUTH_INVALID_STATUS)
        self.assert_blackbox_called()

    def test_token_scopes_insufficient_fails(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(scope='123'),
        )

        resp = self.make_request()
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['oauth_token.invalid'])
        self.check_db_ok()
        self.check_events_empty()
        self.assert_error_recorded_to_statbox(reason='insufficient_token_scopes')
        self.assert_blackbox_called()


@istest
class TestSecretsReadBrowserKeyView(TestSecretsBrowserKeyBase):

    default_url = '/1/bundle/account/secrets/browser_key/'
    http_method = 'get'
    http_query_args = dict(
        consumer='dev',
    )

    def assert_events_recorded_to_statbox(self):
        super(TestSecretsReadBrowserKeyView, self).assert_events_recorded_to_statbox('read')

    def test_read_empty_key_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(scope=BROWSER_KEY_OAUTH_SCOPE),
        )

        resp = self.make_request()
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['browser_key'], b64encode(''))
        self.check_db_ok()
        self.check_events_empty()
        self.assert_events_recorded_to_statbox()
        self.assert_blackbox_called()

    def test_read_key_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=BROWSER_KEY_OAUTH_SCOPE,
                attributes={'account.browser_key': b64encode(TEST_BROWSER_KEY)},
            ),
        )

        resp = self.make_request()
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        eq_(resp['browser_key'], b64encode(TEST_BROWSER_KEY))
        self.check_db_ok()
        self.check_events_empty()
        self.assert_events_recorded_to_statbox()
        self.assert_blackbox_called()


@istest
class TestSecretsWriteBrowserKeyView(TestSecretsBrowserKeyBase):

    default_url = '/1/bundle/account/secrets/browser_key/?consumer=dev'
    http_method = 'post'
    http_query_args = dict(
        browser_key=b64encode(TEST_BROWSER_KEY),
        append='false',
    )

    def assert_events_recorded_to_statbox(self):
        super(TestSecretsWriteBrowserKeyView, self).assert_events_recorded_to_statbox('saved')

    def test_write_key_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(scope=BROWSER_KEY_OAUTH_SCOPE),
        )

        resp = self.make_request()
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        self.check_db_ok(sharddb_query_count=1, browser_key=TEST_BROWSER_KEY)
        self.check_events_ok()
        self.assert_events_recorded_to_statbox()
        self.assert_blackbox_called()

    def test_update_key_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(scope=BROWSER_KEY_OAUTH_SCOPE),
        )

        resp = self.make_request(query_args=dict(browser_key=b64encode(TEST_BROWSER_KEY_2)))
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        self.check_db_ok(sharddb_query_count=1, browser_key=TEST_BROWSER_KEY_2)
        self.check_events_ok()
        self.assert_events_recorded_to_statbox()
        self.assert_blackbox_called()

    def test_append_key_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(scope=BROWSER_KEY_OAUTH_SCOPE),
        )

        resp = self.make_request(
            query_args=dict(
                browser_key=b64encode(TEST_BROWSER_KEY_2),
                append='true',
            ),
        )
        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'ok')
        self.check_db_ok(sharddb_query_count=1, browser_key=TEST_BROWSER_KEY_2)  # Увы, SQLite не умеет делать append
        self.check_events_ok()
        self.assert_events_recorded_to_statbox()
        self.assert_blackbox_called()

    def test_unicode_key_error(self):
        resp = self.make_request(
            query_args=dict(
                browser_key=u'привет',
            ),
        )

        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['browser_key.invalid'])

    def test_non_alphabet_key(self):
        resp = self.make_request(
            query_args=dict(
                browser_key=u'.*?',
            ),
        )

        eq_(resp.status_code, 200)

        resp = json.loads(resp.data)
        eq_(resp['status'], 'error')
        eq_(resp['errors'], ['browser_key.invalid'])


@istest
class TestSecretsDeleteBrowserKeyView(TestSecretsBrowserKeyBase):

    default_url = '/1/bundle/account/secrets/browser_key/'
    http_method = 'delete'
    http_query_args = dict(consumer='dev')

    def assert_events_recorded_to_statbox(self):
        super(TestSecretsDeleteBrowserKeyView, self).assert_events_recorded_to_statbox('deleted')

    def test_delete_key_ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                scope=BROWSER_KEY_OAUTH_SCOPE,
                attributes={'account.browser_key': b64encode(TEST_BROWSER_KEY)},
            ),
        )
        self.env.db.serialize(
            blackbox_userinfo_response(
                attributes={'account.browser_key': b64encode(TEST_BROWSER_KEY)},
            ),
        )

        resp = self.make_request()
        self.assert_ok_response(resp)
        self.check_db_ok(sharddb_query_count=1, browser_key=None)
        self.check_events_ok()
        self.assert_events_recorded_to_statbox()
        self.assert_blackbox_called()
