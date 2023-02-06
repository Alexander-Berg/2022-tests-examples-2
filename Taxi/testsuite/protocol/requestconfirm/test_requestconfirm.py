import copy
import datetime
import json
import time
import uuid

import bson
import pytest

from order_core_switch_parametrize import PROTOCOL_SWITCH_TO_ORDER_CORE
from protocol.ordercommit import order_commit_common

API_OVER_DATA_WORK_MODE = {
    '__default__': {'__default__': 'oldway'},
    'parks-activation-client': {'protocol': 'newway'},
}

SOLO_PHONE_OPTION = {
    'call_dialog_message_prefix': 'solo call dialog message prefix',
    'label': 'solo phone',
    'type': 'main',
}
MAIN_PHONE_OPTION = {
    'call_dialog_message_prefix': 'main call dialog message prefix',
    'label': 'main phone',
    'type': 'main',
}
EXTRA_PHONE_OPTION = {
    'call_dialog_message_prefix': 'extra call dialog message prefix',
    'label': 'extra phone',
    'type': 'extra',
}

RECEIPT = {
    'area_ids': {'ufa': 'f2313a01f2b14ae883147cce1b34eb36'},
    'areas': ['ufa'],
    'calc_class': 'yandex',
    'calc_method': 2,
    'calc_total': 157.0,
    'details': [
        {
            'count': 1,
            'name': 'child_chair.booster',
            'meter_type': 'distance',
            'meter_value': 10703.691472337661,
            'per': 1000.0,
            'price': 8.0,
            'service_type': 'free_route',
            'sum': 85.62953177870129,
            'zone_names': ['ufa'],
        },
        {
            'meter_type': 'time',
            'meter_value': 1283.0,
            'per': 60.0,
            'price': 1.0,
            'service_type': 'free_route',
            'sum': 21.383333333333333,
            'zone_names': ['ufa'],
        },
        {
            'meter_type': 'time',
            'meter_value': 2,
            'per': 60,
            'price': 9,
            'service_type': 'waiting',
            'sum': 20.1,
            'zone_names': ['moscow'],
        },
        {
            'meter_type': 'time',
            'meter_value': 2,
            'per': 60,
            'price': 9,
            'service_type': 'waiting',
            'sum': 20.1,
            'zone_names': ['moscow'],
        },
    ],
    'distances_by_areas': {'ufa': 10703.691472337661},
    'dst_actual_point': {'lat': 54.70032, 'lon': 55.994981666666675},
    'dst_address': 'addr1',
    'dst_order_point': {'lat': 54.701095, 'lon': 55.995109},
    'durations_by_areas': {'ufa': 1283.0},
    'min_price': 49.0,
    'src_address': 'addr2',
    'src_point': {'lat': 54.775290524, 'lon': 56.0231119848},
    'sum': 155.0,
    'tariff_id': 'cc9db53fbfcf4223a594cf291d4da436',
    'total': 155.0,
    'total_distance': 10703.691472337661,
    'total_duration': 1283.0,
    'transfer': False,
    'version': '8.35 (290)',
}

DRIVER_RECEIPT = {
    'calc_class': 'yandex',
    'calc_method': 2,
    'details': [
        {
            'meter_type': 'distance',
            'meter_value': 7291.123637088756,
            'per': 1000,
            'price': 9,
            'service_type': 'free_route',
            'skip_before': 2000,
            'sum': 65.6201127337988,
            'zone_names': ['moscow'],
        },
        {
            'meter_type': 'time',
            'meter_value': 225,
            'per': 60,
            'price': 9,
            'service_type': 'free_route',
            'sum': 33.75,
            'zone_names': ['moscow'],
        },
        {
            'meter_type': 'time',
            'meter_value': 2,
            'per': 60,
            'price': 9,
            'service_type': 'waiting',
            'sum': 120,
            'zone_names': ['moscow'],
        },
        {
            'meter_type': 'time',
            'meter_value': 2,
            'per': 60,
            'price': 9,
            'service_type': 'waiting',
            'sum': 420,
            'zone_names': ['moscow'],
        },
    ],
    'transfer': False,
    'min_price': 100,
    'tariff_id': 'bae9c9f06203403aa892122e0d255a36',
    'total': 234,
    'total_distance': 8709.048311380839,
    'total_duration': 225,
}


class PricingCompleteData:
    def __init__(self):
        self._final_cost = None
        self._final_cost_meta = None

    def set_final_cost(self, driver_cost, user_cost):
        self._final_cost = {
            'driver': {'total': driver_cost},
            'user': {'total': user_cost},
        }

    def set_final_cost_meta(self, meta):
        self._final_cost_meta = meta

    @property
    def final_cost(self):
        return self._final_cost

    @property
    def final_cost_meta(self):
        return self._final_cost_meta

    def to_json(self):
        if not self.final_cost or not self.final_cost_meta:
            return {}
        return {
            'final_cost': self.final_cost,
            'final_cost_meta': self.final_cost_meta,
            'price_verifications': {
                'uuids': {'recalculated': str(uuid.uuid4())},
            },
        }


def _extract_waiting_params(driver_receipt):
    price = 0
    time = 0

    for detail in driver_receipt['details']:
        if (
                detail['service_type'] == 'waiting'
                or detail['service_type'] == 'waiting_in_transit'
                or detail['service_type'] == 'unloading'
        ):
            price += detail['sum']
            time += detail['meter_value']

    return price, time


def _get_receipt():
    return {
        'area_ids': {'ufa': 'f2313a01f2b14ae883147cce1b34eb36'},
        'areas': ['ufa'],
        'calc_class': 'yandex',
        'calc_method': 2,
        'calc_total': 157.0,
        'details': [
            {
                'count': 1,
                'name': 'child_chair.booster',
                'meter_type': 'distance',
                'meter_value': 10703.691472337661,
                'per': 1000.0,
                'price': 8.0,
                'service_type': 'free_route',
                'sum': 85.62953177870129,
                'zone_names': ['ufa'],
            },
            {
                'meter_type': 'time',
                'meter_value': 1283.0,
                'per': 60.0,
                'price': 1.0,
                'service_type': 'free_route',
                'sum': 21.383333333333333,
                'zone_names': ['ufa'],
            },
        ],
        'distances_by_areas': {'ufa': 10703.691472337661},
        'dst_actual_point': {'lat': 54.70032, 'lon': 55.994981666666675},
        'dst_address': 'addr1',
        'dst_order_point': {'lat': 54.701095, 'lon': 55.995109},
        'durations_by_areas': {'ufa': 1283.0},
        'min_price': 49.0,
        'src_address': 'addr2',
        'src_point': {'lat': 54.775290524, 'lon': 56.0231119848},
        'sum': 155.0,
        'tariff_id': 'cc9db53fbfcf4223a594cf291d4da436',
        'total': 155.0,
        'total_distance': 10703.691472337661,
        'total_duration': 1283.0,
        'transfer': False,
        'version': '8.35 (290)',
    }


def _setup_coupon(db, order_id, value, was_used=True):
    db.order_proc.update(
        {'_id': order_id},
        {
            '$set': {
                'order.coupon': {
                    'id': 'promocode321',
                    'valid': True,
                    'valid_any': True,
                    'value': value,
                    'was_used': was_used,
                },
                'order.with_coupon.paid_supply': True,
            },
        },
    )


def _check_published_prices_when_assign(pricing_data, timestamp, paid_supply):
    assert pricing_data['published']['current_method'] == 'fixed'
    assert 'taximeter' not in pricing_data['published']
    assert pricing_data['published']['fixed']['timestamp'] == timestamp

    expected_driver, expected_user = (
        pricing_data['driver'],
        pricing_data['user'],
    )
    if paid_supply:
        expected_driver = expected_driver['additional_prices']['paid_supply']
        expected_user = expected_user['additional_prices']['paid_supply']
    actual_cost, actual_meta = (
        pricing_data['published']['fixed']['cost'],
        pricing_data['published']['fixed']['meta'],
    )

    assert actual_cost['driver']['total'] == expected_driver['price']['total']
    assert actual_cost['user']['total'] == expected_user['price']['total']
    assert actual_meta['driver'] == expected_driver['meta']
    assert actual_meta['user'] == expected_user['meta']


@pytest.mark.parametrize(
    'params,expected_state',
    [
        (
            {
                'status': 'failed',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
            },
            (200, 'pending', None),
        ),
        (
            {
                'status': 'failed',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
                'cancel': 'paid',
            },
            (406, 'assigned', 'waiting'),
        ),
        (
            {
                'status': 'cancelled',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
            },
            (200, 'finished', 'cancelled'),
        ),
        (
            {
                'status': 'cancelled',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
                'cancel': 'paid',
            },
            (406, 'assigned', 'waiting'),
        ),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=5))
@pytest.mark.parametrize(
    'driving_off',
    [
        False,
        pytest.param(True, marks=pytest.mark.filldb(order_proc='driving_off')),
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_failed_free(
        taxi_protocol,
        db,
        params,
        expected_state,
        order_core_switch_on,
        mock_order_core,
        driving_off,
):
    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
    }
    request_params.update(params)

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)

    proc = db.order_proc.find_one('8c83b49edb274ce0992f337061047375')
    assert expected_state == (
        response.status_code,
        proc['status'],
        proc['order']['taxi_status'],
    )

    if expected_state == (200, 'pending', None):
        assert proc['status'] == 'pending'
        status_update = proc['order_info']['statistics']['status_updates'][-1]
        assert status_update['q'] == 'autoreorder'
        assert status_update['s'] == 'pending'
    elif expected_state == (200, 'finished', 'cancelled'):
        assert proc['status'] == 'finished'
        assert proc['order']['status'] == 'finished'
        assert proc['order']['taxi_status'] == 'cancelled'
        assert proc['order']['cost'] is None
        status_update = proc['order_info']['statistics']['status_updates'][-1]
        assert status_update['s'] == 'finished'
        assert status_update['t'] == 'cancelled'
    elif expected_state == (406, 'assigned', 'waiting'):
        pass
    else:
        pytest.fail('unhandled state %r' % expected_state)

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.parametrize(
    'coupon_was_used,final_user_cost_meta,cost,driver_cost',
    [
        (
            True,
            {'use_cost_includes_coupon': False, 'coupon_value': 100},
            5000,
            234,
        ),
        (
            True,
            {'use_cost_includes_coupon': True, 'coupon_value': 100},
            155,
            234,
        ),
        (
            False,
            {'use_cost_includes_coupon': True, 'coupon_value': 100},
            5000,
            234,
        ),
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_correct_cost(
        taxi_protocol,
        db,
        coupon_was_used,
        final_user_cost_meta,
        cost,
        driver_cost,
        order_core_switch_on,
        mock_order_core,
):
    _setup_coupon(
        db,
        '1c83b49edb274ce0992f337061047375',
        200.0,
        was_used=coupon_was_used,
    )

    request_params = {
        'orderid': 'db60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'db_id': '12345',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'use_recommended_cost': False,
        'user_login': 'disp_login',
        'status': 'complete',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
        'extra': '5000',
        'calc_method': 4,
        'is_captcha': True,
        'is_airplanemode': False,
        'is_offline': True,
        'driver_status': 'free',
        'receipt': RECEIPT,
        'driver_calc_receipt_overrides': DRIVER_RECEIPT,
    }
    pricing_complete_data = PricingCompleteData()
    pricing_complete_data.set_final_cost(
        driver_cost=driver_cost, user_cost=cost,
    )
    pricing_complete_data.set_final_cost_meta(
        {'driver': {}, 'user': final_user_cost_meta},
    )
    request_params.update(pricing_complete_data.to_json())
    uri = '1.x/requestconfirm?clid=999012&apikey='
    api_key = 'd19a9b3b59424881b57adf5b0f367a2c'
    response = taxi_protocol.post(uri + api_key, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one('1c83b49edb274ce0992f337061047375')
    assert proc['order']['cost'] == cost
    assert proc['order']['driver_cost']['cost'] == driver_cost
    assert proc['order_info']['cc'] == cost

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.config(REQUESTCONFIRM_COUPON_RESET_FROM_PRICING_ENABLED=True)
@pytest.mark.parametrize(
    'final_cost_user_meta, expected_coupon_was_used, config_enabled',
    [
        (None, True, True),
        ({'coupon_value': 1}, True, True),
        ({'coupon_value': 0}, False, True),
        ({}, False, True),
        ({'coupon_value': 0}, True, False),
    ],
    ids=[
        'no_pricing_meta',
        'coupon_used_in_pricing',
        'coupon_not_used_in_pricing',
        'empty_meta',
        'coupon_used_but_config_disabled',
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_reset_coupon_from_pricing(
        taxi_protocol,
        db,
        final_cost_user_meta,
        expected_coupon_was_used,
        config_enabled,
        taxi_config,
        order_core_switch_on,
        mock_order_core,
):
    taxi_config.set(
        REQUESTCONFIRM_COUPON_RESET_FROM_PRICING_ENABLED=config_enabled,
    )
    _setup_coupon(db, '1c83b49edb274ce0992f337061047375', 200.0, was_used=True)

    request_params = {
        'orderid': 'db60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'db_id': '12345',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'use_recommended_cost': False,
        'user_login': 'disp_login',
        'status': 'complete',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
        'extra': '5000',
        'calc_method': 4,
        'is_captcha': True,
        'is_airplanemode': False,
        'is_offline': True,
        'driver_status': 'free',
        'receipt': RECEIPT,
        'driver_calc_receipt_overrides': DRIVER_RECEIPT,
    }
    pricing_complete_data = PricingCompleteData()
    if final_cost_user_meta is not None:
        pricing_complete_data.set_final_cost(driver_cost=0, user_cost=0)
        pricing_complete_data.set_final_cost_meta(
            {'driver': {}, 'user': final_cost_user_meta},
        )
    request_params.update(pricing_complete_data.to_json())
    uri = '1.x/requestconfirm?clid=999012&apikey='
    api_key = 'd19a9b3b59424881b57adf5b0f367a2c'
    response = taxi_protocol.post(uri + api_key, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one('1c83b49edb274ce0992f337061047375')
    assert proc['order']['coupon']['was_used'] == expected_coupon_was_used

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=5))
@pytest.mark.config(CARGO_CLAIMS_AUTOREORDER_ENABLED=True)
@pytest.mark.parametrize(
    ['claims_code', 'claims_response', 'expect_reorder'],
    [
        (
            200,
            {'reason': 'mock_config', 'is_autoreorder_enabled': False},
            False,
        ),
        (200, {'reason': 'mock_config', 'is_autoreorder_enabled': True}, True),
        (200, {'reason': 'mock_config'}, True),
        (404, {'error': 'not_found'}, True),
    ],
)
@pytest.mark.parametrize(
    'target_service',
    [
        pytest.param('cargo-claims', id='target_service_cargo_claims'),
        pytest.param(
            'api-proxy',
            marks=(pytest.mark.config(CARGO_PROTOCOL_API_PROXY=True)),
            id='target_service_api_proxy',
        ),
    ],
)
@pytest.mark.parametrize('use_order_core', [False, True])
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_autoreorder(
        taxi_protocol,
        mockserver,
        db,
        claims_code,
        claims_response,
        expect_reorder,
        config,
        mock_order_core,
        use_order_core,
        target_service: str,
        order_core_switch_on,
):
    if use_order_core:
        config.set_values(
            dict(PROCESSING_BACKEND_CPP_SWITCH=['requestconfirm']),
        )

    @mockserver.json_handler(f'/{target_service}/v1/claims/driver-changes')
    def _mock_cargo_claims(request):
        return {'action_disabled': False}

    @mockserver.json_handler(f'/{target_service}/v1/claims/autoreorder')
    def autoreorder(request):
        return mockserver.make_response(
            status=claims_code, response=json.dumps(claims_response),
        )

    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'order.request.cargo_ref_id': '12345'}},
    )
    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'status': 'failed',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
        'db_id': 'some park_id',
    }

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    if use_order_core:
        assert mock_order_core.post_event_times_called == 1
        return
    assert mock_order_core.post_event_times_called == 0

    proc = db.order_proc.find_one('8c83b49edb274ce0992f337061047375')
    if expect_reorder:
        status_update = proc['order_info']['statistics']['status_updates'][-1]
        assert proc['status'] == 'pending'
        assert status_update['q'] == 'autoreorder'
        assert status_update['s'] == 'pending'
        return
    assert proc['status'] == 'finished'

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=5))
@pytest.mark.config(CARGO_CLAIMS_AUTOREORDER_ENABLED=True)
@pytest.mark.config(CARGO_CLAIMS_PAID_CANCEL_ENABLED=True)
@pytest.mark.parametrize(
    'target_service',
    [
        pytest.param('cargo-claims', id='target_service_cargo_claims'),
        pytest.param(
            'api-proxy',
            marks=(pytest.mark.config(CARGO_PROTOCOL_API_PROXY=True)),
            id='target_service_api_proxy',
        ),
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_paid_cancel(
        taxi_protocol,
        mockserver,
        db,
        target_service: str,
        order_core_switch_on,
        mock_order_core,
):
    @mockserver.json_handler(f'/{target_service}/v1/claims/driver-changes')
    def _mock_cargo_claims(request):
        return {'action_disabled': False}

    @mockserver.json_handler(f'/{target_service}/v1/claims/autoreorder')
    def autoreorder(request):
        return mockserver.make_response(
            status=200,
            response=json.dumps(
                {'reason': 'mock_config', 'is_autoreorder_enabled': True},
            ),
        )

    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'order.request.cargo_ref_id': '12345'}},
    )
    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'status': 'failed',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
        'db_id': 'some park_id',
    }

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one('8c83b49edb274ce0992f337061047375')
    status_update = proc['order_info']['statistics']['status_updates'][-1]
    assert proc['status'] == 'pending'
    assert status_update['q'] == 'autoreorder'
    assert status_update['s'] == 'pending'

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=5))
@pytest.mark.parametrize(
    'config_values,reordered',
    [
        ({'DISABLE_AUTOREORDER_FOR_EARLY_HOLD': True}, False),
        ({'DISABLE_AUTOREORDER_FOR_EARLY_HOLD': False}, True),
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_autoreorder_early_hold(
        taxi_protocol,
        now,
        config,
        db,
        config_values,
        reordered,
        order_core_switch_on,
        mock_order_core,
):
    config.set_values(config_values)
    taxi_protocol.invalidate_caches(now=now)
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'payment_tech.early_hold': True}},
    )

    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'status': 'failed',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
    }

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one('8c83b49edb274ce0992f337061047375')
    status_update = proc['order_info']['statistics']['status_updates'][-1]

    if reordered:
        assert proc['status'] == 'pending'
        assert proc['order']['taxi_status'] is None
        assert status_update['q'] == 'autoreorder'
        assert status_update['s'] == 'pending'
    else:
        assert proc['status'] == 'finished'
        assert proc['order']['taxi_status'] == 'failed'
        assert status_update['t'] == 'failed'
        assert status_update['s'] == 'finished'

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=5))
@pytest.mark.config(
    REQUESTCONFIRM_SBP_MOVE_TO_CASH_FAILED_PAYMENT=True,
    REQUESTCONFIRM_SBP_MOVE_TO_CASH_FAILED_PAYMENT_ALLOWED_STATUSES=[
        'complete',
    ],
    REQUESTCONFIRM_SBP_FAILED_INVOICE_STATUSES=['hold-failed'],
)
@pytest.mark.parametrize(
    'order_status,invoice_status,moved_to_cash',
    [
        pytest.param(
            'complete',
            'cleared',
            False,
            id='invoice not failed, do not move to cash',
        ),
        pytest.param(
            'transporting',
            'cleared',
            False,
            id='order not complete, do not move to cash',
        ),
        pytest.param(
            'transporting',
            'hold-failed',
            False,
            id='order not complete, invoice failed, do not move to cash',
        ),
        pytest.param(
            'complete',
            'hold-failed',
            True,
            id='order complete, invoice failed, move to cash',
        ),
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_sbp_move_to_cash(
        taxi_protocol,
        now,
        mockserver,
        db,
        order_status,
        invoice_status,
        moved_to_cash,
        order_core_switch_on,
        mock_order_core,
):
    @mockserver.json_handler('/transactions/v2/invoice/retrieve')
    def transactions_invoice_retrieve(request):
        return {
            'id': '8c83b49edb274ce0992f337061047375',
            'status': invoice_status,
            'foo': (
                'bar'  # check nothing goes wrong if extra fields are present
            ),
        }

    taxi_protocol.invalidate_caches(now=now)
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'payment_tech.type': 'sbp'}},
    )

    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'status': order_status,
        'latitude': '55.733410768',
        'longitude': '37.589179973',
    }

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one('8c83b49edb274ce0992f337061047375')
    moved_to_cash_status_update = proc['order_info']['statistics'][
        'status_updates'
    ][-2]
    status_update = proc['order_info']['statistics']['status_updates'][-1]

    if moved_to_cash and order_core_switch_on:
        assert moved_to_cash_status_update['q'] == 'moved_to_cash'
        assert moved_to_cash_status_update['a'] == {
            'reason_code': 'UNUSABLE_CARD',
            'with_coupon': False,
            'force_action': True,
            'invalidate_transactions': False,
        }

    assert proc['order']['taxi_status'] == order_status
    assert status_update['t'] == order_status

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=5))
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_status_update_is_ivr(
        taxi_protocol, db, order_core_switch_on, mock_order_core,
):
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            '$set': {
                'status': 'driving',
                'order.svo_car_number': 'aaa',
                'order.verson': 1,
                'processing.version': 1,
                'processing.need_start': False,
            },
        },
    )
    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
        'extra': '210',
        'total': '210',
        'sum': '210',
        'user_login': 'Yandex IVR',
        'status': 'transporting',
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    taxi_protocol.post(uri, request_params)
    proc = db.order_proc.find_one('8c83b49edb274ce0992f337061047375')
    status_update = proc['order_info']['statistics']['status_updates'][-1]
    assert status_update['ii'] is True


@pytest.mark.parametrize(
    'params, within_pickup_zone, expected_response, tracker_valid',
    [
        (
            {
                'status': 'waiting',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
            },
            None,
            (200, {'phone_options': []}),
            False,
        ),
        (
            {
                'status': 'waiting',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
            },
            False,
            (200, {'phone_options': []}),
            False,
        ),
        (
            {
                'status': 'waiting',
                'latitude': '55.743410768',
                'longitude': '37.599179973',
            },
            True,
            (200, {'phone_options': []}),
            False,
        ),
        (
            {
                'status': 'waiting',
                'latitude': '56.743410768',
                'longitude': '38.599179973',
            },
            False,
            (
                406,
                {
                    'error': {
                        'error_action': 'show_error',
                        'error_message': (
                            'You need to be at least 500 meters '
                            'closer to the pickup point before you can '
                            'change your status.'
                        ),
                        'meters': 500,
                    },
                },
            ),
            False,
        ),
        (
            {
                'status': 'waiting',
                'latitude': '56.743410768',
                'longitude': '38.599179973',
                'fallback': True,
            },
            None,
            (200, {'phone_options': []}),
            False,
        ),
        (
            {
                'status': 'waiting',
                'fallback': True,
                'coord_providers': [
                    {
                        'type': 'gps',
                        'lat': 56.743410768,
                        'lon': 38.599179973,
                        'accuracy': 0.001,
                        'location_time': 1481790600000,
                        'server_time': 1481790599000,
                        'speed': 20,
                    },
                ],
            },
            None,
            (200, {'phone_options': []}),
            False,
        ),
        (
            {
                'status': 'waiting',
                'fallback': False,
                'coord_providers': [
                    {
                        'type': 'gps',
                        'lat': 0.0,
                        'lon': 0.0,
                        'accuracy': 1,
                        'location_time': 1481790600000,
                        'server_time': 1481790599000,
                        'speed': 20,
                    },
                    {
                        'type': 'lbs',
                        'lat': 56.74341076,
                        'lon': 38.59917997,
                        'accuracy': 0.01,
                        'location_time': 1481790600000,
                        'server_time': 1481790599000,
                        'speed': 20,
                    },
                ],
            },
            None,
            (200, {'phone_options': []}),
            False,
        ),
        (
            {
                'status': 'waiting',
                'fallback': False,
                'latitude': 56.743410768,
                'longitude': 38.599179973,
                'coord_providers': [
                    {
                        'type': 'gps',
                        'lat': 56.743410768,
                        'lon': 38.599179973,
                        'accuracy': 0.001,
                        'location_time': 1481790600000,
                        'server_time': 1481790599000,
                        'speed': 20,
                    },
                    {
                        'type': 'lbs',
                        'lat': 56.743410768,
                        'lon': 38.599179974,
                        'accuracy': 0.01,
                        'location_time': 1481790600000,
                        'server_time': 1481790599000,
                        'speed': 20,
                    },
                ],
            },
            False,
            (
                406,
                {
                    'error': {
                        'error_action': 'show_error',
                        'error_message': (
                            'You need to be at least 500 meters '
                            'closer to the pickup point before you can '
                            'change your status.'
                        ),
                        'meters': 500,
                    },
                },
            ),
            False,
        ),
        (
            {
                'status': 'waiting',
                'fallback': False,
                'latitude': 56.743410768,
                'longitude': 38.599179973,
                'coord_providers': [
                    {
                        'type': 'gps',
                        'lat': 56.743410768,
                        'lon': 38.599179973,
                        'accuracy': 0.001,
                        'location_time': 1481790600000,
                        'server_time': 1481790599000,
                        'speed': 20,
                    },
                    {
                        'type': 'lbs',
                        'lat': 56.743410768,
                        'lon': 38.599179974,
                        'accuracy': 0.01,
                        'location_time': 1481790600000,
                        'server_time': 1481790599000,
                        'speed': 20,
                    },
                ],
            },
            None,
            (200, {'phone_options': []}),
            True,
        ),
        (
            {
                'status': 'waiting',
                'fallback': False,
                'latitude': 57.743410768,
                'longitude': 38.599179973,
                'coord_providers': [
                    {
                        'type': 'gps',
                        'lat': 55.73367,
                        'lon': 37.587874,
                        'accuracy': 0.001,
                        'location_time': 1481790600000,
                        'server_time': 1481790599000,
                        'speed': 20,
                    },
                    {
                        'type': 'lbs',
                        'lat': 55.73367,
                        'lon': 37.587875,
                        'accuracy': 0.01,
                        'location_time': 1481790600000,
                        'server_time': 1481790599000,
                        'speed': 20,
                    },
                ],
            },
            None,
            (200, {'phone_options': []}),
            False,
        ),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.driver_experiments('dont_trust_position')
@pytest.mark.driver_experiments('waiting_coord_providers_check')
@pytest.mark.fixture_now(datetime.timedelta(minutes=5))
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_waiting(
        taxi_protocol,
        db,
        params,
        within_pickup_zone,
        expected_response,
        tracker_valid,
        mockserver,
        order_core_switch_on,
        mock_order_core,
):
    @mockserver.handler('/maps-router/route_jams/')
    def _(request):
        return mockserver.make_response()

    @mockserver.handler('/router-yamaps-masstransit/pedestrian/route')
    def _(request):
        return mockserver.make_response()

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _(request):
        return {}

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        if tracker_valid:
            return {
                'lat': 55.733410768,
                'lon': 37.589179973,
                'timestamp': 1539704268,
                'speed': 123,
                'direction': 328,
            }
        else:
            return {}

    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'order.taxi_status': 'driving'}},
    )
    if within_pickup_zone is not None:
        db.order_proc.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {'$set': {'order.source_within_pp_zone': within_pickup_zone}},
        )
    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'

    request_params.update(params)
    response = taxi_protocol.post(
        '1.x/requestconfirm?clid=999012&apikey=' + apikey, request_params,
    )

    assert expected_response[0] == response.status_code
    assert expected_response[1] == response.json()

    assert mock_order_core.get_fields_times_called == order_core_switch_on

    proc = db.order_proc.find_one('8c83b49edb274ce0992f337061047375')
    assert 'fixed_price_discard_reason' not in proc['order']


@pytest.mark.parametrize(
    'params, within_pickup_zone, expected_response, tracker_valid',
    [
        (
            {
                'status': 'waiting',
                'fallback': False,
                'latitude': 57.743410768,
                'longitude': 38.599179973,
                'coord_providers': [
                    {
                        'type': 'gps',
                        'lat': 55.73367,
                        'lon': 37.587874,
                        'accuracy': 0.001,
                        'location_time': 1481790600000,
                        'server_time': 1481790599000,
                        'speed': 20,
                    },
                    {
                        'type': 'lbs',
                        'lat': 55.73367,
                        'lon': 37.587875,
                        'accuracy': 0.01,
                        'location_time': 1481790600000,
                        'server_time': 1481790599000,
                        'speed': 20,
                    },
                ],
            },
            False,
            (
                406,
                {
                    'error': {
                        'error_action': 'show_error',
                        'error_message': (
                            'You need to be at least 500 meters '
                            'closer to the pickup point before you'
                            ' can '
                            'change your status.'
                        ),
                        'meters': 500,
                    },
                },
            ),
            False,
        ),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.driver_experiments('dont_trust_position')
@pytest.mark.fixture_now(datetime.timedelta(minutes=5))
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_waiting_without_coord_providers_check(
        taxi_protocol,
        db,
        params,
        within_pickup_zone,
        expected_response,
        tracker_valid,
        mockserver,
        order_core_switch_on,
        mock_order_core,
):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        if tracker_valid:
            return {
                'lat': 55.733410768,
                'lon': 37.589179973,
                'timestamp': 1539704268,
                'speed': 123,
                'direction': 328,
            }
        else:
            return {}

    @mockserver.handler('/maps-router/route_jams/')
    def _(request):
        return mockserver.make_response()

    @mockserver.handler('/router-yamaps-masstransit/pedestrian/route')
    def _(request):
        return mockserver.make_response()

    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'order.taxi_status': 'driving'}},
    )
    if within_pickup_zone is not None:
        db.order_proc.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {'$set': {'order.source_within_pp_zone': within_pickup_zone}},
        )
    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'

    request_params.update(params)
    response = taxi_protocol.post(
        '1.x/requestconfirm?clid=999012&apikey=' + apikey, request_params,
    )

    assert expected_response[0] == response.status_code
    assert expected_response[1] == response.json()

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.config(LIVE_LOCATION_IN_WAITING_STATUS_ENABLED=True)
@pytest.mark.parametrize(
    'params,user_tracker_timestamp,expected_response',
    [
        (
            {
                'status': 'waiting',
                'fallback': False,
                'latitude': 57.743410768,
                'longitude': 38.599179973,
                'coord_providers': [],
            },
            1546336800,
            (200, {'phone_options': []}),
        ),
        (
            {
                'status': 'waiting',
                'fallback': False,
                'latitude': 57.743410768,
                'longitude': 38.589179973,
                'coord_providers': [],
            },
            1546336800,
            (
                406,
                {
                    'error': {
                        'error_action': 'show_error',
                        'error_message': (
                            'You need to be at least 500 meters '
                            'closer to the pickup point before you '
                            'can change your status.'
                        ),
                        'meters': 500,
                    },
                },
            ),
        ),
        (
            {
                'status': 'waiting',
                'fallback': False,
                'latitude': 57.743410768,
                'longitude': 38.599179973,
                'coord_providers': [],
            },
            1546250400,
            (
                406,
                {
                    'error': {
                        'error_action': 'show_error',
                        'error_message': (
                            'You need to be at least 500 meters '
                            'closer to the pickup point before '
                            'you can change your status.'
                        ),
                        'meters': 500,
                    },
                },
            ),
        ),
    ],
)
@pytest.mark.driver_experiments('dont_trust_position')
@pytest.mark.now('2019-01-01T10:00:00+0300')
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_waiting_check_live_location(
        taxi_protocol,
        db,
        params,
        user_tracker_timestamp,
        expected_response,
        mockserver,
        order_core_switch_on,
        mock_order_core,
):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {}

    @mockserver.handler('/maps-router/route_jams/')
    def _(request):
        return mockserver.make_response()

    @mockserver.handler('/router-yamaps-masstransit/pedestrian/route')
    def _(request):
        return mockserver.make_response()

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _(request):
        return {}

    @mockserver.handler('/user-tracking/user/position')
    def mock_user_tracker(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'user_id': 'b300bda7d41b4bae8d58dfa93221ef16',
                    'lat': 57.743410768,
                    'lon': 38.599179973,
                    'accuracy': 2,
                    'timestamp': user_tracker_timestamp,
                },
            ),
            200,
        )

    @mockserver.handler('/go-users-trackstory/positions')
    def mock_go_users_tracksotry(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'results': [
                        {
                            'driver_id': (
                                'users_b300bda7d41b4bae8d58dfa93221ef16'
                            ),
                            'position': {
                                'lat': 57.743410768,
                                'lon': 38.599179973,
                                'accuracy': 2,
                                'timestamp': user_tracker_timestamp,
                            },
                        },
                    ],
                },
            ),
            200,
        )

    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'order.taxi_status': 'driving'}},
    )
    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'

    request_params.update(params)
    response = taxi_protocol.post(
        '1.x/requestconfirm?clid=999012&apikey=' + apikey, request_params,
    )

    assert expected_response[0] == response.status_code
    assert expected_response[1] == response.json()

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.config(LIVE_LOCATION_IN_WAITING_STATUS_ENABLED=True)
@pytest.mark.parametrize(
    'params,user_tracker_timestamp,expected_response',
    [
        (
            {
                'status': 'waiting',
                'fallback': False,
                'latitude': 57.743410768,
                'longitude': 38.599179973,
                'coord_providers': [],
            },
            1546336800,
            (200, {'phone_options': []}),
        ),
        (
            {
                'status': 'waiting',
                'fallback': False,
                'latitude': 57.743410768,
                'longitude': 38.589179973,
                'coord_providers': [],
            },
            1546336800,
            (
                406,
                {
                    'error': {
                        'error_action': 'show_error',
                        'error_message': (
                            'You need to be at least 500 meters '
                            'closer to the pickup point before you '
                            'can change your status.'
                        ),
                        'meters': 500,
                    },
                },
            ),
        ),
        (
            {
                'status': 'waiting',
                'fallback': False,
                'latitude': 57.743410768,
                'longitude': 38.599179973,
                'coord_providers': [],
            },
            1546250400,
            (
                406,
                {
                    'error': {
                        'error_action': 'show_error',
                        'error_message': (
                            'You need to be at least 500 meters '
                            'closer to the pickup point before '
                            'you can change your status.'
                        ),
                        'meters': 500,
                    },
                },
            ),
        ),
    ],
)
@pytest.mark.config(USER_TRACKER_READ_FROM_TRACKSTORY_PERCENT=100)
@pytest.mark.driver_experiments('dont_trust_position')
@pytest.mark.now('2019-01-01T10:00:00+0300')
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_waiting_check_live_location_trackstory(
        taxi_protocol,
        db,
        params,
        user_tracker_timestamp,
        expected_response,
        mockserver,
        order_core_switch_on,
        mock_order_core,
):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {}

    @mockserver.handler('/maps-router/route_jams/')
    def _(request):
        return mockserver.make_response()

    @mockserver.handler('/router-yamaps-masstransit/pedestrian/route')
    def _(request):
        return mockserver.make_response()

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _(request):
        return {}

    @mockserver.handler('/user-tracking/user/position')
    def mock_user_tracker(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'user_id': 'b300bda7d41b4bae8d58dfa93221ef16',
                    'lat': 57.743410768,
                    'lon': 38.599179973,
                    'accuracy': 2,
                    'timestamp': user_tracker_timestamp,
                },
            ),
            200,
        )

    @mockserver.handler('/go-users-trackstory/positions')
    def mock_go_users_tracksotry(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'results': [
                        {
                            'driver_id': (
                                'users_b300bda7d41b4bae8d58dfa93221ef16'
                            ),
                            'position': {
                                'lat': 57.743410768,
                                'lon': 38.599179973,
                                'accuracy': 2,
                                'timestamp': user_tracker_timestamp,
                            },
                        },
                    ],
                },
            ),
            200,
        )

    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'order.taxi_status': 'driving'}},
    )
    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'

    request_params.update(params)
    response = taxi_protocol.post(
        '1.x/requestconfirm?clid=999012&apikey=' + apikey, request_params,
    )

    print(response, response.json())

    assert expected_response[0] == response.status_code
    assert expected_response[1] == response.json()

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.now('2016-12-15T11:30:00+0300')
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_reject_with_comment(
        taxi_protocol, db, order_core_switch_on, mock_order_core,
):
    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'status': 'reject',
        'status_change_time': '20170925T134836',
        'latitude': 55.73879972,
        'longitude': 37.58014365,
        'avg_speed': 37,
        'direction': 295.03,
        'time': '20170925T134836',
        'total_distance': 0.0,
        'extra': 'manual',
        'comment_id': 'PHONE_UNAVAILABLE',
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one('8c83b49edb274ce0992f337061047375')
    assert proc['order']['status'] == 'pending'
    assert proc['order']['taxi_status'] is None
    su_rejected = filter(
        lambda x: (
            x.get('a', {}) == {'comment_id': 'PHONE_UNAVAILABLE'}
            and x.get('q', '') == 'autoreorder'
        ),
        proc['order_info']['statistics']['status_updates'],
    )
    assert len(list(su_rejected)) == 1

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.config(
    MIN_PAID_WAITING_TIME_LIMIT={'__default__': 600.0},
    MAX_PAID_WAITING_TIME=600,
)
@pytest.mark.experiments3(filename='exp3_paid_supply_paid_cancel.json')
@pytest.mark.parametrize(
    'add_minimal, paid_cancel_fix, wait_minutes, paid_supply_price, '
    'paid_supply, expected_paid_cancel, expected_cost',
    [
        # 13 minutes not enough, 14 enough, cause due is set to $dateDiff: 209
        # waiting_time = min(wait_time_sec, MAX_PAID_WAITING_TIME) -
        # tariff.categories.st.p.tpi.b * 60 - tariff.categories.waiting * 60
        # waiting_cost = waiting_time * tariff.categories.st.p.tpi.p / 60
        # example:
        # waiting_time = 600 - 5 * 60 - 2 * 60 = 180
        # waiting_cost = 180 * 9 / 60 = 27
        (True, 0, 13, None, False, False, None),  # cancelled too early
        (True, 0, 14, None, False, True, 126),  # cancel is paid
        (True, 0, 50, None, False, True, 126),  # cancel is paid
        # paid supply did not happen
        (True, 0, 14, 43, False, True, 126),
        (True, 0, 13, 43, True, False, None),  # cancelled too early
        # cancel + paid supply price
        (True, 0, 14, 43, True, True, 126 + 43),
        (True, 0, 50, 43, True, True, 126 + 43),
        # paid cancel fix + paid supply price + minimal
        (True, 200, 14, 43, True, True, 369),
        # paid cancel fix + paid supply price
        (False, 200, 14, 43, True, True, 270),
        # paid cancel fix + paid supply price
        (False, 200, 14, 43, True, True, 270),
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_reject_paid_after_long_waiting(
        taxi_protocol,
        recalc_order,
        db,
        now,
        add_minimal,
        paid_cancel_fix,
        wait_minutes,
        paid_supply_price,
        paid_supply,
        expected_paid_cancel,
        expected_cost,
        order_core_switch_on,
        mock_order_core,
):
    recalc_order.set_driver_recalc_result(expected_cost, expected_cost)
    recalc_order.set_user_recalc_result(expected_cost, expected_cost)

    if paid_supply_price is not None:
        db.order_proc.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {
                '$set': {
                    'order.fixed_price.paid_supply_price': paid_supply_price,
                },
            },
        )
    db.tariffs.update(
        {
            'categories': {
                '$elemMatch': {
                    'category_type': 'application',
                    'id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
                },
            },
        },
        {
            '$set': {
                'categories.$.add_minimal_to_paid_cancel': add_minimal,
                'categories.$.paid_cancel_fix': paid_cancel_fix,
            },
        },
    )

    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'order.performer.paid_supply': paid_supply}},
    )
    # Database uses $dateDiff, so changing current time after it is loaded
    later = now + datetime.timedelta(minutes=wait_minutes)
    taxi_protocol.tests_control(now=later)

    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'status': 'reject',
        'status_change_time': '20170925T134836',
        'latitude': 55.7334,
        'longitude': 37.5892,
        'avg_speed': 37,
        'direction': 295.03,
        'time': '20170925T134836',
        'total_distance': 0.0,
        'extra': 'manual',
        'comment_id': 'CLIENT_DID_NOT_COME',
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'

    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one('8c83b49edb274ce0992f337061047375')
    assert proc['order']['cost'] == expected_cost
    if expected_cost:
        order_commit_common.check_current_prices(
            proc, 'final_cost', expected_cost,
        )
    if expected_paid_cancel:
        assert proc['order']['status'] == 'finished'
        assert proc['order']['taxi_status'] == 'cancelled'
        su_rejected = filter(
            lambda x: (
                x.get('a', {}) == {'comment_id': 'CLIENT_DID_NOT_COME'}
                and x.get('r', '') == 'manual'
                and x.get('s', '') == 'finished'
                and x.get('t', '') == 'cancelled'
                and x.get('q', '') != 'autoreorder'
            ),
            proc['order_info']['statistics']['status_updates'],
        )
        assert len(list(su_rejected)) == 1
    else:
        expect_autoreorder = paid_supply_price is None
        assert proc['order']['status'] == (
            'pending' if expect_autoreorder else 'finished'
        )
        assert proc['order']['taxi_status'] == (
            None if expect_autoreorder else 'failed'
        )
        su_rejected = list(
            filter(
                lambda x: (
                    x.get('a', {}) == {'comment_id': 'CLIENT_DID_NOT_COME'}
                    and x.get('r', '') == 'manual'
                ),
                proc['order_info']['statistics']['status_updates'],
            ),
        )
        assert len(su_rejected) == 1
        autoreorder = su_rejected[0].get('q', '') == 'autoreorder'
        assert autoreorder == expect_autoreorder

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.experiments3(filename='exp3_paid_supply_paid_cancel.json')
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_paid_cancel_with_cash(
        taxi_protocol, recalc_order, db, order_core_switch_on, mock_order_core,
):
    _expected_cost = 100
    recalc_order.set_driver_recalc_result(_expected_cost, _expected_cost)
    recalc_order.set_user_recalc_result(_expected_cost, _expected_cost)

    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            '$set': {
                'payment_tech.type': 'cash',
                'order.fixed_price.paid_supply_price': 10,
            },
        },
    )
    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'status': 'reject',
        'status_change_time': '20170925T134836',
        'latitude': 55.7334,
        'longitude': 37.5892,
        'avg_speed': 37,
        'direction': 295.03,
        'time': '20170925T134836',
        'total_distance': 0.0,
        'extra': 'manual',
        'comment_id': 'CLIENT_DID_NOT_COME',
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'

    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200
    proc = db.order_proc.find_one('8c83b49edb274ce0992f337061047375')
    assert proc['order']['cost'] is None


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.config(
    MAX_AUTOREORDER_TIME_LOGIC_ENABLED=True,
    MAX_AUTOREORDER_TIME_FROM_ORDER_BEGIN={'moscow': 600},
)
@pytest.mark.parametrize(
    'order_type, order_minutes',
    [
        ('soon', 4),  # soon / before max wait time
        ('soon', 14),  # soon / after max order time
        ('urgent', 4),  # urgent / before max wait time
        ('urgent', 14),  # urgent / after max order time
        ('exacturgent', 4),  # exacturgent / before max wait time
        ('exacturgent', 14),  # exacturgent / after max order time
        ('exact', 4),  # exact / before max wait time
        ('exact', 14),  # exact / after max order time
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_reject_autoreorder(
        taxi_protocol,
        db,
        now,
        order_type,
        order_minutes,
        order_core_switch_on,
        mock_order_core,
):
    assert order_type is not None

    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'order._type': order_type}},
    )
    urgent_order = order_type == 'soon' or order_type == 'urgent'
    if not urgent_order:
        db.order_proc.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {
                '$set': {
                    'order.request.payment.type': 'corp',
                    'payment_tech.type': 'corp',
                },
            },
        )

    # Database uses $dateDiff, so changing current time after it is loaded
    later = now + datetime.timedelta(minutes=order_minutes)
    taxi_protocol.tests_control(now=later)

    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'status': 'reject',
        'status_change_time': '20170925T134836',
        'latitude': 56.7334,
        'longitude': 37.6892,
        'avg_speed': 37,
        'direction': 295.03,
        'time': '20170925T134836',
        'total_distance': 0.0,
        'extra': 'manual',
        'comment_id': 'CLIENT_DID_NOT_COME',
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'

    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one('8c83b49edb274ce0992f337061047375')
    if urgent_order and order_minutes >= 10:
        assert proc['order']['status'] == 'finished'
        su_rejected = filter(
            lambda x: (
                x.get('a', {}) == {'comment_id': 'CLIENT_DID_NOT_COME'}
                and x.get('r', '') == 'manual'
                and x.get('s', '') == 'finished'
                and x.get('q', '') != 'autoreorder'
            ),
            proc['order_info']['statistics']['status_updates'],
        )
        assert len(list(su_rejected)) == 1
    else:
        assert proc['order']['status'] == 'pending'
        assert proc['order']['taxi_status'] is None
        su_rejected = filter(
            lambda x: (
                x.get('a', {}) == {'comment_id': 'CLIENT_DID_NOT_COME'}
                and x.get('r', '') == 'manual'
                and x.get('q', '') == 'autoreorder'
            ),
            proc['order_info']['statistics']['status_updates'],
        )
        assert len(list(su_rejected)) == 1

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.parametrize(
    'params,expected_state,cost',
    [
        (
            {
                'status': 'failed',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
            },
            (200, 'finished', 'cancelled'),
            126.0,
        ),
        (
            {
                'status': 'failed',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
                'cancel': 'paid',
            },
            (200, 'finished', 'cancelled'),
            126.0,
        ),
        (  # No position autoreorder
            {'status': 'failed'},
            (200, 'pending', None),
            None,
        ),
        (  # No position so it's free
            {'status': 'failed', 'cancel': 'paid'},
            (406, 'assigned', 'waiting'),
            None,
        ),
        (  # No position but dispatch
            {'status': 'failed', 'cancel': 'paid', 'origin': 'dispatch'},
            (200, 'finished', 'cancelled'),
            126.0,
        ),
        (
            {
                'status': 'cancelled',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
            },
            (200, 'finished', 'cancelled'),
            126.0,
        ),
        (
            {
                'status': 'cancelled',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
                'cancel': 'paid',
            },
            (200, 'finished', 'cancelled'),
            126.0,
        ),
        (  # No position autoreorder
            {'status': 'cancelled'},
            (200, 'finished', 'cancelled'),
            None,
        ),
        (  # No position so it's free
            {'status': 'cancelled', 'cancel': 'paid'},
            (406, 'assigned', 'waiting'),
            None,
        ),
        (  # No position but dispatch
            {'status': 'cancelled', 'cancel': 'paid', 'origin': 'dispatch'},
            (200, 'finished', 'cancelled'),
            126.0,
        ),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=15))
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_failed_paid(
        taxi_protocol,
        recalc_order,
        db,
        params,
        expected_state,
        cost,
        order_core_switch_on,
        mock_order_core,
):
    recalc_order.set_driver_recalc_result(cost, cost)
    recalc_order.set_user_recalc_result(cost, cost)

    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
    }
    request_params.update(params)
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)

    proc = db.order_proc.find_one('8c83b49edb274ce0992f337061047375')
    assert expected_state == (
        response.status_code,
        proc['status'],
        proc['order']['taxi_status'],
    )

    if expected_state == (200, 'finished', 'cancelled'):
        assert proc['status'] == 'finished'
        assert proc['order']['status'] == 'finished'
        assert proc['order']['taxi_status'] == 'cancelled'
        assert proc['order']['cost'] == cost
        order_commit_common.check_current_prices(proc, 'final_cost', cost)

        status_update = proc['order_info']['statistics']['status_updates'][-1]
        assert status_update['s'] == 'finished'
        assert status_update['t'] == 'cancelled'
    elif expected_state == (200, 'pending', None):
        assert proc['status'] == 'pending'
        status_update = proc['order_info']['statistics']['status_updates'][-1]
        assert status_update['q'] == 'autoreorder'
        assert status_update['s'] == 'pending'
    elif expected_state == (406, 'assigned', 'waiting'):
        pass
    else:
        pytest.fail('unhandled state %r' % expected_state)

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.parametrize(
    'params',
    [
        (
            {
                'status': 'failed',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
            }
        ),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=5))
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_failed_driver(
        taxi_protocol, db, params, order_core_switch_on, mock_order_core,
):
    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a111111111111111',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
    }
    request_params.update(params)
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 400

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.parametrize(
    'params,expected_cost,expected_calc_method,expected_calc_total',
    [
        (
            {
                'status': 'complete',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
                'extra': '210',
            },
            210.0,
            None,
            None,
        ),
        (
            {
                'status': 'complete',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
                'extra': '210',
                'calc_method': 1,
            },
            210.0,
            'taximeter',
            None,
        ),
        (
            {
                'status': 'complete',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
                'extra': '210',
                'calc_method': 2,
            },
            210.0,
            'fixed',
            None,
        ),
        (
            {
                'status': 'complete',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
                'extra': '210',
                'calc_method': 3,
            },
            210.0,
            'other',
            None,
        ),
        (
            {
                'status': 'complete',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
                'extra': '210',
                'calc_method': 4,
            },
            210.0,
            'order-cost',
            None,
        ),
        (
            {
                'status': 'complete',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
                'extra': '210',
                'calc_method': 5,
            },
            210.0,
            'pool',
            None,
        ),
        (
            {
                'status': 'complete',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
                'extra': '210',
                'calc_method': 6,
            },
            210.0,
            None,
            None,
        ),
        (
            {
                'status': 'complete',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
                'extra': '210',
                'calc_method': 1,
                'calc_total': 543.21,
            },
            210.0,
            'taximeter',
            543.21,
        ),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=5))
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_calc_params(
        taxi_protocol,
        db,
        params,
        expected_cost,
        expected_calc_method,
        expected_calc_total,
        mockserver,
        order_core_switch_on,
        mock_order_core,
):
    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
    }
    request_params.update(params)
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one('8c83b49edb274ce0992f337061047375')
    assert proc['status'] == 'finished'
    assert proc['order']['taxi_status'] == 'complete'
    assert proc['order']['cost'] == expected_cost
    order_commit_common.check_current_prices(proc, 'final_cost', expected_cost)
    assert proc['order'].get('calc_method') == expected_calc_method
    assert proc['order'].get('calc_total') == expected_calc_total

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.parametrize(
    'orderid,params,expected_cost,pcv',
    [
        (
            '8c83b49edb274ce0992f337061047375',
            {
                'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
                'uuid': 'a5709ce56c2740d9a536650f5390de0b',
                'clid': '999012',
                'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
            },
            210.0,
            10000,
        ),
        (
            '8c83b49edb274ce0992f337061047376',
            {
                'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04e',
                'uuid': 'a5709ce56c2740d9a536650f5390de0c',
                'clid': '999013',
                'apikey': 'd19a9b3b59424881b57adf5b0f367a2d',
            },
            247.8,
            11800,
        ),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=5))
@pytest.mark.filldb(order_proc='corp')
@pytest.mark.filldb(parks='corp')
@pytest.mark.config(CALCULATE_VAT_ON_REQUESTCONFIRM=True)
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_calc_vat(
        taxi_protocol,
        db,
        orderid,
        params,
        expected_cost,
        pcv,
        order_core_switch_on,
        mock_order_core,
):
    request_params = {
        'status': 'complete',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
        'extra': '210',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
    }
    request_params.update(params)
    uri = (
        '1.x/requestconfirm?clid='
        + params['clid']
        + '&apikey='
        + params['apikey']
    )
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    data = response.json()
    assert data == {
        'taximeter_cost': expected_cost,
        'enable_no_change_flow': False,
        'phone_options': [],
        'final_cost': {
            # from `extra`
            'driver': 210.0,
            # from `extra`
            'user': 210.0,
        },
    }

    proc = db.order_proc.find_one(orderid)
    assert proc['performer']['park_corp_vat'] == pcv

    assert mock_order_core.get_fields_times_called == order_core_switch_on


CURRENT_PRICES = {
    'order.pricing_data.published.fixed.cost.driver.total': 152.0,
    'order.pricing_data.published.fixed.cost.user.total': 302.0,
    'order.pricing_data.published.taximeter.cost.driver.total': 153.0,
    'order.pricing_data.published.taximeter.cost.user.total': 303.0,
    'order.pricing_data.published.current_method': 'taximeter',
}

CURRENT_META = {
    'driver': {'foo': 42.0},
    'user': {'bar': 42.42, 'baz': 42.4242},
}


def _update_with_meta(src, extra, key):
    result = copy.deepcopy(src)
    result.update({key: extra})
    return result


@pytest.mark.parametrize(
    'order_fix, additional_params, exp_cost, final_cost, final_meta',
    [
        # fallback to minimal
        ({}, {}, 199, None, None),
        # fallback to cc
        ({'order_info.cc': 3500}, {}, 3500, None, None),
        # fallback to fixed
        ({'order.fixed_price.price': 2750}, {}, 2750, None, None),
        # use current_prices.current_cost
        (
            {
                'order.current_prices.current_cost.driver.total': 151.0,
                'order.current_prices.current_cost.user.total': 301.0,
            },
            {},
            301,
            None,
            None,
        ),
        # fallback to current_prices.current_cost
        (
            {
                'order.current_prices.current_cost.driver.total': 151.0,
                'order.current_prices.current_cost.user.total': 301.0,
            },
            {'dispatch_selected_price': 'fixed'},
            301,
            None,
            None,
        ),
        # use pricing_data.published.taximeter
        (
            CURRENT_PRICES,
            {},
            303,
            {'driver': {'total': 153}, 'user': {'total': 303}},
            {'driver': {}, 'user': {}},
        ),
        # use dispatch_selected_price.fixed
        (
            CURRENT_PRICES,
            {'dispatch_selected_price': 'fixed'},
            302,
            {'driver': {'total': 152}, 'user': {'total': 302}},
            {'driver': {}, 'user': {}},
        ),
        # use dispatch_selected_price.taximeter
        (
            CURRENT_PRICES,
            {'dispatch_selected_price': 'taximeter'},
            303,
            {'driver': {'total': 153}, 'user': {'total': 303}},
            {'driver': {}, 'user': {}},
        ),
        # fallback to dispatch_selected_price.taximeter
        (
            CURRENT_PRICES,
            {'dispatch_selected_price': 'unsupported'},
            303,
            {'driver': {'total': 153}, 'user': {'total': 303}},
            {'driver': {}, 'user': {}},
        ),
        # use dispatch_selected_price.fixed cost & meta
        (
            _update_with_meta(
                CURRENT_PRICES,
                CURRENT_META,
                key='order.pricing_data.published.fixed.meta',
            ),
            {'dispatch_selected_price': 'fixed'},
            302,
            {'driver': {'total': 152}, 'user': {'total': 302}},
            CURRENT_META,
        ),
        # use dispatch_selected_price fixed with manual_accept
        (
            CURRENT_PRICES,
            {'dispatch_selected_price': 'fixed', 'need_manual_accept': True},
            302,
            {'driver': {'total': 152}, 'user': {'total': 302}},
            {'driver': {}, 'user': {}},
        ),
    ],
    ids=[
        'minimal',
        'cc',
        'fixed_price',
        'current_prices',
        'fallback_to_current_prices',
        'fallback_to_published_taximeter',
        'published_fixed',
        'published_taximeter',
        'fallback_to_published_taximeter',
        'published_with_meta',
        'published_with_manual_accept',
    ],
)
@pytest.mark.parametrize('payment_type_is_cash', [False, True])
@pytest.mark.parametrize('use_recommended_cost', [False, True])
@pytest.mark.now('2016-12-15T11:30:00+0300')
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_disp_complete(
        taxi_protocol,
        db,
        order_fix,
        exp_cost,
        final_cost,
        final_meta,
        additional_params,
        payment_type_is_cash,
        use_recommended_cost,
        order_core_switch_on,
        mock_order_core,
):
    if order_fix:
        db.order_proc.update(
            {'_id': '8c83b49edb274ce0992f337061047375'}, {'$set': order_fix},
        )
    if payment_type_is_cash:
        db.order_proc.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {'$set': {'payment_tech.type': 'cash'}},
        )

    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'origin': 'dispatch',
        'use_recommended_cost': use_recommended_cost,
        'user_login': 'disp_login',
        'dispatch_api_version': '1.0',
        'status': 'complete',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
        'extra': '5000',
        'calc_method': 6,
    }
    request_params.update(additional_params)
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    data = response.json()

    complete_with_pricing_data = (final_cost is not None) and (
        ('dispatch_selected_price' in additional_params)
        or (use_recommended_cost is True)
    )
    user_cost = (
        final_cost['user']['total'] if complete_with_pricing_data else exp_cost
    )
    driver_cost = (
        final_cost['driver']['total']
        if complete_with_pricing_data
        else exp_cost
    )
    assert data == {
        'taximeter_cost': driver_cost,
        'phone_options': [],
        'enable_no_change_flow': False,
        'final_cost': {'driver': driver_cost, 'user': user_cost},
    }

    content_type = response.headers['Content-Type']
    assert content_type == 'application/json; charset=utf-8'

    proc = db.order_proc.find_one('8c83b49edb274ce0992f337061047375')
    assert proc['order']['cost'] == user_cost
    current_prices = proc['order'].get('current_prices', {})
    if complete_with_pricing_data:
        assert current_prices['final_cost']['driver'] == final_cost['driver']
        assert current_prices['final_cost']['user'] == final_cost['user']
        assert current_prices.get('final_cost_meta') == final_meta
    else:
        assert 'final_cost' not in current_prices
        assert 'final_cost_meta' not in current_prices

    disp_cost = proc['order']['disp_cost']
    if 'dispatch_selected_price' in additional_params:
        need_manual_accept = additional_params.get('need_manual_accept', False)
    else:
        need_manual_accept = (not payment_type_is_cash) and (
            not use_recommended_cost
        )
    assert disp_cost is not None
    assert disp_cost['disp_cost'] == (
        user_cost if complete_with_pricing_data else 5000
    )
    assert disp_cost['taximeter_cost'] == driver_cost
    assert disp_cost['operator_login'] == 'disp_login'
    assert disp_cost['use_recommended_cost'] != need_manual_accept
    assert disp_cost['dispatch_api_version'] == '1.0'

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.now('2016-12-15T11:30:00+0300')
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_complete_stat(
        taxi_protocol, db, order_core_switch_on, mock_order_core,
):
    receipt = _get_receipt()
    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'db_id': '12345',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'origin': 'dispatch',
        'use_recommended_cost': False,
        'user_login': 'disp_login',
        'status': 'complete',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
        'extra': '5000',
        'calc_method': 4,
        'is_captcha': True,
        'is_airplanemode': False,
        'is_offline': True,
        'driver_status': 'free',
        'receipt': receipt,
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one('8c83b49edb274ce0992f337061047375')
    assert proc['order']['taximeter_receipt'] == receipt
    assert 'driver_cost' in proc['order']

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.now('2016-12-15T11:30:00+0300')
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_null_receipt(
        taxi_protocol, db, order_core_switch_on, mock_order_core,
):
    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'db_id': '12345',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'origin': 'dispatch',
        'use_recommended_cost': False,
        'user_login': 'disp_login',
        'status': 'complete',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
        'extra': '5000',
        'calc_method': 4,
        'is_captcha': True,
        'is_airplanemode': False,
        'is_offline': True,
        'driver_status': 'free',
        'receipt': None,
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.parametrize(
    'receipt, driver_receipt',
    [
        (
            {
                'area_ids': {'ufa': 'f2313a01f2b14ae883147cce1b34eb36'},
                'areas': ['ufa'],
                'calc_class': 'yandex',
                'calc_method': 2,
                'calc_total': 157.0,
                'details': [
                    {
                        'count': 1,
                        'name': 'child_chair.booster',
                        'meter_type': 'distance',
                        'meter_value': 10703.691472337661,
                        'per': 1000.0,
                        'price': 8.0,
                        'service_type': 'free_route',
                        'sum': 85.62953177870129,
                        'zone_names': ['ufa'],
                    },
                    {
                        'meter_type': 'time',
                        'meter_value': 1283.0,
                        'per': 60.0,
                        'price': 1.0,
                        'service_type': 'free_route',
                        'sum': 21.383333333333333,
                        'zone_names': ['ufa'],
                    },
                    {
                        'meter_type': 'time',
                        'meter_value': 2,
                        'per': 60,
                        'price': 9,
                        'service_type': 'waiting',
                        'sum': 20,
                        'zone_names': ['moscow'],
                    },
                    {
                        'meter_type': 'time',
                        'meter_value': 2,
                        'per': 60,
                        'price': 9,
                        'service_type': 'waiting',
                        'sum': 20,
                        'zone_names': ['moscow'],
                    },
                    {
                        'meter_type': 'time',
                        'meter_value': 120,
                        'per': 60,
                        'price': 9,
                        'service_type': 'unloading',
                        'sum': 18,
                        'zone_names': ['moscow'],
                    },
                ],
                'distances_by_areas': {'ufa': 10703.691472337661},
                'dst_actual_point': {
                    'lat': 54.70032,
                    'lon': 55.994981666666675,
                },
                'dst_address': 'addr1',
                'dst_order_point': {'lat': 54.701095, 'lon': 55.995109},
                'durations_by_areas': {'ufa': 1283.0},
                'min_price': 49.0,
                'src_address': 'addr2',
                'src_point': {'lat': 54.775290524, 'lon': 56.0231119848},
                'sum': 155.0,
                'tariff_id': 'cc9db53fbfcf4223a594cf291d4da436',
                'total': 155.0,
                'total_distance': 10703.691472337661,
                'total_duration': 1283.0,
                'transfer': False,
                'version': '8.35 (290)',
            },
            {
                'calc_class': 'yandex',
                'calc_method': 1,
                'details': [
                    {
                        'meter_type': 'distance',
                        'meter_value': 7291.123637088756,
                        'per': 1000,
                        'price': 9,
                        'service_type': 'free_route',
                        'skip_before': 2000,
                        'sum': 65.6201127337988,
                        'zone_names': ['moscow'],
                    },
                    {
                        'meter_type': 'time',
                        'meter_value': 225,
                        'per': 60,
                        'price': 9,
                        'service_type': 'free_route',
                        'sum': 33.75,
                        'zone_names': ['moscow'],
                    },
                    {
                        'meter_type': 'time',
                        'meter_value': 2,
                        'per': 60,
                        'price': 9,
                        'service_type': 'waiting',
                        'sum': 20,
                        'zone_names': ['moscow'],
                    },
                    {
                        'meter_type': 'time',
                        'meter_value': 120,
                        'per': 60,
                        'price': 9,
                        'service_type': 'unloading',
                        'sum': 18,
                        'zone_names': ['moscow'],
                    },
                    {
                        'meter_type': 'time',
                        'meter_value': 2,
                        'per': 60,
                        'price': 9,
                        'service_type': 'waiting_',
                        'sum': 20,
                        'zone_names': ['moscow'],
                    },
                ],
                'transfer': False,
                'min_price': 100,
                'tariff_id': 'bae9c9f06203403aa892122e0d255a36',
                'total': 195,
                'total_distance': 8709.048311380839,
                'total_duration': 225,
            },
        ),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_driver_receipt(
        taxi_protocol,
        db,
        receipt,
        driver_receipt,
        order_core_switch_on,
        mock_order_core,
):
    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'db_id': '12345',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'use_recommended_cost': False,
        'user_login': 'disp_login',
        'status': 'complete',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
        'extra': '5000',
        'calc_method': 4,
        'is_captcha': True,
        'is_airplanemode': False,
        'is_offline': True,
        'driver_status': 'free',
        'receipt': receipt,
        'driver_calc_receipt_overrides': driver_receipt,
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one('8c83b49edb274ce0992f337061047375')
    assert proc['order']['calc_total'] == 157
    assert proc['order']['taximeter_receipt'] == receipt
    assert proc['order']['driver_cost']['cost'] == driver_receipt['total']
    assert proc['order']['driver_cost']['calc_method'] == 'taximeter'
    assert proc['order']['driver_cost']['reason'] == 'taximeter'

    price, time = _extract_waiting_params(driver_receipt)

    assert proc['order']['driver_calc_info']['waiting_cost'] == price
    assert proc['order']['driver_calc_info']['waiting_time'] == time

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.parametrize(
    'receipt, driver_receipt', [(RECEIPT, DRIVER_RECEIPT)],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.parametrize('paid_supply', [False, True])
@pytest.mark.parametrize('coupon', [False, True])
@pytest.mark.parametrize(
    'final_cost_meta',
    [None, {'user': {'a': 1.2, 'b': 3.4}, 'driver': {'c': 5.6, 'd': 7.8}}],
    ids=['no_meta', 'with_meta'],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_fixed_price(
        taxi_protocol,
        db,
        receipt,
        driver_receipt,
        paid_supply,
        coupon,
        final_cost_meta,
        order_core_switch_on,
        mock_order_core,
):
    if paid_supply:
        db.order_proc.update(
            {'_id': '1c83b49edb274ce0992f337061047375'},
            {
                '$set': {
                    'order.fixed_price.paid_supply_price': 63,
                    'order.performer.paid_supply': True,
                },
            },
        )

    if coupon:
        _setup_coupon(db, '1c83b49edb274ce0992f337061047375', 200.0)

    request_params = {
        'orderid': 'db60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'db_id': '12345',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'use_recommended_cost': False,
        'user_login': 'disp_login',
        'status': 'complete',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
        'extra': '5000',
        'calc_method': 4,
        'is_captcha': True,
        'is_airplanemode': False,
        'is_offline': True,
        'driver_status': 'free',
        'receipt': receipt,
        'driver_calc_receipt_overrides': copy.deepcopy(driver_receipt),
    }
    request_params['driver_calc_receipt_overrides']['total'] = 241 + (
        63 if paid_supply else 0
    )
    pricing_complete_data = PricingCompleteData()
    if final_cost_meta:
        pricing_complete_data.set_final_cost(driver_cost=241, user_cost=157)
        pricing_complete_data.set_final_cost_meta(final_cost_meta)
    pricing_updates = pricing_complete_data.to_json()
    request_params.update(pricing_updates)
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one('1c83b49edb274ce0992f337061047375')
    assert proc['order']['calc_total'] == 157
    assert proc['order']['cost'] == 5000
    assert proc['order']['driver_cost']['cost'] == 241 + (
        63 if paid_supply else 0
    )
    assert proc['order']['driver_cost']['reason'] == 'fixed'
    if final_cost_meta:
        assert proc['order']['current_prices']['final_cost'] == {
            'driver': {'total': 241},
            'user': {'total': 157},
        }
        assert (
            proc['order']['current_prices']['final_cost_meta']
            == final_cost_meta
        )
        assert (
            proc['order']['pricing_data']['links']['yt']
            == pricing_updates['price_verifications']['uuids']
        )
    else:
        assert 'final_cost_meta' not in proc['order']['current_prices']

    exp_total_price = 4800 if coupon else 5000
    order_commit_common.check_current_prices(
        proc, 'final_cost', exp_total_price,
    )

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.parametrize(
    'receipt, driver_receipt', [(RECEIPT, DRIVER_RECEIPT)],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.parametrize('fixed_price_discard_reason', [None, 'far_from_b'])
def test_requestconfirm_fixed_price_discard_reason(
        taxi_protocol, db, receipt, driver_receipt, fixed_price_discard_reason,
):
    if fixed_price_discard_reason:
        patch = {
            'calc_method': 1,
            'fixed_price_discard_reason': fixed_price_discard_reason,
        }
        receipt.update(patch)
        driver_receipt.update(patch)

    request_params = {
        'orderid': 'db60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'db_id': '12345',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'use_recommended_cost': False,
        'user_login': 'disp_login',
        'status': 'complete',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
        'extra': '5000',
        'calc_method': 4,
        'is_captcha': True,
        'is_airplanemode': False,
        'is_offline': True,
        'driver_status': 'free',
        'receipt': receipt,
        'driver_calc_receipt_overrides': driver_receipt,
    }

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one('1c83b49edb274ce0992f337061047375')
    if fixed_price_discard_reason:
        assert (
            proc['order']['fixed_price_discard_reason']
            == fixed_price_discard_reason
        )
    else:
        assert 'fixed_price_discard_reason' not in proc['order']


@pytest.mark.parametrize(
    'params,expected_state',
    [
        (
            {
                'status': 'driving',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
            },
            (200, 'pending', None),
        ),
    ],
)
@pytest.mark.parametrize(
    'paid_supply', [False, True], ids=['no_paid_supply', 'paid_supply'],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=5))
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_assign_calc(
        taxi_protocol,
        mockserver,
        mocked_time,
        load_binary,
        db,
        params,
        expected_state,
        order_core_switch_on,
        mock_order_core,
        paid_supply,
):
    @mockserver.json_handler('/maps-router/route_jams/')
    def route_jams(request):
        return mockserver.make_response(
            load_binary('route_jams.protobuf'),
            content_type='application/x-protobuf',
        )

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 2.1,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _(request):
        return {}

    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'driverclientchat_enabled': True,
    }
    request_params.update(params)
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'status': 'pending'}},
    )
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'performer.presetcar': True}},
    )
    if paid_supply:
        db.order_proc.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {'$set': {'candidates.1.paid_supply': True}},
        )
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one('8c83b49edb274ce0992f337061047375')
    pricing_data = proc['order']['pricing_data']
    assert 'published' in pricing_data
    _check_published_prices_when_assign(
        pricing_data, mocked_time.now, paid_supply,
    )

    assert mock_order_core.get_fields_times_called == order_core_switch_on
    assert mock_order_core.set_fields_times_called == order_core_switch_on

    for n in range(1000):
        proc = db.order_proc.find_one('8c83b49edb274ce0992f337061047375')
        a_r_time = proc['order_info']['statistics'].get('assign_route_time', 0)
        if a_r_time > 0:
            assert proc['candidates'][1]['driverclientchat_enabled'] is True
            assert 'driverclientchat_enabled' not in proc['candidates'][0]
            break
        time.sleep(0.01)
    else:
        pytest.fail('order_info.statistics error')


@pytest.mark.config(
    TAXIMETER_WAITING_STATUS_PARAMS_BY_CITIES={
        '__default__': {
            'enable': True,
            'maxOrderDistance': 500,
            'maxOrderDistanceAirPort': 500,
            'maxOrderDistanceLinear': 40,
            'maxOrderPedestrianDistance': 250,
            'maxOrderPedestrianDistanceAirport': 500,
            'maxPhoneCallDistance': 2000,
            'maxPhoneCallDistanceAirport': 3000,
            'maxPhoneCallDistanceLinear': 100,
            'maxSpeed': 20,
            'responseTimeout': 5,
            'routeTimeoutMs': 30000,
        },
        'cities': {'Москва': {'maxOrderDistance': 100, 'responseTimeout': 10}},
    },
)
@pytest.mark.parametrize(
    'params,expected_response,',
    [
        (
            {
                'status': 'waiting',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
            },
            (200, {'phone_options': []}),
        ),
        (
            {'status': 'waiting', 'latitude': '55', 'longitude': '37'},
            (
                406,
                {
                    'error': {
                        'error_action': 'show_error',
                        'error_message': (
                            'You need to be at least 100 meters '
                            'closer to the pickup point before you can '
                            'change your status.'
                        ),
                        'meters': 100,
                    },
                },
            ),
        ),
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_driver_far_waiting_waiting_error_experiment(
        taxi_protocol,
        db,
        params,
        expected_response,
        mockserver,
        order_core_switch_on,
        mock_order_core,
):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {}

    @mockserver.handler('/maps-router/route_jams/')
    def _(request):
        return mockserver.make_response()

    @mockserver.handler('/router-yamaps-masstransit/pedestrian/route')
    def _(request):
        return mockserver.make_response()

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _(request):
        return {}

    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'order.taxi_status': 'driving'}},
    )

    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
    }
    request_params.update(params)

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)

    assert response.status_code == expected_response[0]
    assert response.json() == expected_response[1]

    if response.status_code == 200:
        # captcha and fallback are under experiment only
        order_proc = db.order_proc.find_one(
            {'_id': '8c83b49edb274ce0992f337061047375'},
        )
        assert order_proc['waiting_mode'] == 'regular'

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.config(
    TAXIMETER_WAITING_STATUS_PARAMS_BY_CITIES={
        '__default__': {
            'enable': False,
            'maxOrderDistance': 500,
            'maxOrderDistanceAirPort': 500,
            'maxOrderDistanceLinear': 40,
            'maxOrderPedestrianDistance': 250,
            'maxOrderPedestrianDistanceAirport': 500,
            'maxPhoneCallDistance': 2000,
            'maxPhoneCallDistanceAirport': 3000,
            'maxPhoneCallDistanceLinear': 100,
            'maxSpeed': 20,
            'responseTimeout': 5,
            'routeTimeoutMs': 30000,
        },
        'cities': {},
    },
)
@pytest.mark.parametrize(
    'params,expected_response_code,',
    [
        pytest.param(
            {'status': 'waiting', 'latitude': '55', 'longitude': '37'},
            200,
            id='no_experiment',
        ),
        pytest.param(
            {
                'status': 'waiting',
                'latitude': '55',
                'longitude': '37',
                'is_captcha': True,
            },
            406,
            id='experiment_without_captcha',
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='requestconfirm_waiting_status_checks',
                    consumers=['protocol/requestconfirm'],
                    clauses=[
                        {
                            'value': {
                                'max_distance_auto': 100,
                                'max_distance_pedestrian': 100,
                                'check_all_coord_providers': False,
                                'allow_no_position': True,
                                'use_captcha': False,
                            },
                            'predicate': {'type': 'true'},
                        },
                    ],
                ),
            ],
        ),
        pytest.param(
            {
                'status': 'waiting',
                'latitude': '55',
                'longitude': '37',
                'is_captcha': True,
            },
            406,
            id='experiment_by_taxi_class',
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='requestconfirm_waiting_status_checks',
                    consumers=['protocol/requestconfirm'],
                    clauses=[
                        {
                            'value': {
                                'max_distance_auto': 100,
                                'max_distance_pedestrian': 100,
                                'check_all_coord_providers': False,
                                'allow_no_position': True,
                                'use_captcha': False,
                            },
                            'predicate': {
                                'type': 'in_set',
                                'init': {
                                    'set': ['econom'],
                                    'arg_name': 'taxi_class',
                                    'set_elem_type': 'string',
                                },
                            },
                        },
                    ],
                ),
            ],
        ),
        pytest.param(
            {
                'status': 'waiting',
                'latitude': '55',
                'longitude': '37',
                'is_captcha': True,
            },
            200,
            id='experiment_by_other_taxi_class',
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='requestconfirm_waiting_status_checks',
                    consumers=['protocol/requestconfirm'],
                    clauses=[
                        {
                            'value': {
                                'max_distance_auto': 100,
                                'max_distance_pedestrian': 100,
                                'check_all_coord_providers': False,
                                'allow_no_position': True,
                                'use_captcha': False,
                            },
                            'predicate': {
                                'type': 'in_set',
                                'init': {
                                    'set': ['express', 'courier'],
                                    'arg_name': 'taxi_class',
                                    'set_elem_type': 'string',
                                },
                            },
                        },
                    ],
                ),
            ],
        ),
        pytest.param(
            {
                'status': 'waiting',
                'latitude': '55',
                'longitude': '37',
                'is_captcha': True,
            },
            200,
            id='experiment_with_captcha',
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='requestconfirm_waiting_status_checks',
                    consumers=['protocol/requestconfirm'],
                    clauses=[
                        {
                            'value': {
                                'max_distance_auto': 100,
                                'max_distance_pedestrian': 100,
                                'check_all_coord_providers': False,
                                'allow_no_position': True,
                                'use_captcha': True,
                            },
                            'predicate': {'type': 'true'},
                        },
                    ],
                ),
            ],
        ),
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_waiting_status_checks_experiment(
        taxi_protocol,
        db,
        params,
        expected_response_code,
        mockserver,
        order_core_switch_on,
        mock_order_core,
):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {}

    @mockserver.handler('/maps-router/route_jams/')
    def _(request):
        return mockserver.make_response()

    @mockserver.handler('/router-yamaps-masstransit/pedestrian/route')
    def _(request):
        return mockserver.make_response()

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _(request):
        return {}

    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'order.taxi_status': 'driving'}},
    )

    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
    }
    request_params.update(params)

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)

    assert response.status_code == expected_response_code

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.config(
    TAXIMETER_WAITING_STATUS_PARAMS_BY_CITIES={
        '__default__': {
            'enable': True,
            'maxOrderDistance': 500,
            'maxOrderDistanceAirPort': 500,
            'maxOrderPedestrianDistance': 250,
            'maxOrderPedestrianDistanceAirport': 500,
            'maxPhoneCallDistance': 2000,
            'maxPhoneCallDistanceAirport': 3000,
            'maxSpeed': 20,
            'responseTimeout': 5,
            'routeTimeoutMs': 30000,
        },
        'cities': {'Москва': {'maxOrderDistance': 100, 'responseTimeout': 10}},
    },
)
@pytest.mark.parametrize(
    'params,expected_response,',
    [
        (
            {
                'status': 'waiting',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
            },
            (200, {'phone_options': []}),
        ),
        (
            {'status': 'waiting', 'latitude': '55', 'longitude': '37'},
            (
                406,
                {'error': {'error_action': 'show_captcha', 'meters': 100}},
            ),  # without waiting_error it's always 200, waiting_error is on
        ),
    ],
)
@pytest.mark.driver_experiments('waiting_captcha')
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_driver_far_waiting_waiting_captcha_experiment(
        taxi_protocol,
        mockserver,
        db,
        params,
        expected_response,
        order_core_switch_on,
        mock_order_core,
):
    @mockserver.handler('/maps-router/route_jams/')
    def _(request):
        return mockserver.make_response()

    @mockserver.handler('/router-yamaps-masstransit/pedestrian/route')
    def _(request):
        return mockserver.make_response()

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _(request):
        return {}

    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'order.taxi_status': 'driving'}},
    )

    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
    }
    request_params.update(params)

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)

    assert response.status_code == expected_response[0]
    assert response.json() == expected_response[1]

    if response.status_code == 200:
        # captcha and fallback are under experiment only
        order_proc = db.order_proc.find_one(
            {'_id': '8c83b49edb274ce0992f337061047375'},
        )
        assert order_proc['waiting_mode'] == 'regular'

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.parametrize(
    ['experiments', 'config_enabled', 'service_response', 'expected'],
    [(['personal_wallet'], True, True, False)],
)
@pytest.mark.config(API_OVER_DATA_WORK_MODE=API_OVER_DATA_WORK_MODE)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_no_parks_activation(
        taxi_protocol,
        db,
        experiments,
        config_enabled,
        service_response,
        expected,
        config,
        user_experiments,
        order_core_switch_on,
        mock_order_core,
):
    config.set(PERSONAL_WALLET_ENABLED=config_enabled)
    user_experiments.set_value(experiments)
    db.order_proc.update_one(
        {
            '_id': '8c83b49edb274ce0992f337061047375',
            'candidates.car_number': 'Х492НК78',
        },
        {'$set': {'candidates.$.tariff_currency': 'currency'}},
    )
    db.tariff_settings.update_one(
        {'hz': 'moscow'}, {'$set': {'country': 'country'}},
    )
    db.parks.update_one(
        {'_id': '999012', 'account.contracts.is_of_card': False},
        {'$set': {'account.contracts.$.is_of_card': True}},
    )

    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'db_id': '12345',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'origin': 'dispatch',
        'use_recommended_cost': False,
        'user_login': 'disp_login',
        'status': 'complete',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
        'extra': '5000',
        'calc_method': 4,
        'is_captcha': True,
        'is_airplanemode': False,
        'is_offline': True,
        'driver_status': 'free',
        'receipt': _get_receipt(),
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey

    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200
    assert response.json()['enable_no_change_flow'] == expected

    assert mock_order_core.get_fields_times_called == order_core_switch_on


def add_extra_phone(db):
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            '$set': {
                'order.request.extra_user_phone_id': bson.ObjectId(
                    '568e7d45f52db432e4dc7d7d',
                ),
            },
        },
    )


@pytest.mark.translations(
    client_messages={
        # default label
        'requestconfirm.phone_label': {'en': 'solo phone'},
        'requestconfirm.phone_label.extra': {'en': 'extra phone'},
        'requestconfirm.phone_label.main': {'en': 'main phone'},
        # default call_dialog_message_prefix
        'requestconfirm.call_dialog_message_prefix': {
            'en': 'solo call dialog message prefix',
        },
        'requestconfirm.call_dialog_message_prefix.extra': {
            'en': 'extra call dialog message prefix',
        },
        'requestconfirm.call_dialog_message_prefix.main': {
            'en': 'main call dialog message prefix',
        },
        # econom label
        'requestconfirm.phone_label.econom': {'en': 'econom solo phone'},
        'requestconfirm.phone_label.econom.extra': {
            'en': 'econom extra phone',
        },
        'requestconfirm.phone_label.econom.main': {'en': 'econom main phone'},
        # econom call_dialog_message_prefix
        'requestconfirm.call_dialog_message_prefix.econom': {
            'en': 'econom solo call dialog message prefix',
        },
        'requestconfirm.call_dialog_message_prefix.econom.extra': {
            'en': 'econom extra call dialog message prefix',
        },
        'requestconfirm.call_dialog_message_prefix.econom.main': {
            'en': 'econom main call dialog message prefix',
        },
    },
)
@pytest.mark.parametrize(
    'test_prepare, expected_phone_options',
    [
        pytest.param(None, [SOLO_PHONE_OPTION]),
        pytest.param(
            None,
            [
                {
                    'label': 'econom solo phone',
                    'call_dialog_message_prefix': (
                        'econom solo call dialog message prefix'
                    ),
                    'type': 'main',
                },
            ],
            marks=pytest.mark.config(
                FOR_ANOTHER_OPTIONS_BY_TARIFF={
                    '__default__': {},
                    'econom': {'tanker_prefix': 'econom'},
                },
            ),
        ),
        pytest.param(add_extra_phone, [EXTRA_PHONE_OPTION, MAIN_PHONE_OPTION]),
        pytest.param(
            add_extra_phone,
            [MAIN_PHONE_OPTION, EXTRA_PHONE_OPTION],
            marks=pytest.mark.config(
                FOR_ANOTHER_OPTIONS_BY_TARIFF={
                    '__default__': {},
                    'econom': {
                        'types_priority': [{'type': 'main', 'weight': 100}],
                    },
                },
            ),
        ),
        pytest.param(
            add_extra_phone,
            [
                {
                    'label': 'econom extra phone',
                    'call_dialog_message_prefix': (
                        'econom extra call dialog message prefix'
                    ),
                    'type': 'extra',
                },
                {
                    'label': 'econom main phone',
                    'call_dialog_message_prefix': (
                        'econom main call dialog message prefix'
                    ),
                    'type': 'main',
                },
            ],
            marks=pytest.mark.config(
                FOR_ANOTHER_OPTIONS_BY_TARIFF={
                    '__default__': {},
                    'econom': {'tanker_prefix': 'econom'},
                },
            ),
        ),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_extra_phone(
        taxi_protocol,
        expected_phone_options,
        test_prepare,
        db,
        order_core_switch_on,
        mock_order_core,
):
    if test_prepare:
        test_prepare(db)

    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'db_id': '12345',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'origin': 'dispatch',
        'use_recommended_cost': False,
        'user_login': 'disp_login',
        'status': 'complete',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
        'extra': '5000',
        'calc_method': 4,
        'is_captcha': True,
        'is_airplanemode': False,
        'is_offline': True,
        'driver_status': 'free',
        'receipt': _get_receipt(),
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey

    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200
    body = response.json()
    assert body['phone_options'] == expected_phone_options

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.parametrize(
    'services, expected_url',
    [
        ({}, None),
        (
            {
                'eats': {'enabled': False, 'voice_file_url': 'test1.mp3'},
                'grocery': {'enabled': True},
            },
            None,
        ),
        (
            {
                'eats': {'enabled': False, 'voice_file_url': 'test1.mp3'},
                'grocery': {'enabled': False, 'voice_file_url': 'test2.mp3'},
            },
            None,
        ),
        (
            {
                'eats': {'enabled': True, 'voice_file_url': 'test1.mp3'},
                'grocery': {'enabled': False, 'voice_file_url': 'test2.mp3'},
            },
            'test1.mp3',
        ),
        (
            {
                'eats': {'enabled': False, 'voice_file_url': 'test1.mp3'},
                'grocery': {'enabled': True, 'voice_file_url': 'test2.mp3'},
            },
            'test2.mp3',
        ),
        (
            {
                'eats': {'enabled': True, 'voice_file_url': 'test1.mp3'},
                'grocery': {'enabled': True, 'voice_file_url': 'test2.mp3'},
            },
            'test1.mp3',
        ),
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_superapp_voice_url(
        taxi_protocol,
        experiments3,
        services,
        expected_url,
        db,
        order_core_switch_on,
        mock_order_core,
):
    experiments3.add_experiment(
        name='superapp_screens',
        consumers=['protocol/requestconfirm'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={
            'on_order': {
                'priority': ['eats', 'grocery'],
                'services': services,
            },
        },
    )
    taxi_protocol.tests_control(invalidate_caches=True)
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            '$set': {
                'status': 'driving',
                'order.svo_car_number': 'aaa',
                'order.verson': 1,
                'processing.version': 1,
                'processing.need_start': False,
            },
        },
    )
    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
        'extra': '210',
        'total': '210',
        'sum': '210',
        'user_login': 'Yandex IVR',
        'status': 'transporting',
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey

    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200
    body = response.json()
    if expected_url:
        assert body['superapp_voice_promo']['file_url'] == expected_url
    else:
        assert 'superapp_voice_promo' not in body

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.parametrize(
    'db_id, tin',
    [
        ('field_not_found', None),
        ('yandex', None),
        ('self_assign', '7719246912'),
        ('selfemployed_fns', 'inn_number'),
    ],
)
@pytest.mark.config(SAVE_TIN_ENABLED=True)
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_tin(
        taxi_protocol,
        db,
        mockserver,
        db_id,
        tin,
        order_core_switch_on,
        mock_order_core,
):
    driver_uuid = 'a5709ce56c2740d9a536650f5390de0b'

    @mockserver.json_handler('/selfemployed/selfemployed-info')
    def get(request):
        return {'inn': 'inn_number'}

    @mockserver.handler('/maps-router/route_jams/')
    def _(request):
        return mockserver.make_response()

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _(request):
        return {}

    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            '$set': {
                'status': 'pending',
                'order.taxi_status': 'pending',
                'performer.presetcar': True,
                'candidates.1.db_id': db_id,
            },
        },
    )

    db.dbdrivers.update(
        {'driver_id': driver_uuid}, {'$set': {'park_id': db_id}},
    )

    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': driver_uuid,
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'status': 'driving',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
    }

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    order = db.order_proc.find_one({'_id': '8c83b49edb274ce0992f337061047375'})

    if tin:
        assert 'tin' in order['order']['performer']
        assert order['order']['performer']['tin'] == tin
    else:
        assert 'tin' not in order['order']['performer']

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.config(
    TAXIMETER_WAITING_STATUS_PARAMS_BY_CITIES={
        '__default__': {
            'enable': True,
            'maxOrderDistance': 500,
            'maxOrderDistanceAirPort': 500,
            'maxOrderDistanceLinear': 40,
            'maxOrderPedestrianDistance': 250,
            'maxOrderPedestrianDistanceAirport': 500,
            'maxPhoneCallDistance': 2000,
            'maxPhoneCallDistanceAirport': 3000,
            'maxPhoneCallDistanceLinear': 100,
            'maxSpeed': 20,
            'responseTimeout': 5,
            'routeTimeoutMs': 30000,
        },
        'cities': {'Москва': {'maxOrderDistance': 100, 'responseTimeout': 10}},
    },
)
@pytest.mark.parametrize(
    'params,expected_response,',
    [
        (
            {'status': 'waiting', 'latitude': '55', 'longitude': '37'},
            (406, {'error': {'error_action': 'show_captcha', 'meters': 100}}),
        ),
        (
            {
                'status': 'waiting',
                'latitude': '55',
                'longitude': '37',
                'is_captcha': True,
            },
            (200, {'phone_options': []}),
        ),
        (
            {
                'status': 'waiting',
                'latitude': '55',
                'longitude': '37',
                'fallback': True,
            },
            (200, {'phone_options': []}),
        ),
        (
            {
                'status': 'waiting',
                'latitude': '55',
                'longitude': '37',
                'origin': 'dispatch',
            },
            (200, {'phone_options': []}),
        ),
    ],
)
@pytest.mark.driver_experiments('waiting_captcha')
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_driver_far_waiting_experiment(
        taxi_protocol,
        db,
        params,
        expected_response,
        mockserver,
        order_core_switch_on,
        mock_order_core,
):
    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {}

    @mockserver.handler('/maps-router/route_jams/')
    def _(request):
        return mockserver.make_response()

    @mockserver.handler('/router-yamaps-masstransit/pedestrian/route')
    def _(request):
        return mockserver.make_response()

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _(request):
        return {}

    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'order.taxi_status': 'driving'}},
    )

    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
    }
    request_params.update(params)

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)

    assert response.status_code == expected_response[0]
    assert response.json() == expected_response[1]

    if response.status_code == 200:
        if request_params.get('is_captcha', False):
            order_proc = db.order_proc.find_one(
                {'_id': '8c83b49edb274ce0992f337061047375'},
            )
            assert order_proc['waiting_mode'] == 'captcha'

        if request_params.get('fallback', False):
            order_proc = db.order_proc.find_one(
                {'_id': '8c83b49edb274ce0992f337061047375'},
            )
            assert order_proc['waiting_mode'] == 'fallback'


# 37.58917997300821,
# 55.73341076871702


@pytest.mark.config(
    SKOLKOVO_ASYNC_SEND_REQUEST=False, ROUTER_MAPS_ENABLED=True,
)
@pytest.mark.parametrize(
    'cur_status, src, dest, params, stq_expected',
    [
        pytest.param(
            'driving',
            (55.7334, 37.58917),
            (55, 37),
            {'status': 'waiting'},
            False,
        ),
        pytest.param(
            'pending', (50, 40), (55, 37), {'status': 'driving'}, True,
        ),
        pytest.param(
            'driving',
            (55.7334, 37.58917),
            (50, 40),
            {'status': 'waiting'},
            True,
        ),
        pytest.param(
            'pending', (55, 37), (50, 40), {'status': 'driving'}, False,
        ),
    ],
)
@pytest.mark.user_experiments('skolkovo_api_integration')
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_skolkovo(
        taxi_protocol,
        db,
        cur_status,
        src,
        dest,
        params,
        mockserver,
        stq_expected,
        order_core_switch_on,
        mock_order_core,
):
    requested_skolkovo_access_stq = False

    @mockserver.json_handler(
        '/stq-agent/queues/api/add/toll_roads_get_skolkovo_access',
    )
    def stq_agent_add_task(request):
        nonlocal requested_skolkovo_access_stq
        requested_skolkovo_access_stq = True

        return {}

    @mockserver.handler('/maps-router/route_jams/')
    def _(request):
        return mockserver.make_response()

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def batch_zones_filter(request):
        data = json.loads(request.get_data())
        assert data.get('allowed_zone_types') == ['skolkovo']
        results = [
            {'in_zone': data['points'][i][0] == 50}
            for i in range(len(data['points']))
        ]
        return {'results': results}

    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            '$set': {
                'status': cur_status,
                'order.taxi_status': cur_status,
                'performer.presetcar': True,
                'order.request.source.geopoint': src,
                'order.request.destinations.0.geopoint': dest,
            },
        },
    )

    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161219T083000',
        'time': '20161219T083000',
        'avg_speed': '0',
        'direction': '0',
        'latitude': 55.7334,
        'longitude': 37.58917,
    }

    request_params.update(params)

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)

    assert response.status_code == 200
    assert requested_skolkovo_access_stq == stq_expected

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_get_query_fail(taxi_protocol, db, order_core_switch_on):
    response = taxi_protocol.get('1.x/requestconfirm')
    assert response.status_code == 400


@pytest.mark.parametrize(
    'receipt, driver_receipt',
    [
        (
            {
                'area_ids': {'ufa': 'f2313a01f2b14ae883147cce1b34eb36'},
                'areas': ['ufa'],
                'calc_method': 2,
                'calc_total': 157.0,
                'details': [
                    {
                        'meter_type': 'time',
                        'meter_value': 1283.0,
                        'per': 60.0,
                        'price': 1.0,
                        'service_type': 'free_route',
                        'sum': 21.383333333333333,
                        'zone_names': ['ufa'],
                    },
                ],
                'distances_by_areas': {'ufa': 10703.691472337661},
                'dst_actual_point': {
                    'lat': 54.70032,
                    'lon': 55.994981666666675,
                },
                'dst_address': 'addr1',
                'dst_order_point': {'lat': 54.701095, 'lon': 55.995109},
                'durations_by_areas': {'ufa': 1283.0},
                'min_price': 49.0,
                'src_address': 'addr2',
                'src_point': {'lat': 54.775290524, 'lon': 56.0231119848},
                'sum': 155.0,
                'tariff_id': 'cc9db53fbfcf4223a594cf291d4da436',
                'total': 155.0,
                'total_distance': 10703.691472337661,
                'total_duration': 1283.0,
                'transfer': False,
                'version': '8.35 (290)',
            },
            {
                'calc_method': 2,
                'details': [
                    {
                        'meter_type': 'distance',
                        'meter_value': 7291.123637088756,
                        'per': 1000,
                        'price': 9,
                        'service_type': 'free_route',
                        'skip_before': 2000,
                        'sum': 65.6201127337988,
                        'zone_names': ['moscow'],
                    },
                    {
                        'meter_type': 'time',
                        'meter_value': 225,
                        'per': 60,
                        'price': 9,
                        'service_type': 'free_route',
                        'sum': 33.75,
                        'zone_names': ['moscow'],
                    },
                ],
                'transfer': False,
                'min_price': 100,
                'tariff_id': 'bae9c9f06203403aa892122e0d255a36',
                'total': 5.800000000000001,
                'total_distance': 8709.048311380839,
                'total_duration': 225,
            },
        ),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(order_proc='rounding')
@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={'__default__': {'__default__': 0.1}},
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_rounding(
        taxi_protocol,
        db,
        receipt,
        driver_receipt,
        order_core_switch_on,
        mock_order_core,
):
    request_params = {
        'orderid': 'db60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'db_id': '12345',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'use_recommended_cost': False,
        'user_login': 'disp_login',
        'status': 'complete',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
        'calc_method': 4,
        'is_captcha': True,
        'is_airplanemode': False,
        'is_offline': True,
        'driver_status': 'free',
        'receipt': receipt,
        'driver_calc_receipt_overrides': driver_receipt,
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey

    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one('1c83b49edb274ce0992f337061047375')
    driver_cost = proc['order']['driver_cost']['cost']
    assert round(driver_cost * 10) == 58

    assert mock_order_core.get_fields_times_called == order_core_switch_on


WITH_CONTACT_PHONE = {
    'contact_phone_id': bson.ObjectId('5714f45e98956f06baaae3d4'),
}


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.translations(
    client_messages={
        'requestconfirm.phone_label': {'en': 'solo phone'},
        'requestconfirm.phone_label.extra': {'en': 'extra phone'},
        'requestconfirm.phone_label.main': {'en': 'main phone'},
        'requestconfirm.call_dialog_message_prefix': {
            'en': 'solo call dialog message prefix',
        },
        'requestconfirm.call_dialog_message_prefix.extra': {
            'en': 'extra call dialog message prefix',
        },
        'requestconfirm.call_dialog_message_prefix.main': {
            'en': 'main call dialog message prefix',
        },
    },
)
@pytest.mark.parametrize(
    ('point_a_extra', 'point_b_extra', 'expected_phone_options'),
    (
        pytest.param({}, {}, [SOLO_PHONE_OPTION], id='no_extra'),
        pytest.param(
            WITH_CONTACT_PHONE,
            {},
            [EXTRA_PHONE_OPTION, MAIN_PHONE_OPTION],
            id='source_extra',
        ),
        pytest.param(
            {},
            WITH_CONTACT_PHONE,
            [EXTRA_PHONE_OPTION, MAIN_PHONE_OPTION],
            id='destination_extra',
        ),
    ),
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_route_extra_phone(
        taxi_protocol,
        mockserver,
        db,
        point_a_extra,
        point_b_extra,
        expected_phone_options,
        order_core_switch_on,
        mock_order_core,
):
    @mockserver.handler('/maps-router/route_jams/')
    def _(request):
        return mockserver.make_response()

    route_update = (
        {'order.request.source.extra_data': point_a_extra}
        if point_a_extra
        else {}
    )
    route_update.update(
        {'order.request.destinations.0.extra_data': point_b_extra}
        if point_b_extra
        else {},
    )

    if route_update:
        db.order_proc.update(
            {'_id': '1c83b49edb274ce0992f337061047375'},
            {'$set': route_update},
        )

    request_params = {
        'orderid': 'db60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'status': 'waiting',
        'latitude': '55.73367',
        'longitude': '37.587874',
    }

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    body = response.json()
    assert body['phone_options'] == expected_phone_options

    assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.now('2021-11-25T16:30:00+0300')
@pytest.mark.parametrize(
    'order_proc_updates, params, params_updates,',
    [
        (
            {
                '$set': {
                    'status': 'pending',
                    'order.taxi_status': 'pending',
                    'performer.presetcar': True,
                },
            },
            {'status': 'driving'},
            None,
        ),
        (None, {'status': 'complete'}, None),
        (
            {
                '$set': {
                    'status': 'pending',
                    'order.taxi_status': 'pending',
                    'performer.presetcar': True,
                },
            },
            {'status': 'driving'},
            {'status': 'complete'},
        ),
    ],
    ids=[
        'set_at_begin',
        'set_after_complete',
        'set_at_begin_and_update_after_end',
    ],
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_set_and_change_taximeter_app(
        order_proc_updates,
        taxi_protocol,
        mockserver,
        db,
        params,
        params_updates,
        order_core_switch_on,
        mock_order_core,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _(request):
        return {}

    order_proc_id = {'_id': '8c83b49edb274ce0992f337061047375'}
    if order_proc_updates:
        db.order_proc.update(order_proc_id, order_proc_updates)
    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
    }
    request_params.update(params)
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    old_taximeter_app = 'Taximeter%209.92%20(1074007349)'
    expected_old_taximeter_app = 'Taximeter 9.92 (1074007349)'

    uri = (
        '1.x/requestconfirm?taximeter_app='
        + old_taximeter_app
        + '&clid=999012&apikey='
        + apikey
    )
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200
    proc = db.order_proc.find_one(order_proc_id)
    assert (
        expected_old_taximeter_app
        == proc['order']['performer']['taximeter_app']
    )
    if params_updates:
        request_params.update(params_updates)
        new_taximeter_app = 'Taximeter%2010.4%20(1074046521)'
        expected_new_taximeter_app = 'Taximeter 10.4 (1074046521)'
        uri = (
            '1.x/requestconfirm?taximeter_app='
            + new_taximeter_app
            + '&clid=999012&apikey='
            + apikey
        )
        response = taxi_protocol.post(uri, request_params)
        assert response.status_code == 200
        proc = db.order_proc.find_one(order_proc_id)
        assert (
            expected_new_taximeter_app
            == proc['order']['performer']['taximeter_app']
        )
    if order_core_switch_on and params_updates:
        assert mock_order_core.get_fields_times_called == 2
    else:
        assert mock_order_core.get_fields_times_called == order_core_switch_on


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=5))
@pytest.mark.parametrize(
    'order_proc_set, is_paid_cancel_in_order',
    [
        (
            {
                '$set': {
                    'status': 'pending',
                    'order.taxi_status': 'pending',
                    'performer.presetcar': True,
                    'order.performer.paid_supply': False,
                    'candidates.$.paid_supply': False,
                    'performer.paid_supply': False,
                    'order.paid_cancel_in_driving': {
                        'price': 500,
                        'free_cancel_timeout': 300,
                        'for_paid_supply': True,
                    },
                },
            },
            False,
        ),
        (
            {
                '$set': {
                    'status': 'pending',
                    'order.taxi_status': 'pending',
                    'performer.presetcar': True,
                    'order.performer.paid_supply': False,
                    'candidates.$.paid_supply': False,
                    'performer.paid_supply': False,
                    'order.paid_cancel_in_driving': {
                        'price': 500,
                        'free_cancel_timeout': 300,
                        'for_paid_supply': True,
                    },
                    'decoupling': {
                        'user_price_info.paid_cancel_in_driving': {
                            'price': 500,
                            'free_cancel_timeout': 300,
                            'for_paid_supply': True,
                        },
                        'driver_price_info.paid_cancel_in_driving': {
                            'price': 500,
                            'free_cancel_timeout': 300,
                            'for_paid_supply': True,
                        },
                    },
                },
            },
            False,
        ),
        (
            {
                '$set': {
                    'status': 'pending',
                    'order.taxi_status': 'pending',
                    'performer.presetcar': True,
                    'order.performer.paid_supply': True,
                    'candidates.$.paid_supply': True,
                    'performer.paid_supply': True,
                    'order.paid_cancel_in_driving': {
                        'price': 500,
                        'free_cancel_timeout': 300,
                        'for_paid_supply': True,
                    },
                },
            },
            True,
        ),
        (
            {
                '$set': {
                    'status': 'pending',
                    'order.taxi_status': 'pending',
                    'performer.presetcar': True,
                    'order.performer.paid_supply': True,
                    'candidates.$.paid_supply': True,
                    'performer.paid_supply': True,
                    'order.paid_cancel_in_driving': {
                        'price': 500,
                        'free_cancel_timeout': 300,
                        'for_paid_supply': True,
                    },
                    'decoupling': {
                        'user_price_info.paid_cancel_in_driving': {
                            'price': 500,
                            'free_cancel_timeout': 300,
                            'for_paid_supply': True,
                        },
                        'driver_price_info.paid_cancel_in_driving': {
                            'price': 500,
                            'free_cancel_timeout': 300,
                            'for_paid_supply': True,
                        },
                    },
                },
            },
            True,
        ),
        (
            {
                '$set': {
                    'status': 'pending',
                    'order.taxi_status': 'pending',
                    'performer.presetcar': True,
                    'order.performer.paid_supply': True,
                    'candidates.$.paid_supply': True,
                    'performer.paid_supply': False,
                    'order.paid_cancel_in_driving': {
                        'price': 500,
                        'free_cancel_timeout': 300,
                        'for_paid_supply': False,
                    },
                },
            },
            True,
        ),
    ],
    ids=[
        'find_free_ride_after_paid_supply',
        'find_free_ride_after_paid_supply with decoupling',
        'find_paid_ride_after_paid_supply',
        'find_paid_ride_after_paid_supply_with_decoupling',
        'paid_cancel_but_not_because_of_paid_supply',
    ],
)
@pytest.mark.experiments3(
    filename='exp3_no_paid_cancel_after_free_supply.json',
)
@PROTOCOL_SWITCH_TO_ORDER_CORE
def test_requestconfirm_no_paid_cancel_after_free_supply(
        taxi_protocol,
        mockserver,
        db,
        config,
        order_proc_set,
        is_paid_cancel_in_order,
        order_core_switch_on,
        mock_order_core,
):
    @mockserver.handler('/maps-router/route_jams/')
    def _(request):
        return mockserver.make_response()

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _(request):
        return {}

    config.set_values(dict(PROCESSING_BACKEND_CPP_SWITCH=['requestconfirm']))
    driver_uuid = 'a5709ce56c2740d9a536650f5390de0b'

    db.order_proc.update(
        {
            '_id': '8c83b49edb274ce0992f337061047375',
            'candidates.car_number': 'Х492НК78',
        },
        order_proc_set,
    )

    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': driver_uuid,
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'status': 'driving',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one({'_id': '8c83b49edb274ce0992f337061047375'})
    assert (
        'paid_cancel_in_driving' in proc['order']
    ) == is_paid_cancel_in_order
    if 'decoupling' in proc['order']:
        assert (
            'paid_cancel_in_driving'
            in proc['order']['decoupling']['user_price_info']
        ) == is_paid_cancel_in_order

        assert (
            'paid_cancel_in_driving'
            in proc['order']['decoupling']['driver_price_info']
        ) == is_paid_cancel_in_order
