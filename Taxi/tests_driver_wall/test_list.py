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
}


@pytest.fixture(autouse=True, name='mock_driver_profiles')
def _mock_driver_profiles(mockserver):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock(request):
        return {
            'profiles': [
                {'park_driver_profile_id': 'dbid1', 'data': {'locale': 'en'}},
            ],
        }


@pytest.mark.now('2018-08-05T00:00:00Z')
async def test_basic(taxi_driver_wall, mock_fleet_parks_list, mockserver):
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
                    'has_more': True,
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
        return {'items': [fetch(item) for item in request.json['items']]}

    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/list',
        params={'to': '2018-08-06T00:00:00.000Z', 'limit': 2},
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200

    assert response.json() == {
        '111d7e58b5a14bff9f65b8dc0bede3b4': {
            'text': 'some_text_1',
            'type': 'newsletter',
            'format': 'Raw',
            'timestamp': '2018-08-01T12:00:00.000Z',
        },
        '222b56eec1794602ac85a7e3ba53450e': {
            'text': 'some_text_2',
            'type': 'newsletter',
            'format': 'Raw',
            'timestamp': '2018-08-02T12:00:00.000Z',
        },
    }


@pytest.mark.now('2018-08-05T00:00:00Z')
async def test_feeds_with_image(
        taxi_driver_wall, mock_fleet_parks_list, mockserver,
):
    def fetch(request):
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
                            'payload': {
                                'title': 'Новость с image_id',
                                'image_id': '01012019/hexhexhex',
                                'series_id': 'my_series1',
                                'text': 'Текст',
                            },
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
        return {'items': [fetch(item) for item in request.json['items']]}

    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/list',
        params={'to': '2018-08-06T00:00:00.000Z'},
        headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200

    assert response.json() == {
        '111d7e58b5a14bff9f65b8dc0bede3b4': {
            'title': 'Новость с image_id',
            'text': 'Текст',
            'type': 'newsletter',
            'format': 'Raw',
            'series_id': 'my_series1',
            'timestamp': '2018-08-01T12:00:00.000Z',
            'image_urls': {
                'base_urls_groups_key': 'TAXIMETER_FILE_STORAGE',
                'image_query_path': (
                    '/get-taximeter/wall-images/01012019/hexhexhex.png'
                ),
                'images_query_paths': [
                    '/get-taximeter/wall-images/01012019/hexhexhex-320.png',
                    '/get-taximeter/wall-images/01012019/hexhexhex-480.png',
                    '/get-taximeter/wall-images/01012019/hexhexhex-800.png',
                    '/get-taximeter/wall-images/01012019/hexhexhex-1024.png',
                ],
            },
        },
    }


@pytest.mark.now('2020-11-25T17:00:00.000Z')
async def test_several_feeds_request(
        taxi_driver_wall, mock_fleet_parks_list, mockserver,
):
    def fetch(request):
        if request['service'] == 'driver-wall':
            if request['earlier_than'] != '2020-11-25T12:09:00.445+00:00':
                return {
                    'etag_changed': True,
                    'response': {
                        'etag': '3f7c3ef6acd25a23a555123ffd70fa91',
                        'feed': [
                            {
                                'created': '2020-11-24T10:17:00.811964+0000',
                                'feed_id': '22e516280acb4292b77c8fb22c928378',
                                'request_id': 'request_id',
                                'last_status': {
                                    'created': (
                                        '2020-11-24T10:17:00.817342+0000'
                                    ),
                                    'status': 'published',
                                },
                                'payload': {
                                    'alert': False,
                                    'expire': '2020-11-29T10:17:00+0000',
                                    'format': 'Raw',
                                    'image_id': (
                                        '20201123/2a9a7fc522a291a251f9'
                                        '50e749c5954a'
                                    ),
                                    'important': False,
                                    'notification_mode': 'normal',
                                    'series_id': '2987',
                                    'teaser': 'aaa',
                                    'text': 'test',
                                    'thumbnail': (
                                        'iVBORw0KGgoAAAANSUhEUgAAAAUAAAADCA'
                                        'IAAADUVFKvAAAAO0lEQVQImQEwAM//AWBN'
                                        'RwUHCAoHCP/+/fv7/wLq9PQMCAcaBfwWA/'
                                        '3++wUC/v373unh8AcE4vby8fvyFZsac2Fg'
                                        'B/YAAAAASUVORK5CYII='
                                    ),
                                    'title': 'test',
                                    'type': 'newsletter',
                                    'url': 'https://ru.wikipedia.org/',
                                    'url_open_mode': 'browser',
                                },
                            },
                        ],
                        'has_more': False,
                        'polling_delay': 10,
                    },
                }
            return {
                'etag_changed': True,
                'response': {
                    'etag': '3f7c3ef6acd25a23a555123ffd70fa91',
                    'feed': [
                        {
                            'created': '2020-11-18T14:03:09.497641+0000',
                            'feed_id': '52e30f1c61504904b723971fa8852a8d',
                            'request_id': 'request_id',
                            'last_status': {
                                'created': '2020-11-18T14:03:09.501501+0000',
                                'status': 'published',
                            },
                            'payload': {
                                'alert': True,
                                'expire': '2020-11-18T14:15:30+00:00',
                                'format': 'Raw',
                                'important': False,
                                'teaser': 'Перейти',
                                'text': 'Тыдыщь',
                                'title': 'From feeds with love 2!',
                                'type': 'newsletter',
                                'url': 'http://driver.yandex',
                            },
                        },
                    ],
                    'has_more': True,
                    'polling_delay': 10,
                },
            }
        return {
            'etag_changed': True,
            'response': {
                'etag': '3f7c3ef6acd25a23a555123ffd70fa91',
                'feed': [
                    {
                        'created': '2020-11-18T14:03:09.497641+0000',
                        'feed_id': '11130f1c61504904b723971fa8852a8d',
                        'request_id': 'request_id',
                        'last_status': {
                            'created': '2020-11-18T14:03:09.501501+0000',
                            'status': 'published',
                        },
                        'payload': {
                            'alert': True,
                            'expire': '2020-11-18T14:15:30+00:00',
                            'format': 'Raw',
                            'important': False,
                            'teaser': 'Перейти',
                            'text': 'Тыдыщь',
                            'title': 'From feeds with love 2!',
                            'type': 'newsletter',
                            'url': 'http://driver.yandex',
                        },
                    },
                ],
                'has_more': False,
                'polling_delay': 10,
            },
        }

    @mockserver.json_handler('/feeds/v1/batch/fetch')
    def _mock_batch_fetch_feeds(request):
        return {'items': [fetch(item) for item in request.json['items']]}

    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/list',
        params={'to': '2020-11-25T12:09:00.445Z', 'limit': 20},
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200

    assert '22e516280acb4292b77c8fb22c928378' in response.json()

    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/list',
        params={'to': '2020-11-25T12:09:00.445Z'},
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200

    assert '22e516280acb4292b77c8fb22c928378' in response.json()


@pytest.mark.now('2020-11-25T17:00:00.000Z')
async def test_driver_fullscreen_404(
        taxi_driver_wall, mock_fleet_parks_list, mockserver,
):
    def fetch(request):
        if request['service'] == 'driver-wall':
            if request['earlier_than'] != '2020-11-25T12:09:00.445+00:00':
                return {
                    'etag_changed': True,
                    'response': {
                        'etag': '3f7c3ef6acd25a23a555123ffd70fa91',
                        'feed': [
                            {
                                'created': '2020-11-24T10:17:00.811964+0000',
                                'feed_id': '22e516280acb4292b77c8fb22c928378',
                                'request_id': 'request_id',
                                'last_status': {
                                    'created': (
                                        '2020-11-24T10:17:00.817342+0000'
                                    ),
                                    'status': 'published',
                                },
                                'payload': {
                                    'alert': False,
                                    'expire': '2020-11-29T10:17:00+0000',
                                    'format': 'Raw',
                                    'image_id': (
                                        '20201123/2a9a7fc522a291a251f9'
                                        '50e749c5954a'
                                    ),
                                    'important': False,
                                    'notification_mode': 'normal',
                                    'series_id': '2987',
                                    'teaser': 'aaa',
                                    'text': 'test',
                                    'thumbnail': (
                                        'iVBORw0KGgoAAAANSUhEUgAAAAUAAAADCA'
                                        'IAAADUVFKvAAAAO0lEQVQImQEwAM//AWBN'
                                        'RwUHCAoHCP/+/fv7/wLq9PQMCAcaBfwWA/'
                                        '3++wUC/v373unh8AcE4vby8fvyFZsac2Fg'
                                        'B/YAAAAASUVORK5CYII='
                                    ),
                                    'title': 'test',
                                    'type': 'newsletter',
                                    'url': 'https://ru.wikipedia.org/',
                                    'url_open_mode': 'browser',
                                },
                            },
                        ],
                        'has_more': False,
                        'polling_delay': 10,
                    },
                }
            return {
                'etag_changed': True,
                'response': {
                    'etag': '3f7c3ef6acd25a23a555123ffd70fa91',
                    'feed': [
                        {
                            'created': '2020-11-18T14:03:09.497641+0000',
                            'feed_id': '52e30f1c61504904b723971fa8852a8d',
                            'request_id': 'request_id',
                            'last_status': {
                                'created': '2020-11-18T14:03:09.501501+0000',
                                'status': 'published',
                            },
                            'payload': {
                                'alert': True,
                                'expire': '2020-11-18T14:15:30+00:00',
                                'format': 'Raw',
                                'important': False,
                                'teaser': 'Перейти',
                                'text': 'Тыдыщь',
                                'title': 'From feeds with love 2!',
                                'type': 'newsletter',
                                'url': 'http://driver.yandex',
                            },
                        },
                    ],
                    'has_more': True,
                    'polling_delay': 10,
                },
            }
        raise error.Error404()

    @mockserver.json_handler('/feeds/v1/batch/fetch')
    def _mock_batch_fetch_feeds(request):
        try:
            return {'items': [fetch(item) for item in request.json['items']]}
        except error.Error404:
            return mockserver.make_response('Not found or invalid method', 404)

    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/list',
        params={'to': '2020-11-25T12:09:00.445Z', 'limit': 20},
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200


@pytest.mark.now('2018-08-05T00:00:00Z')
async def test_driver_communications_feeds(
        taxi_driver_wall, mock_fleet_parks_list, mockserver, load_json,
):
    def fetch(request):
        responses = load_json('driver_communications_feeds_resopnses.json')
        return {
            'etag_changed': True,
            'response': responses[request['service']],
        }

    @mockserver.json_handler('/feeds/v1/batch/fetch')
    def _mock_batch_fetch_feeds(request):
        return {'items': [fetch(item) for item in request.json['items']]}

    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/list',
        params={'to': '2018-08-06T00:00:00.000Z'},
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200

    data = response.json()

    assert '111d7e58b5a14bff9f65b8dc0bede3b4' in data
    assert '11117e58b5a14bff9f65b8dc0bede3b4' in data
    assert '222d7e58b5a14bff9f65b8dc0bede3b4' not in data
    assert '22227e58b5a14bff9f65b8dc0bede3b4' not in data


@pytest.mark.now('2018-08-05T00:00:00Z')
@pytest.mark.experiments3(filename='driver_channels_experiment.json')
async def test_experiments_channel(
        taxi_driver_wall, mock_fleet_parks_list, mockserver,
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
                    'has_more': True,
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
        return {'items': [fetch(item) for item in request.json['items']]}

    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/list',
        params={'to': '2018-08-06T00:00:00.000Z', 'limit': 2},
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200


@pytest.mark.now('2020-11-25T17:00:00.000Z')
@pytest.mark.config(
    DRIVER_WALL_FEEDS_SERVICES=[
        'driver-wall',
        'driver-fullscreen',
        'other-service',
    ],
)
async def test_feeds_services_config(
        taxi_driver_wall, mock_fleet_parks_list, mockserver, load_json,
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
        return {'items': [fetch(item) for item in request.json['items']]}

    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/list',
        params={'to': '2020-11-25T12:09:00.445Z', 'limit': 20},
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200

    assert '909f5466959b4df09d278d0297c45b40' in response.json()
    assert '52e30f1c61504904b723971fa8852a8d' in response.json()
    assert 'd07c2b19b15d4d5197e17a9e89e20529' in response.json()
