# -*- coding: utf-8 -*-
from contextlib import contextmanager
import importlib
import itertools
import sys
from unittest import TestCase

import mock
from nose_parameterized import parameterized
import six
import yenv


LOCALHOST_ENV_TYPES = ['production', 'rc', 'testing', 'development']
INTRANET_ENV_TYPES = ['production', 'rc', 'testing']
STRESS_ENV_TYPES = ['stress']
ALL_ENVIRONMENT_TYPES_BY_NAME = {
    'localhost': LOCALHOST_ENV_TYPES,
    'intranet': INTRANET_ENV_TYPES,
    'stress': STRESS_ENV_TYPES,
}

run_for_all_environments = parameterized.expand(
    (env_name, env_type)
    for env_name, env_types in ALL_ENVIRONMENT_TYPES_BY_NAME.items()
    for env_type in env_types
)


def for_env(env_names, env_types):
    return parameterized.expand(
        itertools.product(env_names, env_types),
    )


class BaseSettingsModuleTestCase(TestCase):
    BASE_MODULE = 'passport.backend.api.settings'
    SETTINGS_MODULE = 'passport.backend.api.settings.settings'
    ALL_ENVIRONMENT_TYPES_BY_NAME = ALL_ENVIRONMENT_TYPES_BY_NAME

    def setUp(self):
        self.settings = None
        self._imported = None

    def tearDown(self):
        self._unload_settings_modules()

    @contextmanager
    def with_yenv(self, env_name='intranet', env_type='production'):
        with mock.patch.object(yenv, 'name', env_name):
            with mock.patch.object(yenv, 'type', env_type):
                try:
                    yield
                except Exception as err:
                    six.reraise(
                        err.__class__,
                        err.__class__('{} [yenv.name={} yenv.type={}]'.format(
                            err, env_name, env_type,
                        )),
                        sys.exc_info()[2],
                    )

    def _unload_settings_modules(self):
        for module in self._imported or []:
            if module in sys.modules:
                del sys.modules[module]

    def get_settings(self):
        if self.settings:
            return self.settings
        modules_before = set(sys.modules.keys())
        try:
            self.settings = importlib.import_module(self.SETTINGS_MODULE)
            return self.settings
        finally:
            modules_after = set(sys.modules.keys())
            self._imported = modules_after - modules_before

    def assert_settings_equal(self, **kwargs):
        for attr_name, expected in kwargs.items():
            value = getattr(self.settings, attr_name)
            self.assertEqual(
                value,
                expected,
                'Unexpected settings.{} value: {} != {}'.format(attr_name, value, expected),
            )
