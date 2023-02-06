# pylint: disable=C0302

import pytest


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {'__default__': False, 'claim_route_points': True},
    },
)
@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
async def test_pull_dispatch_filter_route(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        pull_dispatch_enabled,
        mock_driver_tags_v1_match_profile,
):
    waybill_info_pull_dispatch['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled
    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    expected_current_route_pts = [
        'source',
        'destination',
        'destination',
        'destination',
    ]
    if not pull_dispatch_enabled:
        expected_current_route_pts = [
            'source',
            *expected_current_route_pts,
            'destination',
        ]
    assert expected_current_route_pts == [
        pt['type'] for pt in response.json()['current_route']
    ]


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {'__default__': False, 'claim_route_points': True},
    },
)
@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
async def test_pull_dispatch_filter_return_in_route(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        pull_dispatch_enabled,
        mock_driver_tags_v1_match_profile,
):
    waybill_info_pull_dispatch['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled

    waybill_info_pull_dispatch['execution']['points'][0][
        'is_return_required'
    ] = True

    waybill_info_pull_dispatch['execution']['points'][1][
        'is_return_required'
    ] = True

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    expected_current_route_pts = [
        'source',
        'destination',
        'destination',
        'destination',
    ]
    if not pull_dispatch_enabled:
        expected_current_route_pts = [
            'source',
            *expected_current_route_pts,
            'destination',
            'return',
            'return',
        ]
    assert expected_current_route_pts == [
        pt['type'] for pt in response.json()['current_route']
    ]


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {'__default__': False, 'claim_route_points': True},
    },
)
@pytest.mark.parametrize('current_point_index', [0, 1, 2, 3, 4, 5])
async def test_pull_dispatch_current_point_always_in_route(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        current_point_index,
        mock_driver_tags_v1_match_profile,
):
    waybill_info_pull_dispatch['dispatch']['is_pull_dispatch'] = True

    for point_idx in range(current_point_index):
        waybill_info_pull_dispatch['execution']['points'][point_idx][
            'is_resolved'
        ] = True

    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    current_point = response.json()['current_point']
    assert current_point['id'] in [
        pt['id'] for pt in response.json()['current_route']
    ]


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {
            '__default__': False,
            'hide_pull_dispatch_fake_item': True,
        },
    },
)
async def test_pull_dispatch_hide_pull_dispatch_fake_item_in_state(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        mock_driver_tags_v1_match_profile,
):
    response = await get_driver_cargo_state(default_order_id)
    assert response.status_code == 200

    current_route = response.json()['current_route']
    expected_items = [{'quantity': 1, 'title': 'meow 2'}]

    for point in current_route:
        assert expected_items == point['items']


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_orders_pull_dispatch_filters',
    consumers=['cargo-orders/build-lavka-timer-settings'],
    clauses=[],
    default_value={
        'enabled': True,
        'filters': {
            '__default__': False,
            'hide_pull_dispatch_fake_item': True,
        },
    },
)
@pytest.mark.parametrize(
    'waybill_tpl, point_id, expected_response',
    [
        pytest.param(
            'cargo-dispatch/v1_waybill_info_tpl.json',
            642500,
            {'items': []},
            id='destination_point',
        ),
    ],
)
async def test_pull_dispatch_hide_pull_dispatch_fake_item_in_items(
        taxi_cargo_orders,
        mock_driver_tags_v1_match_profile,
        get_driver_cargo_items,
        default_order_id,
        fetch_order,
        waybill_state,
        point_id,
        expected_response,
        waybill_tpl,
):
    waybill_info = waybill_state.load_waybill(waybill_tpl)

    waybill_info['dispatch']['is_pull_dispatch'] = True
    waybill_info['waybill']['items'].append(
        {
            'delivered_quantity': 1,
            'dropoff_point': 'seg_1_point_2',
            'item_id': 'item1',
            'pickup_point': 'seg_1_point_1',
            'quantity': 1,
            'return_point': 'seg_1_point_3',
            'title': 'PullDispatchFakeItem',
        },
    )

    cargo_ref_id = 'order/' + default_order_id

    response = await get_driver_cargo_items(cargo_ref_id, point_id)

    assert response.json() == expected_response
