# pylint: disable=redefined-outer-name, import-error
import json

from pricing_extended import mocking_base
import pytest

from . import utils_request


class CouponsContext(mocking_base.BasicMock):
    def __init__(self):
        super().__init__()
        self.response = {
            'valid': True,
            'descr': 'good coupon',
            'currency_code': '$',
            'format_currency': False,
            'value': 0.0,
            'details': ['important', 'details', 'for', 'coupon'],
            'series_purpose': 'support',
            'expire_at': '2017-05-01T00:00:00+00:00',
        }
        self.locale = 'en'
        self.expected_order_id = None

    def set_expected_order_id(self, order_id):
        self.expected_order_id = order_id

    def check_request(self, request):
        data = json.loads(request.get_data())
        assert not data['format_currency']
        assert data['phone_id'] == 'PHONE_ID'
        assert data['current_yandex_uid'] == 'YANDEX_UID'
        assert data['zone_name'] == 'moscow'
        assert data['country'] == 'rus'
        assert data['time_zone'] == 'Europe/Moscow'
        assert data['locale'] == self.locale
        assert data['payment_info']
        assert 'coupon' in data['payment_options']
        assert 'apns_token' in data and data['apns_token'] == 'APNS_TOKEN'
        assert 'gcm_token' in data and data['gcm_token'] == 'GCM_TOKEN'
        assert 'device_id' in data and data['device_id'] == 'DEVICE_ID'
        assert 'payload' in data
        assert 'waypoints' in data['payload']
        assert len(data['payload']['waypoints']) == 2
        assert (
            request.headers['User-Agent'] == utils_request.DEFAULT_USER_AGENT
        )
        if self.expected_order_id:
            assert data['order_id'] == self.expected_order_id
        else:
            assert 'order_id' not in data

    def set_locale(self, value):
        self.locale = value

    def set_value(self, value):
        self.response['value'] = value

    def set_valid(self, value):
        self.response['valid'] = value

    def clear(self):
        self.response['value'] = 0.0


@pytest.fixture
def coupons():
    return CouponsContext()


@pytest.fixture
def mock_coupons(mockserver, coupons):
    @mockserver.json_handler('/coupons/v1/couponcheck')
    def coupons_check_handler(request):
        coupons.check_request(request)
        return coupons.process(mockserver)

    return coupons_check_handler
