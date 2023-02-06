# -*- coding: utf-8 -*-
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_COUNTRY_CODE,
    TEST_DEVICE_INFO,
    TEST_PHONE_NUMBER,
    TEST_TIMESTAMP_UPDATED,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base import (
    BaseYaKeyBackupTestView,
    CommonYakeyBackupTestMixin,
)


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
)
class TestBackupInfo(BaseYaKeyBackupTestView, CommonYakeyBackupTestMixin):
    default_url = '/1/bundle/yakey_backup/info/?consumer=mobileproxy'
    http_method = 'post'

    @property
    def http_query_args(self):
        return {
            'track_id': self.track_id,
            'number': TEST_PHONE_NUMBER.e164,
            'country': TEST_COUNTRY_CODE,
        }

    def get_expected_response(self, device_name=None):
        return {
            'backup_info': {
                'updated': TEST_TIMESTAMP_UPDATED,
                'device_name': device_name,
            },
        }

    def test_get_info_ok(self):
        self.setup_track()
        self.setup_blackbox_response(
            info_only=True,
            updated=TEST_TIMESTAMP_UPDATED,
            device_name=TEST_DEVICE_INFO['device_name'],
        )

        resp = self.make_request()
        self.assert_ok_response(
            resp,
            **self.get_expected_response(
                device_name=TEST_DEVICE_INFO['device_name'],
            )
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('succeeded', _exclude=['step']),
        ])

    def test_get_info_no_device_info_ok(self):
        self.setup_track()
        self.setup_blackbox_response(info_only=True, updated=TEST_TIMESTAMP_UPDATED, device_name=None)

        resp = self.make_request()
        self.assert_ok_response(resp, **self.get_expected_response())
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('succeeded', _exclude=['step']),
        ])

    def test_get_info_not_found_error(self):
        self.setup_track()
        self.setup_blackbox_response(is_found=False)

        resp = self.make_request()
        self.assert_error_response(resp, ['yakey_backup.not_found'])
