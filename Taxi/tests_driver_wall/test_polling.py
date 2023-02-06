import pytest

import tests_driver_wall.error404 as error

DEFAULT_HEADERS = {
    'X-YaTaxi-Driver-Profile-Id': 'uuid1',
    'X-YaTaxi-Park-Id': 'dbid1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'Accept-language': 'ru',
    'If-None-Match': 'badetag',
}


@pytest.mark.now('2018-08-05T00:00:00Z')
async def test_feeds(
        taxi_driver_wall, mock_fleet_parks_list, driver_authorizer, mockserver,
):
    def fetch(request):
        assert 'earlier_than' not in request
        if request['etag'] == '18d667a167fa5d35b6ab67bfb29c2eef':
            return {'etag_changed': False}
        if request['service'] == 'driver-wall':
            return {
                'etag_changed': True,
                'response': {
                    'etag': '18d667a167fa5d35b6ab67bfb29c2eef',
                    'feed': [
                        {
                            'created': '2018-08-01T12:00:00.000000+0000',
                            'feed_id': '111d7e58b5a14bff9f65b8dc0bede3b4',
                            'request_id': 'request_id',
                            'last_status': {
                                'created': '2020-05-06T12:52:25.917119+0000',
                                'status': 'published',
                            },
                            'payload': {'text': 'some_text_1'},
                        },
                        {
                            'created': '2018-08-02T12:00:00.000000+0000',
                            'feed_id': '222b56eec1794602ac85a7e3ba53450e',
                            'request_id': 'request_id',
                            'last_status': {
                                'created': '2020-05-06T12:52:25.672798+0000',
                                'status': 'published',
                            },
                            'payload': {'text': 'some_text_2'},
                        },
                        {
                            'created': '2018-08-03T12:00:00.000000+0000',
                            'feed_id': '333b56eec1794602ac85a7e3ba53450e',
                            'request_id': 'request_id',
                            'last_status': {
                                'created': '2020-05-06T12:52:25.672798+0000',
                                'status': 'published',
                            },
                            'payload': {'text': 'some_text_3'},
                        },
                        {
                            'created': '2018-08-04T23:59:20.000000+0000',
                            'feed_id': '444b56eec1794602ac85a7e3ba53450e',
                            'request_id': 'request_id',
                            'last_status': {
                                'created': '2020-05-06T12:52:25.672798+0000',
                                'status': 'published',
                            },
                            'payload': {'text': 'some_text_3'},
                        },
                        {
                            'created': '2018-08-04T23:59:20.000000+0000',
                            'feed_id': '555b56eec1794602ac85a7e3ba53450e',
                            'request_id': 'request_id',
                            'last_status': {
                                'created': '2020-05-06T12:52:25.672798+0000',
                                'status': 'published',
                            },
                            'payload': {'text': 'some_text_3'},
                        },
                    ],
                    'has_more': False,
                    'polling_delay': 30,
                },
            }
        return {
            'etag_changed': True,
            'response': {
                'etag': '18d667a167fa5d35b6ab67bfb29c2eef',
                'feed': [
                    {
                        'created': '2018-08-01T12:00:00.000000+0000',
                        'feed_id': '11117e58b5a14bff9f65b8dc0bede3b4',
                        'request_id': 'request_id',
                        'last_status': {
                            'created': '2020-05-06T12:52:25.917119+0000',
                            'status': 'published',
                        },
                        'payload': {'text': 'some_text_1'},
                    },
                    {
                        'created': '2018-08-05T23:59:21.000000+0000',
                        'feed_id': '22227e58b5a14bff9f65b8dc0bede3b4',
                        'request_id': 'request_id',
                        'last_status': {
                            'created': '2020-05-06T12:52:25.917119+0000',
                            'status': 'published',
                        },
                        'payload': {'text': 'some_text_1'},
                    },
                ],
                'has_more': False,
                'polling_delay': 30,
            },
        }

    @mockserver.json_handler('/feeds/v1/batch/fetch')
    def _mock_batch_fetch_feeds(request):
        try:
            return {'items': [fetch(item) for item in request.json['items']]}
        except error.Error404:
            return mockserver.make_response('Not found or invalid method', 404)

    params = {'from': '2018-08-01T00:00:00.000Z', 'limit': 4}

    headers = DEFAULT_HEADERS.copy()

    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/polling', params=params, headers=headers,
    )
    assert response.status_code == 200
    etag = response.headers['ETag']

    assert (
        etag
        == '18d667a167fa5d35b6ab67bfb29c2eef:18d667a167fa5d35b6ab67bfb29c2eef'
    )

    data = response.json()

    assert '333b56eec1794602ac85a7e3ba53450e' in data
    assert '444b56eec1794602ac85a7e3ba53450e' in data
    assert '555b56eec1794602ac85a7e3ba53450e' in data
    assert '111b56eec1794602ac85a7e3ba53450e' not in data

    headers['If-None-Match'] = etag
    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/polling', params=params, headers=headers,
    )
    assert response.status_code == 304


@pytest.mark.now('2018-08-05T00:00:00Z')
async def test_feeds_with_same_created(
        taxi_driver_wall, mock_fleet_parks_list, driver_authorizer, mockserver,
):
    def fetch(request):
        assert 'earlier_than' not in request
        if request['etag'] == '18d667a167fa5d35b6ab67bfb29c2eef':
            return {'etag_changed': False}
        if request['service'] == 'driver-wall':
            return {
                'etag_changed': True,
                'response': {
                    'etag': '18d667a167fa5d35b6ab67bfb29c2eef',
                    'feed': [
                        {
                            'created': '2018-08-01T12:00:00.000000+0000',
                            'feed_id': '111d7e58b5a14bff9f65b8dc0bede3b4',
                            'request_id': 'request_id',
                            'last_status': {
                                'created': '2020-05-06T12:52:25.917119+0000',
                                'status': 'published',
                            },
                            'payload': {'text': 'some_text_1'},
                        },
                        {
                            'created': '2018-08-02T12:00:00.000000+0000',
                            'feed_id': '222b56eec1794602ac85a7e3ba53450e',
                            'request_id': 'request_id',
                            'last_status': {
                                'created': '2020-05-06T12:52:25.672798+0000',
                                'status': 'published',
                            },
                            'payload': {'text': 'some_text_2'},
                        },
                        {
                            'created': '2018-08-02T12:00:00.000000+0000',
                            'feed_id': '333b56eec1794602ac85a7e3ba53450e',
                            'request_id': 'request_id',
                            'last_status': {
                                'created': '2020-05-06T12:52:25.672798+0000',
                                'status': 'published',
                            },
                            'payload': {'text': 'some_text_3'},
                        },
                    ],
                    'has_more': False,
                    'polling_delay': 30,
                },
            }
        return {
            'etag_changed': True,
            'response': {
                'etag': '18d667a167fa5d35b6ab67bfb29c2eef',
                'feed': [
                    {
                        'created': '2018-08-02T12:00:00.000000+0000',
                        'feed_id': '11117e58b5a14bff9f65b8dc0bede3b4',
                        'request_id': 'request_id',
                        'last_status': {
                            'created': '2020-05-06T12:52:25.917119+0000',
                            'status': 'published',
                        },
                        'payload': {'text': 'some_text_1'},
                    },
                    {
                        'created': '2018-08-02T12:00:00.000000+0000',
                        'feed_id': '22227e58b5a14bff9f65b8dc0bede3b4',
                        'request_id': 'request_id',
                        'last_status': {
                            'created': '2020-05-06T12:52:25.917119+0000',
                            'status': 'published',
                        },
                        'payload': {'text': 'some_text_1'},
                    },
                ],
                'has_more': False,
                'polling_delay': 30,
            },
        }

    @mockserver.json_handler('/feeds/v1/batch/fetch')
    def _mock_batch_fetch_feeds(request):
        try:
            return {'items': [fetch(item) for item in request.json['items']]}
        except error.Error404:
            return mockserver.make_response('Not found or invalid method', 404)

    params = {'from': '2018-08-01T00:00:00.000Z', 'limit': 3}

    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/polling',
        params=params,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    data = response.json()

    assert {
        '222b56eec1794602ac85a7e3ba53450e',
        '333b56eec1794602ac85a7e3ba53450e',
        '11117e58b5a14bff9f65b8dc0bede3b4',
        '22227e58b5a14bff9f65b8dc0bede3b4',
    } == set(data)


@pytest.mark.now('2018-08-05T00:00:00Z')
async def test_feeds_update_not_all_services(
        taxi_driver_wall, mock_fleet_parks_list, driver_authorizer, mockserver,
):
    def fetch(request):
        if request['etag'] == '18d667a167fa5d35b6ab67bfb29c2eef':
            return {'etag_changed': False}
        if request['service'] == 'driver-wall':
            return {
                'etag_changed': True,
                'response': {
                    'etag': '18d667a167fa5d35b6ab67bfb29c2eef',
                    'feed': [
                        {
                            'created': '2018-08-01T12:00:00.000000+0000',
                            'feed_id': '111d7e58b5a14bff9f65b8dc0bede3b4',
                            'request_id': 'request_id',
                            'last_status': {
                                'created': '2020-05-06T12:52:25.917119+0000',
                                'status': 'published',
                            },
                            'payload': {'text': 'some_text_1'},
                        },
                        {
                            'created': '2018-08-02T12:00:00.000000+0000',
                            'feed_id': '222b56eec1794602ac85a7e3ba53450e',
                            'request_id': 'request_id',
                            'last_status': {
                                'created': '2020-05-06T12:52:25.672798+0000',
                                'status': 'published',
                            },
                            'payload': {'text': 'some_text_2'},
                        },
                        {
                            'created': '2018-08-02T12:00:00.000000+0000',
                            'feed_id': '333b56eec1794602ac85a7e3ba53450e',
                            'request_id': 'request_id',
                            'last_status': {
                                'created': '2020-05-06T12:52:25.672798+0000',
                                'status': 'published',
                            },
                            'payload': {'text': 'some_text_3'},
                        },
                    ],
                    'has_more': False,
                    'polling_delay': 30,
                },
            }
        return {
            'etag_changed': True,
            'response': {
                'etag': '18d667a167fa5d35b6ab67bfb29c2eef',
                'feed': [
                    {
                        'created': '2018-08-02T12:00:00.000000+0000',
                        'feed_id': '11117e58b5a14bff9f65b8dc0bede3b4',
                        'request_id': 'request_id',
                        'last_status': {
                            'created': '2020-05-06T12:52:25.917119+0000',
                            'status': 'published',
                        },
                        'payload': {'text': 'some_text_1'},
                    },
                    {
                        'created': '2018-08-02T12:00:00.000000+0000',
                        'feed_id': '22227e58b5a14bff9f65b8dc0bede3b4',
                        'request_id': 'request_id',
                        'last_status': {
                            'created': '2020-05-06T12:52:25.917119+0000',
                            'status': 'published',
                        },
                        'payload': {'text': 'some_text_1'},
                    },
                ],
                'has_more': False,
                'polling_delay': 30,
            },
        }

    @mockserver.json_handler('/feeds/v1/batch/fetch')
    def _mock_batch_fetch_feeds(request):
        try:
            return {'items': [fetch(item) for item in request.json['items']]}
        except error.Error404:
            return mockserver.make_response('Not found or invalid method', 404)

    params = {'from': '2018-08-01T00:00:00.000Z', 'limit': 3}

    headers = {
        'X-YaTaxi-Driver-Profile-Id': 'uuid1',
        'X-YaTaxi-Park-Id': 'dbid1',
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': '9.40',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'Accept-language': 'ru',
        'If-None-Match': (
            '18d667a167fa5d35b6ab67bfb29c2eef:'
            '11111111111111111111111111111111'
        ),
    }

    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/polling', params=params, headers=headers,
    )
    assert response.status_code == 200
    data = response.json()

    assert {
        '222b56eec1794602ac85a7e3ba53450e',
        '333b56eec1794602ac85a7e3ba53450e',
        '11117e58b5a14bff9f65b8dc0bede3b4',
        '22227e58b5a14bff9f65b8dc0bede3b4',
    } == set(data)

    headers = {
        'X-YaTaxi-Driver-Profile-Id': 'uuid1',
        'X-YaTaxi-Park-Id': 'dbid1',
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': '9.40',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'Accept-language': 'ru',
        'If-None-Match': (
            '11111111111111111111111111111111:'
            '18d667a167fa5d35b6ab67bfb29c2eef'
        ),
    }

    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/polling', params=params, headers=headers,
    )
    assert response.status_code == 200
    data = response.json()

    assert {
        '222b56eec1794602ac85a7e3ba53450e',
        '333b56eec1794602ac85a7e3ba53450e',
        '11117e58b5a14bff9f65b8dc0bede3b4',
        '22227e58b5a14bff9f65b8dc0bede3b4',
    } == set(data)


@pytest.mark.now('2018-08-05T00:00:00Z')
async def test_driver_communicaitions_feeds(
        taxi_driver_wall,
        mock_fleet_parks_list,
        driver_authorizer,
        mockserver,
        load_json,
):
    def fetch(request):
        responses = load_json('driver_communications_feeds_resopnses.json')
        return {
            'etag_changed': True,
            'response': responses[request['service']],
        }

    @mockserver.json_handler('/feeds/v1/batch/fetch')
    def _mock_batch_fetch_feeds(request):
        try:
            return {'items': [fetch(item) for item in request.json['items']]}
        except error.Error404:
            return mockserver.make_response('Not found or invalid method', 404)

    params = {'from': '2018-08-01T00:00:00.000Z'}

    headers = {
        'X-YaTaxi-Driver-Profile-Id': 'uuid1',
        'X-YaTaxi-Park-Id': 'dbid1',
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': '9.40',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'Accept-language': 'ru',
        'If-None-Match': 'badetag',
    }

    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/polling', params=params, headers=headers,
    )
    assert response.status_code == 200

    data = response.json()

    assert '111d7e58b5a14bff9f65b8dc0bede3b4' in data
    assert '11117e58b5a14bff9f65b8dc0bede3b4' in data
    assert '222d7e58b5a14bff9f65b8dc0bede3b4' not in data
    assert '22227e58b5a14bff9f65b8dc0bede3b4' not in data


@pytest.mark.now('2018-08-05T00:00:00Z')
async def test_feeds_several_request(
        taxi_driver_wall, mock_fleet_parks_list, driver_authorizer, mockserver,
):
    def fetch(request):
        if request['service'] == 'driver-wall':
            if 'earlier_than' not in request:
                return {
                    'etag_changed': True,
                    'response': {
                        'etag': '18d667a167fa5d35b6ab67bfb29c2eef',
                        'feed': [
                            {
                                'created': '2018-08-01T12:00:00.000000+0000',
                                'feed_id': '111b56eec1794602ac85a7e3ba53450e',
                                'request_id': 'request_id',
                                'last_status': {
                                    'created': (
                                        '2020-05-06T12:52:25.917119+0000'
                                    ),
                                    'status': 'published',
                                },
                                'payload': {'text': 'some_text_1'},
                            },
                            {
                                'created': '2018-08-02T12:00:00.000000+0000',
                                'feed_id': '222b56eec1794602ac85a7e3ba53450e',
                                'request_id': 'request_id',
                                'last_status': {
                                    'created': (
                                        '2020-05-06T12:52:25.672798+0000'
                                    ),
                                    'status': 'published',
                                },
                                'payload': {'text': 'some_text_2'},
                            },
                        ],
                        'has_more': True,
                        'polling_delay': 30,
                    },
                }
            return {
                'etag_changed': True,
                'response': {
                    'etag': '18d667a167fa5d35b6ab67bfb29c2eef',
                    'feed': [
                        {
                            'created': '2018-08-03T12:00:00.000000+0000',
                            'feed_id': '333b56eec1794602ac85a7e3ba53450e',
                            'request_id': 'request_id',
                            'last_status': {
                                'created': '2020-05-06T12:52:25.672798+0000',
                                'status': 'published',
                            },
                            'payload': {'text': 'some_text_3'},
                        },
                        {
                            'created': '2018-08-04T23:59:20.000000+0000',
                            'feed_id': '444b56eec1794602ac85a7e3ba53450e',
                            'request_id': 'request_id',
                            'last_status': {
                                'created': '2020-05-06T12:52:25.672798+0000',
                                'status': 'published',
                            },
                            'payload': {'text': 'some_text_3'},
                        },
                    ],
                    'has_more': False,
                    'polling_delay': 30,
                },
            }
        return {
            'etag_changed': True,
            'response': {
                'etag': '18d667a167fa5d35b6ab67bfb29c2eef',
                'feed': [],
                'has_more': False,
                'polling_delay': 30,
            },
        }

    @mockserver.json_handler('/feeds/v1/batch/fetch')
    def _mock_batch_fetch_feeds(request):
        try:
            return {'items': [fetch(item) for item in request.json['items']]}
        except error.Error404:
            return mockserver.make_response('Not found or invalid method', 404)

    headers = {
        'X-YaTaxi-Driver-Profile-Id': 'uuid1',
        'X-YaTaxi-Park-Id': 'dbid1',
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': '9.40',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'Accept-language': 'ru',
        'If-None-Match': 'badetag',
    }

    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/polling',
        params={'from': '2018-08-01T00:00:00.000Z', 'limit': 3},
        headers=headers,
    )
    assert response.status_code == 200

    data = response.json()

    assert {
        '222b56eec1794602ac85a7e3ba53450e',
        '333b56eec1794602ac85a7e3ba53450e',
        '444b56eec1794602ac85a7e3ba53450e',
    } == set(data)

    assert (
        response.headers['ETag']
        == '18d667a167fa5d35b6ab67bfb29c2eef:18d667a167fa5d35b6ab67bfb29c2eef'
    )

    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/polling',
        params={'from': '2018-08-01T00:00:00.000Z'},
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert {
        '111b56eec1794602ac85a7e3ba53450e',
        '222b56eec1794602ac85a7e3ba53450e',
        '333b56eec1794602ac85a7e3ba53450e',
        '444b56eec1794602ac85a7e3ba53450e',
    } == set(data)


@pytest.mark.now('2018-08-05T00:00:00Z')
@pytest.mark.experiments3(filename='driver_channels_experiment.json')
async def test_channel_experiments(
        taxi_driver_wall, mock_fleet_parks_list, driver_authorizer, mockserver,
):
    def fetch(request):
        assert sorted(request['channels']) == [
            'taximeter:City:МОСКВА',
            'taximeter:Country:РОССИЯ',
            'taximeter:Driver:dbid1:uuid1',
            'taximeter:Experiment:driver_wall_channel_experiment',
            'taximeter:Park:dbid1',
        ]
        if request['service'] == 'driver-wall':
            return {
                'etag_changed': True,
                'response': {
                    'etag': '18d667a167fa5d35b6ab67bfb29c2eef',
                    'feed': [
                        {
                            'created': '2018-08-01T12:00:00.000000+0000',
                            'feed_id': '111d7e58b5a14bff9f65b8dc0bede3b4',
                            'request_id': 'request_id',
                            'last_status': {
                                'created': '2020-05-06T12:52:25.917119+0000',
                                'status': 'published',
                            },
                            'payload': {'text': 'some_text_1'},
                        },
                    ],
                    'has_more': False,
                    'polling_delay': 30,
                },
            }
        return {
            'etag_changed': True,
            'response': {
                'etag': '18d667a167fa5d35b6ab67bfb29c2eef',
                'feed': [
                    {
                        'created': '2018-08-01T12:00:00.000000+0000',
                        'feed_id': '11117e58b5a14bff9f65b8dc0bede3b4',
                        'request_id': 'request_id',
                        'last_status': {
                            'created': '2020-05-06T12:52:25.917119+0000',
                            'status': 'published',
                        },
                        'payload': {'text': 'some_text_1'},
                    },
                ],
                'has_more': False,
                'polling_delay': 30,
            },
        }

    @mockserver.json_handler('/feeds/v1/batch/fetch')
    def _mock_batch_fetch_feeds(request):
        try:
            return {'items': [fetch(item) for item in request.json['items']]}
        except error.Error404:
            return mockserver.make_response('Not found or invalid method', 404)

    params = {'from': '2018-08-01T00:00:00.000Z', 'limit': 4}

    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/polling',
        params=params,
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200


@pytest.mark.now('2018-08-05T00:00:00Z')
@pytest.mark.config(
    DRIVER_WALL_FEEDS_SERVICES=[
        'driver-wall',
        'driver-fullscreen',
        'other-service',
    ],
)
async def test_feeds_services_config(
        taxi_driver_wall,
        mock_fleet_parks_list,
        driver_authorizer,
        mockserver,
        load_json,
):
    def fetch(request):
        if request['service'] == 'driver-wall':
            return {
                'etag_changed': True,
                'response': load_json('feeds_driver_wall_fetch.json'),
            }
        if request['service'] == 'driver-fullscreen':
            return {
                'etag_changed': True,
                'response': load_json('feeds_driver_fullscreen_fetch.json'),
            }
        if request['service'] == 'other-service':
            return {
                'etag_changed': True,
                'response': load_json('feeds_other_service_fetch.json'),
            }
        assert False
        return {}

    @mockserver.json_handler('/feeds/v1/batch/fetch')
    def _mock_batch_fetch_feeds(request):
        try:
            return {'items': [fetch(item) for item in request.json['items']]}
        except error.Error404:
            return mockserver.make_response('Not found or invalid method', 404)

    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/polling',
        params={'from': '2018-08-01T00:00:00.000Z', 'limit': 3},
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
