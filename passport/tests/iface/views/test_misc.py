# -*- coding: utf-8 -*-
from django.conf import settings
from django.urls import reverse_lazy
import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.oauth.api.tests.iface.views.base import (
    BaseIfaceApiTestCase,
    BaseScopesTestCase,
    CommonCookieTests,
)
from passport.backend.oauth.core.test.utils import iter_eq


class TestAllScopes(BaseScopesTestCase):
    default_url = reverse_lazy('iface_all_scopes')

    def default_params(self):
        return {
            'consumer': 'oauth_frontend',
            'language': 'ru',
        }

    def test_ok(self):
        rv = self.make_request()
        self.assert_status_ok(rv)
        all_scopes = self.visible_scopes()
        all_scopes['Тестирование OAuth'].update(
            {
                'test:limited:grant_type:assertion': {
                    'title': 'позволять только по доверенности',
                    'requires_approval': False,
                    'is_ttl_refreshable': False,
                    'ttl': None,
                },
                'test:invisible': {
                    'title': 'скрываться',
                    'requires_approval': False,
                    'is_ttl_refreshable': False,
                    'ttl': None,
                },
                'test:limited:ip': {
                    'title': 'позволять только по IP',
                    'requires_approval': False,
                    'is_ttl_refreshable': False,
                    'ttl': None,
                },
                'test:limited:client': {
                    'title': 'позволять только приложению',
                    'requires_approval': False,
                    'is_ttl_refreshable': False,
                    'ttl': None,
                },
                'test:unlimited': {
                    'title': 'позволять всё',
                    'requires_approval': False,
                    'is_ttl_refreshable': False,
                    'ttl': None,
                },
                'test:limited:grant_type:password': {
                    'title': 'позволять только с паролем',
                    'requires_approval': False,
                    'is_ttl_refreshable': False,
                    'ttl': None,
                },
                'test:abc': {
                    'title': 'управлять в ABC',
                    'requires_approval': False,
                    'is_ttl_refreshable': False,
                    'ttl': None,
                },
                'test:default_phone': {
                    'title': 'узнавать телефон',
                    'requires_approval': False,
                    'is_ttl_refreshable': False,
                    'ttl': None,
                },
                'test:basic_scope': {
                    'title': 'ничего не делать',
                    'requires_approval': False,
                    'is_ttl_refreshable': False,
                    'ttl': None,
                },
            },
        )
        iter_eq(
            rv['all_scopes'],
            all_scopes,
        )


class TestUserInfo(BaseScopesTestCase, CommonCookieTests):
    default_url = reverse_lazy('iface_user_info')

    def default_params(self):
        return {
            'consumer': 'oauth_frontend',
            'language': 'ru',
        }

    def visible_scopes_with_slugs(self):
        return {
            'Тестирование OAuth (test)': {
                'test:foo': {
                    'title': 'фу (test:foo)',
                    'requires_approval': False,
                    'ttl': None,
                    'is_ttl_refreshable': False,
                    'tags': ['test_tag'],
                },
                'test:bar': {
                    'title': 'бар (test:bar)',
                    'requires_approval': False,
                    'ttl': None,
                    'is_ttl_refreshable': False,
                    'tags': [],
                },
                'test:ttl': {
                    'title': 'протухать (test:ttl)',
                    'requires_approval': False,
                    'ttl': 60,
                    'is_ttl_refreshable': False,
                    'tags': [],
                },
                'test:ttl_refreshable': {
                    'title': 'подновляться (test:ttl_refreshable)',
                    'requires_approval': False,
                    'ttl': 300,
                    'is_ttl_refreshable': True,
                    'tags': [],
                },
                'test:premoderate': {
                    'title': 'премодерироваться (test:premoderate)',
                    'requires_approval': True,
                    'ttl': None,
                    'is_ttl_refreshable': False,
                    'tags': [],
                },
                'test:hidden': {
                    'title': 'прятаться (test:hidden)',
                    'requires_approval': False,
                    'ttl': None,
                    'is_ttl_refreshable': False,
                    'tags': [],
                },
                'test:xtoken': {
                    'title': 'выдавать (test:xtoken)',
                    'requires_approval': False,
                    'ttl': None,
                    'is_ttl_refreshable': False,
                    'tags': [],
                },
            },
            'Стрельбы по OAuth (lunapark)': {
                'lunapark:use': {
                    'title': 'стрелять (lunapark:use)',
                    'requires_approval': False,
                    'ttl': None,
                    'is_ttl_refreshable': False,
                    'tags': [],
                },
            },
            'Пароли приложений (app_password)': {
                'app_password:calendar': {
                    'title': 'пользоваться календарём (app_password:calendar)',
                    'requires_approval': False,
                    'ttl': None,
                    'is_ttl_refreshable': False,
                    'tags': [],
                },
            },
            'Деньги (money)': {
                'money:all': {
                    'title': 'тратить деньги (money:all)',
                    'requires_approval': False,
                    'ttl': None,
                    'is_ttl_refreshable': False,
                    'tags': [],
                },
            },
        }

    def setUp(self):
        super(TestUserInfo, self).setUp()
        self.setup_blackbox_response(
            attributes={
                settings.BB_ATTR_ACCOUNT_IS_CORPORATE: '1',
            },
        )

    def test_ok(self):
        rv = self.make_request()
        self.assert_response_ok(
            rv,
            visible_scopes=self.visible_scopes(hide_tags=False),
            is_ip_internal=False,
            allow_register_yandex_clients=False,
        )

    def test_ok_for_intranet(self):
        with mock.patch(
            'passport.backend.oauth.api.api.iface.views.is_yandex_ip',
            mock.Mock(return_value=True),
        ):
            rv = self.make_request()
        self.assert_response_ok(
            rv,
            visible_scopes=self.visible_scopes_with_slugs(),
            is_ip_internal=True,
            allow_register_yandex_clients=True,
        )

    def test_ok_for_intranet_force_no_slugs(self):
        with mock.patch(
            'passport.backend.oauth.api.api.iface.views.is_yandex_ip',
            mock.Mock(return_value=True),
        ):
            rv = self.make_request(force_no_slugs=True)
        self.assert_response_ok(
            rv,
            visible_scopes=self.visible_scopes(hide_tags=False),
            is_ip_internal=True,
            allow_register_yandex_clients=True,
        )


class TestSettings(BaseIfaceApiTestCase):
    default_url = reverse_lazy('iface_settings')

    def default_params(self):
        return {
            'consumer': 'oauth_frontend',
        }

    def test_ok(self):
        rv = self.make_request()
        self.assert_status_ok(rv)
        ok_('invalidate_tokens_on_callback_change' in rv)
        eq_(rv['x_token_scopes'], ['test:xtoken'])
