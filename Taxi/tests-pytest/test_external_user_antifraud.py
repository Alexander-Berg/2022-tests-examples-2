import pytest
import datetime
import json

from taxi.conf import settings
from taxi.core import arequests
from taxi.core import async
from taxi.external import user_antifraud


ORDER_DOC = {
    '_id': 'order_id1',
    'status': 'assigned',
    'taxi_status': 'driving',
    'user_phone_id': 'user_phone_id1',
    'user_uid': 'user_uid1',
    'user_id': 'user_id1',
    'uber_id': 'uber_id1',
    'city': 'Moscow',
    'nz': 'mytishchi',
    'created': datetime.datetime.strptime('2022-02-22 22:22:22', '%Y-%m-%d %H:%M:%S'),
    'payment_tech': {
        'type': 'card',
        'main_card_payment_id': 'card-1234',
    },
    'class': 'vip',
    'device_id': 'device_id1',
    'antifraud_group': 1,
    'current_prices': {
        'kind': 'fixed',
        'user_ride_display_price': 510,
        'user_total_display_price': 511,
        'user_total_price': 512,
    },
    'fixed_price': {
      'destination': [
         37.565305946734,
         55.7455375419869
      ],
      'driver_price': 513,
      'max_distance_from_b': 501,
      'price': 514,
      'price_original': 515,
      'show_price_in_taximeter': False,
    },
}


def _check_test_request(req):
    assert req['currency'] == 'RUB'
    assert req['current_price'] == 512
    assert req['fixed_price_original'] == 515
    assert req['is_fixed_price']


@pytest.inline_callbacks
def test_get_status(patch):

    @patch('taxi.core.arequests.post')
    @async.inline_callbacks
    def mock_post_request(url, timeout=None, *args, **kwargs):
        _check_test_request(kwargs['json'])
        response = {
            'use_custom_config': True,
            'status': 'hacked',
        }
        yield
        async.return_value(arequests.Response(
            status_code=200, content=json.dumps(response)))

    order_doc = ORDER_DOC

    qargs = user_antifraud.QueryArgs(
        order_doc, order_doc['payment_tech'], order_doc['class'],
        order_doc['antifraud_group'], currency='RUB',
        current_price=order_doc['current_prices']['user_total_price'],
        is_fixed_price=('fixed_price' in order_doc),
        personal_phone_id='personal_phone_id'
    )

    user_antifraud_status = yield user_antifraud.get_status(
        settings.STQ_TVM_SERVICE_NAME, qargs, log_extra=None)

    assert user_antifraud_status['use_custom_config']
    assert user_antifraud_status['status'] == 'hacked'
