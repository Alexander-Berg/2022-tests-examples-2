# -*- coding: utf-8 -*-
from importlib import import_module

from passport.backend.api.settings.tests.base import (
    BaseSettingsModuleTestCase,
    run_for_all_environments,
)


class TestSettings(BaseSettingsModuleTestCase):
    @run_for_all_environments
    def test_ok_in_all_environments(self, env_name, env_type):
        with self.with_yenv(env_name=env_name, env_type=env_type):
            self.get_settings()

    def test_wrong_env_name__exception(self):
        with self.with_yenv(env_name='nonexistent'):
            with self.assertRaises(Exception):
                self.get_settings()

    def test_wrong_env_type__exception(self):
        with self.with_yenv(env_type='nonexistent'):
            with self.assertRaises(Exception):
                self.get_settings()

    def test_all_settings_are_imported(self):
        imported_settings = self.get_settings()
        base_settings_module = import_module(self.BASE_MODULE)

        errors = []
        for settings_module_name in dir(base_settings_module):
            if settings_module_name.startswith('__'):
                continue  # это не подмодуль
            if settings_module_name in (
                'secrets',  # секреты обычно не экспортируются наружу as-is, а используются другими сеттингами
                'translations',  # переводы берутся напрямую из этого модуля
            ):
                continue

            settings_module = import_module(self.BASE_MODULE + '.' + settings_module_name)
            for setting in dir(settings_module):
                if not setting.isupper() or setting.startswith('_'):
                    continue  # это не публичная настройка

                if setting not in dir(imported_settings):
                    errors.append(
                        '  setting %s from `%s` not imported in `settings.py`' % (setting, settings_module_name),
                    )

        if errors:
            raise AssertionError('%d import errors:\n%s' % (len(errors), '\n'.join(errors)))
