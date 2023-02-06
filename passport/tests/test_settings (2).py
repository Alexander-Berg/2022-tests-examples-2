# -*- coding: utf-8 -*-
import mock
from passport.backend.api.settings.tests.base import (
    BaseSettingsModuleTestCase,
    run_for_all_environments,
)
from passport.backend.core.test.test_utils import OPEN_PATCH_TARGET


class TestSettings(BaseSettingsModuleTestCase):
    SETTINGS_MODULE = 'passport.backend.api.settings_override.overridden_settings'

    def setUp(self):
        super(TestSettings, self).setUp()
        self.mock_open = mock.mock_open(read_data='')
        self.open_patch = mock.patch(OPEN_PATCH_TARGET, self.mock_open)
        self.open_patch.start()

    def tearDown(self):
        self.open_patch.stop()
        super(TestSettings, self).tearDown()

    @run_for_all_environments
    def test_ok_in_all_environments(self, env_name, env_type):
        with self.with_yenv(env_name=env_name, env_type=env_type):
            self.get_settings()
