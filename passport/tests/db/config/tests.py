# -*- coding: utf-8 -*-
from time import time

from django.test.utils import override_settings
import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.oauth.core.db.config.base import (
    BaseJsonConfig,
    BaseYamlConfig,
    LoadConfigsError,
)
from passport.backend.oauth.core.db.config.scopes import get_scopes
from passport.backend.oauth.core.test.framework import BaseTestCase
import yatest.common as yc


class TestBaseJsonConfig(BaseTestCase):
    @raises(LoadConfigsError)
    def test_bad_filename(self):
        config = BaseJsonConfig(filename='foo.bar')
        config.load()

    def test_no_error_if_have_data(self):
        config = BaseJsonConfig(filename='foo.bar')
        config.config = {'foo': 'bar'}
        config.load()


class TestBaseYamlConfig(BaseTestCase):
    @raises(LoadConfigsError)
    def test_bad_filename(self):
        config = BaseYamlConfig(filename='foo.bar')
        config.load()

    def test_no_error_if_have_data(self):
        config = BaseYamlConfig(filename='foo.bar')
        config.config = {'foo': 'bar'}
        config.load()


@override_settings(
    LOGIN_TO_UID_MAPPING_CONFIG=yc.source_path('passport/backend/oauth/configs/login_to_uid_mapping.json'),
    SCOPE_TRANSLATIONS_CONFIG=yc.source_path('passport/backend/oauth/configs/scope_translations.json'),
    SCOPE_SHORT_TRANSLATIONS_CONFIG=yc.source_path('passport/backend/oauth/configs/scope_short_translations.json'),
    SERVICE_TRANSLATIONS_CONFIG=yc.source_path('passport/backend/oauth/configs/service_translations.json'),
    SCOPES_CONFIG=yc.source_path('passport/backend/oauth/configs/scopes.testing.json'),
)
class TestScopesConfig(BaseTestCase):
    def setUp(self):
        super(TestScopesConfig, self).setUp()
        LazyLoader.flush('Scopes')
        LazyLoader.flush('LoginToUidMapping')

    def test_load(self):
        scopes_config = get_scopes()
        login_to_uid_mapping = LazyLoader.get_instance('LoginToUidMapping')
        login_to_uid_mapping.expires_at = time() + 3600  # должен всё равно загрузиться принудительно

        ok_(scopes_config.is_expired)
        ok_(scopes_config.config is None)
        ok_(login_to_uid_mapping.config is None)

        scopes_config.load()

        ok_(not scopes_config.is_expired)
        ok_(scopes_config.config)
        ok_(login_to_uid_mapping.config)

    def test_lazy_load(self):
        scopes_config = get_scopes()
        login_to_uid_mapping = LazyLoader.get_instance('LoginToUidMapping')
        login_to_uid_mapping.expires_at = time() + 3600  # должен всё равно загрузиться принудительно

        ok_(scopes_config.is_expired)
        ok_(scopes_config.config is None)
        ok_(login_to_uid_mapping.config is None)

        ok_(scopes_config.data)

        ok_(not scopes_config.is_expired)
        ok_(scopes_config.config)
        ok_(login_to_uid_mapping.config)

    def test_reload(self):
        scopes_config = get_scopes()
        scopes_config.load()
        scopes_config.load()


class TestDeviceNamesMappingConfig(BaseTestCase):
    def setUp(self):
        super(TestDeviceNamesMappingConfig, self).setUp()
        self.initial_data = {'foo': 'bar'}
        LazyLoader.flush('DeviceNamesMapping')
        self.loader = LazyLoader.get_instance('DeviceNamesMapping')
        self.loader.config = self.initial_data

    def test_load(self):
        """Проверяем, что конфиг успешно грузится и парсится"""
        data = self.loader.data
        ok_(data)
        ok_(data != self.initial_data)

    def test_error_on_postprocess(self):
        self.loader.postprocess = mock.Mock(side_effect=ValueError)
        with assert_raises(ValueError):
            self.loader.data
        # Проверяем, что при следующим чтении (и так в течение минуты)
        # мы получим не ошибку, а старые закешированные данные
        eq_(self.loader.data, self.initial_data)

    def test_error_on_postprocess_with_no_data(self):
        self.loader.config = {}
        self.loader.postprocess = mock.Mock(side_effect=ValueError)
        with assert_raises(ValueError):
            self.loader.data
        # Проверяем, что при следующим чтении (и так в течение минуты)
        # мы получим не ошибку, а старые закешированные данные
        eq_(self.loader.data, {})

        # сбрасываем mtimes, чтобы прочитать файл повторно
        self.loader._files_mtimes = None
        # Так как старых данных нет, при повторном чтении снова получим ошибку
        with assert_raises(ValueError):
            self.loader.data


@override_settings(
    TOKEN_PARAMS_CONFIG=yc.source_path('passport/backend/oauth/configs/token_params.testing.yaml'),
)
class TestTokenParamsConfig(BaseTestCase):
    def setUp(self):
        super(TestTokenParamsConfig, self).setUp()
        self.initial_data = {'force_stateless': []}
        LazyLoader.flush('TokenParams')
        self.loader = LazyLoader.get_instance('TokenParams')
        self.loader.config = self.initial_data

    def test_load(self):
        """Проверяем, что конфиг успешно грузится и парсится"""
        data = self.loader.data
        ok_(data)
        ok_(data != self.initial_data)
        ok_(self.loader.stateless_rules_by_client_id)

    def test_error_on_postprocess(self):
        self.loader.postprocess = mock.Mock(side_effect=ValueError)
        with assert_raises(ValueError):
            self.loader.data
        # Проверяем, что при следующим чтении (и так в течение минуты)
        # мы получим не ошибку, а старые закешированные данные
        eq_(self.loader.data, self.initial_data)

    def test_error_on_postprocess_with_no_data(self):
        self.loader.config = {}
        self.loader.postprocess = mock.Mock(side_effect=ValueError)
        with assert_raises(ValueError):
            self.loader.data
        # Проверяем, что при следующим чтении (и так в течение минуты)
        # мы получим не ошибку, а старые закешированные данные
        eq_(self.loader.data, {})

        # сбрасываем mtimes, чтобы прочитать файл повторно
        self.loader._files_mtimes = None
        # Так как старых данных нет, при повторном чтении снова получим ошибку
        with assert_raises(ValueError):
            self.loader.data


@override_settings(
    CLIENT_LISTS_CONFIG=yc.source_path('passport/backend/oauth/configs/client_lists.testing.yaml'),
)
class TestClientListsConfig(BaseTestCase):
    def setUp(self):
        super(TestClientListsConfig, self).setUp()
        self.initial_data = {}
        LazyLoader.flush('ClientLists')
        self.loader = LazyLoader.get_instance('ClientLists')
        self.loader.config = self.initial_data

    def test_load(self):
        """Проверяем, что конфиг успешно грузится и парсится"""
        data = self.loader.data
        ok_(data)
        ok_(data != self.initial_data)
