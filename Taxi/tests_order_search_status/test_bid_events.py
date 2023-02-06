import json

import pytest

from tests_order_search_status import eventus_tools
from tests_order_search_status import utils


def sorted_redis_keys(redis_store):
    cursor = 0
    pattern = '*'
    ret = []
    while True:
        cursor, keys = redis_store.scan(cursor=cursor, match=pattern)
        ret += keys
        if cursor == 0:
            break
    return sorted([key.decode('ascii') for key in ret])


@pytest.fixture(autouse=True)
def mocks(mockserver):
    @mockserver.json_handler('/udriver-photos/driver-photos/v1/fleet/photos')
    def _driver_photos_v1_fleet_photos(request):
        return {'actual_photos': []}

    @mockserver.json_handler('/driver-ratings/v2/driver/rating/batch-retrieve')
    def _driver_rating_batch_retrieve(request):
        assert request.headers['X-Ya-Service-Name'] == 'order-search-status'
        return {'ratings': []}

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/stats/retrieve-by-uniques',
    )
    def _unique_drivers_trips_count_batch_retrieve(request):
        return {'stats': []}


@pytest.mark.now('2022-04-18T09:05:20.000000+0000')
async def test_bid_created_event(
        taxi_order_search_status,
        taxi_eventus_orchestrator_mock,
        testpoint,
        redis_store,
        mockserver,
):
    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_search_status, eventus_tools.bid_pipeline(),
    )

    @testpoint('bids_sink_testpoint')
    def bids_sink_testpoint(data):
        return data

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie1'

    @mockserver.json_handler('/udriver-photos/driver-photos/v1/fleet/photos')
    def _driver_photos_v1_fleet_photos(request):
        return {
            'actual_photos': [
                {
                    'actual_photo': {
                        'portrait_url': 'https://portrait_url_1',
                        'avatar_url': 'https://avatar_url_1',
                    },
                    'unique_driver_id': 'unique_driver_1',
                },
                {
                    'actual_photo': {
                        'portrait_url': 'https://portrait_url_2',
                        'avatar_url': 'https://avatar_url_2',
                    },
                    'unique_driver_id': 'unique_driver_2',
                },
                {
                    'actual_photo': {
                        'portrait_url': 'https://portrait_url_3',
                        'avatar_url': 'https://avatar_url_3',
                    },
                    'unique_driver_id': 'unique_driver_3',
                },
                {
                    'actual_photo': {
                        'portrait_url': 'https://portrait_url_4',
                        'avatar_url': 'https://avatar_url_4',
                    },
                    'unique_driver_id': 'unique_driver_4',
                },
            ],
        }

    @mockserver.json_handler('/driver-ratings/v2/driver/rating/batch-retrieve')
    def _driver_rating_batch_retrieve(request):
        assert request.headers['X-Ya-Service-Name'] == 'order-search-status'
        return {
            'ratings': [
                {'unique_driver_id': 'unique_driver_1', 'rating': '4.1000'},
                {'unique_driver_id': 'unique_driver_2', 'rating': '4.2'},
                {'unique_driver_id': 'unique_driver_3', 'rating': '4.3'},
                {'unique_driver_id': 'unique_driver_4', 'rating': '4.4'},
            ],
        }

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/stats/retrieve-by-uniques',
    )
    def _unique_drivers_trips_count_batch_retrieve(request):
        return {
            'stats': [
                {'unique_driver_id': 'unique_driver_1', 'trips_count': 11},
                {'unique_driver_id': 'unique_driver_2', 'trips_count': 22},
                {'unique_driver_id': 'unique_driver_3', 'trips_count': 33},
                {'unique_driver_id': 'unique_driver_4'},
            ],
        }

    events = [
        utils.bid_related_event(
            'bid_created',
            'order_1',
            'bid_id_1',
            'uuid1',
            0,
            unique_driver_id='unique_driver_1',
            price=40.55,
            created_at='2022-04-18T09:05:22.000000Z',
            timeout=30,
            driver_name='Driver_1',
            car_model='Kia Rio',
            start_eta=300,
        ),
        utils.bid_related_event(
            'bid_created',
            'order_1',
            'bid_id_2',
            'uuid2',
            0,
            unique_driver_id='unique_driver_2',
            price=42,
            created_at='2022-04-18T09:05:00.000000Z',
            timeout=35,
            driver_name='Driver_2',
            car_model='Skoda Oktavia',
            start_eta=250,
        ),
        utils.bid_related_event(
            'bid_created',
            'order_1',
            'bid_id_3',
            'uuid1',
            1,
            unique_driver_id='unique_driver_1',
            price=50,
            created_at='2022-04-18T09:05:30.000000Z',
            timeout=30,
            driver_name='Driver_1',
            car_model='Kia Rio',
            start_eta=200,
        ),
        utils.bid_related_event(
            'bid_created',
            'order_2',
            'bid_id_1',
            'uuid3',
            0,
            unique_driver_id='unique_driver_3',
            price=41,
            created_at='2022-04-18T09:05:22.000000Z',
            timeout=30,
            driver_name='Driver_3',
            car_model='Kia Rio',
            start_eta=300,
        ),
        utils.bid_related_event(
            'bid_created',
            'order_2',
            'bid_id_2',
            'uuid4',
            0,
            unique_driver_id='unique_driver_4',
            price=40,
            created_at='2022-04-18T09:05:50.000000Z',
            timeout=20,
            driver_name='Driver_4',
            car_model='Hyundai Solaris',
            start_eta=350,
        ),
    ]

    response = await taxi_order_search_status.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-search-status-bids',
                'data': '\n'.join(events),
                'topic': 'smth',
                'cookie': 'cookie1',
            },
        ),
    )
    assert response.status_code == 200

    result = (await bids_sink_testpoint.wait_call())['data']
    for value in result.values():
        value.sort(
            key=lambda x: (x['iteration'], x['bid_id'], x['driver_name']),
        )
    assert result == {
        'order_2': [
            {
                'iteration': 0,
                'bid_id': 'bid_id_1',
                'multioffer_id': 'multioffer_order_2',
                'driver_name': 'Driver_3',
                'car_model': 'Kia Rio',
                'created_at': 1650272722,
                'timeout': 30,
                'price': 41.0,
                'start_eta': 300,
                'driver_avatar_url': 'https://avatar_url_3',
                'rating': '4.3',
                'trips_count': 33,
            },
            {
                'iteration': 0,
                'bid_id': 'bid_id_2',
                'multioffer_id': 'multioffer_order_2',
                'driver_name': 'Driver_4',
                'car_model': 'Hyundai Solaris',
                'created_at': 1650272750,
                'timeout': 20,
                'price': 40.0,
                'start_eta': 350,
                'driver_avatar_url': 'https://avatar_url_4',
                'rating': '4.4',
            },
        ],
        'order_1': [
            {
                'iteration': 0,
                'bid_id': 'bid_id_1',
                'multioffer_id': 'multioffer_order_1',
                'driver_name': 'Driver_1',
                'car_model': 'Kia Rio',
                'created_at': 1650272722,
                'timeout': 30,
                'price': 40.55,
                'start_eta': 300,
                'driver_avatar_url': 'https://avatar_url_1',
                'rating': '4.1000',
                'trips_count': 11,
            },
            {
                'iteration': 0,
                'bid_id': 'bid_id_2',
                'multioffer_id': 'multioffer_order_1',
                'driver_name': 'Driver_2',
                'car_model': 'Skoda Oktavia',
                'created_at': 1650272700,
                'timeout': 35,
                'price': 42.0,
                'start_eta': 250,
                'driver_avatar_url': 'https://avatar_url_2',
                'rating': '4.2',
                'trips_count': 22,
            },
            {
                'iteration': 1,
                'bid_id': 'bid_id_3',
                'multioffer_id': 'multioffer_order_1',
                'driver_name': 'Driver_1',
                'car_model': 'Kia Rio',
                'created_at': 1650272730,
                'timeout': 30,
                'price': 50.0,
                'start_eta': 200,
                'driver_avatar_url': 'https://avatar_url_1',
                'rating': '4.1000',
                'trips_count': 11,
            },
        ],
    }
    await commit.wait_call()

    assert sorted_redis_keys(redis_store) == [
        'order_1:bid_id:bid_id_1',
        'order_1:bid_id:bid_id_2',
        'order_1:bid_id:bid_id_3',
        'order_1:bid_ids:0',
        'order_1:bid_ids:1',
        'order_2:bid_id:bid_id_1',
        'order_2:bid_id:bid_id_2',
        'order_2:bid_ids:0',
    ]
    for set_key, response in [
            ('order_1:bid_ids:0', ['bid_id_1', 'bid_id_2']),
            ('order_1:bid_ids:1', ['bid_id_3']),
            ('order_2:bid_ids:0', ['bid_id_1', 'bid_id_2']),
    ]:
        assert (
            sorted(
                [
                    bid_id.decode('ascii')
                    for bid_id in redis_store.smembers(set_key)
                ],
            )
            == response
        )

    for hash_key, response in [
            (
                'order_1:bid_id:bid_id_1',
                {
                    b'bid_id': b'bid_id_1',
                    b'multioffer_id': b'multioffer_order_1',
                    b'driver_name': b'Driver_1',
                    b'car_model': b'Kia Rio',
                    b'created_at': b'1650272722',
                    b'timeout': b'30',
                    b'price': b'40.550000',
                    b'start_eta': b'300',
                    b'driver_avatar_url': b'https://avatar_url_1',
                    b'rating': b'4.1000',
                    b'trips_count': b'11',
                },
            ),
            (
                'order_1:bid_id:bid_id_2',
                {
                    b'bid_id': b'bid_id_2',
                    b'multioffer_id': b'multioffer_order_1',
                    b'driver_name': b'Driver_2',
                    b'car_model': b'Skoda Oktavia',
                    b'created_at': b'1650272700',
                    b'timeout': b'35',
                    b'price': b'42.000000',
                    b'start_eta': b'250',
                    b'driver_avatar_url': b'https://avatar_url_2',
                    b'rating': b'4.2',
                    b'trips_count': b'22',
                },
            ),
            (
                'order_1:bid_id:bid_id_3',
                {
                    b'bid_id': b'bid_id_3',
                    b'multioffer_id': b'multioffer_order_1',
                    b'driver_name': b'Driver_1',
                    b'car_model': b'Kia Rio',
                    b'created_at': b'1650272730',
                    b'timeout': b'30',
                    b'price': b'50.000000',
                    b'start_eta': b'200',
                    b'driver_avatar_url': b'https://avatar_url_1',
                    b'rating': b'4.1000',
                    b'trips_count': b'11',
                },
            ),
            (
                'order_2:bid_id:bid_id_1',
                {
                    b'bid_id': b'bid_id_1',
                    b'multioffer_id': b'multioffer_order_2',
                    b'driver_name': b'Driver_3',
                    b'car_model': b'Kia Rio',
                    b'created_at': b'1650272722',
                    b'timeout': b'30',
                    b'price': b'41.000000',
                    b'start_eta': b'300',
                    b'driver_avatar_url': b'https://avatar_url_3',
                    b'rating': b'4.3',
                    b'trips_count': b'33',
                },
            ),
            (
                'order_2:bid_id:bid_id_2',
                {
                    b'bid_id': b'bid_id_2',
                    b'multioffer_id': b'multioffer_order_2',
                    b'driver_name': b'Driver_4',
                    b'car_model': b'Hyundai Solaris',
                    b'created_at': b'1650272750',
                    b'timeout': b'20',
                    b'price': b'40.000000',
                    b'start_eta': b'350',
                    b'driver_avatar_url': b'https://avatar_url_4',
                    b'rating': b'4.4',
                },
            ),
    ]:
        assert redis_store.hgetall(hash_key) == response


@pytest.mark.redis_store(
    ['sadd', 'order_1:bid_ids:0', 'bid_id_1'],
    [
        'hmset',
        'order_1:bid_id:bid_id_1',
        {
            'bid_id': 'bid_id_1',
            'multioffer_id': 'multioffer_order_1',
            'driver_name': 'Driver_1',
            'car_model': 'Kia',
            'created_at': '1650272750',
            'timeout': '20',
            'price': '41.000000',
            'start_eta': '350',
        },
    ],
    ['sadd', 'order_1:bid_ids:1', 'bid_id_2', 'bid_id_3', 'bid_id_4'],
    [
        'hmset',
        'order_1:bid_id:bid_id_2',
        {
            'bid_id': 'bid_id_2',
            'multioffer_id': 'multioffer_order_1',
            'driver_name': 'Driver_2',
            'car_model': 'Kia',
            'created_at': '1650272750',
            'timeout': '20',
            'price': '42.000000',
            'start_eta': '350',
        },
    ],
    [
        'hmset',
        'order_1:bid_id:bid_id_3',
        {
            'bid_id': 'bid_id_3',
            'multioffer_id': 'multioffer_order_1',
            'driver_name': 'Driver_3',
            'car_model': 'Kia',
            'created_at': '1650272750',
            'timeout': '20',
            'price': '43.000000',
            'start_eta': '350',
        },
    ],
    [
        'hmset',
        'order_1:bid_id:bid_id_4',
        {
            'bid_id': 'bid_id_4',
            'multioffer_id': 'multioffer_order_1',
            'driver_name': 'Driver_4',
            'car_model': 'Kia',
            'created_at': '1650272750',
            'timeout': '20',
            'price': '43.000000',
            'start_eta': '350',
        },
    ],
    ['sadd', 'order_2:bid_ids:2', 'bid_id_6'],
    [
        'hmset',
        'order_2:bid_id:bid_id_6',
        {
            'bid_id': 'bid_id_6',
            'multioffer_id': 'multioffer_order_2',
            'driver_name': 'Driver_6',
            'car_model': 'Kia',
            'created_at': '1650272750',
            'timeout': '20',
            'price': '42.000000',
            'start_eta': '350',
        },
    ],
)
@pytest.mark.now('2022-04-18T09:05:20.000000+0000')
async def test_bid_rejects_event(
        taxi_order_search_status,
        taxi_eventus_orchestrator_mock,
        testpoint,
        redis_store,
):
    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_order_search_status, eventus_tools.bid_pipeline(),
    )

    @testpoint('bids_sink_testpoint')
    def bids_sink_testpoint(data):
        return data

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie1'

    events = [
        # driver cancelled bid_id_3
        utils.bid_related_event(
            'bid_cancelled',
            'order_1',
            'bid_id_3',
            'uuid1',
            1,
            reason='manual',
        ),
        # user rejected bid_id_4
        utils.bid_related_event(
            'bid_rejected', 'order_1', 'bid_id_4', 'uuid1', 1, reason='manual',
        ),
        # create bid bid_id_5 to order_1:bid_ids:1
        utils.bid_related_event(
            'bid_created',
            'order_1',
            'bid_id_5',
            'uuid1',
            1,
            unique_driver_id='unique_driver_1',
            price=42,
            created_at='2022-04-18T09:05:00.000000Z',
            timeout=35,
            driver_name='Driver_5',
            car_model='Kia',
            start_eta=250,
        ),
        # create bid bid_id_7 for order_2
        utils.bid_related_event(
            'bid_created',
            'order_2',
            'bid_id_7',
            'uuid1',
            2,
            unique_driver_id='unique_driver_1',
            price=50,
            created_at='2022-04-18T09:05:30.000000Z',
            timeout=30,
            driver_name='Driver_7',
            car_model='Kia Rio',
            start_eta=200,
        ),
        # new iteration for order_2
        utils.bid_related_event(
            'bid_rejected',
            'order_2',
            'bid_id_6',
            'uuid3',
            2,
            reason='new_iteration',
        ),
    ]

    response = await taxi_order_search_status.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-search-status-bids',
                'data': '\n'.join(events),
                'topic': 'smth',
                'cookie': 'cookie1',
            },
        ),
    )
    assert response.status_code == 200
    await bids_sink_testpoint.wait_call()
    await commit.wait_call()

    assert sorted_redis_keys(redis_store) == [
        'order_1:bid_id:bid_id_1',
        'order_1:bid_id:bid_id_2',
        'order_1:bid_id:bid_id_3',
        'order_1:bid_id:bid_id_4',
        'order_1:bid_id:bid_id_5',
        'order_1:bid_ids:0',
        'order_1:bid_ids:1',
        'order_2:bid_id:bid_id_6',
    ]
    for set_key, response in [
            ('order_1:bid_ids:0', ['bid_id_1']),
            ('order_1:bid_ids:1', ['bid_id_2', 'bid_id_5']),
    ]:
        assert (
            sorted(
                [
                    bid_id.decode('ascii')
                    for bid_id in redis_store.smembers(set_key)
                ],
            )
            == response
        )
