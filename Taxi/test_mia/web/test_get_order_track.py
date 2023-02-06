import datetime

import pytest


@pytest.mark.parametrize(
    'test',
    [
        {
            'request': {'order_id': 'test_order_id'},
            'expected': {
                'route': [
                    {'lon': 1.1, 'lat': 2.2},
                    {'lon': 1.1, 'lat': 2.2},
                    {'lon': 3.3, 'lat': 4.4},
                ],
                'track': [
                    {
                        'lon': 37.45069122314453,
                        'lat': 55.720542907714844,
                        'timestamp': '2020-07-15T21:25:34+03:00',
                        'direction': 1.1,
                    },
                    {
                        'lon': 37.45051956176758,
                        'lat': 55.72353744506836,
                        'timestamp': '2020-07-15T21:26:05+03:00',
                    },
                ],
            },
        },
    ],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'archive-api', 'src': 'mia'}])
async def test_get_order_track(
        taxi_mia_web, mockserver, test, order_archive_mock,
):
    def get_order_proc():
        return {
            'test_order_id': {
                '_id': 'test_order_id',
                'performer': {'park_id': 'test_park_id', 'candidate_index': 2},
                'order': {
                    'performer': {
                        'db_id': 'test_db_id',
                        'uuid': 'test_driver_uuid',
                    },
                    'request': {
                        'source': {'geopoint': [1.1, 2.2]},
                        'destinations': [
                            {'geopoint': [1.1, 2.2]},
                            {'geopoint': [3.3, 4.4]},
                        ],
                    },
                },
                'order_info': {
                    '_id': 'order_id_1',
                    'statistics': {
                        'status_updates': [
                            {
                                'i': 1,
                                'c': datetime.datetime(
                                    2020, 9, 11, 11, 13, 17,
                                ),
                            },
                            {
                                'i': 2,
                                'c': datetime.datetime(
                                    2020, 9, 11, 11, 13, 17, 16,
                                ),
                            },
                            {
                                'i': 2,
                                'c': datetime.datetime(
                                    2020, 9, 11, 11, 13, 17, 20,
                                ),
                            },
                            {
                                'i': 1,
                                'c': datetime.datetime(
                                    2020, 9, 11, 11, 13, 17, 16,
                                ),
                            },
                        ],
                    },
                },
            },
            'order_id_1': {
                '_id': 'order_id_1',
                'performer': {'park_id': 'test_park_id', 'candidate_index': 2},
                'order': {
                    'performer': {
                        'db_id': 'test_db_id',
                        'uuid': 'test_driver_uuid',
                    },
                    'request': {},
                },
                'order_info': {
                    'statistics': {
                        'status_updates': [
                            {
                                'i': 1,
                                'c': datetime.datetime(
                                    2020, 9, 11, 11, 13, 17,
                                ),
                            },
                            {
                                'i': 2,
                                'c': datetime.datetime(
                                    2020, 9, 11, 11, 13, 17, 16,
                                ),
                            },
                            {
                                'i': 2,
                                'c': datetime.datetime(
                                    2020, 9, 11, 11, 13, 17, 20,
                                ),
                            },
                            {
                                'i': 1,
                                'c': datetime.datetime(
                                    2020, 9, 11, 11, 13, 17, 16,
                                ),
                            },
                        ],
                    },
                },
            },
        }

    order_archive_mock.set_order_proc(get_order_proc().values())

    @mockserver.json_handler('/driver-trackstory/get_track')
    async def _get_track(request):
        assert request.json['id'] == 'test_db_id_test_driver_uuid'
        return mockserver.make_response(
            json={
                'id': 'test_db_id_test_driver_uuid',
                'track': [
                    {
                        'lat': 55.720542907714844,
                        'lon': 37.45069122314453,
                        'timestamp': 1594837534,
                        'direction': 1.1,
                    },
                    {
                        'lat': 55.72353744506836,
                        'lon': 37.45051956176758,
                        'timestamp': 1594837565,
                    },
                ],
            },
        )

    order_id = test['request']['order_id']
    response = await taxi_mia_web.get(
        f'/v1/taxi/get_order_track?order_id={order_id}',
    )

    assert response.status == 200

    content = await response.json()
    assert content == test['expected']


@pytest.mark.config(TVM_RULES=[{'dst': 'archive-api', 'src': 'mia'}])
async def test_get_order_track_404(taxi_mia_web, order_archive_mock):
    response = await taxi_mia_web.get(
        f'/v1/taxi/get_order_track?order_id=test_order_id',
    )

    assert response.status == 404

    content = await response.json()
    assert content['code'] == 'order_not_found'
    assert content['message'] == 'Order test_order_id is not found'
