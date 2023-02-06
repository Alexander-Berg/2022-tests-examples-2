# -*- coding: utf-8 -*-
import mock
from nose.tools import (
    assert_is_none,
    eq_,
)
from passport.backend.core.builders.historydb_api.faker.historydb_api import app_key_info
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.core.types.mobile_device_info import MobileDeviceInfo


@with_settings_hosts(
    INVALID_DEVICE_IDS={
        '0',
        '00000000-0000-0000-0000-000000000000',
    },
)
class MobileDeviceInfoTestCase(PassportTestCase):

    def test_create_from_track_with_device_hardware_id(self):
        track = mock.Mock(device_hardware_id='test_id', device_ifv=None)
        info = MobileDeviceInfo.from_track(track)

        eq_(info.device_id, 'test_id')

    def test_create_from_track_with_device_ifv(self):
        track = mock.Mock(device_hardware_id='', device_ifv='TEST_id')
        info = MobileDeviceInfo.from_track(track)

        eq_(info.device_id, 'test_id')

    def test_create_from_track_with_no_device_id(self):
        track = mock.Mock(device_hardware_id='', device_ifv='')
        info = MobileDeviceInfo.from_track(track)

        assert_is_none(info)

    def test_create_from_track_with_invalid_device_id(self):
        track = mock.Mock(device_hardware_id='', device_ifv='0')
        info = MobileDeviceInfo.from_track(track)

        assert_is_none(info)

    def test_create_from_app_key_info_for_ios(self):
        key_info = app_key_info(is_ios=True, device_ifv='TEST_ID')
        info = MobileDeviceInfo.from_app_key_info(key_info)

        eq_(info.device_id, 'test_id')

    def test_create_from_app_key_info_for_android(self):
        key_info = app_key_info(is_ios=False, device_hardware_id='TEST_ID')
        info = MobileDeviceInfo.from_app_key_info(key_info)

        eq_(info.device_id, 'test_id')

    def test_create_from_app_key_info_with_invalid_device_id(self):
        key_info = app_key_info(is_ios=False, device_hardware_id='00000000-0000-0000-0000-000000000000')
        info = MobileDeviceInfo.from_app_key_info(key_info)

        assert_is_none(info)

    def test_create_from_app_key_info_with_invalid_json(self):
        info = MobileDeviceInfo.from_app_key_info('{bad json')

        assert_is_none(info)
