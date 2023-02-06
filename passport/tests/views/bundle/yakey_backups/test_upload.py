# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_BACKUP,
    TEST_COUNTRY_CODE,
    TEST_DATETIME_UPDATED,
    TEST_DEVICE_INFO,
    TEST_DEVICE_INFO_DECODED,
    TEST_PHONE_NUMBER,
    TEST_TIMESTAMP_UPDATED,
)
from passport.backend.core.db.faker.db import (
    yakey_backup_insert,
    yakey_backup_update,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import DatetimeNow

from .base import (
    BaseYaKeyBackupTestView,
    CommonYakeyBackupTestMixin,
)


TEST_BACKUP_2 = 'klaatu barada nikto'


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
)
class TestUploadTestCase(BaseYaKeyBackupTestView, CommonYakeyBackupTestMixin):
    default_url = '/1/bundle/yakey_backup/upload/?consumer=mobileproxy'
    http_method = 'post'

    step = 'upload'

    @property
    def http_query_args(self):
        return {
            'track_id': self.track_id,
            'number': TEST_PHONE_NUMBER.e164,
            'country': TEST_COUNTRY_CODE,
            'backup': TEST_BACKUP,
        }

    def test_invalid_form(self):
        resp = self.make_request(exclude_args=['backup'])
        self.assert_error_response(resp, ['backup.empty'])

    def test_upload_backup_already_exists_error(self):
        self.setup_track()
        self.setup_blackbox_response()

        resp = self.make_request()
        self.assert_error_response(resp, ['yakey_backup.exists'])
        self.env.statbox.assert_has_written([])
        eq_(len(self.env.blackbox.requests), 1)
        eq_(len(self.env.blackbox.get_requests_by_method('yakey_backup')), 1)

    def test_upload_force_update_ok(self):
        self.setup_track()
        self.setup_blackbox_response(is_found=True, updated=TEST_TIMESTAMP_UPDATED)

        resp = self.make_request(query_args=dict(force_update=True, backup=TEST_BACKUP_2))
        self.assert_ok_response(resp)
        self.env.statbox.assert_contains([
            self.env.statbox.entry('succeeded'),
        ], offset=-1)

        values = {
            'phone_number': int(TEST_PHONE_NUMBER.digital),
            'backup': TEST_BACKUP_2.encode('utf8'),
            'updated': DatetimeNow(),
            'device_name': None,
        }

        self.assert_db_ok(
            backup=TEST_BACKUP_2,
            queries=[yakey_backup_update(TEST_DATETIME_UPDATED).values([values])],
        )
        eq_(len(self.env.blackbox.requests), 1)
        eq_(len(self.env.blackbox.get_requests_by_method('yakey_backup')), 1)

    def test_upload_new(self):
        self.setup_track()
        self.setup_blackbox_response(is_found=False)

        resp = self.make_request()
        self.assert_ok_response(resp)
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('succeeded'),
        ])

        values = {
            'phone_number': int(TEST_PHONE_NUMBER.digital),
            'backup': TEST_BACKUP.encode('utf8'),
            'updated': DatetimeNow(),
            'device_name': None,
        }

        self.assert_db_ok(queries=[yakey_backup_insert().values([values])])
        eq_(len(self.env.blackbox.requests), 1)
        eq_(len(self.env.blackbox.get_requests_by_method('yakey_backup')), 1)

    def test_full_device_info_ok(self):
        self.setup_track()
        self.setup_blackbox_response(is_found=False)

        resp = self.make_request(query_args=TEST_DEVICE_INFO)
        self.assert_ok_response(resp)
        values = {
            'phone_number': int(TEST_PHONE_NUMBER.digital),
            'backup': TEST_BACKUP.encode('utf8'),
            'updated': DatetimeNow(),
            'device_name': TEST_DEVICE_INFO['device_name'],
        }

        self.assert_db_ok(
            queries=[yakey_backup_insert().values([values])],
            device_name=TEST_DEVICE_INFO['device_name'],
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('succeeded', **TEST_DEVICE_INFO_DECODED),
        ])
