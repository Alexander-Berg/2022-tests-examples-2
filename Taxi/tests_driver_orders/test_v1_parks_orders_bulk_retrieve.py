import json

import pytest

ENDPOINT = 'v1/parks/orders/bulk_retrieve'


async def common_request(
        taxi_driver_orders, request, code, expected_response, headers=None,
):
    response = await taxi_driver_orders.post(
        ENDPOINT, json=request, headers=headers,
    )

    assert response.status_code == code, response.text
    assert response.json() == expected_response


TVM_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgcIl4p7EKsE:Nm38paL'
    'Swu60FIV0cUk9hSUatu7A8vo0SCK2vPBOO7n9PbbCIlP'
    '3i6W02gtgN9JGe4LmPp9r3BTyzkdbO32g9Kn-hWgrKGUz'
    '3YvG5Ch70ze3XJnYRvySFzSgY5Hzh63UFE9eeZJLTtiu'
    'OTzQWtPoTjpqm-F9liwrmDXND7WAQv8'
)

TEST_BAD_PARAMS = [
    (
        {
            'query': {
                'park': {
                    'id': 'park_id',
                    'order': {'ids': ['orderxxx', 'orderxxx']},
                },
            },
        },
        {
            'code': '400',
            'message': (
                'Field \'query.park.order.ids\' must contain unique values'
            ),
        },
    ),
]


@pytest.mark.parametrize('payload, expected_response', TEST_BAD_PARAMS)
async def test_bad_request(
        taxi_driver_orders, fleet_parks_shard, payload, expected_response,
):
    await common_request(taxi_driver_orders, payload, 400, expected_response)


@pytest.mark.yt(
    schemas=['yt_orders_dyn_schema.yaml'],
    dyn_table_data=['yt_orders_dyn_data.yaml'],
)
async def test_empty_orders(taxi_driver_orders, fleet_parks_shard, yt_apply):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_???',
                'order': {'ids': ['1'], 'cut_hidden_fields': False},
            },
        },
    }

    expected_response = {'orders': [{'id': '1'}]}

    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.yt(
    schemas=['yt_orders_dyn_schema.yaml'],
    dyn_table_data=['yt_orders_dyn_data.yaml'],
)
async def test_one_order(taxi_driver_orders, fleet_parks_shard, yt_apply):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_0',
                'order': {'ids': ['order0'], 'cut_hidden_fields': False},
            },
        },
    }

    expected_response = {
        'orders': [
            {
                'id': 'order0',
                'order': {
                    'address_from': {
                        'address': 'Москва, Рядом с: улица Островитянова, 47',
                        'lat': 55.6348324304,
                        'lon': 37.541191945,
                    },
                    'address_to': {
                        'address': 'Москва, Гостиница Прибалтийская',
                        'lat': 55.5545,
                        'lon': 37.8989,
                    },
                    'booked_at': '2019-05-01T07:05:00+00:00',
                    'driving_at': '2019-05-01T07:10:00+00:00',
                    'category': 'vip',
                    'amenities': ['animal_transport'],
                    'client_price': '100.9900',
                    'driver_profile_id': 'driver_id_0',
                    'driver_profile': {
                        'id': 'driver_id_0',
                        'name': 'driver_name_0',
                    },
                    'ended_at': '2019-05-01T07:20:00+00:00',
                    'payment_method': 'corp',
                    'price': '159.9991',
                    'provider': 'partner',
                    'receipt_details': [],
                    'route_points': [
                        {
                            'address': 'Россия, Химки, Нагорная улица',
                            'lat': 55.123,
                            'lon': 37.1,
                        },
                        {
                            'address': 'Москва, Улица 1',
                            'lat': 55.5111,
                            'lon': 37.222,
                        },
                    ],
                    'short_id': 1,
                    'status': 'complete',
                    'tariff': {'id': 'tariff_id_0', 'name': 'tariff_name_0'},
                    'transporting_at': '2019-05-01T07:17:00+00:00',
                    'vehicle': {
                        'id': 'car_id_0',
                        'name': 'car_model_0',
                        'number': 'car_number_0',
                        'callsign': 'callsign_0',
                    },
                    'created_at': '2019-05-01T07:00:00+00:00',
                    'mileage': '1500.0000',
                    'waited_at': '2019-05-01T07:15:00+00:00',
                    'cancellation_description': 'canceled',
                },
            },
        ],
    }

    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.yt(
    schemas=['yt_orders_dyn_schema.yaml'],
    dyn_table_data=['yt_orders_dyn_data.yaml'],
)
async def test_many_orders(taxi_driver_orders, fleet_parks_shard, yt_apply):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_1',
                'order': {
                    'ids': ['order1', 'order???', 'order2'],
                    'cut_hidden_fields': False,
                },
            },
        },
    }

    expected_response = {
        'orders': [
            {
                'id': 'order1',
                'order': {
                    'address_from': {
                        'address': 'Вильнюсская улица, 7к2',
                        'lat': 55.6022246645,
                        'lon': 37.5224489641,
                    },
                    'booked_at': '2019-05-01T13:20:00+00:00',
                    'driving_at': '2019-05-01T13:18:00+00:00',
                    'category': 'mkk',
                    'driver_profile_id': 'driver_id_1',
                    'driver_profile': {
                        'id': 'driver_id_1',
                        'name': 'driver_name_1',
                    },
                    'ended_at': '2019-05-01T14:30:00+00:00',
                    'payment_method': 'cash',
                    'provider': 'none',
                    'short_id': 1,
                    'status': 'complete',
                    'created_at': '2019-05-01T13:18:00+00:00',
                },
            },
            {'id': 'order???'},
            {
                'id': 'order2',
                'order': {
                    'address_from': {
                        'address': 'Москва, Рядом с: улица Островитянова, 47',
                        'lat': 55.6348324304,
                        'lon': 37.541191945,
                    },
                    'booked_at': '2019-05-01T09:18:00+00:00',
                    'category': 'econom',
                    'client_price': '157.0000',
                    'driver_profile_id': 'driver_id_2',
                    'driver_profile': {'id': 'driver_id_2'},
                    'ended_at': '2019-05-01T14:18:00+00:00',
                    'payment_method': 'cash',
                    'price': '157.0000',
                    'provider': 'none',
                    'receipt_details': [
                        {
                            'count': 376,
                            'name': 'waiting',
                            'price': '56.4000',
                            'price_for_one': '9.0000',
                        },
                    ],
                    'short_id': 2,
                    'status': 'complete',
                    'vehicle': {'id': 'car_id_2'},
                    'created_at': '2019-05-01T09:18:00+00:00',
                    'mileage': '0.9939',
                },
            },
        ],
    }

    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.yt(
    schemas=['yt_orders_dyn_schema.yaml'],
    dyn_table_data=['yt_orders_dyn_data.yaml'],
)
async def test_payment_category_null(
        taxi_driver_orders, fleet_parks_shard, yt_apply,
):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_3',
                'order': {'ids': ['order6'], 'cut_hidden_fields': False},
            },
        },
    }

    expected_response = {
        'orders': [
            {
                'id': 'order6',
                'order': {
                    'address_from': {
                        'address': 'Abc6',
                        'lat': 55.6022246645,
                        'lon': 37.5224489641,
                    },
                    'address_to': {
                        'address': 'Москва, Abc6',
                        'lat': 55.5545,
                        'lon': 37.8989,
                    },
                    'tariff': {'id': 'tariff_id', 'name': ''},
                    'route_points': [
                        {
                            'address': 'Россия, Химки, Нагорная улица',
                            'lat': 55.123,
                            'lon': 37.1,
                        },
                        {
                            'address': 'Москва, Улица 1',
                            'lat': 55.5111,
                            'lon': 37.222,
                        },
                    ],
                    'client_price': '100.0000',
                    'price': '100.0000',
                    'receipt_details': [],
                    'booked_at': '2019-05-01T19:30:00+00:00',
                    'category': 'vip',
                    'driving_at': '2019-05-01T19:30:00+00:00',
                    'provider': 'platform',
                    'short_id': 6,
                    'status': 'driving',
                    'created_at': '2019-05-01T19:00:00+00:00',
                },
            },
        ],
    }

    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.yt(
    schemas=['yt_orders_dyn_schema.yaml'],
    dyn_table_data=['yt_orders_dyn_data.yaml'],
)
@pytest.mark.parametrize(
    'order_id',
    [
        'order_not_found',
        'park',
        'yandex_cancelled',
        'yandex_incorrect_receipt_address',
        'yandex',
        'fields',
        'wrong_fields',
        'string_fields',
    ],
)
@pytest.mark.pgsql('orders', files=['db.sql'])
async def test_file(
        taxi_driver_orders, fleet_parks_shard, load_json, order_id, yt_apply,
):
    await common_request(
        taxi_driver_orders,
        {
            'query': {
                'park': {
                    'id': 'park_id_0',
                    'order': {'ids': [order_id], 'cut_hidden_fields': False},
                },
            },
        },
        200,
        load_json(f'expected_{order_id}.json'),
    )


@pytest.mark.yt(
    schemas=['yt_orders_dyn_schema.yaml'],
    dyn_table_data=['yt_orders_dyn_data.yaml'],
)
@pytest.mark.parametrize('return_is_partially_hidden', [True, False])
async def test_return_is_partially_hidden(
        taxi_driver_orders, fleet_parks_shard, return_is_partially_hidden,
):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_0',
                'order': {
                    'ids': ['order0'],
                    'cut_hidden_fields': False,
                    'return_is_partially_hidden': return_is_partially_hidden,
                },
            },
        },
    }

    expected_response = {
        'orders': [
            {
                'id': 'order0',
                'order': {
                    'address_from': {
                        'address': 'Москва, Рядом с: улица Островитянова, 47',
                        'lat': 55.6348324304,
                        'lon': 37.541191945,
                    },
                    'address_to': {
                        'address': 'Москва, Гостиница Прибалтийская',
                        'lat': 55.5545,
                        'lon': 37.8989,
                    },
                    'booked_at': '2019-05-01T07:05:00+00:00',
                    'driving_at': '2019-05-01T07:10:00+00:00',
                    'category': 'vip',
                    'amenities': ['animal_transport'],
                    'client_price': '100.9900',
                    'driver_profile_id': 'driver_id_0',
                    'driver_profile': {
                        'id': 'driver_id_0',
                        'name': 'driver_name_0',
                    },
                    'ended_at': '2019-05-01T07:20:00+00:00',
                    'payment_method': 'corp',
                    'price': '159.9991',
                    'provider': 'partner',
                    'receipt_details': [],
                    'route_points': [
                        {
                            'address': 'Россия, Химки, Нагорная улица',
                            'lat': 55.123,
                            'lon': 37.1,
                        },
                        {
                            'address': 'Москва, Улица 1',
                            'lat': 55.5111,
                            'lon': 37.222,
                        },
                    ],
                    'short_id': 1,
                    'status': 'complete',
                    'tariff': {'id': 'tariff_id_0', 'name': 'tariff_name_0'},
                    'transporting_at': '2019-05-01T07:17:00+00:00',
                    'vehicle': {
                        'id': 'car_id_0',
                        'name': 'car_model_0',
                        'number': 'car_number_0',
                        'callsign': 'callsign_0',
                    },
                    'created_at': '2019-05-01T07:00:00+00:00',
                    'mileage': '1500.0000',
                    'waited_at': '2019-05-01T07:15:00+00:00',
                    'cancellation_description': 'canceled',
                },
            },
        ],
    }

    if return_is_partially_hidden:
        expected_response['orders'][0]['is_partially_hidden'] = False

    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.yt(
    schemas=['yt_orders_dyn_schema.yaml'],
    dyn_table_data=['yt_orders_dyn_data.yaml'],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Order:SetCar:Items:park_id_3',
        {'order6': json.dumps({'provider': 2})},
    ],
)
async def test_cut_hidden_fields(
        taxi_driver_orders, fleet_parks_shard, yt_apply,
):
    payload = {
        'query': {'park': {'id': 'park_id_3', 'order': {'ids': ['order6']}}},
    }

    expected_response = {
        'orders': [
            {
                'id': 'order6',
                'order': {
                    'address_from': {
                        'address': 'Abc6',
                        'lat': 55.6022246645,
                        'lon': 37.5224489641,
                    },
                    'tariff': {'id': 'tariff_id', 'name': ''},
                    'booked_at': '2019-05-01T19:30:00+00:00',
                    'driving_at': '2019-05-01T19:30:00+00:00',
                    'provider': 'platform',
                    'short_id': 6,
                    'status': 'driving',
                    'created_at': '2019-05-01T19:00:00+00:00',
                },
            },
        ],
    }

    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.yt(
    schemas=['yt_orders_dyn_schema.yaml'],
    dyn_table_data=['yt_orders_dyn_data.yaml'],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Order:SetCar:Items:park_id_3',
        {'order6': json.dumps({'provider': 2})},
    ],
)
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[
        {'src': 'driver-orders-app-api', 'dst': 'driver-orders'},
        {'src': 'statistics', 'dst': 'driver-orders'},
        {'src': 'driver-categories-api', 'dst': 'driver-orders'},
        {'src': 'driver-authorizer', 'dst': 'driver-orders'},
        {'src': 'driver-trackstory', 'dst': 'driver-orders'},
        {'src': 'fleet-parks', 'dst': 'driver-orders'},
        {'src': 'replication', 'dst': 'driver-orders'},
    ],
    TVM_SERVICES={
        'driver-orders-app-api': 2016535,
        'statistics': 2014904,
        'driver-categories-api': 2013376,
        'driver-authorizer': 2015945,
        'driver-trackstory': 2017853,
        'fleet-parks': 2013704,
        'replication': 2011622,
    },
)
async def test_fallback_yt(
        taxi_driver_orders,
        fleet_parks_shard,
        yt_apply,
        taxi_driver_orders_monitor,
):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_3',
                'order': {'ids': ['order6', 'order99']},
            },
        },
        'lookup_yt': True,
    }

    expected_response = {
        'orders': [
            {
                'id': 'order6',
                'order': {
                    'address_from': {
                        'address': 'Abc6',
                        'lat': 55.6022246645,
                        'lon': 37.5224489641,
                    },
                    'booked_at': '2019-05-01T19:30:00+00:00',
                    'created_at': '2019-05-01T19:00:00+00:00',
                    'driving_at': '2019-05-01T19:30:00+00:00',
                    'provider': 'platform',
                    'short_id': 6,
                    'status': 'driving',
                    'tariff': {'id': 'tariff_id', 'name': ''},
                },
            },
            {
                'id': 'order99',
                'order': {
                    'address_from': {
                        'address': (
                            'От борта: Россия, Ростов-на-Дону, '
                            'микрорайон Темерник, улица Думенко'
                        ),
                        'lat': 47.292952,
                        'lon': 39.738583,
                    },
                    'address_to': {'address': 'По указанию'},
                    'booked_at': '2021-11-18T15:46:01+00:00',
                    'cancellation_description': 'description_canceled_1',
                    'client_price': '222.0000',
                    'created_at': '2021-11-18T15:46:01+00:00',
                    'driving_at': '2021-11-18T15:46:01+00:00',
                    'driver_profile': {'id': 'driver_id_0', 'name': 'Алексей'},
                    'driver_profile_id': 'driver_id_0',
                    'ended_at': '2021-11-18T15:46:01+00:00',
                    'mileage': '9305.4277',
                    'payment_method': 'cash',
                    'price': '224.0000',
                    'provider': 'partner',
                    'amenities': ['conditioner'],
                    'receipt_details': [
                        {
                            'name': 'waiting_in_transit',
                            'price': '209.3333',
                            'count': 628,
                            'price_for_one': '20.0000',
                        },
                    ],
                    'short_id': 2,
                    'status': 'complete',
                    'tariff': {
                        'id': 'tariff_id_park_0',
                        'name': 'Тариф парка',
                    },
                    'transporting_at': '2021-11-18T15:46:01+00:00',
                    'vehicle': {
                        'callsign': '222',
                        'id': '222',
                        'name': '222',
                        'number': '222',
                    },
                    'waited_at': '2021-11-18T15:46:01+00:00',
                },
            },
        ],
    }
    headers = {'X-Ya-Service-Ticket': TVM_SERVICE_TICKET}

    await taxi_driver_orders.tests_control(reset_metrics=True)
    yt_orders_reads = await taxi_driver_orders_monitor.get_metric(
        'yt_orders_reads',
    )
    assert yt_orders_reads == {}

    await common_request(
        taxi_driver_orders, payload, 200, expected_response, headers=headers,
    )

    yt_orders_reads = await taxi_driver_orders_monitor.get_metric(
        'yt_orders_reads',
    )
    assert yt_orders_reads == {'driver-orders-app-api': 1}


@pytest.mark.config(DRIVER_ORDERS_FETCH_OLD_ORDERS_FROM_YT=False)
@pytest.mark.yt(
    schemas=['yt_orders_dyn_schema.yaml'],
    dyn_table_data=['yt_orders_dyn_data.yaml'],
)
async def test_fallback_yt_disabled_by_config(
        taxi_driver_orders, fleet_parks_shard, yt_apply,
):
    payload = {
        'query': {'park': {'id': 'park_id_4', 'order': {'ids': ['order99']}}},
    }

    expected_response = {'orders': [{'id': 'order99'}]}

    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.yt(
    schemas=['yt_orders_dyn_schema.yaml'],
    dyn_table_data=['yt_orders_dyn_data.yaml'],
)
async def test_fallback_yt_disabled_by_request(
        taxi_driver_orders, fleet_parks_shard, yt_apply,
):
    payload = {
        'query': {'park': {'id': 'park_id_3', 'order': {'ids': ['order99']}}},
        'lookup_yt': False,
    }

    expected_response = {'orders': [{'id': 'order99'}]}

    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.config(DRIVER_ORDERS_FORCE_FALLBACK_YT=True)
@pytest.mark.yt(
    schemas=['yt_orders_dyn_schema.yaml'],
    dyn_table_data=['yt_orders_dyn_data.yaml'],
)
async def test_force_fallback_yt(
        taxi_driver_orders, fleet_parks_shard, yt_apply,
):
    payload = {
        'query': {'park': {'id': 'park_id_3', 'order': {'ids': ['order99']}}},
        'lookup_yt': False,
    }

    expected_response = {
        'orders': [
            {
                'id': 'order99',
                'order': {
                    'address_from': {
                        'address': (
                            'От борта: Россия, Ростов-на-Дону, '
                            'микрорайон Темерник, улица Думенко'
                        ),
                        'lat': 47.292952,
                        'lon': 39.738583,
                    },
                    'address_to': {'address': 'По указанию'},
                    'amenities': ['conditioner'],
                    'booked_at': '2021-11-18T15:46:01+00:00',
                    'cancellation_description': 'description_canceled_1',
                    'client_price': '222.0000',
                    'created_at': '2021-11-18T15:46:01+00:00',
                    'driver_profile': {'id': 'driver_id_0', 'name': 'Алексей'},
                    'driver_profile_id': 'driver_id_0',
                    'driving_at': '2021-11-18T15:46:01+00:00',
                    'ended_at': '2021-11-18T15:46:01+00:00',
                    'mileage': '9305.4277',
                    'payment_method': 'cash',
                    'price': '224.0000',
                    'provider': 'partner',
                    'receipt_details': [
                        {
                            'count': 628,
                            'name': 'waiting_in_transit',
                            'price': '209.3333',
                            'price_for_one': '20.0000',
                        },
                    ],
                    'short_id': 2,
                    'status': 'complete',
                    'tariff': {
                        'id': 'tariff_id_park_0',
                        'name': 'Тариф парка',
                    },
                    'transporting_at': '2021-11-18T15:46:01+00:00',
                    'vehicle': {
                        'callsign': '222',
                        'id': '222',
                        'name': '222',
                        'number': '222',
                    },
                    'waited_at': '2021-11-18T15:46:01+00:00',
                },
            },
        ],
    }

    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.parametrize(
    'lookup_yt, fallback_yt',
    [
        pytest.param(True, None, id='find_in_yt'),
        pytest.param(False, True, id='fallback_on_yt'),
        pytest.param(False, False, id='wo_fallback'),
    ],
)
@pytest.mark.yt(
    schemas=['yt_orders_dyn_schema_v2.yaml'],
    dyn_table_data=['yt_orders_dyn_data_v2.yaml'],
)
async def test_order_flags(
        taxi_driver_orders,
        fleet_parks_shard,
        yt_apply_force,
        lookup_yt,
        fallback_yt,
        taxi_config,
):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_3',
                'order': {
                    'ids': ['order_with_flags', 'order6', 'order_only_in_yt'],
                },
            },
        },
        'lookup_yt': lookup_yt,
    }
    if fallback_yt is not None:
        taxi_config.set_values(
            {'DRIVER_ORDERS_FORCE_FALLBACK_YT': fallback_yt},
        )
    response = await taxi_driver_orders.post(ENDPOINT, json=payload)

    assert response.status_code == 200
    orders = response.json()['orders']
    assert len(orders) == 3
    for order in orders:
        if order['id'] == 'order_with_flags':
            assert order['order']['flags'] == ['flag_1', 'flag_2']
        elif order['id'] == 'order_only_in_yt':
            if fallback_yt in (None, True):
                assert order['order']['flags'] == ['driver_freightage']
            else:
                assert order == {'id': 'order_only_in_yt'}
        elif order['id'] == 'order6':
            assert 'flags' not in order['order']
