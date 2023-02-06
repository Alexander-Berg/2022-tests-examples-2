import copy
import json

import pytest

from tests_driver_orders_builder import utils

_ORDER_SETCAR_ITEMS = 'Order:SetCar:Items'
PARK_ID = 'park1'
ALIAS_ID = '4d605a2849d747079b5d8c7012830419'

MOCKED_NOW = '2021-08-18T09:00:00+03:00'
GOOD_CHANGE_ID = '36cae0c2c9b8493f5a5bb2dca5b9fa21'


@pytest.mark.parametrize(
    'change_id',
    [GOOD_CHANGE_ID, '000000c2c9b8493f5a5bb2dca5000000'],
    ids=['good_change_id', 'bad_change_id'],
)
@pytest.mark.now(MOCKED_NOW)
async def test_user_ready(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        mockserver,
        change_id,
        order_proc,
):
    order_proc_json = load_json('order_core_fields_user_ready_response.json')
    order_proc.order_proc['fields']['changes'] = order_proc_json['document'][
        'changes'
    ]
    setcar_item = load_json('setcar.json')
    setcar_item['client_chat_id'] = '0000000000'  # To not forming push
    redis_store.hset(
        _ORDER_SETCAR_ITEMS + ':' + PARK_ID, ALIAS_ID, json.dumps(setcar_item),
    )

    response = await taxi_driver_orders_builder.post(
        '/v2/setcar/update/user_ready',
        headers={'Content-type': 'application/json'},
        data=json.dumps(
            {
                'driver': {
                    'park_id': PARK_ID,
                    'driver_profile_id': 'driver1',
                    'alias_id': ALIAS_ID,
                },
                'order_id': 'test_order_id',
                'change_id': change_id,
            },
        ),
    )

    redis_setcar = json.loads(
        redis_store.hget(_ORDER_SETCAR_ITEMS + ':' + PARK_ID, ALIAS_ID),
    )
    expected_setcar = copy.deepcopy(setcar_item)

    if change_id == GOOD_CHANGE_ID:
        assert response.status_code == 200
        assert response.json()['setcar'] == expected_setcar
    else:
        assert response.status_code == 410

    assert redis_setcar == expected_setcar


@pytest.mark.parametrize(
    'change_id, use_cos',
    [
        pytest.param(GOOD_CHANGE_ID, True, id='good_change_id_use_COS'),
        pytest.param(GOOD_CHANGE_ID, False, id='good_change_id_wo_COS'),
        pytest.param(
            '000000c2c9b8493f5a5bb2dca5000000', None, id='bad_change',
        ),
    ],
)
@pytest.mark.now(MOCKED_NOW)
async def test_client_geo_sharing(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        mockserver,
        change_id,
        use_cos,
        taxi_config,
        order_proc,
):
    order_proc_json = load_json('order_core_fields_geo_sharing_response.json')
    order_proc.order_proc['fields']['changes'] = order_proc_json['document'][
        'changes'
    ]
    order_proc.order_proc['fields']['order']['user_id'] = order_proc_json[
        'document'
    ]['order']['user_id']
    setcar_item = load_json('setcar.json')
    redis_store.hset(
        _ORDER_SETCAR_ITEMS + ':' + PARK_ID, ALIAS_ID, json.dumps(setcar_item),
    )
    utils.set_order_status(
        redis_store, PARK_ID, ALIAS_ID, utils.OrderStatus.Waiting,
    )
    if use_cos is not None:
        taxi_config.set_values({'TAXIMETER_USE_COS_FOR_GEO_SHARING': use_cos})

    response = await taxi_driver_orders_builder.post(
        '/v2/setcar/update/client_geo_sharing',
        headers={'Content-type': 'application/json'},
        data=json.dumps(
            {
                'driver': {
                    'park_id': PARK_ID,
                    'driver_profile_id': 'driver1',
                    'alias_id': ALIAS_ID,
                },
                'order_id': 'test_order_id',
                'change_id': change_id,
            },
        ),
    )

    redis_setcar = json.loads(
        redis_store.hget(_ORDER_SETCAR_ITEMS + ':' + PARK_ID, ALIAS_ID),
    )
    expected_setcar = copy.deepcopy(setcar_item)

    if change_id == GOOD_CHANGE_ID:
        assert response.status_code == 200
        expected_setcar['client_geo_sharing'] = {
            'is_enabled': True,
            'track_id': 'some_user_id',
        }
        assert response.json()['setcar'] == expected_setcar
    else:
        assert response.status_code == 410

    assert redis_setcar == expected_setcar


CHANGE_POINT_B = '53bbef67e883ffb0edd5a296996fd871'
ADD_ROUTE_POINT = 'bed84746c0e2556eaaa220b661858c92'
CHANGE_ROUTE_POINT = 'c3107a1c8064bf3d0219541c0d871780'
CHANGE_POINT_B_WITH_ROUTE_POINT = '559e26c4f6d04c5f3b0c01d7b24ad85b'
REMOVE_ROUTE_POINT = '63666690091787cf2d0e7311cbcf4d8c'

DEFAULT_ADDRESS_TO = {
    'Street': 'Петрозаводская улица, 34',
    'Lat': 55.867584,
    'Lon': 37.489059,
    'Region': '',
    'Order': 1,
    'ArrivalDistance': 20,
}
CHANGED_ADDRESS_TO = {
    'Street': 'Петрозаводская улица, 32А',
    'Lat': 55.86,
    'Lon': 37.48,
    'Region': '',
    'Order': 1,
    'ArrivalDistance': 20,
}
SOME_ROUTE_POINTS = [
    {
        'Street': 'Петрозаводская улица, 11к1',
        'Lat': 55.86,
        'Lon': 37.50,
        'Region': '',
        'Order': 1,
        'ArrivalDistance': 20,
    },
]


@pytest.mark.parametrize(
    'change_id, expected_address_to, expected_route_points',
    [
        ([CHANGE_POINT_B, DEFAULT_ADDRESS_TO, []]),
        (
            [
                ADD_ROUTE_POINT,
                DEFAULT_ADDRESS_TO,
                [
                    {
                        'Street': 'Петрозаводская улица, 10',
                        'Lat': 55.86,
                        'Lon': 37.50,
                        'Region': '',
                        'Order': 1,
                        'ArrivalDistance': 20,
                    },
                ],
            ]
        ),
        (
            [
                CHANGE_ROUTE_POINT,
                DEFAULT_ADDRESS_TO,
                [
                    {
                        'Street': 'Петрозаводская улица, 11к1',
                        'Lat': 55.86,
                        'Lon': 37.50,
                        'Region': '',
                        'Order': 1,
                        'ArrivalDistance': 20,
                    },
                ],
            ]
        ),
        (
            [
                CHANGE_POINT_B_WITH_ROUTE_POINT,
                CHANGED_ADDRESS_TO,
                [
                    {
                        'Street': 'Петрозаводская улица, 11к1',
                        'Lat': 55.86,
                        'Lon': 37.50,
                        'Region': '',
                        'Order': 1,
                        'ArrivalDistance': 20,
                    },
                ],
            ]
        ),
        ([REMOVE_ROUTE_POINT, CHANGED_ADDRESS_TO, []]),
    ],
    ids=[
        'change_point_b',
        'add_route_point',
        'change_route_point',
        'change_point_b_with_route_point',
        'remove_route_point',
    ],
)
@pytest.mark.now(MOCKED_NOW)
async def test_destinations(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        mockserver,
        change_id,
        expected_address_to,
        expected_route_points,
        order_proc,
):
    order_proc_json = load_json('order_core_fields_destinations_response.json')
    order_proc.order_proc['fields']['changes'] = order_proc_json['document'][
        'changes'
    ]
    setcar_item = load_json('setcar.json')
    redis_store.hset(
        _ORDER_SETCAR_ITEMS + ':' + PARK_ID, ALIAS_ID, json.dumps(setcar_item),
    )
    utils.set_order_status(
        redis_store, PARK_ID, ALIAS_ID, utils.OrderStatus.Waiting,
    )
    if change_id in (
            ADD_ROUTE_POINT,
            CHANGE_ROUTE_POINT,
            CHANGE_POINT_B_WITH_ROUTE_POINT,
    ):
        expected_address_to['Order'] = 2

    if change_id == REMOVE_ROUTE_POINT:
        expected_address_to['Order'] = 1
        setcar_item['route_points'] = SOME_ROUTE_POINTS

    response = await taxi_driver_orders_builder.post(
        '/v2/setcar/update/destinations',
        headers={'Content-type': 'application/json'},
        data=json.dumps(
            {
                'driver': {
                    'park_id': PARK_ID,
                    'driver_profile_id': 'driver1',
                    'alias_id': ALIAS_ID,
                },
                'order_id': 'test_order_id',
                'change_id': change_id,
            },
        ),
    )

    redis_setcar = json.loads(
        redis_store.hget(_ORDER_SETCAR_ITEMS + ':' + PARK_ID, ALIAS_ID),
    )
    expected_setcar = copy.deepcopy(setcar_item)
    expected_setcar['address_to'] = expected_address_to
    expected_setcar['route_points'] = expected_route_points
    del expected_setcar['driver_fixed_price']
    del expected_setcar['fixed_price']

    assert response.status_code == 200
    assert response.json()['setcar']['address_to'] == expected_address_to
    assert response.json()['setcar']['route_points'] == expected_route_points
    assert redis_setcar == expected_setcar


@pytest.mark.config(
    DRIVER_ORDERS_BUILDER_SETCAR_USE_CARGO_FIXEDPRICE_ENABLED=True,
)
@pytest.mark.now(MOCKED_NOW)
async def test_destinations_with_cargo_fixed_price(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        mockserver,
        order_proc,
        mock_cargo_setcar_data,
):
    order_proc.set_file(load_json, 'order_core_response_cargo.json')
    order_proc_json = load_json('order_core_fields_destinations_response.json')
    order_proc.order_proc['fields']['changes'] = order_proc_json['document'][
        'changes'
    ]

    mock_cargo_setcar_data(
        pricing={
            'price': {'total': '123', 'client_total': '165'},
            'taxi_pricing_response_parts': {
                'taximeter_meta': {
                    'max_distance_from_b': 137.0,
                    'show_price_in_taximeter': True,
                },
            },
        },
    )

    setcar_item = load_json('setcar.json')
    redis_store.hset(
        _ORDER_SETCAR_ITEMS + ':' + PARK_ID, ALIAS_ID, json.dumps(setcar_item),
    )
    utils.set_order_status(
        redis_store, PARK_ID, ALIAS_ID, utils.OrderStatus.Waiting,
    )

    response = await taxi_driver_orders_builder.post(
        '/v2/setcar/update/destinations',
        headers={'Content-type': 'application/json'},
        data=json.dumps(
            {
                'driver': {
                    'park_id': PARK_ID,
                    'driver_profile_id': 'driver1',
                    'alias_id': ALIAS_ID,
                },
                'order_id': 'test_order_id',
                'change_id': CHANGE_POINT_B,
            },
        ),
    )
    assert response.status_code == 200

    redis_setcar = json.loads(
        redis_store.hget(_ORDER_SETCAR_ITEMS + ':' + PARK_ID, ALIAS_ID),
    )

    assert redis_setcar['driver_fixed_price'] == {
        'max_distance': 137.0,
        'price': 123.0,
        'show': True,
    }
    assert redis_setcar['fixed_price'] == {
        'max_distance': 137.0,
        'price': 165.0,
        'show': True,
    }


DO_NOT_CALL_CHANGE_ID = GOOD_CHANGE_ID
PLS_CALL_CHANGE_ID = 'pls_call_change_id'


@pytest.mark.parametrize(
    'change_id',
    [
        DO_NOT_CALL_CHANGE_ID,
        PLS_CALL_CHANGE_ID,
        '000000c2c9b8493f5a5bb2dca5000000',
    ],
    ids=['dont_call_change_id', 'pls_call_change_id', 'bad_change_id'],
)
@pytest.mark.parametrize(
    'requirements, pretty_requirements_added, pretty_requirements_deleted',
    [
        ([], [{'id': 'dont_call'}], []),
        (
            [{'id': 'some_requiement'}, {'id': 'some_requiement2'}],
            [
                {'id': 'some_requiement'},
                {'id': 'some_requiement2'},
                {'id': 'dont_call'},
            ],
            [{'id': 'some_requiement'}, {'id': 'some_requiement2'}],
        ),
        (
            [{'id': 'some_requiement'}, {'id': 'dont_call'}],
            [{'id': 'some_requiement'}, {'id': 'dont_call'}],
            [{'id': 'some_requiement'}],
        ),
    ],
    ids=[
        'empty_requrements',
        'some_requirements',
        'requirements_with_dont_call',
    ],
)
@pytest.mark.now(MOCKED_NOW)
async def test_dont_call(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        mockserver,
        change_id,
        requirements,
        pretty_requirements_added,
        pretty_requirements_deleted,
        order_proc,
):
    order_proc_json = load_json('order_core_fields_dont_call_response.json')
    order_proc.order_proc['fields']['changes'] = order_proc_json['document'][
        'changes'
    ]
    setcar_item = load_json('setcar.json')
    setcar_item['requirement_list'] = requirements
    redis_store.hset(
        _ORDER_SETCAR_ITEMS + ':' + PARK_ID, ALIAS_ID, json.dumps(setcar_item),
    )
    utils.set_order_status(
        redis_store, PARK_ID, ALIAS_ID, utils.OrderStatus.Waiting,
    )

    response = await taxi_driver_orders_builder.post(
        '/v2/setcar/update/dont_call',
        headers={'Content-type': 'application/json'},
        data=json.dumps(
            {
                'driver': {
                    'park_id': PARK_ID,
                    'driver_profile_id': 'driver1',
                    'alias_id': ALIAS_ID,
                },
                'order_id': 'test_order_id',
                'change_id': change_id,
            },
        ),
    )

    redis_setcar = json.loads(
        redis_store.hget(_ORDER_SETCAR_ITEMS + ':' + PARK_ID, ALIAS_ID),
    )
    expected_setcar = copy.deepcopy(setcar_item)

    if change_id in (DO_NOT_CALL_CHANGE_ID, PLS_CALL_CHANGE_ID):
        assert response.status_code == 200
        # assert 'update_notification' in response.json()
        if change_id == DO_NOT_CALL_CHANGE_ID:
            expected_setcar['requirement_list'] = pretty_requirements_added
        if change_id == PLS_CALL_CHANGE_ID:
            expected_setcar['requirement_list'] = pretty_requirements_deleted
        assert response.json()['setcar'] == expected_setcar
    else:
        assert response.status_code == 410

    assert redis_setcar == expected_setcar


ADD_PORCH_NUMBER_CHANGE_ID = GOOD_CHANGE_ID
DEL_PORCH_NUMBER_CHANGE_ID = 'del_porch_number_change_id'


@pytest.mark.parametrize(
    ['change_id', 'old_street', 'needed_street'],
    [
        (
            ADD_PORCH_NUMBER_CHANGE_ID,
            'Нагорный проезд, 37/23',
            'Нагорный проезд, 37/23, подъезд 3',
        ),
        (
            ADD_PORCH_NUMBER_CHANGE_ID,
            'Нагорный проезд, 37/23, подъезд 1',
            'Нагорный проезд, 37/23, подъезд 3',
        ),
        (
            DEL_PORCH_NUMBER_CHANGE_ID,
            'Нагорный проезд, 37/23',
            'Нагорный проезд, 37/23',
        ),
        (
            DEL_PORCH_NUMBER_CHANGE_ID,
            'Нагорный проезд, 37/23, подъезд 3',
            'Нагорный проезд, 37/23',
        ),
        ('000000c2c9b8493f5a5bb2dca5000000', '', ''),
    ],
    ids=[
        'add_porch_number_change_id_without_porch',
        'add_porch_number_change_id_with_porch',
        'del_porch_number_change_id_without_porch',
        'del_porch_number_change_id_with_porch',
        'bad_change_id',
    ],
)
@pytest.mark.now(MOCKED_NOW)
async def test_porch_number(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        mockserver,
        change_id,
        old_street,
        needed_street,
        order_proc,
):
    order_proc_json = load_json('order_core_fields_porch_number_response.json')
    order_proc.order_proc['fields']['changes'] = order_proc_json['document'][
        'changes'
    ]
    setcar_item = load_json('setcar.json')
    setcar_item['address_from']['Street'] = old_street
    redis_store.hset(
        _ORDER_SETCAR_ITEMS + ':' + PARK_ID, ALIAS_ID, json.dumps(setcar_item),
    )

    response = await taxi_driver_orders_builder.post(
        '/v2/setcar/update/porchnumber',
        headers={'Content-type': 'application/json'},
        data=json.dumps(
            {
                'driver': {
                    'park_id': PARK_ID,
                    'driver_profile_id': 'driver1',
                    'alias_id': ALIAS_ID,
                },
                'order_id': 'test_order_id',
                'change_id': change_id,
            },
        ),
    )

    redis_setcar = json.loads(
        redis_store.hget(_ORDER_SETCAR_ITEMS + ':' + PARK_ID, ALIAS_ID),
    )
    expected_setcar = copy.deepcopy(setcar_item)

    if change_id in (ADD_PORCH_NUMBER_CHANGE_ID, DEL_PORCH_NUMBER_CHANGE_ID):
        assert response.status_code == 200
        assert 'update_notification' in response.json()
        expected_setcar['address_from']['Street'] = needed_street
        if change_id == ADD_PORCH_NUMBER_CHANGE_ID:
            expected_setcar['address_from']['Porch'] = '3'
        if change_id == DEL_PORCH_NUMBER_CHANGE_ID:
            del expected_setcar['address_from']['Porch']
        assert response.json()['setcar'] == expected_setcar
    else:
        assert response.status_code == 410

    assert redis_setcar == expected_setcar


@pytest.mark.parametrize(
    'change_id',
    [GOOD_CHANGE_ID, '000000c2c9b8493f5a5bb2dca5000000'],
    ids=['good_change_id', 'bad_change_id'],
)
@pytest.mark.now(MOCKED_NOW)
async def test_comment(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        mockserver,
        change_id,
        order_proc,
):
    order_proc_json = load_json('order_core_fields_comment_response.json')
    order_proc.order_proc['fields']['changes'] = order_proc_json['document'][
        'changes'
    ]
    setcar_item = load_json('setcar.json')
    redis_store.hset(
        _ORDER_SETCAR_ITEMS + ':' + PARK_ID, ALIAS_ID, json.dumps(setcar_item),
    )

    response = await taxi_driver_orders_builder.post(
        '/v2/setcar/update/comment',
        headers={'Content-type': 'application/json'},
        data=json.dumps(
            {
                'driver': {
                    'park_id': PARK_ID,
                    'driver_profile_id': 'driver1',
                    'alias_id': ALIAS_ID,
                },
                'order_id': 'test_order_id',
                'change_id': change_id,
            },
        ),
    )

    redis_setcar = json.loads(
        redis_store.hget(_ORDER_SETCAR_ITEMS + ':' + PARK_ID, ALIAS_ID),
    )
    expected_setcar = copy.deepcopy(setcar_item)

    if change_id == GOOD_CHANGE_ID:
        assert response.status_code == 200
        expected_setcar['description'] = 'privet!'
        assert response.json()['setcar'] == expected_setcar
    else:
        assert response.status_code == 410

    assert redis_setcar == expected_setcar


@pytest.mark.now(MOCKED_NOW)
async def test_bad_order_core_response(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        mockserver,
        order_proc,
):
    setcar_item = load_json('setcar.json')
    redis_store.hset(
        _ORDER_SETCAR_ITEMS + ':' + PARK_ID, ALIAS_ID, json.dumps(setcar_item),
    )

    response = await taxi_driver_orders_builder.post(
        '/v2/setcar/update/user_ready',
        headers={'Content-type': 'application/json'},
        data=json.dumps(
            {
                'driver': {
                    'park_id': PARK_ID,
                    'driver_profile_id': 'driver1',
                    'alias_id': ALIAS_ID,
                },
                'order_id': 'test_order_id',
                'change_id': GOOD_CHANGE_ID,
            },
        ),
    )

    redis_setcar = json.loads(
        redis_store.hget(_ORDER_SETCAR_ITEMS + ':' + PARK_ID, ALIAS_ID),
    )
    expected_setcar = copy.deepcopy(setcar_item)

    assert response.status_code == 410
    assert redis_setcar == expected_setcar
