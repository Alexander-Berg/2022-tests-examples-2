# -*- coding: utf-8 -*-
from passport.backend.api.settings.tests.base import (
    BaseSettingsModuleTestCase,
    for_env,
)


class TestBlackboxSettings(BaseSettingsModuleTestCase):
    def assert_blackbox_settings(
        self,
        yenv_name,
        yenv_type,
        blackbox_url,
        blackbox_availability_test_uid,
        ticket_parser2_blackbox_env,
    ):
        with self.with_yenv(yenv_name, yenv_type):
            self.get_settings()
            self.assert_settings_equal(
                BLACKBOX_URL=blackbox_url,
                BLACKBOX_AVAILABILITY_TEST_UID=blackbox_availability_test_uid,
                TICKET_PARSER2_BLACKBOX_ENV=ticket_parser2_blackbox_env,
            )

    @for_env(['localhost'], ['development', 'testing'])
    def test_localhost_dev_and_testing(self, yenv_name, yenv_type):
        self.assert_blackbox_settings(
            yenv_name,
            yenv_type,
            blackbox_url='https://pass-test.yandex.ru/',
            blackbox_availability_test_uid=3000153923,
            ticket_parser2_blackbox_env='testing',
        )

    def test_localhost_rc(self):
        self.assert_blackbox_settings(
            'localhost',
            'rc',
            blackbox_url='https://blackbox-rc.yandex.net/',
            blackbox_availability_test_uid=172997057,
            ticket_parser2_blackbox_env='production',
        )

    def test_localhost_production(self):
        self.assert_blackbox_settings(
            'localhost',
            'production',
            blackbox_url='https://blackbox.yandex.net/',
            blackbox_availability_test_uid=172997057,
            ticket_parser2_blackbox_env='production',
        )

    def test_intranet_testing(self):
        self.assert_blackbox_settings(
            'intranet',
            'testing',
            blackbox_url='https://blackbox-test.yandex-team.ru/',
            blackbox_availability_test_uid=1100000000000005,
            ticket_parser2_blackbox_env='intranet_testing',
        )

    @for_env(['intranet'], ['rc', 'production'])
    def test_intranet_rc_and_production(self, env_name, env_type):
        self.assert_blackbox_settings(
            env_name,
            env_type,
            blackbox_url='https://blackbox.yandex-team.ru/',
            blackbox_availability_test_uid=1120000000011117,
            ticket_parser2_blackbox_env='intranet_production',
        )
