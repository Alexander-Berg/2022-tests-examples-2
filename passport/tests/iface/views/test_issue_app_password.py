# -*- coding: utf-8 -*-
from time import time

from django.conf import settings
from django.urls import reverse_lazy
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.passport.faker import (
    passport_bundle_api_error_response,
    passport_ok_response,
)
from passport.backend.core.logging_utils.helpers import mask_sessionid
from passport.backend.oauth.api.api.iface.utils import token_to_response
from passport.backend.oauth.api.tests.iface.views.base import BaseIfaceApiTestCase
from passport.backend.oauth.core.db.client import Client
from passport.backend.oauth.core.db.eav import CREATE
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.token import (
    list_tokens_by_uid,
    TOKEN_TYPE_NORMAL,
)
from passport.backend.oauth.core.db.token.normal_token import get_max_tokens_per_uid_and_client
from passport.backend.oauth.core.test.base_test_data import (
    TEST_OTHER_UID,
    TEST_UID,
    TEST_USER_IP,
)
from passport.backend.oauth.core.test.fake_configs import (
    mock_grants,
    mock_scope_grant,
)


class TestIssueAppPassword(BaseIfaceApiTestCase):
    default_url = reverse_lazy('iface_issue_app_password')
    http_method = 'POST'

    def setUp(self):
        super(TestIssueAppPassword, self).setUp()
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('app_password:calendar')],
            default_title='Календарь',
        )) as client:
            self.test_client = client
        self.fake_grants.set_data({
            'app_password:calendar': mock_scope_grant(grant_types=['frontend_assertion']),
            'oauth_frontend': mock_grants(grants={'iface_api': ['*']}),
            'grant_type:frontend_assertion': mock_scope_grant(grant_types=['frontend_assertion']),
        })
        self.fake_passport.set_response_value(
            'app_password_created_send_notifications',
            passport_ok_response(),
        )
        self.setup_blackbox_response()

    def default_params(self):
        return {
            'consumer': 'oauth_frontend',
            'language': 'ru',
        }

    def _check_statbox_ok(self, token):
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
                'action': 'issue',
                'status': 'ok',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'token_id': str(token.id),
                'login_id': f't:{token.id}',
                'token_type': TOKEN_TYPE_NORMAL,
                'scopes': 'app_password:calendar',
                'grant_type': 'frontend_assertion',
                'create_time': str(token.created),
                'issue_time': str(token.issued),
                'user_ip': TEST_USER_IP,
                'consumer_ip': TEST_USER_IP,
                'user_agent': 'curl',
                'yandexuid': 'yu',
                'device_id': 'device_id',
                'device_name': 'Windows NT',
                'has_alias': '1',
                'password_passed': '0',
                'token_reused': '0',
            },
        ])

    def _check_historydb_ok(self, token):
        self.check_historydb_event_entry(
            {
                'action': 'create',
                'target': 'token',
                'grant_type': 'frontend_assertion',
                'uid': str(TEST_UID),
                'token_id': str(token.id),
                'token_type': TOKEN_TYPE_NORMAL,
                'client_id': self.test_client.display_id,
                'scopes': 'app_password:calendar',
                'user_ip': TEST_USER_IP,
                'consumer_ip': TEST_USER_IP,
                'user_agent': 'curl',
                'yandexuid': 'yu',
                'device_id': 'device_id',
                'device_name': 'Windows NT',
                'has_alias': '1',
                'password_passed': '0',
            },
            entry_index=-1,
        )

    def test_ok(self):
        rv = self.make_request(
            client_id=self.test_client.display_id,
            device_id='device_id',
            device_name='Windows NT',
        )
        self.assert_status_ok(rv)

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 1)
        token = tokens[0]
        eq_(rv['token_alias'], token.alias)
        eq_(rv['token'], token_to_response(token, self.test_client))
        self._check_statbox_ok(token)
        self._check_historydb_ok(token)

        eq_(len(self.fake_passport.requests), 1)
        self.fake_passport.requests[0].assert_post_data_equals({
            'uid': TEST_UID,
            'app_type': 'calendar',
            'app_name': 'Windows NT',
        })

    def test_ok_user_has_no_password(self):
        self.setup_blackbox_response(have_password=False, age=-1)
        rv = self.make_request(
            client_id=self.test_client.display_id,
            device_id='device_id',
            device_name='Windows NT',
        )
        self.assert_status_ok(rv)

        tokens = list_tokens_by_uid(TEST_UID)
        eq_(len(tokens), 1)
        token = tokens[0]
        eq_(rv['token_alias'], token.alias)
        eq_(rv['token'], token_to_response(token, self.test_client))

        self._check_statbox_ok(token)
        self._check_historydb_ok(token)

        eq_(len(self.fake_passport.requests), 1)
        self.fake_passport.requests[0].assert_post_data_equals({
            'uid': TEST_UID,
            'app_type': 'calendar',
            'app_name': 'Windows NT',
        })
        self.fake_passport.requests[0].assert_headers_contain({
            'Ya-Consumer-Client-Ip': TEST_USER_IP,
        })

    def test_ok_but_failed_to_send_notifications(self):
        self.fake_passport.set_response_value(
            'app_password_created_send_notifications',
            passport_bundle_api_error_response('exception.unhandled'),
        )
        rv = self.make_request(
            client_id=self.test_client.display_id,
            device_id='device_id',
            device_name='Nokia 3110',
        )
        self.assert_status_ok(rv)
        eq_(len(self.fake_passport.requests), 1)

    def test_not_client_creator_ok(self):
        rv = self.make_request(
            client_id=self.test_client.display_id,
            device_id='device_id',
            device_name='Nokia 3110',
            uid=TEST_OTHER_UID,
        )
        self.assert_status_ok(rv)

        tokens = list_tokens_by_uid(TEST_OTHER_UID)
        eq_(len(tokens), 1)
        token = tokens[0]
        eq_(token.alias, rv['token_alias'])

    def test_reuse(self):
        rv1 = self.make_request(
            client_id=self.test_client.display_id,
            device_id='device_id',
            device_name='Nokia 3110',
        )
        self.assert_status_ok(rv1)
        rv2 = self.make_request(
            client_id=self.test_client.display_id,
            device_id='device_id',
            device_name='Nokia 3110',
        )
        self.assert_status_ok(rv2)
        eq_(rv1['token_alias'], rv2['token_alias'])

        rv3 = self.make_request(
            client_id=self.test_client.display_id,
            device_id='other_device_id',
            device_name='Nokia 3110',
        )
        self.assert_status_ok(rv3)
        ok_(rv3['token_alias'] != rv1['token_alias'])

    def test_access_denied(self):
        self.fake_grants.set_data({
            'oauth_frontend': mock_grants(grants={'iface_api': ['*']}),
        })
        rv = self.make_request(
            client_id=self.test_client.display_id,
            device_id='device_id',
            device_name='Nokia 3110',
        )
        self.assert_status_error(rv, ['access.denied'])

    def test_token_limit_exceeded(self):
        max_token_count = get_max_tokens_per_uid_and_client()
        for i in range(max_token_count):
            rv = self.make_request(
                client_id=self.test_client.display_id,
                device_id='device_id_%s' % i,
                device_name='Nokia 3110',
            )
            self.assert_status_ok(rv)

        rv = self.make_request(
            client_id=self.test_client.display_id,
            device_id='device_id',
            device_name='Nokia 3110',
        )
        self.assert_status_error(rv, ['token.limit_exceeded'])
        self.check_statbox_entry(
            {
                'mode': 'issue_token',
                'grant_type': 'frontend_assertion',
                'status': 'warning',
                'reason': 'limit.exceeded',
                'uid': str(TEST_UID),
                'client_id': self.test_client.display_id,
                'user_ip': TEST_USER_IP,
                'limit': str(max_token_count),
                'valid_token_count': str(max_token_count),
                'total_token_count': str(max_token_count),
            },
            entry_index=-1,
        )

    def test_token_limit_not_exceeded_after_glogout(self):
        max_token_count = get_max_tokens_per_uid_and_client()
        for i in range(max_token_count):
            rv = self.make_request(
                client_id=self.test_client.display_id,
                device_id='device_id_%s' % i,
                device_name='Nokia 3110',
            )
            self.assert_status_ok(rv)

        rv = self.make_request(
            client_id=self.test_client.display_id,
            device_id='device_id',
            device_name='Nokia 3110',
        )
        self.assert_status_error(rv, ['token.limit_exceeded'])

        self.setup_blackbox_response(
            attributes={settings.BB_ATTR_GLOGOUT: time() + 10},
        )
        rv = self.make_request(
            client_id=self.test_client.display_id,
            device_id='device_id',
            device_name='Nokia 3110',
        )
        self.assert_status_ok(rv)

    def test_token_limit_not_exceeded_after_revoking_app_passwords(self):
        max_token_count = get_max_tokens_per_uid_and_client()
        for i in range(max_token_count):
            rv = self.make_request(
                client_id=self.test_client.display_id,
                device_id='device_id_%s' % i,
                device_name='Nokia 3110',
            )
            self.assert_status_ok(rv)

        rv = self.make_request(
            client_id=self.test_client.display_id,
            device_id='device_id',
            device_name='Nokia 3110',
        )
        self.assert_status_error(rv, ['token.limit_exceeded'])

        self.setup_blackbox_response(
            attributes={settings.BB_ATTR_REVOKER_APP_PASSWORDS: time() + 10},
        )
        rv = self.make_request(
            client_id=self.test_client.display_id,
            device_id='device_id',
            device_name='Nokia 3110',
        )
        self.assert_status_ok(rv)

    def test_password_not_entered(self):
        self.setup_blackbox_response(age=-1)
        rv = self.make_request(
            client_id=self.test_client.display_id,
            device_id='device_id',
            device_name='Nokia 3110',
        )
        self.assert_status_error(rv, ['password.required'])

    def test_password_not_entered_recently(self):
        self.setup_blackbox_response(age=100500)
        rv = self.make_request(
            client_id=self.test_client.display_id,
            device_id='device_id',
            device_name='Nokia 3110',
        )
        self.assert_status_error(rv, ['password.required'])

    def test_client_not_applicable(self):
        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:foo')],
            default_title='Bad',
        )) as client:
            pass
        rv = self.make_request(
            client_id=client.display_id,
            device_id='device_id',
            device_name='Nokia 3110',
        )
        self.assert_status_error(rv, ['client.not_applicable'])
