import copy
import datetime

import pytest

from protocol.ordercommit import order_commit_common

ORDER_ID = '1c83b49edb274ce0992f337061047375'
ALIAS_ID = 'db60d02916ae4a1a91eafa3a1a8ed04d'
DRIVER_WAITING_TIME = 5
DRIVER_WAITING_PRICE = 99.5
USER_WAITING_TIME = 4
USER_WAITING_PRICE = 40.2


def check_decoupling_prices(
        proc,
        user_cost,
        user_cost_is_unusual,
        driver_cost,
        driver_cost_is_unusual,
):
    if user_cost == 0.0:
        user_cost = None

    # decoupled user fixed
    assert proc['order'].get('cost') == user_cost
    assert (
        proc['order']['decoupling']['user_price_info'].get('cost') == user_cost
    )
    assert (
        proc['order']['decoupling']['user_price_info'].get('cost_is_unusual')
        is user_cost_is_unusual
    )
    # decoupled driver fixed
    assert (
        proc['order']['decoupling']['driver_price_info'].get('cost')
        == driver_cost
    )
    assert (
        proc['order']['decoupling']['driver_price_info'].get('cost_is_unusual')
        is driver_cost_is_unusual
    )


def check_calc_infos(proc):
    assert proc['order']['calc_info']['waiting_cost'] == USER_WAITING_PRICE
    assert proc['order']['calc_info']['waiting_time'] == USER_WAITING_TIME
    assert (
        proc['order']['driver_calc_info']['waiting_cost']
        == DRIVER_WAITING_PRICE
    )
    assert (
        proc['order']['driver_calc_info']['waiting_time']
        == DRIVER_WAITING_TIME
    )


@pytest.mark.parametrize(
    'orderid,params,expected_cost,pcv',
    [
        (
            ORDER_ID,
            {
                'orderid': ALIAS_ID,
                'uuid': 'a5709ce56c2740d9a536650f5390de0b',
                'clid': '999012',
                'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
            },
            317.0,
            10000,
        ),
        (
            ORDER_ID,
            {
                'orderid': ALIAS_ID,
                'uuid': 'a5709ce56c2740d9a536650f5390de0c',
                'clid': '999013',
                'apikey': 'd19a9b3b59424881b57adf5b0f367a2d',
            },
            380.4,
            12000,
        ),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=5))
@pytest.mark.filldb(parks='corp')
@pytest.mark.config(CALCULATE_VAT_ON_REQUESTCONFIRM=True)
def test_requestconfirm_calc_vat(
        taxi_protocol, mockserver, db, orderid, params, expected_cost, pcv,
):
    @mockserver.json_handler('/statistics/v1/metrics/store')
    def mock_metrics_store(request):
        return {}

    request_params = {
        'status': 'complete',
        'extra': expected_cost,
        'latitude': '55.733410768',
        'longitude': '37.589179973',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
    }
    request_params.update(params)

    db.order_proc.update(
        {'_id': ORDER_ID},
        {
            '$set': {
                'order.performer.clid': params['clid'],
                'performer.park_id': params['clid'],
                'performer.driver_id': params['clid'] + '_' + params['uuid'],
            },
        },
    )
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
        'phone_options': [],
        'final_cost': {
            # from order.decoupling.driver_price_info.fixed_price
            'driver': 317.0,
            # from `extra`
            'user': expected_cost,
        },
    }

    proc = db.order_proc.find_one(orderid)
    assert proc['performer']['park_corp_vat'] == pcv


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
                        'meter_value': USER_WAITING_TIME,
                        'per': 60,
                        'price': 9,
                        'service_type': 'waiting',
                        'sum': USER_WAITING_PRICE,
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
                        'meter_value': DRIVER_WAITING_TIME,
                        'per': 60,
                        'price': 9,
                        'service_type': 'waiting',
                        'sum': DRIVER_WAITING_PRICE,
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
def test_requestconfirm_driver_taximeter_price(
        taxi_protocol, mockserver, db, receipt, driver_receipt,
):
    @mockserver.json_handler('/statistics/v1/metrics/store')
    def mock_metrics_store(request):
        return {}

    request_params = {
        'orderid': ALIAS_ID,
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
        'extra': '674',
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

    proc = db.order_proc.find_one(ORDER_ID)
    assert proc['order']['taximeter_receipt'] == receipt

    assert proc['order']['calc_total'] == 157
    check_calc_infos(proc)
    assert proc['order']['cost'] == 674
    check_decoupling_prices(proc, 674, None, driver_receipt['total'], None)
    order_commit_common.check_current_prices(proc, 'final_cost', 674)


@pytest.mark.parametrize(
    'receipt, driver_receipt',
    [
        (
            {
                'area_ids': {'ufa': 'f2313a01f2b14ae883147cce1b34eb36'},
                'areas': ['ufa'],
                'calc_class': 'yandex_v2',
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
                        'meter_value': USER_WAITING_TIME,
                        'per': 60,
                        'price': 9,
                        'service_type': 'waiting',
                        'sum': USER_WAITING_PRICE,
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
                        'meter_value': DRIVER_WAITING_TIME,
                        'per': 60,
                        'price': 9,
                        'service_type': 'waiting',
                        'sum': DRIVER_WAITING_PRICE,
                        'zone_names': ['moscow'],
                    },
                ],
                'transfer': False,
                'min_price': 100,
                'tariff_id': 'bae9c9f06203403aa892122e0d255a36',
                'total': 317 + 100,
                'total_distance': 8709.048311380839,
                'total_duration': 225,
            },
        ),
    ],
)
@pytest.mark.parametrize(
    'paid_supply, paid_supply_user, paid_supply_driver',
    [(False, 0, 0), (True, 63, 63), (True, 0, 63)],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_requestconfirm_fixed_price(
        taxi_protocol,
        mockserver,
        db,
        receipt,
        driver_receipt,
        paid_supply,
        paid_supply_user,
        paid_supply_driver,
):
    @mockserver.json_handler('/statistics/v1/metrics/store')
    def mock_metrics_store(request):
        return {}

    if paid_supply:
        db.order_proc.update(
            {'_id': '1c83b49edb274ce0992f337061047375'},
            {
                '$set': {
                    'order.fixed_price.paid_supply_price': paid_supply_user,
                    'order.performer.paid_supply': True,
                    'order.decoupling.driver_price_info.paid_supply_price': (
                        paid_supply_driver
                    ),
                    'order.decoupling.user_price_info.paid_supply_price': (
                        paid_supply_user
                    ),
                },
            },
        )

    request_params = {
        'orderid': ALIAS_ID,
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
        'extra': str(633 + 41 + (paid_supply_user if paid_supply else 0)),
        'calc_method': 4,
        'is_captcha': True,
        'is_airplanemode': False,
        'is_offline': True,
        'driver_status': 'free',
        'receipt': receipt,
        'driver_calc_receipt_overrides': copy.deepcopy(driver_receipt),
    }
    request_params['driver_calc_receipt_overrides'][
        'total'
    ] += paid_supply_driver
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one(ORDER_ID)

    assert proc['order']['calc_total'] == 157
    check_calc_infos(proc)
    user_cost = 633 + 41 + paid_supply_user
    assert proc['order']['cost'] == user_cost
    driver_cost = 317 + 100 + paid_supply_driver
    check_decoupling_prices(proc, user_cost, None, driver_cost, None)
    order_commit_common.check_current_prices(proc, 'final_cost', user_cost)


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
                        'meter_value': USER_WAITING_TIME,
                        'per': 60,
                        'price': 9,
                        'service_type': 'waiting',
                        'sum': USER_WAITING_PRICE,
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
                        'meter_value': DRIVER_WAITING_TIME,
                        'per': 60,
                        'price': 9,
                        'service_type': 'waiting',
                        'sum': DRIVER_WAITING_PRICE,
                        'zone_names': ['moscow'],
                    },
                ],
                'transfer': False,
                'min_price': 100,
                'tariff_id': 'bae9c9f06203403aa892122e0d255a36',
                'total': 234,
                'total_distance': 8709.048311380839,
                'total_duration': 225,
            },
        ),
    ],
)
@pytest.mark.parametrize(
    'calc_method,fixed_price,taximeter_price,'
    'decoupling_driver_price,cost_is_unusual',
    [
        # method unknown, no fixed or taximeter
        # fallback result order_info.driver_cc
        (None, None, None, 150.0, True),
        # method unknown but user method is fix, result fixed_price
        (None, 317.0, None, 317.0, True),
        # method order-cost, but no fixed or taximeter
        # fallback result order_info.driver_cc
        (4, None, None, 150.0, True),
        # method order-cost, result driver receipt price
        (4, None, 234, 234.0, None),
        # method order-cost, result driver receipt price
        (4, 317.0, 234, 234.0, None),
        # method fixed, but no fixed or taximeter
        # fallback result order_info.driver_cc
        (2, None, None, 150.0, True),
        # method fixed, but no fixed
        (2, None, 234, 234.0, None),
        # method fixed
        (2, 317.0, 234, 234.0, None),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_requestconfirm_driver_price_origin_driver_no_manual(
        taxi_protocol,
        mockserver,
        db,
        receipt,
        driver_receipt,
        calc_method,
        fixed_price,
        taximeter_price,
        decoupling_driver_price,
        cost_is_unusual,
):
    @mockserver.json_handler('/statistics/v1/metrics/store')
    def mock_metrics_store(request):
        return {}

    request_params = {
        'orderid': ALIAS_ID,
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
        'extra': '674',
        'calc_method': 4,
        'is_captcha': True,
        'is_airplanemode': False,
        'is_offline': True,
        'driver_status': 'free',
        'receipt': receipt,
    }
    if calc_method is not None and taximeter_price is not None:
        update_params = {'calc_method': calc_method, 'total': taximeter_price}
        driver_receipt.update(update_params)
        request_params.update(
            {'driver_calc_receipt_overrides': driver_receipt},
        )

    db.order_proc.update(
        {'_id': ORDER_ID},
        {
            '$set': {
                'order.decoupling.driver_price_info.fixed_price': fixed_price,
            },
        },
    )

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one(ORDER_ID)
    assert proc['order']['calc_total'] == 157
    assert proc['order']['cost'] == 674
    check_decoupling_prices(
        proc, 674, None, decoupling_driver_price, cost_is_unusual,
    )
    order_commit_common.check_current_prices(proc, 'final_cost', 674)


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
                        'meter_value': USER_WAITING_TIME,
                        'per': 60,
                        'price': 9,
                        'service_type': 'waiting',
                        'sum': USER_WAITING_PRICE,
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
                        'meter_value': DRIVER_WAITING_TIME,
                        'per': 60,
                        'price': 9,
                        'service_type': 'waiting',
                        'sum': DRIVER_WAITING_PRICE,
                        'zone_names': ['moscow'],
                    },
                ],
                'transfer': False,
                'min_price': 100,
                'tariff_id': 'bae9c9f06203403aa892122e0d255a36',
                'total': 417,
                'total_distance': 8709.048311380839,
                'total_duration': 225,
            },
        ),
    ],
)
@pytest.mark.parametrize(
    'calc_method,fixed_price,decoupling_user_price,cost_is_unusual',
    [
        # just use taximeter's user price
        (2, 633.0, 5000, None),
        (2, None, 5000, None),
        (1, 633.0, 5000, None),
        (4, 633.0, 5000, None),
        # strange calc methods
        (3, 633.0, 5000, True),
        (5, 633.0, 5000, True),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_requestconfirm_user_price_origin_driver_no_manual(
        taxi_protocol,
        mockserver,
        db,
        receipt,
        driver_receipt,
        calc_method,
        fixed_price,
        decoupling_user_price,
        cost_is_unusual,
):
    @mockserver.json_handler('/statistics/v1/metrics/store')
    def mock_metrics_store(request):
        return {}

    receipt.update({'calc_method': calc_method})
    request_params = {
        'orderid': ALIAS_ID,
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
        'calc_method': calc_method,
        'is_captcha': True,
        'is_airplanemode': False,
        'is_offline': True,
        'driver_status': 'free',
        'receipt': receipt,
        'driver_calc_receipt_overrides': driver_receipt,
    }

    db.order_proc.update(
        {'_id': ORDER_ID},
        {
            '$set': {
                'order.decoupling.user_price_info.fixed_price': fixed_price,
            },
        },
    )

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one(ORDER_ID)
    assert proc['order']['calc_total'] == 157
    check_calc_infos(proc)
    assert proc['order']['cost'] == decoupling_user_price
    check_decoupling_prices(
        proc, decoupling_user_price, cost_is_unusual, 417.0, None,
    )
    order_commit_common.check_current_prices(
        proc, 'final_cost', decoupling_user_price,
    )


@pytest.mark.parametrize(
    'paid_supply, paid_supply_user, paid_supply_driver, calc_method_taximeter',
    [
        (False, None, None, False),
        (True, 0, 100, False),
        (True, 100, 100, False),
        (False, None, None, True),
        (True, 0, 100, True),
        (True, 100, 100, True),
    ],
)
def test_requestconfirm_paid_supply_prices(
        taxi_protocol,
        mockserver,
        db,
        paid_supply,
        paid_supply_user,
        paid_supply_driver,
        calc_method_taximeter,
):
    @mockserver.json_handler('/statistics/v1/metrics/store')
    def mock_metrics_store(request):
        return {}

    driver_cost = 317 + 100 + (paid_supply_driver if paid_supply else 0)

    db.order_proc.update(
        {'_id': ORDER_ID},
        {'$set': {'order.decoupling.user_price_info.fixed_price': 633}},
    )
    if paid_supply:
        db.order_proc.update(
            {'_id': ORDER_ID},
            {
                '$set': {
                    'order.fixed_price.paid_supply_price': paid_supply_user,
                    'order.performer.paid_supply': True,
                    'order.decoupling.driver_price_info.paid_supply_price': (
                        paid_supply_driver
                    ),
                    'order.decoupling.user_price_info.paid_supply_price': (
                        paid_supply_user
                    ),
                },
            },
        )

    request_params = {
        'orderid': ALIAS_ID,
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
        'calc_method': 1 if calc_method_taximeter else 2,
        'is_captcha': True,
        'is_airplanemode': False,
        'is_offline': True,
        'driver_status': 'free',
        'receipt': {
            'area_ids': {'ufa': 'f2313a01f2b14ae883147cce1b34eb36'},
            'areas': ['ufa'],
            'calc_method': 1 if calc_method_taximeter else 2,
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
                    'meter_value': USER_WAITING_TIME,
                    'per': 60,
                    'price': 9,
                    'service_type': 'waiting',
                    'sum': USER_WAITING_PRICE,
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
        },
        'driver_calc_receipt_overrides': {
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
                    'meter_value': DRIVER_WAITING_TIME,
                    'per': 60,
                    'price': 9,
                    'service_type': 'waiting',
                    'sum': DRIVER_WAITING_PRICE,
                    'zone_names': ['moscow'],
                },
            ],
            'transfer': False,
            'min_price': 100,
            'tariff_id': 'bae9c9f06203403aa892122e0d255a36',
            'total': driver_cost,
            'total_distance': 8709.048311380839,
            'total_duration': 225,
        },
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one(ORDER_ID)

    finished_user_cost = 5000
    assert proc['order']['cost'] == finished_user_cost
    check_decoupling_prices(proc, finished_user_cost, None, driver_cost, None)
    order_commit_common.check_current_prices(
        proc, 'final_cost', finished_user_cost,
    )


FIXED_PRICE = 1
CURRENT_COST = 2
TARIFF_COST = 3
FALLBACK = 4
CURRENT_PRICES = 5
PUBLISHED_PRICES = 6


@pytest.mark.parametrize(
    'price_source, user_cost, driver_cost, cost_is_unusual',
    [
        (FIXED_PRICE, 633.0, 317.0, None),
        (CURRENT_COST, 300.0, 150.0, None),
        (TARIFF_COST, 200.0, 100.0, None),
        (FALLBACK, 5000.0, 5000.0, True),
        (CURRENT_PRICES, 301.0, 151.0, None),
        (PUBLISHED_PRICES, 302.0, 152.0, None),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_requestconfirm_disp_complete(
        taxi_protocol,
        mockserver,
        db,
        price_source,
        user_cost,
        driver_cost,
        cost_is_unusual,
):
    @mockserver.json_handler('/statistics/v1/metrics/store')
    def mock_metrics_store(request):
        return {}

    request_params = {
        'orderid': ALIAS_ID,
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'origin': 'dispatch',
        'use_recommended_cost': False,
        'user_login': 'disp_login',
        'dispatch_api_version': '1.0',
        'status': 'complete',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
        'extra': '5000',
        'calc_method': 6,
    }
    if price_source > FIXED_PRICE:
        db.order_proc.update(
            {'_id': ORDER_ID},
            {
                '$unset': {
                    'order.decoupling.user_price_info.fixed_price': '',
                    'order.decoupling.driver_price_info.fixed_price': '',
                },
            },
        )

    if price_source > CURRENT_COST:
        db.order_proc.update(
            {'_id': ORDER_ID},
            {'$unset': {'order_info.cc': '', 'order_info.driver_cc': ''}},
        )

    if price_source > TARIFF_COST:
        db.order_proc.update(
            {'_id': ORDER_ID},
            {
                '$unset': {
                    'order.tariff_cost': '',
                    'order.driver_cost.tariff_cost': '',
                },
            },
        )

    if price_source > FALLBACK:
        db.order_proc.update(
            {'_id': '1c83b49edb274ce0992f337061047375'},
            {
                '$set': {
                    'order.current_prices.current_cost.driver.total': (
                        driver_cost
                    ),
                    'order.current_prices.current_cost.user.total': user_cost,
                },
            },
        )

    if price_source > CURRENT_PRICES:
        db.order_proc.update(
            {'_id': '1c83b49edb274ce0992f337061047375'},
            {
                '$set': {
                    'order.pricing_data.published.fixed.cost.driver.total': (
                        driver_cost
                    ),
                    'order.pricing_data.published.fixed.cost.user.total': (
                        user_cost
                    ),
                    'order.pricing_data.published.current_method': 'fixed',
                },
            },
        )
        request_params.update({'dispatch_selected_cost': 'fixed'})

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    content_type = response.headers['Content-Type']
    assert content_type == 'application/json; charset=utf-8'

    data = response.json()
    assert data == {
        'taximeter_cost': driver_cost,
        'phone_options': [],
        'final_cost': {'driver': driver_cost, 'user': user_cost},
    }

    proc = db.order_proc.find_one(ORDER_ID)
    assert proc['status'] == 'finished'
    assert proc['order']['taxi_status'] == 'complete'
    check_decoupling_prices(
        proc, user_cost, cost_is_unusual, driver_cost, cost_is_unusual,
    )

    disp_cost = proc['order']['disp_cost']
    assert disp_cost is not None
    assert disp_cost['disp_cost'] == 5000
    assert disp_cost['taximeter_cost'] == driver_cost
    assert disp_cost['operator_login'] == 'disp_login'
    assert disp_cost['use_recommended_cost'] is True
    assert disp_cost['dispatch_api_version'] == '1.0'

    order_commit_common.check_current_prices(proc, 'final_cost', user_cost)


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.config(
    MIN_PAID_WAITING_TIME_LIMIT={'__default__': 600.0},
    MAX_PAID_WAITING_TIME=600,
)
@pytest.mark.experiments3(filename='exp3_paid_supply_paid_cancel.json')
@pytest.mark.parametrize(
    'wait_seconds',
    [
        # 13 minutes not enough, 14 enough, cause due is set to $dateDiff: 209
        # waiting_time = min(wait_time_sec, MAX_PAID_WAITING_TIME) -
        809,  # $dateDiff + MIN_PAID_WAITING_TIME = 209 + 600
        1809,  # check MAX_PAID_WAITING_TIME cap
    ],
)
# tariff.categories.st.p.tpi.b * 60 - tariff.categories.waiting * 60
# waiting_cost = waiting_time * tariff.categories.st.p.tpi.p / 60
# waiting_time = 600 - 5 * 60 - 2 * 60 = 180
@pytest.mark.parametrize(
    'driver_add_minimal, driver_paid_cancel_fix, driver_cost',
    [
        # waiting_cost = 180 * 9 / 60 = 27
        # minimal is 99
        (False, 200, 200 + 27),  # paid_cancel_fix + waiting_cost
        (True, 0, 99 + 27),  # minimal(99) + waiting_cost
    ],
)
@pytest.mark.parametrize(
    'user_add_minimal, user_paid_cancel_fix, user_cost',
    [
        # waiting_cost = 180 * 18 / 60 = 54
        # minimal is 198
        (False, 400, 400 + 54),  # paid_cancel_fix + waiting_cost
        (True, 0, 198 + 54),  # minimal + waiting_cost
    ],
)
@pytest.mark.parametrize(
    'user_paid_supply_price, driver_paid_supply_price, paid_supply',
    [
        (None, None, False),
        (43, 43, False),
        (43, 43, True),
        # user cost nullified
        (0, 43, False),
        (0, 43, True),
    ],
)
def test_requestconfirm_reject_paid_after_long_waiting(
        taxi_protocol,
        recalc_order,
        db,
        now,
        load_json,
        mockserver,
        wait_seconds,
        driver_add_minimal,
        driver_paid_cancel_fix,
        driver_cost,
        user_add_minimal,
        user_paid_cancel_fix,
        user_cost,
        user_paid_supply_price,
        driver_paid_supply_price,
        paid_supply,
):
    @mockserver.json_handler('/statistics/v1/metrics/store')
    def mock_metrics_store(request):
        return {}

    if paid_supply:
        user_cost += user_paid_supply_price
        driver_cost += driver_paid_supply_price
    recalc_order.set_driver_recalc_result(
        driver_cost, driver_cost, {'driver_meta': driver_cost},
    )
    recalc_order.set_user_recalc_result(
        user_cost, user_cost, {'user_meta': user_cost},
    )

    if user_paid_supply_price is not None:
        db.order_proc.update(
            {'_id': ORDER_ID},
            {
                '$set': {
                    'order.fixed_price.paid_supply_price': (
                        user_paid_supply_price
                    ),
                    'order.decoupling.user_price_info.paid_supply_price': (
                        user_paid_supply_price
                    ),
                    'order.decoupling.driver_price_info.paid_supply_price': (
                        driver_paid_supply_price
                    ),
                },
            },
        )
    db.order_proc.update(
        {'_id': ORDER_ID},
        {'$set': {'order.performer.paid_supply': paid_supply}},
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
                'categories.$.add_minimal_to_paid_cancel': driver_add_minimal,
                'categories.$.paid_cancel_fix': driver_paid_cancel_fix,
            },
        },
    )

    # Database uses $dateDiff, so changing current time after it is loaded
    later = now + datetime.timedelta(seconds=wait_seconds)
    taxi_protocol.tests_control(now=later)

    request_params = {
        'orderid': ALIAS_ID,
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

    proc = db.order_proc.find_one(ORDER_ID)
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

    user_cost_is_unusual = None

    check_decoupling_prices(
        proc, user_cost, user_cost_is_unusual, driver_cost, None,
    )
    if user_cost:
        order_commit_common.check_current_prices(proc, 'final_cost', user_cost)
    current_prices = proc['order']['current_prices']
    assert current_prices['kind'] == 'final_cost'
    assert current_prices['final_cost'] == {
        'driver': {'total': driver_cost},
        'user': {'total': user_cost},
    }
    assert current_prices['final_cost_meta'] == {
        'driver': {
            'driver_meta': driver_cost,
            'paid_cancel_in_waiting_price': driver_cost,
        },
        'user': {
            'user_meta': user_cost,
            'paid_cancel_in_waiting_price': user_cost,
        },
    }


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.config(MIN_PAID_WAITING_TIME=600, MAX_PAID_WAITING_TIME=600)
def test_requestconfirm_reject_free_after_short_waiting(
        taxi_protocol, mockserver, db, now,
):
    @mockserver.json_handler('/statistics/v1/metrics/store')
    def mock_metrics_store(request):
        return {}

    short_waiting = 808  # dateDiff + MIN_PAID_WAITING_TIME - 1 = 209 + 600 - 1
    # Database uses $dateDiff, so changing current time after it is loaded
    later = now + datetime.timedelta(seconds=short_waiting)
    taxi_protocol.tests_control(now=later)

    request_params = {
        'orderid': ALIAS_ID,
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

    proc = db.order_proc.find_one(ORDER_ID)
    # autoreorder
    assert proc['order']['status'] == 'pending'
    assert proc['order']['taxi_status'] is None
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
    assert autoreorder is True
    assert proc['order']['cost'] is None


@pytest.mark.parametrize(
    'params,expected_state,user_cost,driver_cost',
    [
        (
            {
                'status': 'failed',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
            },
            (200, 'finished', 'cancelled'),
            252.0,
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
            252.0,
            126.0,
        ),
        (  # No position autoreorder
            {'status': 'failed'},
            (200, 'pending', None),
            None,
            None,
        ),
        (  # No position so it's free
            {'status': 'failed', 'cancel': 'paid'},
            (406, 'assigned', 'waiting'),
            None,
            None,
        ),
        (  # No position but dispatch
            {'status': 'failed', 'cancel': 'paid', 'origin': 'dispatch'},
            (200, 'finished', 'cancelled'),
            252.0,
            126.0,
        ),
        (
            {
                'status': 'cancelled',
                'latitude': '55.733410768',
                'longitude': '37.589179973',
            },
            (200, 'finished', 'cancelled'),
            252.0,
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
            252.0,
            126.0,
        ),
        (  # No position autoreorder
            {'status': 'cancelled'},
            (200, 'finished', 'cancelled'),
            None,
            None,
        ),
        (  # No position so it's free
            {'status': 'cancelled', 'cancel': 'paid'},
            (406, 'assigned', 'waiting'),
            None,
            None,
        ),
        (  # No position but dispatch
            {'status': 'cancelled', 'cancel': 'paid', 'origin': 'dispatch'},
            (200, 'finished', 'cancelled'),
            252.0,
            126.0,
        ),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=15))
def test_requestconfirm_failed_paid(
        taxi_protocol,
        recalc_order,
        db,
        load_json,
        mockserver,
        params,
        expected_state,
        user_cost,
        driver_cost,
):
    @mockserver.json_handler('/statistics/v1/metrics/store')
    def mock_metrics_store(request):
        return {}

    recalc_order.set_user_recalc_result(user_cost, user_cost)
    recalc_order.set_driver_recalc_result(driver_cost, driver_cost)

    request_params = {
        'orderid': ALIAS_ID,
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

    proc = db.order_proc.find_one(ORDER_ID)
    assert expected_state == (
        response.status_code,
        proc['status'],
        proc['order']['taxi_status'],
    )

    if expected_state == (200, 'finished', 'cancelled'):
        assert proc['status'] == 'finished'
        assert proc['order']['status'] == 'finished'
        assert proc['order']['taxi_status'] == 'cancelled'
        assert proc['order']['cost'] == user_cost
        check_decoupling_prices(proc, user_cost, None, driver_cost, None)
        if user_cost:
            order_commit_common.check_current_prices(
                proc, 'final_cost', user_cost,
            )

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


USER_USUAL_COST_FIXED = 674.0
DRIVER_USUAL_COST_FIXED = 417.0
USER_USUAL_COST_TAX = 5000.0
DRIVER_USUAL_COST_TAX = 234.0


# waiting start time - '2016-12-15T11:33:29+0300'
@pytest.mark.parametrize(
    'ready_for_interact, user_receipt_total, driver_receipt_total,'
    'user_cost, driver_cost, calc_method_taximeter, skip_before',
    [
        # initial fixed_prices - 633 and 317 + paid waiting
        ('2016-12-15T11:30:00+0300', 674.0, 417.0, 634.0, 318.0, False, 0),
        # 1.5 min of waiting with price 9 = 13.1
        # 633 + 13.1 = 646.1 + ceil = 647
        # 317 + 13.1 = 330.1 + ceil = 331
        ('2016-12-15T11:35:00+0300', 674.0, 417.0, 648.0, 332.0, False, 0),
        # full waiting, user 5 mins - 45
        ('2016-12-15T11:50:00+0300', 674.0, 417.0, 674.0, 417.0, False, 0),
        ('2016-12-15T11:30:00+0300', 5000, 234, 4960.0, 135.0, True, 0),
        ('2016-12-15T11:35:00+0300', 5000, 234, 4974.0, 149.0, True, 0),
        ('2016-12-15T11:50:00+0300', 5000, 234, 5000.0, 234.0, True, 0),
        ('2016-12-15T11:37:00+0300', 674.0, 417.0, 666.0, 350.0, False, 0),
        ('2016-12-15T11:37:00+0300', 674.0, 417.0, 639.0, 323.0, False, 180),
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
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.config(CALCULATE_VAT_ON_REQUESTCONFIRM=True)
def test_requestconfirm_limited_paid_waiting(
        ready_for_interact,
        taxi_protocol,
        db,
        mockserver,
        now,
        user_receipt_total,
        driver_receipt_total,
        user_cost,
        driver_cost,
        calc_method_taximeter,
        target_service: str,
        skip_before,
):
    db.order_proc.update(
        {'_id': ORDER_ID}, {'$set': {'order.request.cargo_ref_id': '12345'}},
    )

    @mockserver.json_handler('/statistics/v1/metrics/store')
    def mock_metrics_store(request):
        return {}

    @mockserver.json_handler(f'/{target_service}/v1/claims/driver-changes')
    def _mock_cargo_claims(request):
        return {'action_disabled': False}

    request_params = {
        'orderid': ALIAS_ID,
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
        'extra': str(user_receipt_total),
        'calc_method': 1 if calc_method_taximeter else 2,
        'is_captcha': True,
        'is_airplanemode': False,
        'is_offline': True,
        'driver_status': 'free',
        'receipt': {
            'area_ids': {'ufa': 'f2313a01f2b14ae883147cce1b34eb36'},
            'areas': ['ufa'],
            'calc_method': 1 if calc_method_taximeter else 2,
            'calc_total': 157.0,
            'details': [
                {
                    'meter_type': 'time',
                    'meter_value': 240,
                    'price': 9,
                    'service_type': 'waiting',
                    'skip_before': skip_before,
                    'sum': USER_WAITING_PRICE,
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
            'total': user_receipt_total,
            'total_distance': 10703.691472337661,
            'total_duration': 1283.0,
            'transfer': False,
            'version': '8.35 (290)',
        },
        'driver_calc_receipt_overrides': {
            'calc_method': 1 if calc_method_taximeter else 2,
            'details': [
                {
                    'meter_type': 'time',
                    'meter_value': 300,
                    'price': 9,
                    'skip_before': skip_before,
                    'service_type': 'waiting',
                    'sum': DRIVER_WAITING_PRICE,
                    'zone_names': ['moscow'],
                },
            ],
            'transfer': False,
            'min_price': 100,
            'tariff_id': 'bae9c9f06203403aa892122e0d255a36',
            'total': driver_receipt_total,
            'total_distance': 8709.048311380839,
            'total_duration': 225,
        },
    }

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one(ORDER_ID)

    if calc_method_taximeter:
        order_cost = USER_USUAL_COST_TAX
        taximeter_cost = DRIVER_USUAL_COST_TAX
    else:
        order_cost = USER_USUAL_COST_FIXED
        taximeter_cost = DRIVER_USUAL_COST_FIXED

    assert proc['order']['cost'] == order_cost
    assert proc['order']['calc_total'] == 157
    data = response.json()
    assert data == {
        'taximeter_cost': taximeter_cost,
        'phone_options': [],
        'final_cost': {
            'driver': driver_receipt_total,
            'user': user_receipt_total,
        },
    }
    check_decoupling_prices(proc, order_cost, None, taximeter_cost, None)
    order_commit_common.check_current_prices(proc, 'final_cost', order_cost)


REQUEST_WITHOUT_SKIP_BEFORE = {
    'orderid': ALIAS_ID,
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
    'extra': '674',
    'calc_method': 2,
    'is_captcha': True,
    'is_airplanemode': False,
    'is_offline': True,
    'driver_status': 'free',
    'receipt': {
        'area_ids': {'ufa': 'f2313a01f2b14ae883147cce1b34eb36'},
        'areas': ['ufa'],
        'calc_method': 2,
        'calc_total': 157.0,
        'details': [
            {
                'meter_type': 'time',
                'meter_value': 240,
                'price': 9,
                'service_type': 'waiting',
                'sum': USER_WAITING_PRICE,
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
        'total': 674.0,
        'total_distance': 10703.691472337661,
        'total_duration': 1283.0,
        'transfer': False,
        'version': '8.35 (290)',
    },
    'driver_calc_receipt_overrides': {
        'calc_method': 2,
        'details': [
            {
                'meter_type': 'time',
                'meter_value': 300,
                'price': 9,
                'service_type': 'waiting',
                'sum': DRIVER_WAITING_PRICE,
                'zone_names': ['moscow'],
            },
        ],
        'transfer': False,
        'min_price': 100,
        'tariff_id': 'bae9c9f06203403aa892122e0d255a36',
        'total': 417,
        'total_distance': 8709.048311380839,
        'total_duration': 225,
    },
}

REQUEST_WITHOUT_RECEIPT = {
    'orderid': ALIAS_ID,
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
    'extra': '633',
    'calc_method': 2,
    'is_captcha': True,
    'is_airplanemode': False,
    'is_offline': True,
    'driver_status': 'free',
    'origin': 'dispatch',
}


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
@pytest.mark.parametrize(
    'request_params, order_cost, driver_cost',
    [
        (REQUEST_WITHOUT_SKIP_BEFORE, 674.0, 417.0),
        (REQUEST_WITHOUT_RECEIPT, 633.0, 317.0),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.config(CALCULATE_VAT_ON_REQUESTCONFIRM=True)
def test_requestconfirm_limited_paid_waiting_custom_request(
        taxi_protocol,
        db,
        mockserver,
        now,
        config,
        target_service: str,
        request_params,
        order_cost,
        driver_cost,
):
    @mockserver.json_handler(
        f'/{target_service}/v1/claims/points-ready-status',
    )
    def mock_points_status(request):
        return {
            'ready_points': [
                {'point_id': '62145', 'ready_ts': '2016-12-15T11:30:00+0300'},
            ],
        }

    db.order_proc.update(
        {'_id': ORDER_ID}, {'$set': {'order.request.cargo_ref_id': '12345'}},
    )

    @mockserver.json_handler('/statistics/v1/metrics/store')
    def mock_metrics_store(request):
        return {}

    @mockserver.json_handler(f'/{target_service}/v1/claims/driver-changes')
    def _mock_cargo_claims(request):
        return {'action_disabled': False}

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200

    proc = db.order_proc.find_one(ORDER_ID)

    assert proc['order']['cost'] == order_cost
    data = response.json()
    assert data == {
        'taximeter_cost': driver_cost,
        'phone_options': [],
        'final_cost': {'driver': driver_cost, 'user': order_cost},
    }
    check_decoupling_prices(proc, order_cost, None, driver_cost, None)
    order_commit_common.check_current_prices(proc, 'final_cost', order_cost)
