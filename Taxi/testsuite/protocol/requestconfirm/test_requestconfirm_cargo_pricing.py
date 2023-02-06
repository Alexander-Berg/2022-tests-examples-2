import json

import pytest


ORDER_ID = '1c83b49edb274ce0992f337061047375'
ALIAS_ID = 'db60d02916ae4a1a91eafa3a1a8ed04d'


def check_decoupling_prices(proc, user_cost, driver_cost):
    if user_cost == 0.0:
        user_cost = None
    assert proc['order'].get('cost') == user_cost
    assert (
        proc['order']['decoupling']['user_price_info'].get('cost') == user_cost
    )
    assert (
        proc['order']['decoupling']['driver_price_info'].get('cost')
        == driver_cost
    )


@pytest.mark.config(CARGO_ORDERS_CALC_PRICE_ON_SERVER=True)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.parametrize(
    [
        'cargo_orders_response',
        'expected_price_replacement',
        'expected_response',
        'expected_calc_info',
        'origin',
    ],
    [
        (  # 0
            {
                'is_cargo_pricing': True,
                'order_info': {
                    'destination': {
                        'point': [37.5, 55.7],
                        'address': 'My address is 37.5, 55.7',
                    },
                    'source': {
                        'point': [36.5, 54.7],
                        'address': 'My address is 36.5, 54.7',
                    },
                    'total_duration': 4000.0,
                },
                'receipt': {
                    'total': 1002.0,
                    'total_distance': 1003.0,
                    'waiting': {'sum': 107.0, 'time': 18.0, 'cost': 19.0},
                    'waiting_in_transit': {
                        'sum': 104.0,
                        'time': 15.0,
                        'cost': 16.0,
                    },
                    'services': [
                        {
                            'name': 'door_to_door',
                            'count': 3,
                            'sum': 150.0,
                            'price': 450.0,
                        },
                    ],
                },
                'client_total_price': 123.1,
                'some_unknown_key': 'some_unknown_key',
            },
            True,
            {
                'taximeter_cost': 1002.0,
                'cargo_pricing_receipt': {
                    'total': 1002.0,
                    'total_distance': 1003.0,
                    'waiting': {'sum': 107.0, 'time': 18.0, 'cost': 19.0},
                    'waiting_in_transit': {
                        'sum': 104.0,
                        'time': 15.0,
                        'cost': 16.0,
                    },
                    'services': [
                        {
                            # https://github.yandex-team.ru/taxi/uservices/blob/43806859e33643f4c81ce066fcbcaa6a14232861/services/driver-orders/src/models/parks/orders/bulk_retrieve/receipt.cpp#L73
                            'name': 'door_to_door',
                            'count': 3,
                            'sum': 150.0,
                            'price': 450.0,
                        },
                    ],
                },
                'phone_options': [],
                'final_cost': {
                    # from cargo_orders_response.receipt.total
                    'driver': 1002.0,
                    # from cargo_orders_response.client_total_price
                    'user': 123.1,
                },
            },
            True,
            'driver',
        ),
        (  # 1
            {
                'is_cargo_pricing': True,
                'order_info': {
                    'destination': {
                        'point': [37.5, 55.7],
                        'address': 'My address is 37.5, 55.7',
                    },
                    'source': {
                        'point': [36.5, 54.7],
                        'address': 'My address is 36.5, 54.7',
                    },
                    'total_duration': 4000.0,
                },
                'receipt': {
                    'total': 1002.0,
                    'total_distance': 1003.0,
                    'waiting': {'sum': 107.0, 'time': 18.0, 'cost': 19.0},
                    'waiting_in_transit': {
                        'sum': 104.0,
                        'time': 15.0,
                        'cost': 16.0,
                    },
                    'services': [
                        {
                            'name': 'door_to_door',
                            'count': 3,
                            'sum': 150.0,
                            'price': 450.0,
                        },
                    ],
                },
                'client_total_price': 123.1,
                'some_unknown_key': 'some_unknown_key',
            },
            True,
            {
                'taximeter_cost': 1002.0,
                'cargo_pricing_receipt': {
                    'total': 1002.0,
                    'total_distance': 1003.0,
                    'waiting': {'sum': 107.0, 'time': 18.0, 'cost': 19.0},
                    'waiting_in_transit': {
                        'sum': 104.0,
                        'time': 15.0,
                        'cost': 16.0,
                    },
                    'services': [
                        {
                            # https://github.yandex-team.ru/taxi/uservices/blob/43806859e33643f4c81ce066fcbcaa6a14232861/services/driver-orders/src/models/parks/orders/bulk_retrieve/receipt.cpp#L73
                            'name': 'door_to_door',
                            'count': 3,
                            'sum': 150.0,
                            'price': 450.0,
                        },
                    ],
                },
                'phone_options': [],
                'final_cost': {
                    # from cargo_orders_response.receipt.total
                    'driver': 1002.0,
                    # from cargo_orders_response.client_total_price
                    'user': 123.1,
                },
            },
            True,
            'dispatch',
        ),
        (  # 2
            {
                'is_cargo_pricing': False,
                'receipt': {'total': 1002.0, 'total_distance': 1003.0},
            },
            False,
            {
                'phone_options': [],
                'taximeter_cost': 317.0,
                'final_cost': {
                    # from order.decoupling.driver_price_info.fixed_price
                    'driver': 317.0,
                    # from `extra`
                    'user': 5000.0,
                },
            },
            False,
            'driver',
        ),
        (  # 3
            {
                'is_cargo_pricing': False,
                'receipt': {'total': 1002.0, 'total_distance': 1003.0},
            },
            False,
            {
                'phone_options': [],
                'taximeter_cost': 317.0,
                'final_cost': {
                    # from order.decoupling.driver_price_info.fixed_price
                    'driver': 317.0,
                    # from order.decoupling.user_price_info.fixed_price
                    'user': 633.0,
                },
            },
            False,
            'dispatch',
        ),
        (  # 4
            {
                'is_cargo_pricing': True,
                'receipt': {'total': 1002.0, 'total_distance': 1003.0},
                'order_info': {
                    'destination': {
                        'point': [37.5, 55.7],
                        'address': 'My address is 37.5, 55.7',
                    },
                    'source': {
                        'point': [36.5, 54.7],
                        'address': 'My address is 36.5, 54.7',
                    },
                    'total_duration': 4000.0,
                },
            },
            True,
            {
                'taximeter_cost': 1002.0,
                'cargo_pricing_receipt': {
                    'total': 1002.0,
                    'total_distance': 1003.0,
                },
                'phone_options': [],
                'final_cost': {
                    # from cargo_orders_response.receipt.total
                    'driver': 1002.0,
                    # from cargo_orders_response.receipt.total
                    'user': 1002.0,
                },
            },
            False,
            'driver',
        ),
        (  # 5
            {
                'is_cargo_pricing': True,
                'receipt': {'total': 1002.0, 'total_distance': 1003.0},
                'order_info': {
                    'destination': {
                        'point': [37.5, 55.7],
                        'address': 'My address is 37.5, 55.7',
                    },
                    'source': {
                        'point': [36.5, 54.7],
                        'address': 'My address is 36.5, 54.7',
                    },
                    'total_duration': 4000.0,
                },
            },
            True,
            {
                'taximeter_cost': 1002.0,
                'cargo_pricing_receipt': {
                    'total': 1002.0,
                    'total_distance': 1003.0,
                },
                'phone_options': [],
                'final_cost': {
                    # from cargo_orders_response.receipt.total
                    'driver': 1002.0,
                    # from cargo_orders_response.receipt.total
                    'user': 1002.0,
                },
            },
            False,
            'dispatch',
        ),
        (  # 6
            {'is_cargo_pricing': True},
            False,
            {
                'phone_options': [],
                'taximeter_cost': 317.0,
                'final_cost': {
                    # from order.decoupling.driver_price_info.fixed_price
                    'driver': 317.0,
                    # from `extra`
                    'user': 5000.0,
                },
            },
            False,
            'driver',
        ),
        (  # 7
            {'is_cargo_pricing': True},
            False,
            {
                'phone_options': [],
                'taximeter_cost': 317.0,
                'final_cost': {
                    # from order.decoupling.driver_price_info.fixed_price
                    'driver': 317.0,
                    # from order.decoupling.user_price_info.fixed_price
                    'user': 633.0,
                },
            },
            False,
            'dispatch',
        ),
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
def test_base(
        mockserver,
        taxi_protocol,
        db,
        cargo_orders_response,
        expected_price_replacement,
        expected_response,
        expected_calc_info,
        target_service: str,
        origin,
):
    @mockserver.json_handler(f'/{target_service}/v1/claims/driver-changes')
    def _mock_cargo_claims(request):
        return {'action_disabled': False}

    @mockserver.json_handler('/cargo_orders/v1/calc-price')
    def _mock_calc_price(request):
        assert json.loads(request.get_data()) == {
            'cargo_ref_id': '2982034d68ed48dd8cdcd2bdb68e227c',
            'order_id': '1c83b49edb274ce0992f337061047375',
            'tariff_class': 'econom',
            'status': 'complete',
            'taxi_status': 'waiting',
            'driver_id': 'a5709ce56c2740d9a536650f5390de0b',
            'user_id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'is_usage_confirmed': True,
            'taximeter_cost': 5000.0,
            'source_type': 'requestconfirm',
        }
        return mockserver.make_response(
            status=200, response=json.dumps(cargo_orders_response),
        )

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
        'origin': origin,
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
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200
    assert response.json() == expected_response

    proc = db.order_proc.find_one(ORDER_ID)
    if expected_price_replacement:
        assert proc['order']['calc_method'] == 'fixed'
        assert proc['order']['calc_total'] == 1002.0
        if expected_calc_info:
            assert proc['order']['calc_info'] == {
                'waiting_cost': 107.0,
                'waiting_time': 18.0,
            }
            assert proc['order']['driver_calc_info'] == {
                'waiting_cost': 107.0,
                'waiting_time': 18.0,
            }
    else:
        assert proc['order']['calc_method'] == 'order-cost'
        assert 'calc_info' not in proc['order']
        assert 'driver_calc_info' not in proc['order']
        assert 'calc_total' not in proc['order']
        check_decoupling_prices(
            proc,
            expected_response['final_cost']['user'],
            expected_response['final_cost']['driver'],
        )
    if origin == 'driver':
        assert 'disp_cost' not in proc['order']
    elif origin == 'dispatch':
        disp_cost = proc['order']['disp_cost']
        assert disp_cost is not None
        assert disp_cost['disp_cost'] == 5000
        assert disp_cost['taximeter_cost'] == (
            expected_response['final_cost']['driver']
        )
        assert disp_cost['operator_login'] == 'disp_login'
        assert disp_cost['use_recommended_cost'] is True


@pytest.mark.parametrize(
    ['cargo_orders_response', 'expected_response'],
    [
        (
            {
                'is_cargo_pricing': True,
                'order_info': {
                    'destination': {'point': [37.5, 55.7]},
                    'source': {'point': [36.5, 54.7]},
                },
                'receipt': {
                    'total': 1002.0,
                    'total_distance': 1003.0,
                    'waiting': {'sum': 107.0, 'time': 18.0, 'cost': 19.0},
                    'waiting_in_transit': {
                        'sum': 104.0,
                        'time': 15.0,
                        'cost': 16.0,
                    },
                    'services': [
                        {
                            'name': 'door_to_door',
                            'count': 3,
                            'sum': 150.0,
                            'price': 450.0,
                        },
                    ],
                },
            },
            {
                'taximeter_cost': 1002.0,
                'cargo_pricing_receipt': {
                    'total': 1002.0,
                    'total_distance': 1003.0,
                    'waiting': {'sum': 107.0, 'time': 18.0, 'cost': 19.0},
                    'waiting_in_transit': {
                        'sum': 104.0,
                        'time': 15.0,
                        'cost': 16.0,
                    },
                    'services': [
                        {
                            # https://github.yandex-team.ru/taxi/uservices/blob/43806859e33643f4c81ce066fcbcaa6a14232861/services/driver-orders/src/models/parks/orders/bulk_retrieve/receipt.cpp#L73
                            'name': 'door_to_door',
                            'count': 3,
                            'sum': 150.0,
                            'price': 450.0,
                        },
                    ],
                },
                'phone_options': [],
                'final_cost': {
                    # from cargo_orders_response.receipt.total
                    'driver': 1002.0,
                    # from cargo_orders_response.receipt.total
                    'user': 1002.0,
                },
            },
        ),
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
@pytest.mark.config(CARGO_ORDERS_CALC_PRICE_ON_SERVER=True)
def test_base_with_receipt(
        mockserver,
        taxi_protocol,
        db,
        cargo_orders_response,
        expected_response,
        target_service: str,
):
    @mockserver.json_handler(f'/{target_service}/v1/claims/driver-changes')
    def _mock_cargo_claims(request):
        return {'action_disabled': False}

    @mockserver.json_handler('/cargo_orders/v1/calc-price')
    def _mock_calc_price(request):
        assert json.loads(request.get_data()) == {
            'cargo_ref_id': '2982034d68ed48dd8cdcd2bdb68e227c',
            'order_id': '1c83b49edb274ce0992f337061047375',
            'tariff_class': 'econom',
            'status': 'complete',
            'taxi_status': 'waiting',
            'driver_id': 'a5709ce56c2740d9a536650f5390de0b',
            'user_id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'is_usage_confirmed': True,
            'taximeter_cost': 5000.0,
            'source_type': 'requestconfirm',
        }
        return mockserver.make_response(
            status=200, response=json.dumps(cargo_orders_response),
        )

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
        'extra': '5000',
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
            ],
            'transfer': False,
            'min_price': 100,
            'tariff_id': 'bae9c9f06203403aa892122e0d255a36',
            'total': 234,
            'total_distance': 8709.048311380839,
            'total_duration': 225,
        },
    }

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200
    assert response.json() == expected_response

    proc = db.order_proc.find_one(ORDER_ID)

    assert proc['order']['calc_method'] == 'fixed'
    assert proc['order']['calc_total'] == 1002.0
    assert proc['order']['calc_info'] == {
        'waiting_cost': 107.0,
        'waiting_time': 18.0,
    }
    assert proc['order']['driver_calc_info'] == {
        'waiting_cost': 107.0,
        'waiting_time': 18.0,
    }


@pytest.mark.config(
    CARGO_ORDERS_CALC_PRICE_ON_SERVER=True,
    CARGO_PROTOCOL_API_PROXY=True,
    CARGO_ORDERS_ENABLE_CLIENT_TOTAL_PRICE=True,
)
def test_coupon(mockserver, taxi_protocol, db):
    final_cost_driver_meta = {'key1': 100.0, 'key2': 200.0}
    final_cost_user_meta = {'key3': 100.0, 'key4': 200.0}

    @mockserver.json_handler('/api-proxy/v1/claims/driver-changes')
    def _mock_cargo_claims(request):
        return {'action_disabled': False}

    @mockserver.json_handler('/cargo_orders/v1/calc-price')
    def _mock_calc_price(request):
        return mockserver.make_response(
            status=200,
            response=json.dumps(
                {
                    'is_cargo_pricing': True,
                    'order_info': {
                        'destination': {'point': [37.5, 55.7]},
                        'source': {'point': [36.5, 54.7]},
                    },
                    'receipt': {
                        'total': 1002.0,
                        'total_distance': 1003.0,
                        'waiting': {'sum': 107.0, 'time': 18.0, 'cost': 19.0},
                        'waiting_in_transit': {
                            'sum': 104.0,
                            'time': 15.0,
                            'cost': 16.0,
                        },
                        'services': [
                            {
                                'name': 'door_to_door',
                                'count': 3,
                                'sum': 150.0,
                                'price': 450.0,
                            },
                        ],
                    },
                    'client_total_price': 500.0,
                    'recalc_taxi_pricing_response': {
                        'driver': {'meta': final_cost_driver_meta},
                        'user': {'meta': final_cost_user_meta},
                    },
                    'price_extra_info': {
                        'coupon': {'coupon': 'value123', 'was_applied': True},
                    },
                },
            ),
        )

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
        'extra': '5000',
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
            ],
            'transfer': False,
            'min_price': 100,
            'tariff_id': 'bae9c9f06203403aa892122e0d255a36',
            'total': 234,
            'total_distance': 8709.048311380839,
            'total_duration': 225,
        },
    }

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 200
    assert response.json() == {
        'taximeter_cost': 1002.0,
        'cargo_pricing_receipt': {
            'total': 1002.0,
            'total_distance': 1003.0,
            'waiting': {'sum': 107.0, 'time': 18.0, 'cost': 19.0},
            'waiting_in_transit': {'sum': 104.0, 'time': 15.0, 'cost': 16.0},
            'services': [
                {
                    'name': 'door_to_door',
                    'count': 3,
                    'sum': 150.0,
                    'price': 450.0,
                },
            ],
        },
        'phone_options': [],
        'final_cost': {
            # from cargo_orders_response.receipt.total
            'driver': 1002.0,
            # from cargo_orders_response.client_total_price
            'user': 500.0,
        },
    }

    proc = db.order_proc.find_one(ORDER_ID)

    assert proc['order']['calc_method'] == 'fixed'
    assert proc['order']['calc_total'] == 1002.0
    assert proc['order']['calc_info'] == {
        'waiting_cost': 107.0,
        'waiting_time': 18.0,
    }
    assert proc['order']['driver_calc_info'] == {
        'waiting_cost': 107.0,
        'waiting_time': 18.0,
    }
    assert proc['order']['cost'] == 500.0
    assert proc['order']['driver_cost']['cost'] == 1002.0
    assert proc['order']['driver_cost']['calc_method'] == 'fixed'
    assert proc['order']['current_prices']['kind'] == 'final_cost'
    assert proc['order']['current_prices']['final_cost_meta'] == {
        'driver': final_cost_driver_meta,
        'user': final_cost_user_meta,
    }
    assert proc['order']['coupon']['was_used']


@pytest.mark.config(
    CARGO_ORDERS_CALC_PRICE_ON_SERVER=True,
    CARGO_PROTOCOL_API_PROXY=True,
    CARGO_ORDERS_ENABLE_CLIENT_TOTAL_PRICE=True,
    CARGO_ORDERS_ENABLE_REQUIRED_REQUESTCONFIRM_FOR_C2C=True,
)
def test_required_requestconfirm(mockserver, taxi_protocol, db):
    @mockserver.json_handler('/api-proxy/v1/claims/driver-changes')
    def _mock_cargo_claims(request):
        return {'action_disabled': False}

    @mockserver.json_handler('/cargo_orders/v1/calc-price')
    def _mock_calc_price(request):
        return mockserver.make_response(status=500)

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
        'extra': '5000',
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
            ],
            'transfer': False,
            'min_price': 100,
            'tariff_id': 'bae9c9f06203403aa892122e0d255a36',
            'total': 234,
            'total_distance': 8709.048311380839,
            'total_duration': 225,
        },
    }

    db.order_proc.update(
        {'_id': '1c83b49edb274ce0992f337061047375'},
        {
            '$set': {
                'order.request.payment': {
                    'payment_method_id': 'card-1234',
                    'type': 'card',
                },
                'payment_tech': {
                    'last_known_ip': '2a02:6b8:0:402:8850:5abc:ec62:2fb5',
                    'main_card_billing_id': None,
                    'main_card_payment_id': None,
                    'payment_method_id': 'card-1234',
                    'type': 'card',
                },
            },
        },
    )

    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'
    uri = '1.x/requestconfirm?clid=999012&apikey=' + apikey
    response = taxi_protocol.post(uri, request_params)
    assert response.status_code == 500
