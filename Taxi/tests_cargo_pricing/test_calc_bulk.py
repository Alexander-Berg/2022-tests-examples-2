import copy

from tests_cargo_pricing import utils


async def test_calc_bulk(
        v2_calc_creator, taxi_cargo_pricing_monitor, load_json,
):
    stats_before_request = await taxi_cargo_pricing_monitor.get_metric(
        'cargo_pricing__taxi__categories_count',
    )
    response = await v2_calc_creator.execute()
    assert response.status_code == 200
    resp = response.json()

    assert len(resp['calculations']) == 1

    taxi_calc_resp_example = load_json('expected_taxi_calc_response.json')

    response = resp['calculations'][0]['result']
    assert response.pop('calc_id').startswith('cargo-pricing/v1/')
    assert response == taxi_calc_resp_example

    prepare_req = v2_calc_creator.mock_prepare.request
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

    stats = await taxi_cargo_pricing_monitor.get_metric(
        'cargo_pricing__taxi__categories_count',
    )

    prev_stats = (
        0 if not stats_before_request else stats_before_request['cargocorp']
    )
    assert stats['cargocorp'] - prev_stats == 1


async def test_calc_with_previous_calc_id(v2_calc_creator):
    not_valid_id = 'cargo-pricing/v1/' + '00000000-0000-0000-0000-000000000000'
    v2_calc_creator.payload['calc_requests'][0][
        'previous_calc_id'
    ] = not_valid_id
    response = await v2_calc_creator.execute()
    assert response.status_code == 400
    resp = response.json()
    assert resp == {
        'code': 'recalculation_is_not_supported',
        'message': (
            'previous_calc_id field was found in request, use v1/taxi/calc'
        ),
    }


async def test_calc_cant_construct_error(v2_calc_creator, mock_route):
    mock_route.empty_route = True

    response = await v2_calc_creator.execute()
    assert response.status_code == 400
    resp = response.json()
    assert resp == {
        'code': 'cant_construct_route',
        'message': 'Requested route is insoluble',
    }


async def test_duplicate_tariff_error(v2_calc_creator):
    v2_calc_creator.payload['calc_requests'].append(
        v2_calc_creator.payload['calc_requests'][0],
    )
    response = await v2_calc_creator.execute()
    assert response.status_code == 400
    resp = response.json()
    assert resp == {
        'code': 'duplicate_classes',
        'message': 'Calculations contains duplicate classes',
    }


async def test_different_waypoints_error(v2_calc_creator):
    v2_calc_creator.payload['calc_requests'].append(
        copy.deepcopy(v2_calc_creator.payload['calc_requests'][0]),
    )
    v2_calc_creator.payload['calc_requests'][1]['waypoints'][0][
        'id'
    ] = 'not_identical_id'
    response = await v2_calc_creator.execute()
    assert response.status_code == 400
    resp = response.json()
    assert resp == {
        'code': 'not_identical_waypoints',
        'message': 'Different waypoints are not supported',
    }


async def test_two_calcs(v2_calc_creator):
    second_tariff_req = utils.add_category_to_request(v2_calc_creator)
    second_tariff_req['taxi_requirements'] = {
        'cargo_loaders': 1,
        'cargo_type': 'lcv_m',
    }
    response = await v2_calc_creator.execute()
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['calculations']) == 2

    prepare_req = v2_calc_creator.mock_prepare.request
    assert {*prepare_req.pop('categories')} == {'courier', 'cargocorp'}
    assert prepare_req == {
        'classes_requirements': {
            'cargocorp': {
                'door_to_door': True,
                'cargo_type': 0,
                'cargo_type_int': 1,
            },
            'courier': {
                'cargo_loaders': 1,
                'cargo_type': 1,
                'cargo_type_int': 2,
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


async def test_calc_bulk_with_coupon_and_discounts(
        v2_calc_creator, taxi_cargo_pricing_monitor,
):
    request = v2_calc_creator.payload['calc_requests'][0]
    request['discounts_enabled'] = True
    request['calc_strikeout_price'] = True
    request['payment_info']['coupon'] = 'coupon212'

    v2_calc_creator.mock_recalc.response['price']['user']['strikeout'] = 453
    v2_calc_creator.mock_recalc.response['price']['user']['meta'][
        'coupon_value'
    ] = 153
    response = await v2_calc_creator.execute()
    assert response.status_code == 200
    resp = response.json()

    assert len(resp['calculations']) == 1

    response = resp['calculations'][0]['result']
    assert response['price_extra_info'] == {
        'coupon': {'coupon': 'coupon212', 'was_applied': True},
    }
    assert response['prices'] == {
        'strikeout_price': '453',
        'total_price': '300',
    }

    prepare_req = v2_calc_creator.mock_prepare.request
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
            'payment_info': {
                'method_id': 'corp-xxx',
                'type': 'corp',
                'coupon': 'coupon212',
            },
            'user_id': 'user_id',
        },
        'waypoints': [
            [37.6489887, 55.5737046],
            [37.5447415, 55.9061769],
            [37.6489887, 55.5737046],
        ],
        'additional_payloads': {'need_strikeout_price_modifications': True},
        'zone': 'moscow',
        'modifications_scope': 'cargo',
        'extra': {
            'providers': {
                'discounts': {'is_enabled': True},
                'router': {'is_fallback': True},
            },
        },
        'calc_additional_prices': {
            'antisurge': False,
            'combo_inner': False,
            'combo_order': False,
            'combo_outer': False,
            'plus_promo': False,
            'strikeout': True,
        },
    }


async def test_bulk_calc_yt_calcs_logger(
        v2_calc_creator,
        conf_exp3_yt_calcs_logging_enabled,
        yt_calcs_logger_testpoint,
):
    await conf_exp3_yt_calcs_logging_enabled(enabled=True)
    utils.add_category_to_request(v2_calc_creator)

    response = await v2_calc_creator.execute()
    assert response.status_code == 200
    calculations = response.json()['calculations']
    assert len(calculations) == 2

    log_messages = yt_calcs_logger_testpoint.messages
    assert len(log_messages) == len(calculations)
    for i, _ in enumerate(log_messages):
        assert log_messages[i]['calc_id'] == calculations[i]['calc_id']
        assert log_messages[i]['log_place'] == 'v2_taxi_calc'


async def test_bulk_calc_yt_calcs_logger_disabled(
        v2_calc_creator,
        conf_exp3_yt_calcs_logging_enabled,
        yt_calcs_logger_testpoint,
):
    await conf_exp3_yt_calcs_logging_enabled(enabled=False)
    utils.add_category_to_request(v2_calc_creator)
    response = await v2_calc_creator.execute()
    assert response.status_code == 200

    assert yt_calcs_logger_testpoint.messages == []


async def test_bulk_calc_yt_calcs_logger_exp_kwargs(
        v2_calc_creator, conf_exp3_yt_calcs_logging_enabled, experiments3,
):
    exp3_recorder = experiments3.record_match_tries(
        'cargo_pricing_yt_calcs_logging',
    )

    await conf_exp3_yt_calcs_logging_enabled(enabled=False)
    utils.add_category_to_request(v2_calc_creator)
    response = await v2_calc_creator.execute()
    assert response.status_code == 200

    tries = await exp3_recorder.get_match_tries(ensure_ntries=2)
    for i, _ in enumerate(tries):
        kwargs = tries[i].kwargs
        assert kwargs['consumer'] == 'cargo-pricing/yt_calcs_logging'
        assert kwargs['corp_client_id'] == 'corp_client_id'
        assert kwargs['homezone'] == 'moscow'
        assert kwargs['log_place'] == 'v2_taxi_calc'
        assert kwargs['price_for'] == 'client'
        assert kwargs['source'] == 'unknown'
        assert kwargs['request_timestamp']
    assert tries[0].kwargs['tariff_class'] == 'cargocorp'
    assert tries[1].kwargs['tariff_class'] == 'courier'


async def test_combo_bombo(v2_calc_creator, load_json):
    request = v2_calc_creator.payload['calc_requests'][0]
    request['calculate_combo_prices'] = True
    utils.set_v2prepare_resp_combo(v2_calc_creator, load_json)
    response = await v2_calc_creator.execute()
    assert response.status_code == 200

    assert v2_calc_creator.mock_prepare.request['calc_additional_prices'][
        'combo_order'
    ]
    alternative_options = response.json()['calculations'][0]['result'][
        'alternative_options_calcs'
    ][0]
    assert alternative_options['type'] == 'combo'


NO_CALC_ID = 'cargo-pricing/v1/00000000-0000-0000-0000-000000000000'


async def test_two_calcs_second_no_tariff(v2_calc_creator):
    v2_calc_creator.payload['calc_requests'].append(
        copy.deepcopy(v2_calc_creator.payload['calc_requests'][0]),
    )
    second_calc_req = v2_calc_creator.payload['calc_requests'][1]
    second_calc_req['tariff_class'] = 'courier'
    response = await v2_calc_creator.execute()
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['calculations']) == 2
    assert resp['calculations'][0]['calc_id'] != NO_CALC_ID
    assert resp['calculations'][1] == {
        'calc_id': NO_CALC_ID,
        'result': {
            'code': 'no tariff',
            'message': 'no tariff courier (courier)',
        },
    }


async def test_two_calcs_first_no_tariff(v2_calc_creator):
    v2_calc_creator.payload['calc_requests'].append(
        copy.deepcopy(v2_calc_creator.payload['calc_requests'][0]),
    )
    first_calc_req = v2_calc_creator.payload['calc_requests'][0]
    first_calc_req['tariff_class'] = 'courier'
    response = await v2_calc_creator.execute()
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['calculations']) == 2
    assert resp['calculations'][0] == {
        'calc_id': NO_CALC_ID,
        'result': {
            'code': 'no tariff',
            'message': 'no tariff courier (courier)',
        },
    }
    assert resp['calculations'][1]['calc_id'] != NO_CALC_ID
