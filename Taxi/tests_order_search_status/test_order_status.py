import json

import pytest

from tests_order_search_status import eventus_tools
from tests_order_search_status import utils

HEADERS = {'X-Yandex-UID': '4003514353', 'X-Request-Language': 'ru'}
URL = '/4.0/order-search-status/v1/order-status'

ORDER_6_BID_INFOS = [
    {
        'bid_id': 'bid_id_2',
        'multioffer_id': 'multioffer_order_6',
        'candidate_name': 'Driver_2',
        'car_model': 'Kia',
        'created_at': 1650272750,
        'ttl': 20,
        'price': 41.0,
        'eta': 350,
        'trips_count': 10,
    },
    {
        'bid_id': 'bid_id_3',
        'multioffer_id': 'multioffer_order_6',
        'candidate_name': 'Driver_3',
        'car_model': 'Kia',
        'created_at': 1650272749,
        'ttl': 20,
        'price': 43.0,
        'eta': 350,
    },
    {
        'bid_id': 'bid_id_4',
        'multioffer_id': 'multioffer_order_6',
        'candidate_name': 'Driver_4',
        'car_model': 'Kia',
        'created_at': 1650272750,
        'ttl': 20,
        'price': 43.0,
        'eta': 350,
    },
]


@pytest.mark.redis_store(
    ['sadd', 'order_6:bid_ids:0', 'bid_id_1'],
    [
        'hmset',
        'order_6:bid_id:bid_id_1',
        {
            'bid_id': 'bid_id_1',
            'multioffer_id': 'multioffer_order_6',
            'driver_name': 'Driver_1',
            'car_model': 'Kia',
            'created_at': '1650272750',
            'timeout': '20',
            'price': '41.000000',
            'start_eta': '350',
        },
    ],
    [
        'sadd',
        'order_6:bid_ids:1',
        'bid_id_2',
        'bid_id_3',
        'bid_id_4',
        'bid_id_7',
        'bid_id_8',
    ],
    [
        'hmset',
        'order_6:bid_id:bid_id_2',
        {
            'bid_id': 'bid_id_2',
            'multioffer_id': 'multioffer_order_6',
            'driver_name': 'Driver_2',
            'car_model': 'Kia',
            'created_at': '1650272750',
            'timeout': '20',
            'price': '41.000000',
            'start_eta': '350',
            'trips_count': '10',
        },
    ],
    [
        'hmset',
        'order_6:bid_id:bid_id_3',
        {
            'bid_id': 'bid_id_3',
            'multioffer_id': 'multioffer_order_6',
            'driver_name': 'Driver_3',
            'car_model': 'Kia',
            'created_at': '1650272749',
            'timeout': '20',
            'price': '43.000000',
            'start_eta': '350',
        },
    ],
    [
        'hmset',
        'order_6:bid_id:bid_id_4',
        {
            'bid_id': 'bid_id_4',
            'multioffer_id': 'multioffer_order_6',
            'driver_name': 'Driver_4',
            'car_model': 'Kia',
            'created_at': '1650272750',
            'timeout': '20',
            'price': '43.000000',
            'start_eta': '350',
        },
    ],
)
async def test_v1_order_status(
        taxi_order_search_status,
        testpoint,
        taxi_eventus_orchestrator_mock,
        redis_store,
):
    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint,
        taxi_order_search_status,
        eventus_tools.create_rejects_pipeline(),
    )

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie1'

    events = [
        utils.generate_event('any', 'any', 'multioffer_seen_timeout'),
        utils.generate_event('any', 'any', 'multioffer_seen'),
        utils.generate_event('any', 'any', 'multioffer_accept'),
        utils.generate_event('any', 'any', 'multioffer_win'),
        utils.generate_event('any', 'any', 'multioffer_lose'),
        # previous iteration
        utils.generate_event(
            'order_1',
            'uuid1',
            'multioffer_reject',
            {'auction': {'iteration': 0}},
        ),
        utils.generate_event(
            'order_1',
            'uuid2',
            'multioffer_reject',
            {'auction': {'iteration': 0}},
        ),
        # actual iteration
        utils.generate_event(
            'order_1',
            'uuid1',
            'multioffer_reject',
            {'auction': {'iteration': 1}},
        ),
        utils.generate_event(
            'order_1',
            'uuid2',
            'multioffer_reject',
            {'auction': {'iteration': 1}},
        ),
        # duplicate
        utils.generate_event(
            'order_1',
            'uuid2',
            'multioffer_reject',
            {'auction': {'iteration': 1}},
        ),
        # other cases
        utils.generate_event(
            'order_2',
            'uuid1',
            'multioffer_reject',
            {'auction': {'iteration': 2}},
        ),
        utils.generate_event(
            'order_3',
            'uuid2',
            'multioffer_reject',
            {'auction': {'iteration': 2}},
        ),
        utils.generate_event(
            'order_4', 'uuid1', 'multioffer_reject',
        ),  # auction is None
        utils.generate_event(
            'order_5',
            'uuid1',
            'multioffer_reject',
            {'auction': {'iteration': 10}},
        ),
    ]

    response = await taxi_order_search_status.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-search-status-rejects',
                'data': '\n'.join(events),
                'topic': 'smth',
                'cookie': 'cookie1',
            },
        ),
    )
    assert response.status_code == 200
    await commit.wait_call()

    redis_store.sadd('order_5:auction:9', 'dbid_uuid2')
    etalon = {
        'order_1:auction:1': ['dbid_uuid1', 'dbid_uuid2'],
        'order_2:auction:2': ['dbid_uuid1'],
        'order_3:auction:2': ['dbid_uuid2'],
        'order_4:auction:0': ['dbid_uuid1'],
        'order_5:auction:9': ['dbid_uuid2'],
        'order_5:auction:10': ['dbid_uuid1'],
    }
    utils.check_redis_auction_values(redis_store, etalon)

    for (order_id, iteration, reject_count) in [
            ('order_1', 1, 2),
            ('order_2', 2, 1),
            ('order_3', 2, 1),
            ('order_4', 0, 1),
            ('order_5', 10, 1),
    ]:
        response = await taxi_order_search_status.get(
            URL, headers=HEADERS, params={'order_id': order_id},
        )
        assert response.status_code == 200
        resp_json = response.json()
        assert resp_json == {
            'auction': {
                'iteration': iteration,
                'rejections_count': reject_count,
            },
        }

    response = await taxi_order_search_status.get(
        URL, headers=HEADERS, params={'order_id': 'order_6'},
    )
    resp_json = response.json()
    assert resp_json == {'bids': ORDER_6_BID_INFOS}

    response = await taxi_order_search_status.get(
        URL, headers=HEADERS, params={'order_id': 'not_found'},
    )
    resp_json = response.json()
    assert response.status_code == 404
    assert resp_json['code'] == 'NOT_FOUND'


BIDS = [
    {
        'bid_id': '1',
        'multioffer_id': 'multioffer_id1',
        'candidate_name': 'Name 1',
        'car_model': 'Nissan Almera',
        'created_at': 1649337283,
        'ttl': 30,
        'price': 3101,
        'eta': 15,
        'rating': '4.8',
        'trips_count': 20,
        'driver_avatar_url': 'http://avatars.mdst.yandex.net/photos/603/orig',
    },
    {
        'bid_id': '2',
        'multioffer_id': 'multioffer_id1',
        'candidate_name': 'Name 2',
        'car_model': 'Kia Rio',
        'created_at': 1649337283,
        'ttl': 30,
        'price': 3100.22,
        'eta': 13,
    },
    {
        'bid_id': '3',
        'multioffer_id': 'multioffer_id1',
        'candidate_name': 'Name 3',
        'car_model': 'Nissan Almera',
        'created_at': 1649337283,
        'ttl': 30,
        'price': 3101,
        'eta': 14,
    },
]


@pytest.mark.config(
    ORDER_SEARCH_STATUS_ORDER_STATUS_MOCK={
        'enabled': True,
        'iteration': 2,
        'rejections_count': 5,
        'bids': BIDS,
    },
)
async def test_v1_order_status_mock(taxi_order_search_status):
    response = await taxi_order_search_status.get(
        URL, headers=HEADERS, params={'order_id': 'some_order'},
    )
    assert response.status_code == 200
    resp_json = response.json()

    def key_function(bid):
        return (bid['price'], bid['eta'], bid['created_at'])

    assert resp_json == {
        'auction': {'iteration': 2, 'rejections_count': 5},
        'bids': sorted(BIDS, key=key_function),
    }
