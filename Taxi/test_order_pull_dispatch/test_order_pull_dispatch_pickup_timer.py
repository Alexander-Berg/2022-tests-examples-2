# pylint: disable=C0302

import pytest

DEFAULT_TIMER_CONFIG = pytest.mark.experiments3(
    name='cargo_orders_timers_settings_lavka',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'First point timer',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 'source',
                                'arg_name': 'point_type',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {
                                'value': 0,
                                'arg_name': 'point_index_in_segment',
                                'arg_type': 'int',
                            },
                            'type': 'eq',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'eta_type': 'countdown',
                'description_key': 'actions.show_dialog.default_batch_title',
                'colors': ['black', 'red'],
                'eta_times': [600, 800],
            },
        },
    ],
    is_config=True,
)

TIMER_CONFIG_AUTH_PARAMS = pytest.mark.experiments3(
    name='cargo_orders_timers_settings_lavka',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'First point timer',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': '9.40.0',
                                'arg_name': 'app_version_typed',
                                'arg_type': 'version',
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {
                                'value': 'android',
                                'arg_name': 'app_platform',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'eta_type': 'countdown',
                'description_key': 'actions.show_dialog.default_batch_title',
                'colors': ['black', 'red'],
                'eta_times': [600, 800],
            },
        },
        {
            'title': 'First point timer',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': '9.55.0',
                                'arg_name': 'app_version_typed',
                                'arg_type': 'version',
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {
                                'value': 'ios',
                                'arg_name': 'app_platform',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'eta_type': 'countdown',
                'description_key': 'actions.show_dialog.default_batch_title',
                'description_alert_key': (
                    'actions.show_dialog.default_alert_text'
                ),
                'colors': ['black', 'red'],
                'eta_times': [500, 900],
            },
        },
    ],
    is_config=True,
)

TIMER_CONFIG_ETA_TEXT = pytest.mark.experiments3(
    name='cargo_orders_timers_settings_lavka',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'eta_type': 'text',
        'description_key': 'actions.show_dialog.default_batch_title',
        'colors': ['black', 'red'],
    },
    is_config=True,
)

COUNTDOWN_WITHOUT_TIME_CONFIG = pytest.mark.experiments3(
    name='cargo_orders_timers_settings_lavka',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'First point timer',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 'source',
                                'arg_name': 'point_type',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {
                                'value': 0,
                                'arg_name': 'point_index_in_segment',
                                'arg_type': 'int',
                            },
                            'type': 'eq',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'eta_type': 'countdown',
                'description_key': 'actions.show_dialog.default_batch_title',
                'colors': ['black', 'red'],
                'alert_duration_up_to_eta_sec': 60,
            },
        },
    ],
    is_config=True,
)

COUNTDOWN_WITHOUT_TIME_CONFIG_AND_ALERT_DURATION = pytest.mark.experiments3(
    name='cargo_orders_timers_settings_lavka',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'First point timer',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 'source',
                                'arg_name': 'point_type',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {
                                'value': 0,
                                'arg_name': 'point_index_in_segment',
                                'arg_type': 'int',
                            },
                            'type': 'eq',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'eta_type': 'countdown',
                'description_key': 'actions.show_dialog.default_batch_title',
                'colors': ['black', 'red'],
            },
        },
    ],
    is_config=True,
)

DEFAULT_CLIENT_KIND_CONFIG = pytest.mark.config(
    CARGO_ORDERS_CLIENT_KIND={
        '5e36732e2bc54e088b1466e08e31c486': {
            'client_kind': 'lavka',
            'country_iso3': 'RU',
        },
    },
)

EXPECTED_ACTION = {
    'calculation_awaited': False,
    'eta': '2020-08-18T13:57:09.939497+00:00',
    'type': 'eta',
    'eta_type': 'countdown',
    'description': 'Еще заказ',
    'colors': ['black', 'red'],
    'eta_times': [
        '2020-08-18T13:53:49.939497+00:00',
        '2020-08-18T13:57:09.939497+00:00',
    ],
}

EXPECTED_ACTION_ETA_TEXT = {
    'calculation_awaited': True,
    'eta': '1970-01-01T00:00:00+00:00',
    'type': 'eta',
    'eta_type': 'text',
    'description': 'Еще заказ',
    'colors': ['black', 'red'],
}

EXPECTED_ACTION_V1 = {
    'calculation_awaited': False,
    'eta': '2021-03-23T10:29:12.346759+00:00',
    'type': 'eta',
    'eta_type': 'countdown',
    'description': 'Еще заказ',
    'eta_times': [
        '2021-03-23T10:25:52.346759+00:00',
        '2021-03-23T10:29:12.346759+00:00',
    ],
    'colors': ['black', 'red'],
}

EXPECTED_ACTION_V2 = {
    'calculation_awaited': False,
    'eta': '2021-03-23T10:30:52.346759+00:00',
    'type': 'eta',
    'eta_type': 'countdown',
    'description': 'Еще заказ',
    'description_alert': 'Опоздание',
    'eta_times': [
        '2021-03-23T10:24:12.346759+00:00',
        '2021-03-23T10:30:52.346759+00:00',
    ],
    'colors': ['black', 'red'],
}


@DEFAULT_TIMER_CONFIG
@DEFAULT_CLIENT_KIND_CONFIG
@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
async def test_pull_dispatch_show_pickup_timer(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_with_same_source_point,
        pull_dispatch_enabled,
        mock_driver_tags_v1_match_profile,
        experiments3,
):
    exp3_recorder = experiments3.record_match_tries(
        'cargo_orders_timers_settings_lavka',
    )

    waybill_info_with_same_source_point['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled

    waybill_info_with_same_source_point['execution']['points'][0][
        'was_ready_at'
    ] = '2020-08-18T13:40:49.939497+00:00'
    waybill_info_with_same_source_point['execution']['points'][1][
        'was_ready_at'
    ] = '2020-08-18T13:43:49.939497+00:00'

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    eta_action = next(filter(lambda x: x['type'] == 'eta', actions), None)

    if pull_dispatch_enabled:
        assert eta_action == EXPECTED_ACTION
        tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
        kwargs = tries[0].kwargs
        assert kwargs['lavka_has_market_parcel']
    else:
        assert eta_action is None


EXPECTED_ACTION_POINTS_NOT_READY = {
    'calculation_awaited': False,
    'eta': '2020-08-18T14:10:09.939497+00:00',
    'type': 'eta',
    'eta_type': 'countdown',
    'description': 'Еще заказ',
    'colors': ['black', 'red'],
    'eta_times': [
        '2020-08-18T14:06:49.939497+00:00',
        '2020-08-18T14:10:09.939497+00:00',
    ],
}


@DEFAULT_TIMER_CONFIG
@DEFAULT_CLIENT_KIND_CONFIG
@pytest.mark.parametrize('not_ready_points', [[0], [1], [0, 1]])
async def test_pull_dispatch_skip_pickup_timer_when_points_not_ready(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_with_same_source_point,
        not_ready_points,
        mock_driver_tags_v1_match_profile,
):
    waybill_info_with_same_source_point['dispatch']['is_pull_dispatch'] = True
    waybill_info_with_same_source_point['execution']['points'][0][
        'was_ready_at'
    ] = '2020-08-18T13:40:49.939497+00:00'
    waybill_info_with_same_source_point['execution']['points'][1][
        'was_ready_at'
    ] = '2020-08-18T13:43:49.939497+00:00'
    waybill_info_with_same_source_point['segments'][0]['custom_context'] = {
        'depot_id': '123456',
    }

    for idx in not_ready_points:
        del waybill_info_with_same_source_point['execution']['points'][idx][
            'was_ready_at'
        ]

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    eta_action = next(filter(lambda x: x['type'] == 'eta', actions), None)

    assert eta_action == EXPECTED_ACTION_POINTS_NOT_READY


@DEFAULT_TIMER_CONFIG
@DEFAULT_CLIENT_KIND_CONFIG
async def test_pull_dispatch_skip_pickup_timer_does_not_change(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_with_same_source_point,
        mock_driver_tags_v1_match_profile,
):
    waybill_info_with_same_source_point['dispatch']['is_pull_dispatch'] = True

    # В этом тесте первая точка была собрана позднее нарочно.
    waybill_info_with_same_source_point['execution']['points'][1][
        'was_ready_at'
    ] = '2020-08-18T13:43:49.939497+00:00'
    waybill_info_with_same_source_point['execution']['points'][0][
        'was_ready_at'
    ] = '2020-08-18T13:40:49.939497+00:00'

    waybill_info_with_same_source_point['segments'][0]['custom_context'] = {
        'depot_id': '123456',
    }

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    eta_action = next(filter(lambda x: x['type'] == 'eta', actions), None)

    assert EXPECTED_ACTION == eta_action

    # Курьер забрал первую посылку
    waybill_info_with_same_source_point['execution']['points'][0][
        'visit_status'
    ] = 'visited'
    waybill_info_with_same_source_point['execution']['points'][0][
        'is_resolved'
    ] = True

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    eta_action = next(filter(lambda x: x['type'] == 'eta', actions), None)

    assert EXPECTED_ACTION == eta_action


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {'__default__': False, 'hide_eta_when_not_ready': True},
    },
)
@DEFAULT_TIMER_CONFIG
@DEFAULT_CLIENT_KIND_CONFIG
@pytest.mark.parametrize('not_ready_points', [[0], [1], [0, 1]])
async def test_pull_dispatch_skip_pickup_timer_when_points_not_ready_has_eta(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        not_ready_points,
        mock_driver_tags_v1_match_profile,
        experiments3,
):
    exp3_recorder = experiments3.record_match_tries(
        'cargo_orders_timers_settings_lavka',
    )

    waybill_info_pull_dispatch['execution']['points'][1]['is_resolved'] = False
    waybill_info_pull_dispatch['execution']['points'][1][
        'visit_status'
    ] = 'pending'
    waybill_info_pull_dispatch['execution']['points'][0][
        'was_ready_at'
    ] = '2021-03-23T07:40:49.939497+00:00'
    waybill_info_pull_dispatch['execution']['points'][1][
        'was_ready_at'
    ] = '2021-03-23T07:43:49.939497+00:00'

    for idx in not_ready_points:
        waybill_info_pull_dispatch['execution']['points'][idx][
            'visit_status'
        ] = 'pending'
        del waybill_info_pull_dispatch['execution']['points'][idx][
            'was_ready_at'
        ]

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    eta_action = next(filter(lambda x: x['type'] == 'eta', actions), None)

    assert eta_action is None

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    assert match_tries[0].kwargs['region_id'] == 213
    assert match_tries[0].kwargs['depot_id'] == '23456'


@TIMER_CONFIG_ETA_TEXT
@DEFAULT_CLIENT_KIND_CONFIG
async def test_pull_dispatch_show_text(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_with_same_source_point,
        mock_driver_tags_v1_match_profile,
):
    waybill_info_with_same_source_point['dispatch']['is_pull_dispatch'] = True
    waybill_info_with_same_source_point['segments'][0]['custom_context'] = {
        'depot_id': '123456',
    }

    waybill_info_with_same_source_point['execution']['points'][0][
        'was_ready_at'
    ] = '2020-08-18T13:40:49.939497+00:00'
    waybill_info_with_same_source_point['execution']['points'][1][
        'was_ready_at'
    ] = '2020-08-18T13:43:49.939497+00:00'

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    eta_action = next(filter(lambda x: x['type'] == 'eta', actions), None)

    assert eta_action == EXPECTED_ACTION_ETA_TEXT


AUTH_HEADERS_V1 = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}
AUTH_HEADERS_V2 = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.55',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'ios',
}


@TIMER_CONFIG_AUTH_PARAMS
@DEFAULT_CLIENT_KIND_CONFIG
@pytest.mark.parametrize(
    ['eta_action_value', 'headers'],
    [
        (EXPECTED_ACTION_V1, AUTH_HEADERS_V1),
        (EXPECTED_ACTION_V2, AUTH_HEADERS_V2),
    ],
)
async def test_pull_dispatch_skip_pickup_timer_auth_kwargs(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        eta_action_value,
        headers,
        mock_driver_tags_v1_match_profile,
):
    waybill_info_pull_dispatch['execution']['points'][0]['is_resolved'] = False
    waybill_info_pull_dispatch['execution']['points'][1]['is_resolved'] = False
    waybill_info_pull_dispatch['execution']['points'][1][
        'was_ready_at'
    ] = '2021-03-23T07:43:49.939497+00:00'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/state',
        headers=headers,
        json={'cargo_ref_id': 'order/' + default_order_id},
    )
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    eta_action = next(filter(lambda x: x['type'] == 'eta', actions), None)

    assert eta_action == eta_action_value


@COUNTDOWN_WITHOUT_TIME_CONFIG
@DEFAULT_CLIENT_KIND_CONFIG
@pytest.mark.parametrize('pull_dispatch_enabled', [True])
async def test_pull_dispatch_timer_time_not_set(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_with_same_source_point,
        pull_dispatch_enabled,
        mock_driver_tags_v1_match_profile,
):
    waybill_info_with_same_source_point['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled
    waybill_info_with_same_source_point['segments'][0]['custom_context'] = {
        'depot_id': '123456',
    }

    waybill_info_with_same_source_point['execution']['points'][0][
        'eta'
    ] = '2020-08-18T14:40:49.939497+00:00'

    waybill_info_with_same_source_point['execution']['points'][0][
        'eta_calculation_awaited'
    ] = False

    waybill_info_with_same_source_point['execution']['points'][0][
        'was_ready_at'
    ] = '2020-08-18T13:40:49.939497+00:00'
    waybill_info_with_same_source_point['execution']['points'][1][
        'was_ready_at'
    ] = '2020-08-18T13:43:49.939497+00:00'

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    eta_action = next(filter(lambda x: x['type'] == 'eta', actions), None)

    assert eta_action == {
        'calculation_awaited': False,
        'eta': '2020-08-18T14:40:49.939497+00:00',
        'type': 'eta',
        'eta_type': 'countdown',
        'description': 'Еще заказ',
        'colors': ['black', 'red'],
        'eta_times': [
            '2020-08-18T14:39:49.939497+00:00',
            '2020-08-18T14:40:49.939497+00:00',
        ],
    }


@COUNTDOWN_WITHOUT_TIME_CONFIG_AND_ALERT_DURATION
@DEFAULT_CLIENT_KIND_CONFIG
async def test_pull_dispatch_timer_time_not_set_without_alert(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_with_same_source_point,
        mock_driver_tags_v1_match_profile,
):
    waybill_info_with_same_source_point['dispatch']['is_pull_dispatch'] = True
    waybill_info_with_same_source_point['segments'][0]['custom_context'] = {
        'depot_id': '123456',
    }

    waybill_info_with_same_source_point['execution']['points'][0][
        'eta'
    ] = '2020-08-18T14:40:49.939497+00:00'

    waybill_info_with_same_source_point['execution']['points'][0][
        'eta_calculation_awaited'
    ] = False

    waybill_info_with_same_source_point['execution']['points'][0][
        'was_ready_at'
    ] = '2020-08-18T13:40:49.939497+00:00'
    waybill_info_with_same_source_point['execution']['points'][1][
        'was_ready_at'
    ] = '2020-08-18T13:43:49.939497+00:00'

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    actions = response.json()['current_point']['actions']
    eta_action = next(filter(lambda x: x['type'] == 'eta', actions), None)

    assert eta_action == {
        'calculation_awaited': False,
        'eta': '2020-08-18T14:40:49.939497+00:00',
        'type': 'eta',
        'eta_type': 'countdown',
        'description': 'Еще заказ',
        'colors': ['black', 'red'],
        'eta_times': ['2020-08-18T14:40:49.939497+00:00'],
    }
