# -*- coding: utf-8 -*-
import datetime

from nose.tools import eq_
from passport.backend.core.builders.blackbox.blackbox import Blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_yakey_backup_response
from passport.backend.core.test.test_utils import (
    check_all_url_params_match,
    with_settings,
)
from passport.backend.core.test.time_utils.time_utils import datetime_to_unixtime
from passport.backend.core.types.phone_number.phone_number import PhoneNumber

from .test_blackbox import (
    BaseBlackboxRequestTestCase,
    BaseBlackboxTestCase,
)


TEST_INVALID_PHONE_NUMBER = PhoneNumber.parse('+380390000000', allow_impossible=True)
TEST_PHONE_NUMBER = PhoneNumber.parse('+79090000001')
TEST_PHONE_NUMBER_DIGITAL = int(TEST_PHONE_NUMBER.digital)
TEST_BACKUP = 'abc123456def'
TEST_DATETIME_LONG_AGO = datetime.datetime(1970, 1, 2)
TEST_TIMESTAMP_LONG_AGO = datetime_to_unixtime(TEST_DATETIME_LONG_AGO)
TEST_DEVICE_NAME = 'my device'


@with_settings(BLACKBOX_URL='http://localhost/')
class TestBlackboxRequestYaKeyBackupParse(BaseBlackboxRequestTestCase):
    def get_expected_response(self, found=False, phone_number=TEST_PHONE_NUMBER):
        response = {
            'status': 'EXISTS' if found else 'NOT_FOUND',
        }
        if found:
            response['yakey_backup'] = {
                'phone_number': phone_number,
                'backup': TEST_BACKUP,
                'updated': TEST_TIMESTAMP_LONG_AGO,
                'device_name': TEST_DEVICE_NAME,
            }
        return response

    def test_parse_yakey_backup_exists(self):
        self.set_blackbox_response_value(blackbox_yakey_backup_response(
            phone_number=TEST_PHONE_NUMBER_DIGITAL,
            updated=TEST_TIMESTAMP_LONG_AGO,
            backup=TEST_BACKUP,
            device_name=TEST_DEVICE_NAME,
        ))
        response = self.blackbox.yakey_backup(TEST_PHONE_NUMBER_DIGITAL)
        eq_(response, self.get_expected_response(found=True))

    def test_parse_yakey_backup_not_found(self):
        self.set_blackbox_response_value(
            blackbox_yakey_backup_response(is_found=False),
        )
        response = self.blackbox.yakey_backup(TEST_PHONE_NUMBER_DIGITAL)
        eq_(response, self.get_expected_response())

    def test_parse_yakey_backup_invalid_phone_number(self):
        self.set_blackbox_response_value(blackbox_yakey_backup_response(
            phone_number=int(TEST_INVALID_PHONE_NUMBER.digital),
            updated=TEST_TIMESTAMP_LONG_AGO,
            backup=TEST_BACKUP,
            device_name=TEST_DEVICE_NAME,
        ))
        response = self.blackbox.yakey_backup(TEST_PHONE_NUMBER_DIGITAL)
        eq_(response, self.get_expected_response(found=True, phone_number=TEST_INVALID_PHONE_NUMBER))


@with_settings(
    BLACKBOX_URL='http://test.local/',
)
class TestBlackboxRequestYaKeyBackupUrl(BaseBlackboxTestCase):
    def test_get_yakey_backup_url_default(self):
        request_info = Blackbox().build_yakey_backup_request(TEST_PHONE_NUMBER_DIGITAL)
        check_all_url_params_match(
            request_info.url,
            {
                'phone_number': str(TEST_PHONE_NUMBER_DIGITAL),
                'method': 'yakey_backup',
                'meta': 'False',
                'format': 'json',
            },
        )

    def test_get_yakey_backup_url(self):
        request_info = Blackbox().build_yakey_backup_request(TEST_PHONE_NUMBER_DIGITAL, True)
        check_all_url_params_match(
            request_info.url,
            {
                'phone_number': str(TEST_PHONE_NUMBER_DIGITAL),
                'method': 'yakey_backup',
                'meta': 'True',
                'format': 'json',
            },
        )
