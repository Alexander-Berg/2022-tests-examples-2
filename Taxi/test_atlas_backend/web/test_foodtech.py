# pylint: disable=C0103
import datetime
import decimal
from typing import Any
from typing import Dict
from typing import List

import pytest


NOW = datetime.datetime(2021, 2, 15, 1, 10, 0)


free_couriers_mysql_response = [
    {
        'courier_id': '123123',
        'courier_type': 'bicycle',
        'courier_name': 'Седрак Хлхатян',
        'courier_lat': decimal.Decimal('55.758399'),
        'courier_lon': decimal.Decimal('37.623547'),
        'courier_source': 'eda',
        'courier_status': 'free',
        'free_time': 72,
        'shift_type': 'plan',
        'restaurant_lat': None,
        'restaurant_lon': None,
        'order_lat': None,
        'order_lon': None,
        'restaurant_name': None,
        'restaurant_address': None,
        'order_address': None,
        'order_id': None,
    },
    {
        'courier_id': '12324123',
        'courier_type': 'electric_bicycle',
        'courier_name': 'Ислам Шакарбеков',
        'courier_lat': decimal.Decimal('55.758355'),
        'courier_lon': decimal.Decimal('37.634298'),
        'courier_source': 'lavka',
        'courier_status': 'taken',
        'free_time': 87,
        'shift_type': 'plan',
        'restaurant_lat': decimal.Decimal('55.761414'),
        'restaurant_lon': decimal.Decimal('37.636324'),
        'order_lat': decimal.Decimal('55.767779'),
        'order_lon': decimal.Decimal('37.648632'),
        'restaurant_name': 'Яндекс.Лавка',
        'restaurant_address': 'Кривоколенный переулок, 10с6',
        'order_address': 'Москва, Хоромный тупик, 2/6',
        'order_id': '210218-179951',
    },
    {
        'courier_id': '12324123',
        'courier_type': 'electric_bicycle',
        'courier_name': 'Ислам Шакарбеков',
        'courier_lat': decimal.Decimal('55.758355'),
        'courier_lon': decimal.Decimal('37.634298'),
        'courier_source': 'lavka',
        'courier_status': 'arrived_to_source',
        'free_time': 1212,
        'shift_type': 'plan',
        'restaurant_lat': decimal.Decimal('55.760038'),
        'restaurant_lon': decimal.Decimal('37.625846'),
        'order_lat': decimal.Decimal('55.758944'),
        'order_lon': decimal.Decimal('37.623636'),
        'restaurant_name': 'Про пельмени',
        'restaurant_address': 'Театральный проезд, 5с1',
        'order_address': 'Москва, Третьяковский проезд, 1/4',
        'order_id': '210218-512817',
    },
    {
        'courier_id': '412512',
        'courier_type': 'bicycle',
        'courier_name': 'Барат Бактыяр уулу',
        'courier_lat': decimal.Decimal('55.762001'),
        'courier_lon': decimal.Decimal('37.625127'),
        'courier_source': 'eda',
        'courier_status': 'taken',
        'free_time': 432,
        'shift_type': 'plan',
        'restaurant_lat': decimal.Decimal('55.762080'),
        'restaurant_lon': decimal.Decimal('37.614186'),
        'order_lat': decimal.Decimal('55.757055'),
        'order_lon': decimal.Decimal('37.637389'),
        'restaurant_name': 'Город-Сад',
        'restaurant_address': 'улица Большая Дмитровка, 16к1',
        'order_address': 'Москва, улица Маросейка, 10/1с3',
        'order_id': '210218-518822',
    },
]

free_couriers_response = [
    {
        'courier': {
            'id': '123123',
            'name': 'Седрак Хлхатян',
            'position': {'lat': 55.758399, 'lon': 37.623547},
            'problems': [],
            'shift_type': 'plan',
            'source': 'eda',
            'status': 'free',
            'type': 'bicycle',
            'free_time': 72,
        },
        'orders': [],
    },
    {
        'courier': {
            'id': '12324123',
            'name': 'Ислам Шакарбеков',
            'position': {'lat': 55.758355, 'lon': 37.634298},
            'problems': [],
            'shift_type': 'plan',
            'source': 'lavka',
            'status': 'busy_on_many_orders',
            'type': 'electric_bicycle',
            'free_time': None,
        },
        'orders': [
            {
                'address': 'Москва, Хоромный тупик, 2/6',
                'id': '210218-179951',
                'position': {'lat': 55.767779, 'lon': 37.648632},
                'restaurant': {
                    'address': 'Кривоколенный переулок, 10с6',
                    'name': 'Яндекс.Лавка',
                    'position': {'lat': 55.761414, 'lon': 37.636324},
                },
                'status': 'taken',
            },
            {
                'address': 'Москва, Третьяковский проезд, 1/4',
                'id': '210218-512817',
                'position': {'lat': 55.758944, 'lon': 37.623636},
                'restaurant': {
                    'address': 'Театральный проезд, 5с1',
                    'name': 'Про пельмени',
                    'position': {'lat': 55.760038, 'lon': 37.625846},
                },
                'status': 'arrived_to_source',
            },
        ],
    },
    {
        'courier': {
            'id': '412512',
            'name': 'Барат Бактыяр уулу',
            'position': {'lat': 55.762001, 'lon': 37.625127},
            'problems': [],
            'shift_type': 'plan',
            'source': 'eda',
            'status': 'taken',
            'type': 'bicycle',
            'free_time': None,
        },
        'orders': [
            {
                'address': 'Москва, улица Маросейка, 10/1с3',
                'id': '210218-518822',
                'position': {'lat': 55.757055, 'lon': 37.637389},
                'restaurant': {
                    'address': 'улица Большая Дмитровка, 16к1',
                    'name': 'Город-Сад',
                    'position': {'lat': 55.76208, 'lon': 37.614186},
                },
                'status': 'taken',
            },
        ],
    },
]

del_delay_mysql_response = [
    {
        'order_id': '210218-444746',
        'order_type': 'eda',
        'order_lat': decimal.Decimal('55.833188'),
        'order_lon': decimal.Decimal('49.158085'),
        'restaurant_lat': decimal.Decimal('55.833319'),
        'restaurant_lon': decimal.Decimal('49.153890'),
        'courier_id': 2211505,
        'courier_type': 'bicycle',
        'courier_name': 'Руслан Дарин1',
        'courier_lat': decimal.Decimal('55.835733'),
        'courier_lon': decimal.Decimal('49.147343'),
        'courier_status': 'arrived_to_destination',
        'order_delay_type': 'transfer_to_customer',
        'order_delay_time': 1503,
    },
    # should be filtered by delivery_delay_excluded
    {
        'order_id': '210218-326517',
        'order_type': 'eda',
        'order_lat': decimal.Decimal('55.786860'),
        'order_lon': decimal.Decimal('49.152174'),
        'restaurant_lat': decimal.Decimal('55.789092'),
        'restaurant_lon': decimal.Decimal('49.151303'),
        'courier_id': 2222950,
        'courier_type': 'bicycle',
        'courier_name': 'Андрей Храмов2',
        'courier_lat': decimal.Decimal('55.786372'),
        'courier_lon': decimal.Decimal('49.151638'),
        'courier_status': 'arrived_to_destination',
        'order_delay_type': 'transfer_to_customer',
        'order_delay_time': 937,
    },
    {
        'order_id': '210218-276202',
        'order_type': 'eda',
        'order_lat': decimal.Decimal('55.815974'),
        'order_lon': decimal.Decimal('49.107986'),
        'restaurant_lat': decimal.Decimal('55.817370'),
        'restaurant_lon': decimal.Decimal('49.116628'),
        'courier_id': 1705640,
        'courier_type': 'bicycle',
        'courier_name': 'Евгений Корнилов',
        'courier_lat': decimal.Decimal('55.796380'),
        'courier_lon': decimal.Decimal('49.114919'),
        'courier_status': 'accepted',
        'order_delay_type': 'known_in_advance_lateness',
        'order_delay_time': 2755,
    },
    {
        'order_id': '210218-058354',
        'order_type': 'eda',
        'order_lat': decimal.Decimal('55.780699'),
        'order_lon': decimal.Decimal('49.144853'),
        'restaurant_lat': decimal.Decimal('55.782719'),
        'restaurant_lon': decimal.Decimal('49.153135'),
        'courier_id': 1380167,
        'courier_type': 'bicycle',
        'courier_name': 'Александр Пиляев 1',
        'courier_lat': decimal.Decimal('55.784094'),
        'courier_lon': decimal.Decimal('49.149912'),
        'courier_status': 'arrived_to_destination',
        'order_delay_type': 'transfer_to_customer',
        'order_delay_time': 312,
    },
    {
        'order_id': '210218-361335',
        'order_type': 'eda',
        'order_lat': decimal.Decimal('55.788900'),
        'order_lon': decimal.Decimal('49.141718'),
        'restaurant_lat': decimal.Decimal('55.793900'),
        'restaurant_lon': decimal.Decimal('49.149506'),
        'courier_id': 2600370,
        'courier_type': 'vehicle',
        'courier_name': 'Мансур Усманов',
        'courier_lat': decimal.Decimal('55.753080'),
        'courier_lon': decimal.Decimal('49.165813'),
        'courier_status': 'accepted',
        'order_delay_type': 'on_the_way_to_restaurant',
        'order_delay_time': 532,
    },
]

del_delay_response: List[Dict[str, Any]] = [
    {
        'order': {
            'id': '210218-444746',
            'position': {'lat': '55.833188', 'lon': '49.158085'},
            'status': 'transfer_to_customer',
            'delay': 1503,
        },
        'courier': {
            'id': 2211505,
            'name': 'Руслан Дарин1',
            'type': 'bicycle',
            'position': {'lat': '55.835733', 'lon': '49.147343'},
            'status': 'arrived_to_destination',
        },
        'restaurant': {'position': {'lat': '55.833319', 'lon': '49.153890'}},
        'source': 'eda',
    },
    # Filtered order was here
    {
        'order': {
            'id': '210218-276202',
            'position': {'lat': '55.815974', 'lon': '49.107986'},
            'status': 'known_in_advance_lateness',
            'delay': 2755,
        },
        'courier': {
            'id': 1705640,
            'name': 'Евгений Корнилов',
            'type': 'bicycle',
            'position': {'lat': '55.796380', 'lon': '49.114919'},
            'status': 'accepted',
        },
        'restaurant': {'position': {'lat': '55.817370', 'lon': '49.116628'}},
        'source': 'eda',
    },
    {
        'order': {
            'id': '210218-058354',
            'position': {'lat': '55.780699', 'lon': '49.144853'},
            'status': 'transfer_to_customer',
            'delay': 312,
        },
        'courier': {
            'id': 1380167,
            'name': 'Александр Пиляев 1',
            'type': 'bicycle',
            'position': {'lat': '55.784094', 'lon': '49.149912'},
            'status': 'arrived_to_destination',
        },
        'restaurant': {'position': {'lat': '55.782719', 'lon': '49.153135'}},
        'source': 'eda',
    },
    {
        'order': {
            'id': '210218-361335',
            'position': {'lat': '55.788900', 'lon': '49.141718'},
            'status': 'on_the_way_to_restaurant',
            'delay': 532,
        },
        'courier': {
            'id': 2600370,
            'name': 'Мансур Усманов',
            'type': 'vehicle',
            'position': {'lat': '55.753080', 'lon': '49.165813'},
            'status': 'accepted',
        },
        'restaurant': {'position': {'lat': '55.793900', 'lon': '49.149506'}},
        'source': 'eda',
    },
]


@pytest.mark.config(
    ATLAS_FOODTECH_MONITORING={
        'fast_food_delivery_delay': 2100,
        'free_couriers_orders_history_delay': 14400,
        'in_restaurant_delay': 300,
        'long_free_courier_delay': 1800,
        'native_delivery_delay': 1500,
        'on_the_way_to_client_delay': 300,
        'on_the_way_to_restaurant_delay': 300,
        'order_monitoring_interval': 7200,
        'store_delivery_delay': 480,
        'transfer_to_customer_delay': 300,
    },
)
@pytest.mark.parametrize(
    'username, expected_status',
    [
        ('super_user', 200),
        ('foodtech_monitoring_user', 200),
        ('main_user', 403),
        ('nonexisted_user', 403),
    ],
)
async def test_get_free_couriers(
        atlas_mysql_client_mock,
        load,
        username,
        atlas_blackbox_mock,
        expected_status,
        web_app_client,
        patch,
):
    expected_query = load('get_free_couriers.sql')

    @patch('test_atlas_backend.conftest.MockMysqlPoolWrapper.fetch')
    async def _fetch(*args, **kwargs):
        query = args[0]
        assert query == expected_query
        for row in free_couriers_mysql_response:
            yield row

    response = await web_app_client.post(
        '/api/v1/foodtech/free_couriers',
        json={
            'tl': {'lat': 55.76259849386081, 'lon': 37.620213031768806},
            'br': {'lat': 55.74978423956397, 'lon': 37.63439655303956},
        },
    )

    assert response.status == expected_status
    if response.status == 200:
        content = await response.json()
        assert content == free_couriers_response


@pytest.mark.config(
    ATLAS_FOODTECH_MONITORING={
        'fast_food_delivery_delay': 2100,
        'free_couriers_orders_history_delay': 14400,
        'in_restaurant_delay': 300,
        'long_free_courier_delay': 1800,
        'native_delivery_delay': 1500,
        'on_the_way_to_client_delay': 300,
        'on_the_way_to_restaurant_delay': 300,
        'order_monitoring_interval': 7200,
        'store_delivery_delay': 480,
        'transfer_to_customer_delay': 300,
    },
)
@pytest.mark.parametrize(
    'username, expected_status',
    [
        ('super_user', 200),
        ('foodtech_monitoring_user', 200),
        ('main_user', 403),
        ('nonexisted_user', 403),
    ],
)
async def test_get_delivery_delay(
        atlas_mysql_client_mock,
        username,
        expected_status,
        atlas_blackbox_mock,
        web_app_client,
        patch,
        load,
):
    expected_query = load('get_delivery_delay.sql').format(
        order_delay_type_filter='1 = 1',
    )

    @patch('test_atlas_backend.conftest.MockMysqlPoolWrapper.fetch')
    async def _fetch(*args, **kwargs):
        query = args[0]
        assert query == expected_query
        for row in del_delay_mysql_response:
            yield row

    response = await web_app_client.get(
        '/api/v1/foodtech/delivery_delay/?city=Казань',
    )
    assert response.status == expected_status
    if response.status == 200:
        content = await response.json()
        assert content == del_delay_response


@pytest.mark.config(
    ATLAS_FOODTECH_MONITORING={
        'fast_food_delivery_delay': 2100,
        'free_couriers_orders_history_delay': 14400,
        'in_restaurant_delay': 300,
        'long_free_courier_delay': 1800,
        'native_delivery_delay': 1500,
        'on_the_way_to_client_delay': 300,
        'on_the_way_to_restaurant_delay': 300,
        'order_monitoring_interval': 7200,
        'store_delivery_delay': 480,
        'transfer_to_customer_delay': 300,
    },
)
@pytest.mark.parametrize(
    'username, expected_status, delay_types',
    [
        ('super_user', 200, ['on_the_way_to_restaurant']),
        (
            'super_user',
            200,
            ['on_the_way_to_restaurant', 'known_in_advance_lateness'],
        ),
    ],
)
async def test_get_delivery_delay_filtered(
        atlas_mysql_client_mock,
        username,
        atlas_blackbox_mock,
        expected_status,
        delay_types,
        web_app_client,
        patch,
        load,
):
    delay_types_str = ', '.join([f'\'{x}\'' for x in delay_types])
    expected_query = load('get_delivery_delay.sql').format(
        order_delay_type_filter=f'order_delay_type IN ({delay_types_str})',
    )

    del_delay_response_filtered = [
        x for x in del_delay_response if x['order']['status'] in delay_types
    ]
    del_delay_mysql_response_filtered = [
        x
        for x in del_delay_mysql_response
        if x['order_delay_type'] in delay_types
    ]

    @patch('test_atlas_backend.conftest.MockMysqlPoolWrapper.fetch')
    async def _fetch(*args, **kwargs):
        query = args[0]
        assert query == expected_query
        for row in del_delay_mysql_response_filtered:
            yield row

    response = await web_app_client.get(
        '/api/v1/foodtech/delivery_delay/?city=Казань&'
        'delay_types={}'.format(','.join(delay_types)),
    )

    assert response.status == expected_status
    if response.status == 200:
        content = await response.json()
        assert content == del_delay_response_filtered


@pytest.mark.now(NOW.isoformat())
async def test_resolve_delivery_delay(
        db, username, atlas_blackbox_mock, web_app_client,
):
    # check add new order and remove old id
    order_id = '210218-361335'
    response = await web_app_client.post(
        f'/api/v1/foodtech/delivery_delay/resolve/{order_id}',
        json={'order_status': 'on_the_way_to_restaurant'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'status': 'ok'}

    updated = await db.atlas_delivery_delay_excluded.find(
        {}, {'_id': 0},
    ).to_list(None)
    assert len(updated) == 2
    assert sorted(updated, key=lambda x: x['id']) == [
        {
            'created_at': datetime.datetime(2021, 2, 15, 1, 10),
            'id': '210218-361335',
            'order_status': 'on_the_way_to_restaurant',
        },
        {
            'created_at': datetime.datetime(2021, 2, 15, 1, 0, 0, 528000),
            'id': '210218-444746',
            'order_status': 'on_the_way_to_restaurant',
        },
    ]

    # check updating status of already excluded order
    order_id = '210218-444746'
    response = await web_app_client.post(
        f'/api/v1/foodtech/delivery_delay/resolve/{order_id}',
        json={'order_status': 'transfer_to_customer'},
    )

    assert response.status == 200
    updated = await db.atlas_delivery_delay_excluded.find(
        {}, {'_id': 0},
    ).to_list(None)
    assert len(updated) == 3
    assert sorted(updated, key=lambda x: (x['id'], x['order_status'])) == [
        {
            'created_at': datetime.datetime(2021, 2, 15, 1, 10),
            'id': '210218-361335',
            'order_status': 'on_the_way_to_restaurant',
        },
        {
            'created_at': datetime.datetime(2021, 2, 15, 1, 0, 0, 528000),
            'id': '210218-444746',
            'order_status': 'on_the_way_to_restaurant',
        },
        {
            'created_at': datetime.datetime(2021, 2, 15, 1, 10),
            'id': '210218-444746',
            'order_status': 'transfer_to_customer',
        },
    ]


@pytest.mark.parametrize(
    'username, expected_status',
    [
        ('super_user', 200),
        ('foodtech_monitoring_user', 200),
        ('main_user', 403),
        ('nonexisted_user', 403),
    ],
)
async def test_resolve_delivery_delay_idm(
        db, username, atlas_blackbox_mock, expected_status, web_app_client,
):
    order_id = '210218-361335'
    response = await web_app_client.post(
        f'/api/v1/foodtech/delivery_delay/resolve/{order_id}',
        json={'order_status': 'on_the_way_to_restaurant'},
    )

    assert response.status == expected_status
    if response.status == 200:
        content = await response.json()
        assert content == {'status': 'ok'}
