# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_BACKUP,
    TEST_CONFIRMATION_CODE,
    TEST_COUNTRY_CODE,
    TEST_DEVICE_INFO,
    TEST_DEVICE_INFO_DECODED,
    TEST_DISPLAY_LANGUAGE,
    TEST_PHONE_NUMBER,
    TEST_PHONE_NUMBER_DUMPED,
    TEST_TIMESTAMP_UPDATED,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base import BaseYaKeyBackupTestView


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
)
class TestYakeyBackupIntegrationalTestCase(BaseYaKeyBackupTestView):
    http_method = 'post'

    def send_code(self):
        send_code_url = '/1/bundle/yakey_backup/send_code/?consumer=mobileproxy'
        data = {
            'number': TEST_PHONE_NUMBER.e164,
            'country': TEST_COUNTRY_CODE,
            'display_language': TEST_DISPLAY_LANGUAGE,
        }
        return self.make_request(url=send_code_url, query_args=data)

    def check_code(self):
        check_code_url = '/1/bundle/yakey_backup/check_code/?consumer=mobileproxy'
        data = {
            'code': TEST_CONFIRMATION_CODE,
            'track_id': self.track_id,
        }
        return self.make_request(url=check_code_url, query_args=data)

    def upload(self):
        upload_url = '/1/bundle/yakey_backup/upload/?consumer=mobileproxy'
        data = {
            'track_id': self.track_id,
            'number': TEST_PHONE_NUMBER.e164,
            'country': TEST_COUNTRY_CODE,
            'backup': TEST_BACKUP,
            'device_name': TEST_DEVICE_INFO['device_name'],
        }
        return self.make_request(url=upload_url, query_args=data)

    def download(self):
        download_url = '/1/bundle/yakey_backup/download/?consumer=mobileproxy'
        data = {
            'track_id': self.track_id,
            'number': TEST_PHONE_NUMBER.e164,
            'country': TEST_COUNTRY_CODE,
        }
        return self.make_request(url=download_url, query_args=data)

    def assert_track_ok(self, code_sent=False, code_checked=False):
        if code_checked:
            code_sent = True

        if code_sent:
            eq_(self.track.process_name, 'yakey_backup')
        else:
            ok_(not self.track.process_name)

        ok_(not bool(self.track.phone_confirmation_code) ^ code_sent)
        ok_(not bool(self.track.phone_confirmation_last_send_at) ^ code_sent)
        ok_(not bool(self.track.phone_confirmation_sms_count.get(default=0)) ^ code_sent)
        ok_(not bool(self.track.phone_confirmation_confirms_count.get(default=0)) ^ code_checked)
        ok_(not bool(self.track.phone_confirmation_is_confirmed) ^ code_checked)

        if code_sent:
            eq_(self.track.phone_confirmation_phone_number_original, TEST_PHONE_NUMBER.original)
            eq_(self.track.country, TEST_COUNTRY_CODE)
        else:
            ok_(not self.track.phone_confirmation_phone_number_original)
            ok_(not self.track.country)

        ok_(not self.track.is_captcha_required)
        ok_(not self.track.is_captcha_checked)
        ok_(not self.track.is_captcha_recognized)

    def assert_statbox_ok(self, final_step, **kwargs):
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('succeeded', step='send_code'),
            self.env.statbox.entry('phone_confirmed'),
            self.env.statbox.entry('succeeded', step='check_code'),
            self.env.statbox.entry('succeeded', step=final_step, **kwargs),
        ])

    def _common_part(self):
        self.track = self.track_manager.read(self.track_id)
        self.assert_track_ok()
        send_code_resp = self.send_code()

        self.track = self.track_manager.read(self.track_id)
        expected = {
            'track_id': self.track_id,
            'number': TEST_PHONE_NUMBER_DUMPED,
        }
        self.assert_ok_response(send_code_resp, **expected)
        self.assert_sms_sent()
        self.assert_track_ok(code_sent=True)

        check_code_resp = self.check_code()
        self.track = self.track_manager.read(self.track_id)
        expected = {
            'track_id': self.track_id,
        }
        self.assert_ok_response(check_code_resp, **expected)
        self.assert_track_ok(code_checked=True)

    def test_upload_ok(self):
        self.setup_blackbox_response(is_found=False)

        self._common_part()

        self.assert_db_no_backup_for_number()
        upload_resp = self.upload()
        self.assert_ok_response(upload_resp)
        self.assert_db_ok(device_name=TEST_DEVICE_INFO['device_name'])

        self.assert_statbox_ok('upload', device_name=TEST_DEVICE_INFO_DECODED['device_name'])

    def test_download_ok(self):
        self.setup_blackbox_response(updated=TEST_TIMESTAMP_UPDATED)

        self._common_part()

        download_resp = self.download()
        expected = {
            'backup': TEST_BACKUP,
            'backup_info': {
                'updated': TEST_TIMESTAMP_UPDATED,
                'device_name': TEST_DEVICE_INFO['device_name'],
            }
        }
        self.assert_ok_response(download_resp, **expected)

        self.assert_statbox_ok('download')
