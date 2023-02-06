# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.ydb.exceptions import YdbTemporaryError
from passport.backend.core.ydb.faker.stubs import FakeResultSet
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.turboapp import (
    is_psuid_allowed_for_redirect_uri,
    is_redirect_uri_turboapp,
    make_turboapp_redirect_uri,
    try_exclude_scopes_specific_for_turboapps,
)
from passport.backend.oauth.core.test.framework import (
    ApiTestCase,
    BaseTestCase,
)


TEST_REDIRECT_URI = 'yandexta://ozon/ru'


class TestCommonUtils(BaseTestCase):
    def test_is_redirect_uri_turboapp(self):
        for not_turboapp_url in (
            'https://ozon.ru',
            'yandex://ozon.ru',
        ):
            ok_(not is_redirect_uri_turboapp(not_turboapp_url), '%s must not be turboapp' % not_turboapp_url)

        for turboapp_url in (
            'yandexta://ozon.ru',
            'yandexta://passport.yandex.ru/auth',
        ):
            ok_(is_redirect_uri_turboapp(turboapp_url), '%s must be turboapp' % turboapp_url)

    def test_make_turboapp_redirect_uri(self):
        for turboapp_base_url, redirect_uri in (
            ('http://ozon.ru', 'yandexta://ozon.ru'),
            ('https://ozon.ru', 'yandexta://ozon.ru'),
            ('https://ozon.ru/', 'yandexta://ozon.ru'),
            ('https://ozon.ru/path', 'yandexta://ozon.ru'),
            ('https://ozon.ru/path/', 'yandexta://ozon.ru'),
            ('https://ozon.ru/path/?param=value#fragment', 'yandexta://ozon.ru'),
        ):
            eq_(make_turboapp_redirect_uri(turboapp_base_url), redirect_uri)


class BaseYdbUtilsTestCase(ApiTestCase):
    def setUp(self):
        super(BaseYdbUtilsTestCase, self).setUp()
        self.patch_ydb()
        self.setup_ydb_response()

    def setup_ydb_response(self, found=False):
        rows = []
        if found:
            rows.append({
                'host': 'test-host',
                'partner_id': 'test-partner-id',
                'allow_psuid': True,
            })
        self.fake_ydb.set_execute_return_value(
            [FakeResultSet(rows)],
        )

    def assert_ydb_not_called(self):
        eq_(len(self.fake_ydb.executed_queries()), 0)

    def assert_ydb_called(self):
        eq_(len(self.fake_ydb.executed_queries()), 1)

    def assert_statbox_empty(self):
        self.check_statbox_entries([])


class TestIsPsuidAllowedFirRedirectUri(BaseYdbUtilsTestCase):
    def assert_error_written_to_statbox(self, error, redirect_uri=TEST_REDIRECT_URI):
        expected_entry = {
            'mode': 'issue_psuid',
            'action': 'turboapp_validation',
            'status': 'error',
            'error': error,
            'client_id': self.test_client.display_id,
        }
        if redirect_uri is not None:
            expected_entry.update(redirect_uri=redirect_uri)

        self.check_statbox_entry(expected_entry)

    def test_missing_url(self):
        for redirect_uri in (
            None,
            '',
        ):
            ok_(not is_psuid_allowed_for_redirect_uri(self.test_client, redirect_uri=redirect_uri))
            self.assert_ydb_not_called()
            self.assert_error_written_to_statbox('redirect_uri.missing', redirect_uri=redirect_uri)

    def test_untrusted_url(self):
        ok_(not is_psuid_allowed_for_redirect_uri(self.test_client, redirect_uri=TEST_REDIRECT_URI))
        self.assert_ydb_called()
        self.assert_error_written_to_statbox('redirect_uri.not_trusted')

    def test_ydb_failed(self):
        self.fake_ydb.set_execute_side_effect(YdbTemporaryError)
        ok_(not is_psuid_allowed_for_redirect_uri(self.test_client, redirect_uri=TEST_REDIRECT_URI))
        self.assert_ydb_called()
        self.assert_error_written_to_statbox('ydb.unavailable')

    def test_ok(self):
        self.setup_ydb_response(found=True)
        ok_(is_psuid_allowed_for_redirect_uri(self.test_client, redirect_uri=TEST_REDIRECT_URI))
        self.assert_ydb_called()
        self.assert_statbox_empty()


class TestTryExcludeScopesSpecificForTurboapps(BaseYdbUtilsTestCase):
    def assert_error_written_to_statbox(self, error, redirect_uri=TEST_REDIRECT_URI):
        expected_entry = {
            'mode': 'issue_token',
            'action': 'turboapp_validation',
            'status': 'error',
            'error': error,
            'client_id': self.test_client.display_id,
            'scope': 'test:default_phone',
        }
        if redirect_uri is not None:
            expected_entry.update(redirect_uri=redirect_uri)

        self.check_statbox_entry(expected_entry)

    def test_no_specific_scopes(self):
        scopes = {Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')}
        eq_(
            try_exclude_scopes_specific_for_turboapps(self.test_client, scopes, redirect_uri=None),
            scopes,
        )
        self.assert_ydb_not_called()
        self.assert_statbox_empty()

    def test_phone_scope__no_redirect_uri(self):
        eq_(
            try_exclude_scopes_specific_for_turboapps(
                self.test_client,
                scopes={Scope.by_keyword('test:foo'), Scope.by_keyword('test:default_phone')},
                redirect_uri=None,
            ),
            {Scope.by_keyword('test:foo')},
        )
        self.assert_ydb_not_called()
        self.assert_error_written_to_statbox('redirect_uri.missing', redirect_uri=None)

    def test_phone_scope__redirect_uri_not_turboapp(self):
        eq_(
            try_exclude_scopes_specific_for_turboapps(
                self.test_client,
                scopes={Scope.by_keyword('test:foo'), Scope.by_keyword('test:default_phone')},
                redirect_uri='https://ozon.ru',
            ),
            {Scope.by_keyword('test:foo')},
        )
        self.assert_ydb_not_called()
        self.assert_error_written_to_statbox('redirect_uri.not_turboapp', redirect_uri='https://ozon.ru')

    def test_phone_scope__redirect_uri_not_trusted(self):
        eq_(
            try_exclude_scopes_specific_for_turboapps(
                self.test_client,
                scopes={Scope.by_keyword('test:foo'), Scope.by_keyword('test:default_phone')},
                redirect_uri=TEST_REDIRECT_URI,
            ),
            {Scope.by_keyword('test:foo')},
        )
        self.assert_ydb_called()
        self.assert_error_written_to_statbox('redirect_uri.not_trusted')

    def test_phone_scope__ydb_failed(self):
        self.fake_ydb.set_execute_side_effect(YdbTemporaryError)
        eq_(
            try_exclude_scopes_specific_for_turboapps(
                self.test_client,
                scopes={Scope.by_keyword('test:foo'), Scope.by_keyword('test:default_phone')},
                redirect_uri=TEST_REDIRECT_URI,
            ),
            {Scope.by_keyword('test:foo')},
        )
        self.assert_ydb_called()
        self.assert_error_written_to_statbox('ydb.unavailable')

    def test_phone_scope__redirect_uri_trusted(self):
        self.setup_ydb_response(found=True)
        eq_(
            try_exclude_scopes_specific_for_turboapps(
                self.test_client,
                scopes={Scope.by_keyword('test:foo'), Scope.by_keyword('test:default_phone')},
                redirect_uri=TEST_REDIRECT_URI,
            ),
            {Scope.by_keyword('test:foo'), Scope.by_keyword('test:default_phone')},
        )
        self.assert_ydb_called()
        self.assert_statbox_empty()

    def test_phone_scope__client_whitelisted(self):
        self.fake_client_lists.set_data({'whitelist_for_scope': {'test:default_phone': [self.test_client.display_id]}})
        eq_(
            try_exclude_scopes_specific_for_turboapps(
                self.test_client,
                scopes={Scope.by_keyword('test:foo'), Scope.by_keyword('test:default_phone')},
                redirect_uri=TEST_REDIRECT_URI,
            ),
            {Scope.by_keyword('test:foo'), Scope.by_keyword('test:default_phone')},
        )
        self.assert_ydb_not_called()
        self.assert_statbox_empty()
