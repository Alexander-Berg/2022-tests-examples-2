import json

from dateutil import parser
import pytest

CONSTANT_TIME = '2021-03-15T14:41:10.453105+00:00'

UPDATE_FIELDS_BODY_WITH_EMPTY_FIELDS_TO_UPDATE = {
    'park_id': 'park_id',
    'driver_profile_id': 'driver_profile_id',
    'setcar_id': 'setcar_id',
    'fields': {},
}


@pytest.mark.parametrize(
    'flags, expected_flags',
    [
        pytest.param(['flag_1'], r'{flag_1}', id='one_flag'),
        pytest.param(['flag_1', 'flag_2'], r'{flag_1,flag_2}', id='two_flags'),
        pytest.param(None, None, id='empty_flags'),
    ],
)
@pytest.mark.now(CONSTANT_TIME)
async def test_send_to_coh(
        taxi_driver_orders_app_api,
        contractor_order_history,
        flags,
        expected_flags,
):
    request = {
        'park_id': 'park_id',
        'driver_profile_id': 'driver_profile_id',
        'setcar_id': 'alias_id',
        'fields': {
            'cost_pay': 1.1,
            'cost_total': 1.2,
            'cost_sub': 1.3,
            'cost_commission': 1.4,
            'cost_discount': 1.5,
            'cost_cupon': 1.6,
            'cost_coupon_percent': 1.7,
            'cost_full': 1.8,
            'receipt_data': {'total_distance': 100.5},
            'address_to': {'key1': 'val1', 'key2': 'val2'},
            'fixed_price': {},
            # should not get into COH request
            'subvention': None,
            # 'route_points' is not specified
            # and should not get into COH request
            'flags': flags,
        },
    }

    response = await taxi_driver_orders_app_api.post(
        '/internal/v1/order-db-api/update-fields', json=request,
    )
    assert response.status_code == 200

    coh_request_args = await contractor_order_history.update.wait_call()
    coh_request = coh_request_args['self'].json
    assert coh_request['updated_ts'] == int(
        parser.parse(CONSTANT_TIME).timestamp() * 1000,
    )
    assert coh_request['park_id'] == request['park_id']
    assert coh_request['alias_id'] == request['setcar_id']
    coh_fields = coh_request['order_fields']
    req_fields = request['fields']
    for item in coh_fields:
        name = item['name']
        if name.startswith('cost_'):
            assert float(item['value']) == req_fields[name]
        elif name in ('subvention', 'route_points'):
            assert False
        elif name == 'flags':
            assert item['value'] == expected_flags
        else:
            assert json.loads(item['value']) == req_fields[name]


async def test_send_bad_request(taxi_driver_orders_app_api):
    response = await taxi_driver_orders_app_api.post(
        '/internal/v1/order-db-api/update-fields',
        json=UPDATE_FIELDS_BODY_WITH_EMPTY_FIELDS_TO_UPDATE,
    )
    assert response.status_code == 400
