import copy

import pytest

from tests_cargo_pricing import utils


async def test_first_calc(
        v1_calc_creator, user_options, taxi_cargo_pricing_monitor,
):
    stats_before_calc = await taxi_cargo_pricing_monitor.get_metric(
        'cargo_pricing__taxi__categories_count',
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    resp = response.json()

    assert resp.pop('calc_id').startswith('cargo-pricing/v1/')
    assert (
        resp.pop('taxi_pricing_response')
        == v1_calc_creator.mock_prepare.categories['cargocorp']
    )
    expected_recalc_resp = copy.deepcopy(
        v1_calc_creator.mock_recalc.response['price'],
    )
    expected_recalc_resp['driver']['additional_payloads'].pop('route_parts')
    expected_recalc_resp['user']['additional_payloads'].pop('route_parts')
    assert resp.pop('recalc_taxi_pricing_response') == expected_recalc_resp

    assert resp == {
        'taxi_pricing_response_parts': {
            'taximeter_meta': {
                'max_distance_from_b': 501.0,
                'show_price_in_taximeter': False,
            },
        },
        'details': {
            'pricing_case': 'default',
            'pricing_case_reason': 'is_not_cancelled',
            'currency_code': 'RUB',
            'boarding_price': '20',
            'minimum_price': '20',
            'total_distance': '7082.175781',
            'total_distance_price': '30',
            'total_time': '2154',
            'total_time_price': '9',
            'paid_waiting_in_destination_price': '0',
            'paid_waiting_in_destination_time': '30',
            'paid_waiting_in_destination_total_price': '2',
            'paid_waiting_in_transit_price': '0',
            'paid_waiting_in_transit_time': '0',
            'paid_waiting_price': '0',
            'paid_waiting_time': '60',
            'paid_waiting_total_price': '1',
            'total_surge_price': '13',
            'discount_price': '0',
            'coupon_price': '0',
            'paid_supply_price': '0',
            'requirements': [
                {
                    'count': 1,
                    'included': 0,
                    'name': 'door_to_door',
                    'price_per_unit': '15',
                    'text_keyset': 'tariff',
                    'text_tanker_key': 'service.door_to_door',
                    'total_price': '15',
                },
            ],
            'route_parts': [
                {
                    'area': {'destination': 'dme', 'source': 'moscow'},
                    'distance': {'meters': 22.7, 'price': 24.8},
                    'time': {'seconds': 21.0, 'price': 23.0},
                },
            ],
            'tariff_ref': {
                'category_id': 'user_category_id',
                'category_name': 'cargocorp',
                'tariff_id': 'user_tariff_id',
            },
            'waypoints': [
                {
                    'first_time_arrived_at': '2020-01-01T00:00:00+00:00',
                    'position': [37.6489887, 55.5737046],
                    'resolution_info': {
                        'resolution': 'delivered',
                        'resolved_at': '2020-01-01T00:11:00+00:00',
                    },
                    'route': {
                        'distance_from_start': '0',
                        'time_from_start': '0',
                    },
                    'type': 'pickup',
                    'waiting': {
                        'finish_ts': '2020-01-01T00:11:00+00:00',
                        'free_waiting_time': '600',
                        'paid_waiting': '60',
                        'paid_waiting_disabled': False,
                        'real_performer_waiting': '660',
                        'start_ts': '2020-01-01T00:00:00+00:00',
                        'total_waiting': '660',
                        'was_limited': False,
                    },
                    'cargo_items': [],
                    'merged_points_number': 1,
                },
                {
                    'first_time_arrived_at': '2020-01-01T00:11:30+00:00',
                    'position': [37.5447415, 55.9061769],
                    'resolution_info': {
                        'resolution': 'delivered',
                        'resolved_at': '2020-01-01T00:22:00+00:00',
                    },
                    'route': {
                        'distance_from_start': '3541.087891',
                        'time_from_start': '1077',
                    },
                    'type': 'dropoff',
                    'waiting': {
                        'finish_ts': '2020-01-01T00:22:00+00:00',
                        'free_waiting_time': '600',
                        'paid_waiting': '30',
                        'paid_waiting_disabled': False,
                        'real_performer_waiting': '630',
                        'start_ts': '2020-01-01T00:11:30+00:00',
                        'total_waiting': '630',
                        'was_limited': False,
                    },
                    'cargo_items': [],
                    'merged_points_number': 1,
                },
                {
                    'first_time_arrived_at': '2020-01-01T00:22:00+00:00',
                    'position': [37.6489887, 55.5737046],
                    'resolution_info': {
                        'resolution': 'delivered',
                        'resolved_at': '2020-01-01T00:23:00+00:00',
                    },
                    'route': {
                        'distance_from_start': '7082.175782',
                        'time_from_start': '2154',
                    },
                    'type': 'return',
                    'waiting': {
                        'finish_ts': '2020-01-01T00:23:00+00:00',
                        'free_waiting_time': '600',
                        'paid_waiting': '0',
                        'paid_waiting_disabled': False,
                        'real_performer_waiting': '60',
                        'start_ts': '2020-01-01T00:22:00+00:00',
                        'total_waiting': '60',
                        'was_limited': False,
                    },
                    'cargo_items': [],
                    'merged_points_number': 1,
                },
            ],
        },
        'price': '300',
        'units': {
            'currency': 'RUB',
            'distance': 'kilometer',
            'time': 'minute',
        },
        'services': [
            {
                'components': [
                    {
                        'name': 'boarding',
                        'text': 'Цена подачи',
                        'total_price': '20',
                    },
                    {
                        'name': 'time',
                        'quantity': {'duration': 2154, 'type': 'time'},
                        'text': 'Плата за расчетное время в пути',
                        'total_price': '9',
                    },
                    {
                        'name': 'distance',
                        'quantity': {
                            'total_distance': 7082,
                            'type': 'distance',
                        },
                        'text': 'Плата за расчетный километраж пути',
                        'total_price': '30',
                    },
                ],
                'name': 'base_price',
                'text': 'Базовая цена',
                'total_price': '59',
            },
            {
                'components': [
                    {
                        'name': 'paid_waiting',
                        'quantity': {'duration': 60, 'type': 'time'},
                        'text': 'Платное ожидание в точке получения посылки',
                        'total_price': '1',
                    },
                    {
                        'name': 'paid_waiting_in_destination',
                        'quantity': {'duration': 30, 'type': 'time'},
                        'text': 'Платное ожидание в точке вручения посылки',
                        'total_price': '2',
                    },
                ],
                'name': 'paid_waiting',
                'text': 'Платные ожидания',
                'total_price': '3',
            },
            {
                'components': [
                    {
                        'name': 'surge',
                        'text': 'Повышенный спрос',
                        'total_price': '13',
                    },
                ],
                'name': 'surcharge',
                'text': 'Доплата к стоимости',
                'total_price': '13',
            },
            {
                'components': [
                    {
                        'name': 'door_to_door',
                        'quantity': {
                            'count': 1,
                            'included': 0,
                            'price_per_unit': '15',
                            'type': 'count',
                        },
                        'text': 'От двери до двери',
                        'total_price': '15',
                    },
                ],
                'name': 'requirements',
                'text': 'Требования',
                'total_price': '15',
            },
        ],
    }

    prepare_req = v1_calc_creator.mock_prepare.request
    assert prepare_req == {
        'categories': ['cargocorp'],
        'classes_requirements': {
            'cargocorp': {
                'door_to_door': True,
                'cargo_type': 0,
                'cargo_type_int': 1,
            },
        },
        'tolls': 'DENY',
        'user_info': {
            'application': {
                'name': 'cargo',
                'platform_version': '0.0.0',
                'version': '0.0.0',
            },
            'payment_info': {'method_id': 'corp-xxx', 'type': 'corp'},
            'user_id': 'user_id',
        },
        'waypoints': [
            [37.6489887, 55.5737046],
            [37.5447415, 55.9061769],
            [37.6489887, 55.5737046],
        ],
        'zone': 'moscow',
        'modifications_scope': 'cargo',
        'extra': {
            'providers': {
                'discounts': {'is_enabled': False},
                'router': {'is_fallback': True},
            },
        },
    }

    recalc_req = v1_calc_creator.mock_recalc.request
    recalc_req['user'].pop('backend_variables')
    recalc_req['driver'].pop('backend_variables')

    expected_trip_details = {
        'total_distance': 7082.17578125,
        'total_time': 2154.0,
        'waiting_time': 60.0,
        'waiting_in_transit_time': 0.0,
        'waiting_in_destination_time': 30.0,
        'user_options': user_options,
    }

    assert recalc_req['user'] == {
        'category_prices_id': 'd/5f08c7',
        'modifications': [743, 549],
        'trip_details': expected_trip_details,
    }
    assert recalc_req['driver'] == {
        'category_prices_id': 'c/13330055',
        'modifications': [549, 482],
        'trip_details': expected_trip_details,
    }

    assert recalc_req['trip_info']['geoarea_ids'] == [
        'g/2bab7eff1aa848b681370b2bd83cfbf9',
    ]
    assert recalc_req['additional_payloads'] == {
        'details': 'cargo-pricing/v1/taxi/calc',
        'need_route_parts': False,
    }

    details = resp['details']
    assert round(expected_trip_details['total_distance']) == round(
        float(details['total_distance']),
    )
    assert round(expected_trip_details['total_time']) == round(
        float(details['total_time']),
    )
    stats = await taxi_cargo_pricing_monitor.get_metric(
        'cargo_pricing__taxi__categories_count',
    )
    assert stats['cargocorp'] - stats_before_calc['cargocorp'] == 1


async def test_calc_with_previous_calc_id(
        v1_calc_creator, get_cached_edges, mock_route,
):
    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert v1_calc_creator.mock_prepare.mock.times_called == 1
    assert mock_route.mock.times_called == 2

    res = await get_cached_edges()
    assert len(res['path']) == 44

    second_response = await utils.calc_with_previous_calc_id(
        v1_calc_creator, prev_calc_id=response.json()['calc_id'],
    )
    assert second_response.status_code == 200
    assert v1_calc_creator.mock_prepare.mock.times_called == 1
    assert mock_route.mock.times_called == 2


async def test_recalc_details(v1_calc_creator, get_cached_edges, mock_route):
    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    calc_resp = response.json()

    second_response = await utils.calc_with_previous_calc_id(
        v1_calc_creator, prev_calc_id=response.json()['calc_id'],
    )
    assert second_response.status_code == 200
    recalc_resp = second_response.json()
    # same requests, same clients responses, so result have to be the same
    assert calc_resp['details'] == recalc_resp['details']


async def test_route_choose(v1_calc_creator, setup_fallback_router):
    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    recalc_req = v1_calc_creator.mock_recalc.request
    # Fallback router doesn't add intermediate points
    # 3 route points = 2 edges (А-B + B-C) = 4 path points (А, B, B, C)
    # If `max_distance_between_waypoints` is miscalculated  this assert
    # will fail (see setup_fallback_router)
    assert len(recalc_req['trip_info']['route']) == 4


async def test_router_settings(v1_calc_creator, experiments3):
    experiments3.add_config(
        consumers=['cargo-pricing/v1/taxi/calc'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        name='cargo_pricing_detect_router',
        default_value={'type': 'car', 'tolls': 'no_tolls'},
    )
    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    coords = v1_calc_creator.mock_router.request.pop('rll')
    assert '37.544742,55.906177' in coords and '37.648989,55.573705' in coords
    assert v1_calc_creator.mock_router.request == {
        'avoid': 'tolls',
        'intent': 'ROUTESTATS',
        'features': 'geometry',
        'lang': 'ru-RU',
        'mode': 'approx',
        'origin': 'yataxi',
        'user_id': 'user_id',
        'vehicle_type': 'taxi',
    }


async def test_calc_with_missing_arriving_fallback(
        v1_calc_creator, setup_fallback_router, user_options,
):

    for waypoint in v1_calc_creator.payload['waypoints']:
        waypoint['first_time_arrived_at'] = None

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    recalc_req = v1_calc_creator.mock_recalc.request
    # every point is included in recalc request

    # If `max_distance_between_waypoints` is miscalculated  this assert
    # will fail (see setup_fallback_router)
    assert len(recalc_req['trip_info']['route']) == 4
    # however we lost waiting time
    user_trip_details = recalc_req['user']['trip_details']
    driver_trip_details = recalc_req['driver']['trip_details']
    assert (
        user_trip_details['waiting_time']
        == driver_trip_details['waiting_time']
        == 0
    )
    assert (
        user_trip_details['waiting_in_transit_time']
        == driver_trip_details['waiting_in_transit_time']
        == 0
    )
    assert (
        user_trip_details['waiting_in_destination_time']
        == driver_trip_details['waiting_in_destination_time']
        == 0
    )


async def test_calc_with_cargo_middle_points_cargo_int(v1_calc_creator):
    v1_calc_creator.payload['taxi_requirements']['cargo_loaders'] = 2
    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    prepare_req = v1_calc_creator.mock_prepare.request
    assert prepare_req['classes_requirements'] == {
        'cargocorp': {
            'cargo_loaders': 2,
            'door_to_door': True,
            'cargo_type': 0,
            'cargo_type_int': 1,
        },
    }
    recalc_req = v1_calc_creator.mock_recalc.request
    assert (
        recalc_req['user']['trip_details']['user_options'][
            'fake_middle_point_cargocorp_van.two_loaders_point'
        ]
        == recalc_req['driver']['trip_details']['user_options'][
            'fake_middle_point_cargocorp_van.two_loaders_point'
        ]
        == 2
    )


async def test_calc_with_middle_points_as_options(v1_calc_creator):
    v1_calc_creator.payload['taxi_requirements'].pop('cargo_type')
    v1_calc_creator.payload['taxi_requirements']['cargo_type_int'] = 1
    v1_calc_creator.payload['taxi_requirements']['cargo_loaders'] = 2
    v1_calc_creator.payload['fake_middle_point_express'] = [1, 1, 1]
    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    prepare_req = v1_calc_creator.mock_prepare.request
    assert prepare_req['classes_requirements'] == {
        'cargocorp': {
            'cargo_loaders': 2,
            'door_to_door': True,
            'cargo_type_int': 1,
        },
    }
    recalc_req = v1_calc_creator.mock_recalc.request
    assert (
        recalc_req['user']['trip_details']['user_options'][
            'fake_middle_point_cargocorp_van.two_loaders_point'
        ]
        == recalc_req['driver']['trip_details']['user_options'][
            'fake_middle_point_cargocorp_van.two_loaders_point'
        ]
        == 2
    )


async def test_calc_with_one_point(v1_calc_creator):
    for waypoint in v1_calc_creator.payload['waypoints'][1:]:
        waypoint['first_time_arrived_at'] = None
        waypoint['resolution_info'] = None

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    recalc_req = v1_calc_creator.mock_recalc.request
    user_fake_middle_points = utils.fake_middle_point_count(
        recalc_req['user']['trip_details']['user_options'],
    )
    driver_fake_middle_points = utils.fake_middle_point_count(
        recalc_req['driver']['trip_details']['user_options'],
    )
    assert user_fake_middle_points == 0
    assert driver_fake_middle_points == 0


async def test_calc_with_tariff_substitution(
        v1_calc_creator, overload_tariff_class,
):
    await overload_tariff_class.execute(new_class='courier_for_performer')
    v1_calc_creator.mock_prepare.categories[
        'courier_for_performer'
    ] = v1_calc_creator.mock_prepare.categories['cargocorp']
    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert v1_calc_creator.mock_prepare.request['categories'] == [
        'courier_for_performer',
    ]


async def test_calc_backend_variables_saving(
        v1_calc_creator, overload_tariff_class,
):
    await overload_tariff_class.execute(new_class='courier')
    v1_calc_creator.mock_prepare.categories[
        'courier'
    ] = v1_calc_creator.mock_prepare.categories['cargocorp']

    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert v1_calc_creator.mock_prepare.request['categories'] == ['courier']
    assert (
        'fake_middle_point_express'
        in v1_calc_creator.mock_recalc.request['user']['trip_details'][
            'user_options'
        ]
    )
    assert (
        'fake_middle_point_express'
        in v1_calc_creator.mock_recalc.request['driver']['trip_details'][
            'user_options'
        ]
    )

    await overload_tariff_class.execute(new_class='cargocorp')

    second_response = await utils.calc_with_previous_calc_id(
        v1_calc_creator, prev_calc_id=response.json()['calc_id'],
    )
    assert second_response.status_code == 200

    assert (
        'fake_middle_point_express'
        in v1_calc_creator.mock_recalc.request['user']['trip_details'][
            'user_options'
        ]
    )
    assert (
        'fake_middle_point_express'
        in v1_calc_creator.mock_recalc.request['driver']['trip_details'][
            'user_options'
        ]
    )


async def test_calc_cant_construct_error(v1_calc_creator, mock_route):
    mock_route.empty_route = True
    response = await v1_calc_creator.execute()
    assert response.status_code == 400
    resp = response.json()
    assert resp == {
        'code': 'cant_construct_route',
        'message': 'Requested route is insoluble',
    }


async def test_calc_tariff_not_found(mockserver, v1_calc_creator):
    v1_calc_creator.mock_prepare.error_response = mockserver.make_response(
        json={
            'code': 'NO_CATEGORIES_MATCHED',
            'message': """No categories matched, tried: [courier_for_performer],
            tariff: moscow""",
        },
        status=400,
    )
    response = await v1_calc_creator.execute()
    assert response.status_code == 400
    resp = response.json()
    assert resp == {
        'code': 'tariff_not_found',
        'message': 'Requested tariff not found',
    }


async def test_calc_bad_requirements(mockserver, v1_calc_creator):
    v1_calc_creator.mock_prepare.error_response = mockserver.make_response(
        json={
            'code': 'BAD_REQUIREMENTS',
            'message': 'Select for non-select requirement',
        },
        status=400,
    )
    response = await v1_calc_creator.execute()
    assert response.status_code == 400
    resp = response.json()
    assert resp == {
        'code': 'bad_requirements',
        'message': 'Select for non-select requirement',
    }


async def test_v1_calc_validation(
        v1_calc_creator, validate_request, mock_route,
):
    v1_calc_creator.payload['waypoints'][0].pop('resolution_info')
    response = await v1_calc_creator.execute()
    assert response.status_code == 400
    resp = response.json()
    assert resp == {
        'code': 'invalid_request',
        'message': 'Missing waypoint resolution in resolved order',
    }

    for waypoint in v1_calc_creator.payload['waypoints']:
        if 'resolution_info' in waypoint:
            waypoint.pop('resolution_info')
    response = await v1_calc_creator.execute()
    assert response.status_code == 200


async def test_limit_paid_waiting(v1_calc_creator, limit_paid_waiting):
    first_point = v1_calc_creator.payload['waypoints'][0]
    first_point['first_time_arrived_at'] = utils.from_start(minutes=0)
    first_point['due'] = utils.from_start(minutes=5)
    first_point['resolution_info'] = {
        'resolution': 'delivered',
        'resolved_at': utils.from_start(minutes=20),
    }

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    recalc_req = v1_calc_creator.mock_recalc.request
    assert (
        recalc_req['user']['trip_details']['waiting_time']
        == recalc_req['driver']['trip_details']['waiting_time']
        == 10.0
    )


async def test_calc_with_idempotency_token(
        v1_calc_creator, get_cached_edges, mock_route,
):
    v1_calc_creator.payload = utils.get_default_calc_request()
    v1_calc_creator.payload['idempotency_token'] = 'idempotency_token_1'
    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    previous_calc_id = response.json()['calc_id']
    assert v1_calc_creator.mock_prepare.mock.times_called == 1
    assert mock_route.mock.times_called == 2

    v1_calc_creator.payload = utils.get_default_calc_request()
    v1_calc_creator.payload['idempotency_token'] = 'idempotency_token_1'

    second_response = await v1_calc_creator.execute()
    assert second_response.status_code == 200

    assert second_response.json()['calc_id'] == previous_calc_id


async def test_calc_with_duplicate_edge(v1_calc_creator, mock_route):
    v1_calc_creator.payload['waypoints'].append(
        v1_calc_creator.payload['waypoints'][-1],
    )
    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert mock_route.mock.times_called == 3
    assert len(v1_calc_creator.payload['waypoints']) == 4


async def test_first_calc_with_coupon_and_discounts(
        v1_calc_creator, user_options, taxi_cargo_pricing_monitor, load_json,
):
    utils.enable_coupon_and_discounts(v1_calc_creator, load_json)
    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    resp = response.json()

    assert resp['price_extra_info'] == {
        'coupon': {'coupon': 'coupon212', 'was_applied': True},
    }
    assert resp['strikeout_price'] == '453'

    prepare_req = v1_calc_creator.mock_prepare.request
    assert prepare_req['user_info']['payment_info'] == {
        'method_id': 'corp-xxx',
        'type': 'corp',
        'coupon': 'coupon212',
    }
    assert prepare_req['extra'] == {
        'providers': {
            'discounts': {'is_enabled': True},
            'router': {'is_fallback': True},
        },
    }
    assert prepare_req['additional_payloads'][
        'need_strikeout_price_modifications'
    ]
    assert prepare_req['calc_additional_prices']['strikeout']

    recalc_req = v1_calc_creator.mock_recalc.request
    assert recalc_req['user']['modifications_for_strikeout_price'] == [1, 2, 3]

    details = resp['details']
    assert details['discount_price'] == '17'
    assert details['coupon_price'] == '153'

    resp_services = resp['services']
    discount_services = [x for x in resp_services if x['name'] == 'discount']
    assert discount_services == [
        {
            'components': [
                {
                    'name': 'discount',
                    'text': 'Вычет по скидке',
                    'total_price': '-17',
                },
            ],
            'name': 'discount',
            'text': 'Скидки',
            'total_price': '-17',
        },
    ]

    coupon_services = [x for x in resp_services if x['name'] == 'coupon']
    assert coupon_services == [
        {
            'components': [
                {
                    'name': 'coupon',
                    'text': 'Вычет по промокоду',
                    'total_price': '-153',
                },
            ],
            'name': 'coupon',
            'text': 'Промокоды',
            'total_price': '-153',
        },
    ]


async def test_calc_with_paid_supply_service(
        v2_calc_creator, user_options, taxi_cargo_pricing_monitor,
):
    user_recalc_response = v2_calc_creator.mock_recalc.response['price'][
        'user'
    ]
    recalc_details = user_recalc_response['additional_payloads']['details']
    recalc_details['services'].append(
        {
            'name': 'paid_supply_price',
            'text': {
                'keyset': 'taximeter_driver_messages',
                'tanker_key': 'paid_supply_price_key',
            },
            'price': 43.7,
        },
    )

    response = await v2_calc_creator.execute()
    assert response.status_code == 200
    assert len(response.json()['calculations']) == 1
    resp = response.json()['calculations'][0]['result']

    assert resp['prices']['paid_supply_price'] == '43.7'

    resp_services = resp['details']['services']
    paid_supply_services = [
        x for x in resp_services if x['name'] == 'paid_supply'
    ]
    assert paid_supply_services == [
        {
            'components': [
                {
                    'name': 'paid_supply',
                    'text': 'Цена платной подачи',
                    'total_price': '43.7',
                },
            ],
            'name': 'paid_supply',
            'text': 'Платная подача',
            'total_price': '43.7',
        },
    ]


async def test_calc_with_previous_calc_id_with_coupon_and_discounts(
        v1_calc_creator, get_cached_edges, mock_route,
):
    v1_calc_creator.payload['discounts_enabled'] = True
    v1_calc_creator.payload['calc_strikeout_price'] = True
    v1_calc_creator.payload['payment_info']['coupon'] = 'coupon212'
    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    previous_calc_id = response.json()['calc_id']
    assert v1_calc_creator.mock_prepare.mock.times_called == 1
    assert mock_route.mock.times_called == 2

    second_payload = utils.get_default_calc_request()
    second_payload['previous_calc_id'] = previous_calc_id
    second_payload['calc_strikeout_price'] = True
    # значения не будут использованы, так как они наследуются из контекста
    second_payload['discounts_enabled'] = False
    second_payload['payment_info']['coupon'] = 'wrong'
    v1_calc_creator.payload = second_payload

    utils.set_v2recalc_resp_discounts(
        v1_calc_creator, coupon_value=132, discount_value=19,
    )

    second_response = await v1_calc_creator.execute()
    assert second_response.status_code == 200
    assert v1_calc_creator.mock_prepare.mock.times_called == 1
    assert mock_route.mock.times_called == 2
    second_resp = second_response.json()
    assert second_resp['price_extra_info'] == {
        'coupon': {'coupon': 'coupon212', 'was_applied': True},
    }
    assert second_resp['strikeout_price'] == '453'

    assert second_resp['details']['discount_price'] == '19'
    assert second_resp['details']['coupon_price'] == '132'


@pytest.mark.yt(
    schemas=[
        'yt/yt_calculations_raw_schema.yaml',
        'yt/yt_receipts_raw_schema.yaml',
    ],
    dyn_table_data=['yt/yt_calculations_raw.yaml', 'yt/yt_receipts_raw.yaml'],
)
@pytest.mark.config(
    CARGO_PRICING_DB_SOURCES_FOR_READ={'v1/taxi/calc': ['pg', 'yt']},
)
@pytest.mark.config(CARGO_PRICING_ENABLE_DECODING_BINARY_FROM_YT=True)
async def test_recalc_with_previous_from_yt(
        taxi_cargo_pricing,
        v1_calc_creator,
        yt_apply,
        pgsql,
        get_cached_edges,
        mock_route,
):
    payload = utils.get_default_calc_request()
    payload[
        'previous_calc_id'
    ] = 'cargo-pricing/v1/731d5f77-8c8b-4ac9-b556-9d38357b92b2'
    waypoints = payload['waypoints']
    waypoints[0]['position'] = [30.255537, 59.85355]
    waypoints[1]['position'] = [30.258196, 59.849202]
    waypoints[2]['position'] = [30.244201, 59.850509]

    v1_calc_creator.payload = payload
    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    resp = response.json()
    assert resp['details']['total_time'] == '186'
    assert resp['details']['total_distance'] == '1300.750275'


async def test_calc_v2recalc_with_paid_supply_and_strikeout_price(
        v1_calc_creator, user_options, taxi_cargo_pricing_monitor, load_json,
):
    # тест не моделирует реальную ситуацию на 100 процентов
    # в реальности мы вызываем:
    #   v1/taxi/calc, v2/taxi/add_paid_supply и v1/taxi/calc
    # здесь мы первые два вызова заменяем прямым патчем ответа v2/prepare
    # TODO убрать этот тест после написания тестов для flow paid_supply
    paid_supply_mod_ids = [11, 22, 33]
    paid_supply_strikeout_mod_ids = [10, 20, 30]
    utils.set_v2prepare_resp_discounts(v1_calc_creator, load_json)
    prepare_resp = v1_calc_creator.mock_prepare.categories['cargocorp']
    prepare_resp['user']['additional_prices']['paid_supply'] = {
        'additional_payloads': {
            'modifications_for_strikeout_price': {
                'for_fixed': paid_supply_strikeout_mod_ids,
                'for_taximeter': [40, 50, 60],
            },
        },
        'modifications': {
            'for_fixed': paid_supply_mod_ids,
            'for_taximeter': [44, 55, 66],
        },
        'price': {'total': 675},
        'meta': {},
    }

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    recalc_req = v1_calc_creator.mock_recalc.request

    assert recalc_req['user']['modifications'] == paid_supply_mod_ids
    assert (
        recalc_req['user']['modifications_for_strikeout_price']
        == paid_supply_strikeout_mod_ids
    )
    assert recalc_req['driver']['modifications'] == [549, 482]


async def test_v2_recalc_need_route_parts_in_request(
        v1_calc_creator, setup_v2_recalc_route_parts_request_enabled,
):
    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    recalc_req = v1_calc_creator.mock_recalc.request
    assert recalc_req['additional_payloads'] == {
        'details': 'cargo-pricing/v1/taxi/calc',
        'need_route_parts': True,
    }
