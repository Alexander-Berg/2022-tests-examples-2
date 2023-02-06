# -*- coding: utf-8 -*-
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_BACKUP,
    TEST_COUNTRY_CODE,
    TEST_DEVICE_INFO,
    TEST_DEVICE_INFO_DECODED,
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
class TestDownloadTestCase(BaseYaKeyBackupTestView, CommonYakeyBackupTestMixin):

    default_url = '/1/bundle/yakey_backup/download/?consumer=mobileproxy'
    http_method = 'post'

    step = 'download'

    @property
    def http_query_args(self):
        return {
            'track_id': self.track_id,
            'number': TEST_PHONE_NUMBER.e164,
            'country': TEST_COUNTRY_CODE,
        }

    def get_expected_response(self, device_name=None):
        return {
            'backup': TEST_BACKUP,
            'backup_info': {
                'updated': TEST_TIMESTAMP_UPDATED,
                'device_name': device_name,
            },
        }

    def test_download_ok(self):
        self.setup_track()
        self.setup_blackbox_response(updated=TEST_TIMESTAMP_UPDATED, device_name=None)

        resp = self.make_request()
        self.assert_ok_response(resp, **self.get_expected_response())
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('succeeded'),
        ])

    def test_download_not_found_error(self):
        self.setup_track()
        self.setup_blackbox_response(is_found=False)

        resp = self.make_request()
        self.assert_error_response(resp, ['yakey_backup.not_found'])

    def test_full_device_info_ok(self):
        self.setup_track()
        self.setup_blackbox_response(updated=TEST_TIMESTAMP_UPDATED)

        resp = self.make_request(query_args=TEST_DEVICE_INFO)
        self.assert_ok_response(resp, **self.get_expected_response(TEST_DEVICE_INFO['device_name']))
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('succeeded', **TEST_DEVICE_INFO_DECODED),
        ])
