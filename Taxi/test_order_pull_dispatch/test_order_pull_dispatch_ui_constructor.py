# pylint: disable=C0302

import pytest


def add_ui_to_experiment(experiments3, corp_client_id):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_driver_state_ui',
        consumers=['cargo-orders/ui'],
        clauses=[
            {
                'alias': 'lavka1',
                'enabled': True,
                'extension_method': 'replace',
                'is_paired_signal': False,
                'is_signal': False,
                'predicate': {
                    'init': {
                        'arg_name': 'corp_client_id',
                        'set': [corp_client_id],
                        'set_elem_type': 'string',
                    },
                    'type': 'in_set',
                },
                'title': 'Лавка 1',
                'value': {
                    'screens': [
                        {
                            'name': 'arrive_source_screen',
                            'ui': {'blocks': [{'type': 'cost_plate'}]},
                        },
                        {
                            'name': 'arrive_screen',
                            'ui': {
                                'blocks': [
                                    {'type': 'cost_plate'},
                                    {'type': 'route'},
                                    {'type': 'comment'},
                                ],
                            },
                        },
                        {
                            'name': 'pickup_screen',
                            'ui': {
                                'blocks': [
                                    {'type': 'cost_plate'},
                                    {'type': 'comment'},
                                ],
                            },
                        },
                        {
                            'name': 'dropoff_screen',
                            'ui': {'blocks': [{'type': 'comment'}]},
                        },
                        {
                            'name': 'going_back_screen',
                            'ui': {'blocks': [{'type': 'route'}]},
                        },
                    ],
                },
            },
        ],
        default_value={},
    )


def add_ui_nested_blocks(experiments3, corp_client_id):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_orders_driver_state_ui',
        consumers=['cargo-orders/ui'],
        clauses=[
            {
                'alias': 'lavka1',
                'enabled': True,
                'extension_method': 'replace',
                'is_paired_signal': False,
                'is_signal': False,
                'predicate': {
                    'init': {
                        'arg_name': 'corp_client_id',
                        'set': [corp_client_id],
                        'set_elem_type': 'string',
                    },
                    'type': 'in_set',
                },
                'title': 'Лавка 1',
                'value': {
                    'screens': [
                        {
                            'name': 'arrive_source_screen',
                            'ui': {'blocks': [{'type': 'cost_plate'}]},
                        },
                        {
                            'name': 'arrive_screen',
                            'ui': {
                                'blocks': [{'type': 'constructor_items'}],
                                'nested_blocks': [
                                    [
                                        {
                                            'name': 'door_code',
                                            'type': 'text',
                                            'width_percentage': 30,
                                        },
                                        {
                                            'name': 'porch',
                                            'width_percentage': 70,
                                        },
                                    ],
                                    [
                                        {
                                            'name': 'flat',
                                            'type': 'text',
                                            'width_percentage': 60,
                                        },
                                        {
                                            'name': 'floor',
                                            'type': 'text',
                                            'width_percentage': 40,
                                        },
                                    ],
                                    [
                                        {
                                            'name': 'building_name',
                                            'width_percentage': 50,
                                        },
                                        {
                                            'name': 'door_code_extra',
                                            'width_percentage': 30,
                                        },
                                        {
                                            'name': 'doorbell_name',
                                            'width_percentage': 20,
                                        },
                                    ],
                                    [{'name': 'comment', 'type': 'text'}],
                                ],
                            },
                        },
                        {
                            'name': 'pickup_screen',
                            'ui': {
                                'blocks': [
                                    {'type': 'cost_plate'},
                                    {'type': 'comment'},
                                ],
                            },
                        },
                        {
                            'name': 'dropoff_screen',
                            'ui': {'blocks': [{'type': 'comment'}]},
                        },
                        {
                            'name': 'going_back_screen',
                            'ui': {'blocks': [{'type': 'route'}]},
                        },
                    ],
                },
            },
        ],
        default_value={},
    )


@pytest.mark.parametrize('pull_dispatch_enabled', [True, False])
async def test_pull_dispatch_ui_build(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        experiments3,
        pull_dispatch_enabled,
        mock_driver_tags_v1_match_profile,
        corp_client_id='5e36732e2bc54e088b1466e08e31c486',
):
    waybill_info_pull_dispatch['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled

    add_ui_to_experiment(experiments3, corp_client_id)

    response = await get_driver_cargo_state(default_order_id)

    assert response.status_code == 200

    if not pull_dispatch_enabled:
        assert 'ui' not in response.json()
    else:
        assert 'ui' in response.json()
        assert response.json()['ui'] == {
            'blocks': [
                {'type': 'cost_plate'},
                {'type': 'route'},
                {'type': 'comment'},
            ],
        }


async def test_pull_dispatch_arrive_screens(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        experiments3,
        mock_driver_tags_v1_match_profile,
        pull_dispatch_enabled=True,
        corp_client_id='5e36732e2bc54e088b1466e08e31c486',
):
    waybill_info_pull_dispatch['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled

    add_ui_to_experiment(experiments3, corp_client_id)

    response = await get_driver_cargo_state(default_order_id)

    assert response.status_code == 200
    assert response.json()['ui'] == {
        'blocks': [
            {'type': 'cost_plate'},
            {'type': 'route'},
            {'type': 'comment'},
        ],
    }

    waybill_info_pull_dispatch['execution']['points'][0]['is_resolved'] = False

    response = await get_driver_cargo_state(default_order_id)

    assert response.status_code == 200
    assert response.json()['ui'] == {'blocks': [{'type': 'cost_plate'}]}


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_batch_skip_arrive_screen',
    consumers=['cargo-orders/taximeter-api'],
    clauses=[],
    default_value={
        'enable': True,
        'skip_arrive_screen': True,
        'pickup_label_tanker_key': '123',
    },
)
async def test_pull_dispatch_dropoff_screen(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        experiments3,
        mock_driver_tags_v1_match_profile,
        pull_dispatch_enabled=True,
        corp_client_id='5e36732e2bc54e088b1466e08e31c486',
):
    waybill_info_pull_dispatch['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled

    add_ui_to_experiment(experiments3, corp_client_id)

    exp3_recorder = experiments3.record_match_tries(
        'cargo_orders_driver_state_ui',
    )

    response = await get_driver_cargo_state(default_order_id)

    assert response.status_code == 200
    assert response.json()['ui'] == {'blocks': [{'type': 'comment'}]}

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    assert match_tries[0].kwargs['region_id'] == 213
    assert match_tries[0].kwargs['depot_id'] == '23456'


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='cargo_batch_skip_arrive_screen',
    consumers=['cargo-orders/taximeter-api'],
    clauses=[],
    default_value={
        'enable': True,
        'skip_arrive_screen': True,
        'pickup_label_tanker_key': '123',
    },
)
async def test_pull_dispatch_going_back_screen(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch,
        experiments3,
        mock_driver_tags_v1_match_profile,
        pull_dispatch_enabled=True,
        corp_client_id='5e36732e2bc54e088b1466e08e31c486',
):
    waybill_info_pull_dispatch['dispatch'][
        'is_pull_dispatch'
    ] = pull_dispatch_enabled

    waybill_info_pull_dispatch['execution']['points'][0]['is_resolved'] = True
    waybill_info_pull_dispatch['execution']['points'][1]['is_resolved'] = True
    waybill_info_pull_dispatch['execution']['points'][2]['is_resolved'] = True
    waybill_info_pull_dispatch['execution']['points'][3]['is_resolved'] = True
    waybill_info_pull_dispatch['execution']['points'][4]['is_resolved'] = True

    add_ui_to_experiment(experiments3, corp_client_id)

    response = await get_driver_cargo_state(default_order_id)

    assert response.status_code == 200
    assert response.json()['ui'] == {'blocks': [{'type': 'route'}]}


async def test_pull_dispatch_ui_build_nested(
        taxi_cargo_orders,
        mock_waybill_info,
        get_driver_cargo_state,
        default_order_id,
        waybill_info_pull_dispatch_extra_fields,
        experiments3,
        mock_driver_tags_v1_match_profile,
        corp_client_id='5e36732e2bc54e088b1466e08e31c486',
):

    add_ui_nested_blocks(experiments3, corp_client_id)

    response = await get_driver_cargo_state(default_order_id)

    assert response.status_code == 200
    assert 'ui' in response.json()
    assert response.json()['ui'] == {
        'blocks': [{'type': 'constructor_items'}],
        'constructor_items': [
            [
                {
                    'type': 'text',
                    'title': 'ride_card_cargo_plate_address_details_door_code',
                    'value': '123',
                    'width_percentage': 30.0,
                },
                {
                    'title': 'ride_card_cargo_plate_address_details_porch',
                    'value': '4',
                    'type': 'text',
                    'width_percentage': 70.0,
                },
            ],
            [
                {
                    'type': 'text',
                    'title': 'ride_card_cargo_plate_address_details_flat',
                    'value': '-',
                    'width_percentage': 60.0,
                },
                {
                    'type': 'text',
                    'title': 'ride_card_cargo_plate_address_details_floor',
                    'value': '-',
                    'width_percentage': 40.0,
                },
            ],
            [
                {
                    'type': 'text',
                    'title': (
                        'ride_card_cargo_plate_address_details_building_name'
                    ),
                    'value': 'БК Сити',
                    'width_percentage': 50.0,
                },
                {
                    'type': 'text',
                    'title': (
                        'ride_card_cargo_plate_address_details_door_code_extra'
                    ),
                    'value': '456',
                    'width_percentage': 30.0,
                },
                {
                    'type': 'text',
                    'title': (
                        'ride_card_cargo_plate_address_details_doorbell_name'
                    ),
                    'value': 'Не звоните',
                    'width_percentage': 20.0,
                },
            ],
            [
                {
                    'type': 'text',
                    'title': 'comment',
                    'value': 'вторая точка коммент',
                    'width_percentage': 100.0,
                },
            ],
        ],
    }
