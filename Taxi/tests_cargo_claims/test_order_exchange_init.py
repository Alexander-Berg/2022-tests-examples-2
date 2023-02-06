# pylint: disable=C0302
import datetime

import pytest


@pytest.mark.parametrize(
    (
        'current_claim_status',
        'current_taximeter_status',
        'expected_claim_status',
        'expected_taximeter_status',
        'point_visit_order',
    ),
    (
        # Pickup confirmation
        (
            'performer_found',
            'new',
            'ready_for_pickup_confirmation',
            'pickup_confirmation',
            1,
        ),
        (
            'ready_for_pickup_confirmation',
            'pickup_confirmation',
            'ready_for_pickup_confirmation',
            'pickup_confirmation',
            1,
        ),
        # Delivering confirmation
        (
            'pickuped',
            'delivering',
            'ready_for_delivery_confirmation',
            'droppof_confirmation',
            2,
        ),
        (
            'ready_for_delivery_confirmation',
            'droppof_confirmation',
            'ready_for_delivery_confirmation',
            'droppof_confirmation',
            2,
        ),
        # Return confirmation
        (
            'returning',
            'returning',
            'ready_for_return_confirmation',
            'return_confirmation',
            3,
        ),
        (
            'ready_for_return_confirmation',
            'return_confirmation',
            'ready_for_return_confirmation',
            'return_confirmation',
            3,
        ),
    ),
)
async def test_init_confirmation(
        taxi_cargo_claims,
        esignature_issuer,
        state_controller,
        get_default_driver_auth_headers,
        load_json,
        experiments3,
        get_segment_id,
        raw_exchange_init,
        current_claim_status: str,
        expected_claim_status: str,
        current_taximeter_status: str,
        expected_taximeter_status: str,
        point_visit_order: int,
):
    await state_controller.apply(target_status=current_claim_status)

    experiments_json = load_json('exp3_action_checks.json')
    experiments3.add_experiments_json(experiments_json)

    segment_id = await get_segment_id()
    response = await raw_exchange_init(
        segment_id, point_visit_order=point_visit_order,
    )

    response_json = response.json()
    assert response.status_code == 200, response_json
    assert response_json == {
        'new_status': expected_taximeter_status,
        'new_claim_status': expected_claim_status,
    }

    new_claim_info = await state_controller.get_claim_info()
    assert new_claim_info.current_state.status == expected_claim_status


def _make_timestamp(seconds_from_now, now=None):
    if now is None:
        now = datetime.datetime.now()
    else:
        now = datetime.datetime.strptime(now, '%Y-%m-%dT%H:%M:%S.%f%z')
    return (
        int(
            (
                now
                - datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
            ).total_seconds(),
        )
        - seconds_from_now
    )


NOW = '2020-01-01T00:00:00.000Z'


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    ('coordinate', 'expected_response_error', 'point_checks'),
    (
        pytest.param(
            None,
            None,
            {
                '__default__': {},
                'source': {
                    'distance': {
                        'enable': True,
                        'max_value_meters': 500,
                        'max_position_age_seconds': 60,
                        'allow_for_unknown_position': False,
                        'router': 'fallback',
                    },
                },
            },
            id='no_config_for_point_type',
        ),
        pytest.param(
            None,
            None,
            {
                '__default__': {
                    'distance': {
                        'enable': False,
                        'max_value_meters': 500,
                        'max_position_age_seconds': 60,
                        'allow_for_unknown_position': False,
                        'router': 'fallback',
                    },
                },
            },
            id='config_disabled',
        ),
        pytest.param(
            None,
            'Ваши координаты неизвестны, включите GPS',
            {
                '__default__': {
                    'distance': {
                        'enable': True,
                        'max_value_meters': 500,
                        'max_position_age_seconds': 60,
                        'allow_for_unknown_position': False,
                        'router': 'fallback',
                    },
                },
            },
            id='unknown_position',
        ),
        pytest.param(
            None,
            None,
            {
                '__default__': {
                    'distance': {
                        'enable': True,
                        'max_value_meters': 500,
                        'max_position_age_seconds': 60,
                        'allow_for_unknown_position': True,
                        'router': 'fallback',
                    },
                },
            },
            id='allow_for_unknown_position',
        ),
        pytest.param(
            {
                'direction': 0,
                'lat': 90,
                'lon': 37.6,
                'speed': 0,
                'timestamp': _make_timestamp(300, NOW),
            },
            'Ваши координаты неизвестны, включите GPS',
            {
                '__default__': {
                    'distance': {
                        'enable': True,
                        'max_value_meters': 500,
                        'max_position_age_seconds': 60,
                        'allow_for_unknown_position': False,
                        'router': 'fallback',
                    },
                },
            },
            id='position_too_old',
        ),
        pytest.param(
            {
                'direction': 0,
                'lat': 55.8,
                'lon': 37.6,
                'speed': 0,
                'timestamp': _make_timestamp(0, NOW),
            },
            'Вы находитесь дальше 500 метров от точки назначения',
            {
                '__default__': {
                    'distance': {
                        'enable': True,
                        'max_value_meters': 500,
                        'max_position_age_seconds': 60,
                        'allow_for_unknown_position': False,
                        'router': 'fallback',
                    },
                },
            },
            id='too_far_from_point',
        ),
        pytest.param(
            {
                'direction': 0,
                'lat': 55.6,
                'lon': 37.6,
                'speed': 0,
                'timestamp': _make_timestamp(0, NOW),
            },
            None,
            {
                '__default__': {
                    'distance': {
                        'enable': True,
                        'max_value_meters': 500,
                        'max_position_age_seconds': 60,
                        'allow_for_unknown_position': False,
                        'router': 'fallback',
                    },
                },
            },
            id='position_ok',
        ),
    ),
)
async def test_point_distance_checking(
        mockserver,
        taxi_cargo_claims,
        state_controller,
        get_default_driver_auth_headers,
        coordinate,
        expected_response_error,
        point_checks,
        load_json,
        experiments3,
        get_segment_id,
        raw_exchange_init,
):
    await state_controller.apply(target_status='pickuped')

    experiments_json = load_json('exp3_action_checks.json')
    action_checks_config = next(
        cfg
        for cfg in experiments_json['configs']
        if cfg['name'] == 'cargo_claims_action_checks'
    )
    action_checks_config['default_value']['arrive'] = point_checks
    experiments_json['last_modified_at'] = int(
        datetime.datetime.now().timestamp(),
    )
    experiments3.add_experiments_json(experiments_json)
    await taxi_cargo_claims.invalidate_caches()

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_trackstory_position(request):
        if coordinate:
            return mockserver.make_response(
                json={'position': coordinate, 'type': 'raw'}, status=200,
            )
        return mockserver.make_response(
            json={'message': 'Not found'}, status=404,
        )

    segment_id = await get_segment_id()
    response = await raw_exchange_init(segment_id, point_visit_order=2)

    response_json = response.json()

    if expected_response_error:
        assert response.status_code == 409, response_json
        assert response_json == {
            'code': 'state_transition_forbidden',
            'message': expected_response_error,
        }
    else:
        assert response.status_code == 200, response_json
        assert response_json == {
            'new_status': 'droppof_confirmation',
            'new_claim_status': 'ready_for_delivery_confirmation',
        }


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_scooters_action_checks',
    consumers=['cargo-claims/scooters'],
    clauses=[],
    default_value={
        'battery_exchange_pickup': {'enabled': True},
        'battery_exchange_return': {'enabled': False},
        'battery_exchange_in_scooter': {'enabled': False},
    },
    is_config=True,
)
@pytest.mark.translations(
    cargo={
        'errors.scooters.unknown_error': {
            'en': 'Something scooterable went wrong. Try again',
        },
    },
)
@pytest.mark.parametrize(
    ['scooters_misc_response', 'expected_response'],
    [
        pytest.param(
            {'status': 200, 'json': {}},
            {
                'status': 200,
                'json': {
                    'new_status': 'pickup_confirmation',
                    'new_claim_status': 'ready_for_pickup_confirmation',
                },
            },
            id='check ok',
        ),
        pytest.param(
            {'status': 400, 'json': {'code': '400', 'message': 'Ай ай ай'}},
            {
                'status': 409,
                'json': {
                    'code': 'state_transition_forbidden',
                    'message': 'Ай ай ай',
                },
            },
            id='check failed',
        ),
        pytest.param(
            {'status': 500, 'json': {}},
            {
                'status': 409,
                'json': {
                    'code': 'state_transition_forbidden',
                    'message': 'Вы слишком далеко от точки назначения',
                },
            },
            id='scooters-misc failed',
        ),
    ],
)
async def test_battery_exchange_pickup(
        taxi_cargo_claims,
        mockserver,
        state_controller,
        get_default_driver_auth_headers,
        load_json,
        get_segment_id,
        raw_exchange_init,
        pgsql,
        update_point,
        scooters_misc_response,
        expected_response,
):
    await state_controller.apply(target_status='pickup_arrived')

    update_point(1000, external_order_id='100500')

    @mockserver.json_handler(
        '/scooters-misc/v1/battery-exchange/validation/pickup',
    )
    def _validation_pickup(request):
        assert request.args == {'locale': 'ru', 'recharge_task_id': '100500'}
        return mockserver.make_response(**scooters_misc_response)

    segment_id = await get_segment_id()
    response = await raw_exchange_init(segment_id, point_visit_order=1)

    assert _validation_pickup.times_called == 1

    assert response.status == expected_response['status']
    assert response.json() == expected_response['json']


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_scooters_action_checks',
    consumers=['cargo-claims/scooters'],
    clauses=[],
    default_value={
        'battery_exchange_pickup': {'enabled': False},
        'battery_exchange_return': {'enabled': True},
        'battery_exchange_in_scooter': {'enabled': False},
    },
    is_config=True,
)
@pytest.mark.translations(
    cargo={
        'errors.scooters.unknown_error': {
            'en': 'Something scooterable went wrong. Try again',
        },
    },
)
@pytest.mark.parametrize(
    ['scooters_misc_response', 'expected_response'],
    [
        pytest.param(
            {'status': 200, 'json': {}},
            {
                'status': 200,
                'json': {
                    'new_status': 'droppof_confirmation',
                    'new_claim_status': 'ready_for_delivery_confirmation',
                },
            },
            id='check ok',
        ),
        pytest.param(
            {'status': 400, 'json': {'code': '400', 'message': 'Ай ай ай'}},
            {
                'status': 409,
                'json': {
                    'code': 'state_transition_forbidden',
                    'message': 'Ай ай ай',
                },
            },
            id='check failed',
        ),
        pytest.param(
            {'status': 500, 'json': {}},
            {
                'status': 409,
                'json': {
                    'code': 'state_transition_forbidden',
                    'message': 'Вы слишком далеко от точки назначения',
                },
            },
            id='scooters-misc failed',
        ),
    ],
)
async def test_battery_exchange_return(
        taxi_cargo_claims,
        mockserver,
        state_controller,
        get_default_driver_auth_headers,
        load_json,
        pgsql,
        update_point,
        scooters_misc_response,
        expected_response,
        create_segment_with_performer,
        get_segment_id,
        raw_exchange_init,
):
    claim_info = await state_controller.apply(target_status='delivery_arrived')

    update_point(1000, external_order_id='task_id')
    update_point(1001, external_order_id='item_id')
    update_point(1002, external_order_id='item_id')

    @mockserver.json_handler(
        '/scooters-misc/v1/battery-exchange/validation/return',
    )
    def _validation_return(request):
        assert request.args == {'locale': 'ru', 'recharge_task_id': 'task_id'}
        return mockserver.make_response(**scooters_misc_response)

    segment_id = await get_segment_id()
    response = await raw_exchange_init(
        segment_id, point_visit_order=claim_info.current_state.point_id,
    )

    assert _validation_return.times_called == 1

    assert response.status == expected_response['status']
    assert response.json() == expected_response['json']


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_scooters_action_checks',
    consumers=['cargo-claims/scooters'],
    clauses=[],
    default_value={
        'battery_exchange_pickup': {'enabled': False},
        'battery_exchange_return': {'enabled': False},
        'battery_exchange_in_scooter': {'enabled': True},
    },
    is_config=True,
)
@pytest.mark.translations(
    cargo={
        'errors.scooters.unknown_error': {
            'en': 'Something scooterable went wrong. Try again',
        },
    },
)
@pytest.mark.parametrize(
    ['point_type', 'scooters_misc_response', 'expected_response'],
    [
        pytest.param(
            'destination',
            {'status': 200, 'json': {}},
            {
                'status': 200,
                'json': {
                    'new_status': 'droppof_confirmation',
                    'new_claim_status': 'ready_for_delivery_confirmation',
                },
            },
            id='check ok',
        ),
        pytest.param(
            'destination',
            {'status': 400, 'json': {'code': '400', 'message': 'Ай ай ай'}},
            {
                'status': 409,
                'json': {
                    'code': 'state_transition_forbidden',
                    'message': 'Ай ай ай',
                },
            },
            id='check failed',
        ),
        pytest.param(
            'destination',
            {'status': 500, 'json': {}},
            {
                'status': 409,
                'json': {
                    'code': 'state_transition_forbidden',
                    'message': 'Вы слишком далеко от точки назначения',
                },
            },
            id='scooters-misc failed',
        ),
        pytest.param(
            'source',
            None,
            {
                'status': 200,
                'json': {
                    'new_status': 'pickup_confirmation',
                    'new_claim_status': 'ready_for_pickup_confirmation',
                },
            },
            id='check disabled on source point',
        ),
    ],
)
async def test_battery_exchange_change(
        taxi_cargo_claims,
        mockserver,
        state_controller,
        get_default_driver_auth_headers,
        load_json,
        pgsql,
        update_point,
        point_type,
        scooters_misc_response,
        expected_response,
        create_segment_with_performer,
        get_segment_id,
        raw_exchange_init,
):
    await create_segment_with_performer(
        claim_index=0, use_create_v2=True, multipoints=True,
    )

    if point_type == 'source':
        target_status = 'pickup_arrived'
        next_point_order = 1
    elif point_type == 'destination':
        target_status = 'delivery_arrived'
        next_point_order = 2
    else:
        assert False, 'Wrong point type for test'

    await state_controller.apply(
        target_status=target_status,
        next_point_order=next_point_order,
        fresh_claim=False,
    )

    claim_info = await state_controller.get_claim_info()

    update_point(1000, external_order_id='task_id')
    update_point(1001, external_order_id='item_id')
    update_point(1002, external_order_id='item_id')

    @mockserver.json_handler(
        '/scooters-misc/v1/battery-exchange/validation/change',
    )
    def _validation_change(request):
        assert request.args == {
            'locale': 'ru',
            'recharge_task_id': 'task_id',
            'recharge_item_id': 'item_id',
        }
        return mockserver.make_response(**scooters_misc_response)

    segment_id = await get_segment_id()
    response = await raw_exchange_init(
        segment_id, point_visit_order=claim_info.current_state.point_id,
    )

    assert _validation_change.times_called == (
        1 if scooters_misc_response is not None else 0
    )

    assert response.status == expected_response['status']
    assert response.json() == expected_response['json']


@pytest.mark.xfail(reason='will be fixed in (add ticket)')
async def test_inappropriate_status(
        taxi_cargo_claims,
        esignature_issuer,
        state_controller,
        get_default_driver_auth_headers,
        get_segment_id,
        raw_exchange_init,
):
    await state_controller.apply(target_status='delivered')

    segment_id = await get_segment_id()
    response = await raw_exchange_init(segment_id, point_visit_order=1)

    assert response.status_code == 409
    assert response.json()['code'] == 'inappropriate_status'


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    ('query_pos_coordinate', 'expected_response_error', 'point_checks'),
    (
        pytest.param(
            None,
            None,
            {
                '__default__': {},
                'source': {
                    'distance': {
                        'enable': True,
                        'max_value_meters': 500,
                        'max_position_age_seconds': 60,
                        'allow_for_unknown_position': False,
                        'router': 'fallback',
                        'query_position_flow': {
                            'enable': True,
                            'retry_count': 5,
                            'retry_timeout_ms': 30,
                        },
                    },
                },
            },
            id='no_config_for_point_type',
        ),
        pytest.param(
            None,
            None,
            {
                '__default__': {
                    'distance': {
                        'enable': False,
                        'max_value_meters': 500,
                        'max_position_age_seconds': 60,
                        'allow_for_unknown_position': False,
                        'router': 'fallback',
                        'query_position_flow': {
                            'enable': True,
                            'retry_count': 5,
                            'retry_timeout_ms': 30,
                        },
                    },
                },
            },
            id='config_disabled',
        ),
        pytest.param(
            None,
            'Ваши координаты неизвестны, включите GPS',
            {
                '__default__': {
                    'distance': {
                        'enable': True,
                        'max_value_meters': 500,
                        'max_position_age_seconds': 60,
                        'allow_for_unknown_position': False,
                        'router': 'fallback',
                        'query_position_flow': {
                            'enable': True,
                            'retry_count': 5,
                            'retry_timeout_ms': 30,
                        },
                    },
                },
            },
            id='unknown_position',
        ),
        pytest.param(
            None,
            None,
            {
                '__default__': {
                    'distance': {
                        'enable': True,
                        'max_value_meters': 500,
                        'max_position_age_seconds': 60,
                        'allow_for_unknown_position': True,
                        'router': 'fallback',
                        'query_position_flow': {
                            'enable': True,
                            'retry_count': 5,
                            'retry_timeout_ms': 30,
                        },
                    },
                },
            },
            id='allow_for_unknown_position',
        ),
        pytest.param(
            [
                [
                    {
                        'source': 'Raw',
                        'position': {
                            'direction': 0,
                            'lat': 90,
                            'lon': 37.6,
                            'speed': 0,
                            'timestamp': _make_timestamp(300, NOW),
                        },
                    },
                ],
            ],
            'Ваши координаты неизвестны, включите GPS',
            {
                '__default__': {
                    'distance': {
                        'enable': True,
                        'max_value_meters': 500,
                        'max_position_age_seconds': 60,
                        'allow_for_unknown_position': False,
                        'router': 'fallback',
                        'query_position_flow': {
                            'enable': True,
                            'retry_count': 5,
                            'retry_timeout_ms': 30,
                        },
                    },
                },
            },
            id='position_too_old',
        ),
        pytest.param(
            [
                [
                    {
                        'source': 'Raw',
                        'position': {
                            'direction': 0,
                            'lat': 55.8,
                            'lon': 37.6,
                            'speed': 0,
                            'timestamp': _make_timestamp(0, NOW),
                        },
                    },
                ],
            ],
            'Вы находитесь дальше 500 метров от точки назначения',
            {
                '__default__': {
                    'distance': {
                        'enable': True,
                        'max_value_meters': 500,
                        'max_position_age_seconds': 60,
                        'allow_for_unknown_position': False,
                        'router': 'fallback',
                        'query_position_flow': {
                            'enable': True,
                            'retry_count': 5,
                            'retry_timeout_ms': 30,
                        },
                    },
                },
            },
            id='too_far_from_point',
        ),
        pytest.param(
            [
                [
                    {
                        'source': 'Raw',
                        'position': {
                            'direction': 0,
                            'lat': 55.6,
                            'lon': 37.6,
                            'speed': 0,
                            'timestamp': _make_timestamp(0, NOW),
                        },
                    },
                ],
            ],
            None,
            {
                '__default__': {
                    'distance': {
                        'enable': True,
                        'max_value_meters': 500,
                        'max_position_age_seconds': 60,
                        'allow_for_unknown_position': False,
                        'router': 'fallback',
                        'query_position_flow': {
                            'enable': True,
                            'retry_count': 5,
                            'retry_timeout_ms': 30,
                        },
                    },
                },
            },
            id='position_ok',
        ),
        pytest.param(
            [
                [
                    {
                        'source': 'Adjusted',
                        'position': {
                            'direction': 0,
                            'lat': 55.6,
                            'lon': 37.6,
                            'speed': 0,
                            'timestamp': _make_timestamp(0, NOW),
                        },
                    },
                    {
                        'source': 'Raw',
                        'position': {
                            'direction': 0,
                            'lat': 55.6,
                            'lon': 37.6,
                            'speed': 0,
                            'timestamp': _make_timestamp(300, NOW),
                        },
                    },
                ],
            ],
            None,
            {
                '__default__': {
                    'distance': {
                        'enable': True,
                        'max_value_meters': 500,
                        'max_position_age_seconds': 60,
                        'allow_for_unknown_position': False,
                        'router': 'fallback',
                        'query_position_flow': {
                            'enable': True,
                            'retry_count': 5,
                            'retry_timeout_ms': 30,
                        },
                    },
                },
            },
            id='one_position_old_query_pos_ok',
        ),
    ),
)
async def test_query_positions_checking(
        mockserver,
        taxi_cargo_claims,
        state_controller,
        get_default_driver_auth_headers,
        query_pos_coordinate,
        expected_response_error,
        point_checks,
        load_json,
        experiments3,
        get_segment_id,
        raw_exchange_init,
):
    @mockserver.json_handler('/yagr-raw/service/v2/position/store')
    def yagr_handler(request):
        # pylint: disable=unused-variable
        return ''

    await state_controller.apply(target_status='pickuped')

    experiments_json = load_json('exp3_action_checks.json')
    action_checks_config = next(
        cfg
        for cfg in experiments_json['configs']
        if cfg['name'] == 'cargo_claims_action_checks'
    )
    action_checks_config['default_value']['arrive'] = point_checks
    experiments_json['last_modified_at'] = int(
        datetime.datetime.now().timestamp(),
    )
    experiments3.add_experiments_json(experiments_json)
    await taxi_cargo_claims.invalidate_caches()

    @mockserver.json_handler('/driver-trackstory/query/positions')
    def _driver_trackstory_query_position(request):
        distance = point_checks['__default__']['distance']
        assert request.json['driver_ids'] == ['some_park_some_driver']
        assert request.json['max_age'] == distance['max_position_age_seconds']
        if query_pos_coordinate:
            for position in query_pos_coordinate[-1]:
                if position['position']['timestamp'] >= _make_timestamp(
                        request.json['max_age'], NOW,
                ):
                    break
                return mockserver.make_response(
                    json={'results': [[]]}, status=200,
                )
            return mockserver.make_response(
                json={'results': query_pos_coordinate}, status=200,
            )
        return mockserver.make_response(
            json={'message': 'Driver not found'}, status=400,
        )

    segment_id = await get_segment_id()
    response = await raw_exchange_init(segment_id, point_visit_order=2)

    response_json = response.json()
    response_json.pop('new_route', {})

    if expected_response_error:
        assert response.status_code == 409, response_json
        assert response_json == {
            'code': 'state_transition_forbidden',
            'message': expected_response_error,
        }
    else:
        assert response.status_code == 200, response_json
        assert response_json == {
            'new_status': 'droppof_confirmation',
            'new_claim_status': 'ready_for_delivery_confirmation',
        }


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    ('coordinate', 'point_checks'),
    (
        pytest.param(
            {
                'direction': 0,
                'lat': 55.6,
                'lon': 37.6,
                'speed': 0,
                'timestamp': _make_timestamp(0, NOW),
            },
            {
                '__default__': {
                    'distance': {
                        'enable': True,
                        'max_value_meters': 500,
                        'max_position_age_seconds': 60,
                        'allow_for_unknown_position': False,
                        'router': 'linear',
                        'query_position_flow': {
                            'enable': False,
                            'retry_count': 5,
                            'retry_timeout_ms': 30,
                        },
                    },
                },
            },
            id='linear_distance_without_query_position',
        ),
        pytest.param(
            [
                [
                    {
                        'source': 'Adjusted',
                        'position': {
                            'direction': 0,
                            'lat': 55.6,
                            'lon': 37.6,
                            'speed': 0,
                            'timestamp': _make_timestamp(0, NOW),
                        },
                    },
                    {
                        'source': 'Raw',
                        'position': {
                            'direction': 0,
                            'lat': 55.6,
                            'lon': 37.6,
                            'speed': 0,
                            'timestamp': _make_timestamp(300, NOW),
                        },
                    },
                ],
            ],
            {
                '__default__': {
                    'distance': {
                        'enable': True,
                        'max_value_meters': 500,
                        'max_position_age_seconds': 60,
                        'allow_for_unknown_position': False,
                        'router': 'linear',
                        'query_position_flow': {
                            'enable': True,
                            'retry_count': 5,
                            'retry_timeout_ms': 30,
                        },
                    },
                },
            },
            id='linear_distance_with_query_position',
        ),
    ),
)
async def test_linear_distance_check_actions(
        mockserver,
        taxi_cargo_claims,
        state_controller,
        get_default_driver_auth_headers,
        testpoint,
        coordinate,
        point_checks,
        load_json,
        experiments3,
        get_segment_id,
        raw_exchange_init,
):
    @mockserver.json_handler('/yagr-raw/service/v2/position/store')
    def yagr_handler(request):
        # pylint: disable=unused-variable
        return ''

    await state_controller.apply(target_status='pickuped')

    experiments_json = load_json('exp3_action_checks.json')
    action_checks_config = next(
        cfg
        for cfg in experiments_json['configs']
        if cfg['name'] == 'cargo_claims_action_checks'
    )
    action_checks_config['default_value']['arrive'] = point_checks
    experiments_json['last_modified_at'] = int(
        datetime.datetime.now().timestamp(),
    )
    experiments3.add_experiments_json(experiments_json)
    await taxi_cargo_claims.invalidate_caches()

    @mockserver.json_handler('/driver-trackstory/position')
    def _driver_trackstory_position(request):
        if coordinate:
            return mockserver.make_response(
                json={'position': coordinate, 'type': 'raw'}, status=200,
            )
        return mockserver.make_response(
            json={'message': 'Not found'}, status=404,
        )

    @mockserver.json_handler('/driver-trackstory/query/positions')
    def _driver_trackstory_query_position(request):
        distance = point_checks['__default__']['distance']
        assert request.json['driver_ids'] == ['some_park_some_driver']
        assert request.json['max_age'] == distance['max_position_age_seconds']
        if coordinate:
            for position in coordinate[-1]:
                if position['position']['timestamp'] >= _make_timestamp(
                        request.json['max_age'], NOW,
                ):
                    break
                return mockserver.make_response(
                    json={'results': [[]]}, status=200,
                )
            return mockserver.make_response(
                json={'results': coordinate}, status=200,
            )
        return mockserver.make_response(
            json={'message': 'Driver not found'}, status=400,
        )

    @testpoint('driver-position-great-circle')
    def test_point(data):
        pass

    segment_id = await get_segment_id()
    response = await raw_exchange_init(segment_id, point_visit_order=2)

    response_json = response.json()

    assert response.status_code == 200, response_json
    assert response_json == {
        'new_status': 'droppof_confirmation',
        'new_claim_status': 'ready_for_delivery_confirmation',
    }
    assert test_point.times_called == 1


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_scooters_action_checks',
    consumers=['cargo-claims/scooters'],
    clauses=[],
    default_value={
        'battery_exchange_pickup': {'enabled': False},
        'battery_exchange_return': {'enabled': False},
        'battery_exchange_in_scooter': {'enabled': False},
        'validate_point_visited': {'enabled': True},
    },
    is_config=True,
)
@pytest.mark.translations(
    cargo={
        'errors.scooters.unknown_error': {
            'en': 'Something scooterable went wrong. Try again',
        },
    },
)
@pytest.mark.parametrize(
    ['scooters_misc_response', 'expected_response'],
    [
        pytest.param(
            {'status': 200, 'json': {}},
            {
                'status': 200,
                'json': {
                    'new_status': 'droppof_confirmation',
                    'new_claim_status': 'ready_for_delivery_confirmation',
                },
            },
            id='check ok',
        ),
        pytest.param(
            {'status': 400, 'json': {'code': '400', 'message': 'Ай ай ай'}},
            {
                'status': 409,
                'json': {
                    'code': 'state_transition_forbidden',
                    'message': 'Ай ай ай',
                },
            },
            id='check failed',
        ),
        pytest.param(
            {'status': 500, 'json': {}},
            {
                'status': 409,
                'json': {
                    'code': 'state_transition_forbidden',
                    'message': 'Вы слишком далеко от точки назначения',
                },
            },
            id='scooters-misc failed',
        ),
    ],
)
async def test_validate_via_scooters_ops_return(
        taxi_cargo_claims,
        mockserver,
        state_controller,
        get_default_driver_auth_headers,
        load_json,
        pgsql,
        update_point,
        scooters_misc_response,
        expected_response,
        create_segment_with_performer,
        get_segment_id,
        raw_exchange_init,
):
    claim_info = await state_controller.apply(target_status='delivery_arrived')

    update_point(1000, external_order_id='missions/100500')
    update_point(1001, external_order_id='missions/100500')
    update_point(1002, external_order_id='missions/100500')

    @mockserver.json_handler(
        '/scooters-ops/scooters-ops/old-flow/v1/validation/point-visited',
    )
    def _validation_point_visited(request):
        assert request.args == {
            'locale': 'ru',
            'mission_id': '100500',
            'cargo_point_id': '2',
        }
        return mockserver.make_response(**scooters_misc_response)

    segment_id = await get_segment_id()
    response = await raw_exchange_init(
        segment_id, point_visit_order=claim_info.current_state.point_id,
    )

    assert _validation_point_visited.times_called == 1

    assert response.status == expected_response['status']
    assert response.json() == expected_response['json']


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_scooters_action_checks',
    consumers=['cargo-claims/scooters'],
    clauses=[],
    default_value={
        'battery_exchange_pickup': {'enabled': False},
        'battery_exchange_return': {'enabled': False},
        'battery_exchange_in_scooter': {'enabled': False},
        'validate_point_visited': {'enabled': True},
    },
    is_config=True,
)
@pytest.mark.translations(
    cargo={
        'errors.scooters.unknown_error': {
            'en': 'Something scooterable went wrong. Try again',
        },
    },
)
@pytest.mark.parametrize(
    ['scooters_ops_response', 'expected_response'],
    [
        pytest.param(
            {'status': 200, 'json': {}},
            {
                'status': 200,
                'json': {
                    'new_status': 'pickup_confirmation',
                    'new_claim_status': 'ready_for_pickup_confirmation',
                },
            },
            id='check ok',
        ),
        pytest.param(
            {'status': 400, 'json': {'code': '400', 'message': 'Ай ай ай'}},
            {
                'status': 409,
                'json': {
                    'code': 'state_transition_forbidden',
                    'message': 'Ай ай ай',
                },
            },
            id='check failed',
        ),
        pytest.param(
            {'status': 500, 'json': {}},
            {
                'status': 409,
                'json': {
                    'code': 'state_transition_forbidden',
                    'message': 'Вы слишком далеко от точки назначения',
                },
            },
            id='scooters-ops failed',
        ),
    ],
)
async def test_validate_via_scooters_ops_pickup(
        taxi_cargo_claims,
        mockserver,
        state_controller,
        get_default_driver_auth_headers,
        load_json,
        pgsql,
        update_point,
        scooters_ops_response,
        expected_response,
        get_segment_id,
        raw_exchange_init,
):
    await state_controller.apply(target_status='pickup_arrived')

    update_point(1000, external_order_id='missions/100500')

    @mockserver.json_handler(
        '/scooters-ops/scooters-ops/old-flow/v1/validation/point-visited',
    )
    def _validation_point_visited(request):
        assert request.args == {
            'locale': 'ru',
            'mission_id': '100500',
            'cargo_point_id': '1',
        }
        return mockserver.make_response(**scooters_ops_response)

    segment_id = await get_segment_id()
    response = await raw_exchange_init(segment_id, point_visit_order=1)

    assert _validation_point_visited.times_called == 1

    assert response.status == expected_response['status']
    assert response.json() == expected_response['json']


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_scooters_action_checks',
    consumers=['cargo-claims/scooters'],
    clauses=[],
    default_value={
        'battery_exchange_pickup': {'enabled': False},
        'battery_exchange_return': {'enabled': False},
        'battery_exchange_in_scooter': {'enabled': False},
        'validate_point_visited': {'enabled': True},
    },
    is_config=True,
)
@pytest.mark.translations(
    cargo={
        'errors.scooters.unknown_error': {
            'en': 'Something scooterable went wrong. Try again',
        },
    },
)
@pytest.mark.parametrize(
    ['point_type', 'scooters_ops_response', 'expected_response'],
    [
        pytest.param(
            'destination',
            {'status': 200, 'json': {}},
            {
                'status': 200,
                'json': {
                    'new_status': 'droppof_confirmation',
                    'new_claim_status': 'ready_for_delivery_confirmation',
                },
            },
            id='check ok',
        ),
        pytest.param(
            'destination',
            {'status': 400, 'json': {'code': '400', 'message': 'Ай ай ай'}},
            {
                'status': 409,
                'json': {
                    'code': 'state_transition_forbidden',
                    'message': 'Ай ай ай',
                },
            },
            id='check failed',
        ),
        pytest.param(
            'destination',
            {'status': 500, 'json': {}},
            {
                'status': 409,
                'json': {
                    'code': 'state_transition_forbidden',
                    'message': 'Вы слишком далеко от точки назначения',
                },
            },
            id='scooters-ops failed',
        ),
        pytest.param(
            'source',
            {},
            {
                'status': 200,
                'json': {
                    'new_status': 'pickup_confirmation',
                    'new_claim_status': 'ready_for_pickup_confirmation',
                },
            },
            id='check disabled on source point',
        ),
    ],
)
async def test_validate_via_scooters_ops_change(
        taxi_cargo_claims,
        mockserver,
        state_controller,
        get_default_driver_auth_headers,
        load_json,
        pgsql,
        update_point,
        point_type,
        scooters_ops_response,
        expected_response,
        create_segment_with_performer,
        get_segment_id,
        raw_exchange_init,
):
    await create_segment_with_performer(
        claim_index=0, use_create_v2=True, multipoints=True,
    )

    if point_type == 'source':
        target_status = 'pickup_arrived'
        next_point_order = 1
        cargo_point_id = '1'
    elif point_type == 'destination':
        target_status = 'delivery_arrived'
        next_point_order = 2
        cargo_point_id = '2'
    else:
        assert False, 'Wrong point type for test'

    await state_controller.apply(
        target_status=target_status,
        next_point_order=next_point_order,
        fresh_claim=False,
    )

    claim_info = await state_controller.get_claim_info()

    update_point(1000, external_order_id='missions/100500')
    update_point(1001, external_order_id='missions/100500')
    update_point(1002, external_order_id='missions/100500')

    @mockserver.json_handler(
        '/scooters-ops/scooters-ops/old-flow/v1/validation/point-visited',
    )
    def _validation_change(request):
        assert request.args == {
            'locale': 'ru',
            'mission_id': '100500',
            'cargo_point_id': cargo_point_id,
        }
        return mockserver.make_response(**scooters_ops_response)

    segment_id = await get_segment_id()
    response = await raw_exchange_init(
        segment_id, point_visit_order=claim_info.current_state.point_id,
    )

    assert _validation_change.times_called == (
        1 if scooters_ops_response is not None else 0
    )

    assert response.status == expected_response['status']
    assert response.json() == expected_response['json']
