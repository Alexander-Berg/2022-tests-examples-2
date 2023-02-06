# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.oauth.core.db.device_info import get_device_info
from passport.backend.oauth.core.test.framework import (
    BaseTestCase,
    PatchesMixin,
)


class GetDeviceInfoTestCase(BaseTestCase, PatchesMixin):
    def setUp(self):
        super(GetDeviceInfoTestCase, self).setUp()
        self.patch_device_names_mapping()

    def make_request_values(self, **kwargs):
        values = {
            'uid': '1',
            'username': 'test',
            'uuid': '550e8400-e29b-41d4-a716-446655440000',
            'deviceid': 'xxx',
            'app_id': 'com.yandex.maps',
            'app_platform': 'android',
            'manufacturer': 'htc',
            'model': 'wildfire',
            'app_version': '0.0.1',
            'am_version': '0.0.2',
            'ifv': 'not_ios',
            'device_name': 'Vasya Poupkin\'s phone',
        }
        values.update(kwargs)
        return values

    def test_get_device_info(self):
        request_values = self.make_request_values(device_id='some specific id')
        eq_(
            get_device_info(request_values),
            {
                'uuid': '550e8400-e29b-41d4-a716-446655440000',
                'deviceid': 'xxx',
                'app_id': 'com.yandex.maps',
                'app_platform': 'android',
                'manufacturer': 'htc',
                'model': 'wildfire',
                'model_name': 'wildfire',
                'app_version': '0.0.1',
                'am_version': '0.0.2',
                'ifv': 'not_ios',
                'device_name': 'Vasya Poupkin\'s phone',
                'device_id': 'some specific id',
            },
        )

    def test_get_device_id_from_deviceid(self):
        request_values = self.make_request_values()
        device_info = get_device_info(request_values)
        eq_(device_info['device_id'], 'xxx')

    def test_get_device_id_from_ifv(self):
        request_values = self.make_request_values(deviceid='0')
        device_info = get_device_info(request_values)
        eq_(device_info['device_id'], 'not_ios')

    def test_device_id_null(self):
        request_values = self.make_request_values(
            device_id='',
            deviceid='',
            ifv='00000000-0000-0000-0000-000000000000',
        )
        device_info = get_device_info(request_values)
        ok_('device_id' not in device_info)

    def test_device_name_empty(self):
        request_values = self.make_request_values(
            device_name='',
        )
        device_info = get_device_info(request_values)
        ok_('device_name' not in device_info)

    def test_device_name_stripped_empty(self):
        request_values = self.make_request_values(
            device_name='   ',
        )
        device_info = get_device_info(request_values)
        ok_('device_name' not in device_info)

    def test_device_name_equals_to_model(self):
        request_values = self.make_request_values(
            device_name='model',
            model='model',
        )
        device_info = get_device_info(request_values)
        ok_('device_name' not in device_info)

    def test_device_name_stripped(self):
        request_values = self.make_request_values(
            device_name='  some name  ',
        )
        device_info = get_device_info(request_values)
        eq_(device_info['device_name'], 'some name')

    def test_model_name_by_model_and_manufacturer(self):
        request_values = self.make_request_values(
            model='iPhone7',
            manufacturer='Sony',
        )
        device_info = get_device_info(request_values)
        eq_(device_info['model_name'], 'iPhone Cheap')

    def test_model_name_by_model_and_unknown_manufacturer(self):
        request_values = self.make_request_values(
            model='iPhone7',
            manufacturer='Apple',
        )
        device_info = get_device_info(request_values)
        eq_(device_info['model_name'], 'iPhone 7')

    def test_model_name_by_model(self):
        request_values = self.make_request_values(
            model='iPhone7',
        )
        device_info = get_device_info(request_values)
        eq_(device_info['model_name'], 'iPhone 7')

    def test_model_name_by_manufacturer(self):
        request_values = self.make_request_values(
            manufacturer='Sony',
        )
        device_info = get_device_info(request_values)
        eq_(device_info['model_name'], 'Sony')

    def test_model_name_by_unknown_model(self):
        request_values = self.make_request_values(
            model='iPad',
        )
        device_info = get_device_info(request_values)
        eq_(device_info['model_name'], 'iPad')

    def test_model_name_by_unknown_manufacturer(self):
        request_values = self.make_request_values(
            model=None,
            manufacturer='Apple',
        )
        device_info = get_device_info(request_values)
        eq_(device_info['model_name'], 'Apple')

    def test_model_name_by_all_unknown(self):
        request_values = self.make_request_values(
            model=None,
            manufacturer=None,
        )
        device_info = get_device_info(request_values)
        ok_('model_name' not in device_info)

    def test_aliases(self):
        request_values = self.make_request_values(
            app_version='0.0.1',
            app_version_name='0.0.3',
            am_version=None,
            am_version_name='0.0.4',
        )
        device_info = get_device_info(request_values)
        eq_(device_info['app_version'], '0.0.1')
        eq_(device_info['am_version'], '0.0.4')
        ok_('app_version_name' not in device_info)
        ok_('am_version_name' not in device_info)
