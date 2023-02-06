import json

import pytest


SETCAR_CREATE_URL = '/v2/setcar'
PARAMS = {
    'driver': {
        'park_id': 'park1',
        'driver_profile_id': 'driver1',
        'alias_id': '4d605a2849d747079b5d8c7012830419',
    },
    'order_id': 'test_order_id',
}


# pylint: disable=C0103
pytestmark = [
    pytest.mark.translations(
        taximeter_backend_driver_messages={
            'notification.key': {'ru': 'notify'},
        },
    ),
    pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        is_config=True,
        name='driver_orders_builder_settings',
        consumers=['driver-orders-builder/setcar'],
        clauses=[],
        default_value={'enable_requirements_rebuild': True},
    ),
]


async def _check_comment(
        taxi_driver_orders_builder,
        load_json,
        redis_store,
        description,
        expected_description,
):
    setcar_json = load_json('setcar.json')
    if description is not None:
        setcar_json['description'] = description

    request = PARAMS
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200
    response_json = response.json()['setcar']
    assert response_json['description'] == expected_description
    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)
    assert redis_dict['description'] == expected_description


@pytest.mark.parametrize(
    ('exp_zone', 'request_description', 'expected_description'),
    (
        pytest.param(
            'adler', 'no changes', 'no changes', id='no_changes_without_exp',
        ),
        pytest.param(
            'moscow', None, 'notify', id='only_notification_without_comment',
        ),
        pytest.param(
            'moscow',
            'hello',
            'notify <DELIMETER> hello',
            id='notification_with_comment',
        ),
    ),
)
@pytest.mark.experiments3()
async def test_setcar_comment_extension(
        taxi_driver_orders_builder,
        load_json,
        redis_store,
        mockserver,
        experiments3,
        exp_zone,
        request_description,
        expected_description,
        order_proc,
):
    experiments3.add_experiment(
        clauses=[
            {
                'predicate': {
                    'type': 'in_set',
                    'init': {
                        'set': [exp_zone],
                        'arg_name': 'nearest_zone',
                        'set_elem_type': 'string',
                    },
                },
                'enabled': True,
                'title': '',
                'value': {
                    'notification_key': 'notification.key',
                    'template': '{notification} <DELIMETER> {comment}',
                },
            },
        ],
        name='order_comment_extension',
        consumers=['driver-orders-builder/setcar'],
        match={'enabled': True, 'predicate': {'type': 'true'}},
    )

    order_proc.set_file(load_json, 'order_core_response.json')
    if request_description:
        order_proc.order_proc['fields']['order']['request'][
            'comment'
        ] = request_description

    await _check_comment(
        taxi_driver_orders_builder,
        load_json,
        redis_store,
        request_description,
        expected_description,
    )


@pytest.mark.parametrize(
    ('nearest_zone', 'point_a', 'point_b', 'tariff', 'expected_description'),
    (
        pytest.param(
            'moscow',
            [37.5, 55.7],
            [37.5, 55.7],
            'comfort',
            'notify',
            id='exp_matched',
        ),
        pytest.param(
            'adler',
            [37.5, 55.7],
            [37.5, 55.7],
            'comfort',
            'failed',
            id='failed_by_zone',
        ),
        pytest.param(
            'moscow',
            [36.5, 55.7],
            [37.5, 55.7],
            'comfort',
            'failed',
            id='failed_by_a',
        ),
        pytest.param(
            'moscow',
            [37.5, 55.7],
            [37.5, 56.7],
            'comfort',
            'failed',
            id='failed_by_b',
        ),
        pytest.param(
            'moscow',
            [37.5, 55.7],
            [37.5, 55.7],
            'econom',
            'failed',
            id='failed_by_tariff',
        ),
    ),
)
@pytest.mark.experiments3()
async def test_experiment_matching(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        redis_store,
        experiments3,
        nearest_zone,
        point_a,
        point_b,
        tariff,
        expected_description,
        order_proc,
):
    experiments3.add_experiment(
        clauses=[
            {
                'predicate': {
                    'type': 'all_of',
                    'init': {
                        'predicates': [
                            {
                                'type': 'in_set',
                                'init': {
                                    'set': ['moscow'],
                                    'arg_name': 'nearest_zone',
                                    'set_elem_type': 'string',
                                },
                            },
                            {
                                'type': 'falls_inside',
                                'init': {
                                    'arg_name': 'point_a',
                                    'arg_type': 'linear_ring',
                                    'value': [
                                        [37.3, 55.9],
                                        [37.7, 55.9],
                                        [37.7, 55.5],
                                        [37.3, 55.5],
                                    ],
                                },
                            },
                            {
                                'type': 'falls_inside',
                                'init': {
                                    'arg_name': 'point_b',
                                    'arg_type': 'linear_ring',
                                    'value': [
                                        [37.3, 55.9],
                                        [37.7, 55.9],
                                        [37.7, 55.5],
                                        [37.3, 55.5],
                                    ],
                                },
                            },
                            {
                                'type': 'in_set',
                                'init': {
                                    'set': ['comfort'],
                                    'arg_name': 'tariff',
                                    'set_elem_type': 'string',
                                },
                            },
                        ],
                    },
                },
                'enabled': True,
                'title': '',
                'value': {
                    'notification_key': 'notification.key',
                    'template': '{notification}',
                },
            },
        ],
        name='order_comment_extension',
        consumers=['driver-orders-builder/setcar'],
        match={'enabled': True, 'predicate': {'type': 'true'}},
    )

    order_proc.set_file(load_json, 'order_core_response.json')
    order_proc.order_proc['fields']['order']['request']['comment'] = 'failed'
    order_proc.order_proc['fields']['order']['nz'] = nearest_zone
    order_proc.order_proc['fields']['order']['request']['source'][
        'geopoint'
    ] = point_a
    order_proc.order_proc['fields']['order']['request']['destinations'][0][
        'geopoint'
    ] = point_b
    order_proc.order_proc['fields']['candidates'][0]['tariff_class'] = tariff

    await _check_comment(
        taxi_driver_orders_builder,
        load_json,
        redis_store,
        'failed',
        expected_description,
    )


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'enable_order_proc_request': True,
        'enable_requirements_rebuild': True,
    },
)
@pytest.mark.config(
    LONG_TRIP_CRITERIA={
        '__default__': {
            '__default__': {
                'apply': 'both',
                'distance': 50000,
                'duration': 24000,
            },
        },
    },
)
async def test_has_from_address_when_original_setcar_has_no_comment(
        taxi_driver_orders_builder,
        load_json,
        mockserver,
        setcar_create_params,
        order_proc,
):
    order_proc.set_file(load_json, 'order_core_response3.json')

    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200, response.text
    resp = response.json()['setcar_push']

    from_item = None
    for item in resp['ui']['acceptance_items']:
        if item['type'] == 'default' and item['title'] == 'Откуда:':
            from_item = item

    assert from_item is not None
