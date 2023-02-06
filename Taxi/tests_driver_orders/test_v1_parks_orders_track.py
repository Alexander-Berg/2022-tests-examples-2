import datetime

import dateutil.parser
import pytest


ENDPOINT = 'v1/parks/orders/track'
MOCK_URL = '/driver-trackstory/get_track'


@pytest.mark.parametrize(
    'park_id, order_id',
    [
        ('no_park', 'no_order'),
        ('no_park', 'order1'),
        ('park_id_1', 'no_order'),
    ],
)
async def test_not_found(
        taxi_driver_orders, fleet_parks_shard, park_id, order_id,
):
    response = await taxi_driver_orders.post(
        ENDPOINT, params={'park_id': park_id, 'order_id': order_id},
    )

    assert response.status == 404, response.text
    assert response.json() == {
        'code': '404',
        'message': 'park or order was not found',
    }


@pytest.mark.parametrize('order_id', ['order4', 'order5'])
async def test_empty_driver_id(
        taxi_driver_orders, fleet_parks_shard, order_id,
):
    response = await taxi_driver_orders.post(
        ENDPOINT, params={'park_id': 'park_id_2', 'order_id': order_id},
    )

    assert response.status == 200, response.text
    assert response.json() == {'track': []}


TRACK = [
    {
        'at': '2019-05-01T07:09:00+00:00',
        'lat': 55.773782,
        'lon': 37.605617,
        'speed': 7,
        'direction': 0,
    },
    {
        'at': '2019-05-01T07:10:00+00:00',
        'lat': 55.770000,
        'lon': 37.600000,
        'speed': 3,
        'status': 'driving',
        'direction': 90,
    },
    {
        'at': '2019-05-01T07:14:00+00:00',
        'lat': 55.771000,
        'lon': 37.601000,
        'status': 'driving',
        'speed': 5,
        'direction': 359,
    },
    {
        'at': '2019-05-01T07:15:00+00:00',
        'lat': 55.772000,
        'lon': 37.602000,
        'status': 'waiting',
    },
    {
        'at': '2019-05-01T07:20:00+00:00',
        'lat': 55.772000,
        'lon': 37.602000,
        'status': 'waiting',
    },
    {
        'at': '2019-05-01T07:21:00+00:00',
        'lat': 55.775000,
        'lon': 37.605000,
        'status': 'transporting',
        'speed': 9.12,
    },
    {
        'at': '2019-05-01T07:24:00+00:00',
        'lat': 55.780000,
        'lon': 37.610000,
        'status': 'transporting',
        'speed': -13.000023,
    },
]


@pytest.mark.now('2019-05-01T07:29:42')
async def test_ok(taxi_driver_orders, fleet_parks_shard, mockserver):
    @mockserver.json_handler(MOCK_URL)
    async def mock_driver_trackstory(request):
        def _iso_to_ts(iso):
            return int(datetime.datetime.timestamp(dateutil.parser.parse(iso)))

        request.get_data()
        return {
            'id': 'park_id_8_driver_id_0',
            'track': [
                {
                    'timestamp': _iso_to_ts(point['at']),
                    'lat': point['lat'],
                    'lon': point['lon'],
                    **({'speed': point['speed']} if 'speed' in point else {}),
                    **(
                        {'direction': point['direction']}
                        if 'direction' in point
                        else {}
                    ),
                }
                for point in TRACK
            ],
        }

    response = await taxi_driver_orders.post(
        ENDPOINT, params={'park_id': 'park_id_8', 'order_id': 'order8'},
    )

    assert response.status == 200, response.text
    assert response.json() == {
        'track': [
            {
                'tracked_at': point['at'],
                'location': {'lat': point['lat'], 'lon': point['lon']},
                **({'speed': abs(point['speed'])} if 'speed' in point else {}),
                **(
                    {'order_status': point['status']}
                    if 'status' in point
                    else {}
                ),
                **(
                    {'direction': point['direction']}
                    if 'direction' in point
                    else {}
                ),
            }
            for point in TRACK
        ],
        'distance': 1823.7417699654852,
    }

    assert mock_driver_trackstory.times_called >= 1
    driver_trackstory_request = mock_driver_trackstory.next_call()['request']
    assert driver_trackstory_request.method == 'POST'
    assert driver_trackstory_request.json == {
        'id': 'park_id_8_driver_id_0',
        'adjust': False,
        'simplify': False,
        'no_filter': False,
        'from_time': '2019-05-01T07:05:00+00:00',
        'to_time': '2019-05-01T07:29:42+00:00',
    }
