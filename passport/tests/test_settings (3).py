# -*- coding: utf-8 -*-
import unittest

from passport.backend.core.conf import (
    DynamicSettings,
    Settings,
)
from passport.backend.core.dynamic_config import LoadConfigsError
import pytest
import yatest.common as yc


class SettingsTest(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()

    def tearDown(self):
        del self.settings

    def test_setting_not_found(self):
        with pytest.raises(AttributeError):
            self.settings.TEST

    def test_bad_settings_type(self):
        with pytest.raises(ValueError):
            self.settings.configure({'TEST': 'test'})

    def test_reconfigure(self):
        self.settings.configure(TEST='test')
        with pytest.raises(RuntimeError):
            self.settings.configure(TEST='test1')

    def test_ok(self):
        self.settings.TEST = 'test2'
        self.settings.TEST = 'test3'
        assert 'test3' == self.settings.TEST

    def test_dynamic_settings(self):
        self.settings.configure(
            dynamic_settings=DynamicSettings(
                py_filename=yc.source_path('passport/backend/core/conf/tests/sample_settings.py'),
                import_as_name='sample_settings',
            ),
        )
        assert self.settings.TEST_SETTING == 'test_value'

    def test_dynamic_settings_not_found(self):
        with pytest.raises(LoadConfigsError):
            self.settings.configure(
                dynamic_settings=DynamicSettings(
                    py_filename=yc.source_path('passport/backend/core/conf/tests/sample_settings2.py'),
                    import_as_name='sample_settings',
                ),
            )

    def test_dynamic_settings_invalid(self):
        with pytest.raises(LoadConfigsError):
            self.settings.configure(
                dynamic_settings=DynamicSettings(
                    py_filename=yc.source_path('passport/backend/core/conf/tests/ya.make'),
                    import_as_name='sample_settings',
                ),
            )
