# -*- coding: utf-8 -*-
from django.test.utils import override_settings
import mock
from nose.tools import (
    assert_is_none,
    assert_raises,
)
from passport.backend.oauth.core.db.client import Client
from passport.backend.oauth.core.db.limits import (
    AccessDeniedError,
    restrict_non_yandex_clients,
)
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.test.framework.testcases import DBTestCase


@override_settings(
    FORBID_NONPUBLIC_GRANT_TYPES=True,
    ALLOW_NONPUBLIC_GRANT_TYPES_FOR_CLIENTS_FROM_YANDEX_IPS={
        'password': ['zar'],
    },
    ALLOW_NONPUBLIC_GRANT_TYPES_FOR_CLIENTS_FROM_INTERNET={
        'password': ['foo', 'bar'],
        'sessionid': ['foo', 'bar'],
    },
)
class TestRestrictNonYandexClients(DBTestCase):
    def setUp(self):
        super(TestRestrictNonYandexClients, self).setUp()

        self.test_client = Client.create(
            uid=1,
            scopes=[
                Scope.by_keyword('test:foo'),
                Scope.by_keyword('test:bar'),
            ],
            default_title='Тестовое приложение',
            default_description='Описание',
        )

        self.is_yandex_ip_mock = mock.Mock(return_value=False)
        self.is_yandex_ip_patch = mock.patch(
            'passport.backend.oauth.core.db.limits.is_yandex_ip',
            self.is_yandex_ip_mock,
        )
        self.is_yandex_ip_patch.start()

    def tearDown(self):
        self.is_yandex_ip_patch.stop()
        super(TestRestrictNonYandexClients, self).tearDown()

    def _check(self, grant_type):
        return restrict_non_yandex_clients(grant_type=grant_type, client=self.test_client, user_ip='8.8.8.8')

    def assert_is_not_restricted(self, grant_type='password'):
        assert_is_none(self._check(grant_type))

    def assert_is_restricted(self, grant_type='password'):
        with assert_raises(AccessDeniedError):
            self._check(grant_type)

    def assert_statbox_empty(self):
        self.check_statbox_entries([])

    def assert_statbox_logged(self, action, reason, grant_type='password', is_yandex_ip='0'):
        self.check_statbox_entries([
            dict(
                mode='issue_token_by_nonpublic_grant_type',
                user_ip='8.8.8.8',
                client_id=self.test_client.display_id,
                grant_type=grant_type,
                action=action,
                reason=reason,
                is_yandex_ip=is_yandex_ip,
            ),
        ])

    def test_setting_disabled__allow(self):
        with override_settings(FORBID_NONPUBLIC_GRANT_TYPES=False):
            self.assert_is_not_restricted()
            self.assert_statbox_empty()

    def test_public_grant_type__allow(self):
        self.assert_is_not_restricted(grant_type='authorization_code')
        self.assert_statbox_empty()

    def test_yandex_and_allowed_client__allow(self):
        self.test_client.is_yandex = True
        self.test_client.allow_nonpublic_granttypes = True
        self.assert_is_not_restricted()
        self.assert_statbox_logged(action='allowed', reason='is_yandex_and_allowed')

    def test_yandex_but_not_allowed_client__forbidden(self):
        self.test_client.is_yandex = True
        self.assert_is_restricted()
        self.assert_statbox_logged(action='forbidden', reason='is_yandex_but_not_allowed')

    def test_whitelisted_client__allow(self):
        self.test_client.display_id = 'foo'
        self.assert_is_not_restricted()
        self.assert_statbox_logged(action='allowed', reason='whitelisted')

    def test_other_reason__forbidden(self):
        self.assert_is_restricted()
        self.assert_statbox_logged(action='forbidden', reason='other')

    def test_is_yandex_ip__allow(self):
        self.test_client.display_id = 'zar'
        self.is_yandex_ip_mock.return_value = True
        self.assert_is_not_restricted('password')
        self.assert_statbox_logged(action='allowed', reason='whitelisted', is_yandex_ip='1')

    def test_is_yandex_ip__forbidden(self):
        self.test_client.display_id = 'zar'
        self.is_yandex_ip_mock.return_value = True
        self.assert_is_restricted('sessionid')
        self.assert_statbox_logged(action='forbidden', reason='other', is_yandex_ip='1', grant_type='sessionid')
