import pytest

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
async def test_messages_text(
        taxi_driver_wall, mockserver, mock_fleet_parks_list,
):
    @mockserver.json_handler('/feeds/v1/fetch_by_id')
    def mock_feeds(request):
        if request.json['service'] == 'driver-wall':
            return {
                'feed': [
                    {
                        'created': '2018-08-04T23:59:57.000Z',
                        'feed_id': '111f5466959b4df09d278d0297c45b40',
                        'request_id': 'request_id',
                        'last_status': {
                            'created': '2018-08-04T23:59:57.000Z',
                            'status': 'published',
                        },
                        'payload': {
                            'title': 'Новость 1',
                            'text': 'Привет, водитель!',
                            'type': 'newsletter',
                            'format': 'Raw',
                            'series_id': 'my_series1',
                        },
                    },
                ],
            }
        return {
            'feed': [
                {
                    'created': '2018-08-04T23:59:58.000Z',
                    'feed_id': '222f5466959b4df09d278d0297c45b40',
                    'request_id': 'request_id',
                    'last_status': {
                        'created': '2018-08-04T23:59:58.000Z',
                        'status': 'published',
                    },
                    'payload': {
                        'title': 'Новость 2',
                        'text': 'Больше текста в **markdown**',
                        'random_field': 'Поле, которая отдается as-is',
                        'type': 'newsletter',
                        'format': 'Markdown',
                        'series_id': 'my_series1',
                    },
                },
            ],
        }

    headers_1_driver = {
        'X-YaTaxi-Driver-Profile-Id': 'uuid1',
        'X-YaTaxi-Park-Id': 'dbid1',
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': '9.40',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'Accept-language': 'ru',
    }

    news = {
        '111f5466959b4df09d278d0297c45b40': {
            'title': 'Новость 1',
            'text': 'Привет, водитель!',
            'type': 'newsletter',
            'format': 'Raw',
            'series_id': 'my_series1',
            'timestamp': '2018-08-04T23:59:57.000Z',
        },
        '222f5466959b4df09d278d0297c45b40': {
            'title': 'Новость 2',
            'text': 'Больше текста в **markdown**',
            'random_field': 'Поле, которая отдается as-is',
            'type': 'newsletter',
            'format': 'Markdown',
            'series_id': 'my_series1',
            'timestamp': '2018-08-04T23:59:58.000Z',
        },
    }

    response = await taxi_driver_wall.post(
        'driver/v1/driver-wall/messages',
        headers=headers_1_driver,
        json=[
            '111f5466959b4df09d278d0297c45b40',
            '222f5466959b4df09d278d0297c45b40',
            '333f5466959b4df09d278d0297c45b40',
        ],
    )
    assert response.status_code == 200
    assert response.json() == news
    assert mock_feeds.times_called == 2


@pytest.mark.now('2018-08-05T00:00:00Z')
async def test_messages_with_image(
        taxi_driver_wall, mockserver, mock_fleet_parks_list,
):
    @mockserver.json_handler('/feeds/v1/fetch_by_id')
    def _mock_feeds(request):
        return {
            'feed': [
                {
                    'created': '2018-08-04T16:00:00.000000+0000',
                    'feed_id': '909f5466959b4df09d278d0297c45b40',
                    'request_id': 'request_id',
                    'last_status': {
                        'created': '2020-06-04T16:53:53.538088+0000',
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
        }

    response = await taxi_driver_wall.post(
        'driver/v1/driver-wall/messages',
        headers=DEFAULT_HEADERS,
        json=['909f5466959b4df09d278d0297c45b40'],
    )
    assert response.status_code == 200
    assert response.json() == {
        '909f5466959b4df09d278d0297c45b40': {
            'title': 'Новость с image_id',
            'text': 'Текст',
            'type': 'newsletter',
            'format': 'Raw',
            'series_id': 'my_series1',
            'timestamp': '2018-08-04T16:00:00.000Z',
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


@pytest.mark.now('2018-08-05T00:00:00Z')
async def test_messages(taxi_driver_wall, mockserver, mock_fleet_parks_list):
    @mockserver.json_handler('/feeds/v1/fetch_by_id')
    def _mock_feeds(request):
        assert set(request.json['feed_ids']) == {
            'e80fc43410c8463ebe0a724bd2471e05',
            'd07c2b19b15d4d5197e17a9e89e20529',
            '909f5466959b4df09d278d0297c45b40',
            '4b10731ddf944d20b992b44a3b5493d1',
            '17917a14fb7d4f3188743b7baa077212',
        }
        if request.json['service'] == 'driver-wall':
            return {
                'feed': [
                    {
                        'created': '2020-06-04T16:53:53.112431+0000',
                        'feed_id': '4b10731ddf944d20b992b44a3b5493d1',
                        'request_id': 'request_id',
                        'last_status': {
                            'created': '2020-06-04T16:53:53.215061+0000',
                            'status': 'published',
                        },
                        'payload': {'text': 'Holiday Law effects, Earth'},
                    },
                    {
                        'created': '2020-06-04T16:53:52.960804+0000',
                        'feed_id': '17917a14fb7d4f3188743b7baa077212',
                        'request_id': 'request_id',
                        'last_status': {
                            'created': '2020-06-04T16:53:52.984696+0000',
                            'status': 'published',
                        },
                        'payload': {'text': 'Rekindled Watson using 42'},
                    },
                    {
                        'created': '2020-06-04T16:53:54.073257+0000',
                        'feed_id': 'e80fc43410c8463ebe0a724bd2471e05',
                        'request_id': 'request_id',
                        'last_status': {
                            'created': '2020-06-04T16:53:54.094671+0000',
                            'status': 'published',
                        },
                        'payload': {
                            'text': 'Personal computers, before Easter and',
                        },
                    },
                    {
                        'created': '2020-06-04T16:53:53.68606+0000',
                        'feed_id': 'd07c2b19b15d4d5197e17a9e89e20529',
                        'request_id': 'request_id',
                        'last_status': {
                            'created': '2020-06-04T16:53:53.83445+0000',
                            'status': 'published',
                        },
                        'payload': {'text': 'Widely varying of date.'},
                    },
                ],
            }
        return {
            'feed': [
                {
                    'created': '2020-06-04T16:53:53.478332+0000',
                    'feed_id': '909f5466959b4df09d278d0297c45b40',
                    'request_id': 'request_id',
                    'last_status': {
                        'created': '2020-06-04T16:53:53.538088+0000',
                        'status': 'published',
                    },
                    'payload': {'text': 'A solar Arabic and modern'},
                },
            ],
        }

    response = await taxi_driver_wall.post(
        'driver/v1/driver-wall/messages',
        headers=DEFAULT_HEADERS,
        json=[
            'e80fc43410c8463ebe0a724bd2471e05',
            'd07c2b19b15d4d5197e17a9e89e20529',
            '909f5466959b4df09d278d0297c45b40',
            '4b10731ddf944d20b992b44a3b5493d1',
            '17917a14fb7d4f3188743b7baa077212',
        ],
    )

    assert response.status_code == 200
    assert {x for x in response.json()} == {
        'e80fc43410c8463ebe0a724bd2471e05',
        'd07c2b19b15d4d5197e17a9e89e20529',
        '909f5466959b4df09d278d0297c45b40',
        '4b10731ddf944d20b992b44a3b5493d1',
        '17917a14fb7d4f3188743b7baa077212',
    }


@pytest.mark.now('2018-08-05T00:00:00Z')
@pytest.mark.experiments3(filename='driver_channels_experiment.json')
async def test_experiments_channel(
        taxi_driver_wall, mock_fleet_parks_list, mockserver,
):
    @mockserver.json_handler('/feeds/v1/fetch_by_id')
    def _mock_feeds(request):
        assert sorted(request.json['channels']) == [
            'taximeter:City:МОСКВА',
            'taximeter:Country:РОССИЯ',
            'taximeter:Driver:dbid1:uuid1',
            'taximeter:Experiment:driver_wall_channel_experiment',
            'taximeter:Park:dbid1',
        ]
        if request.json['service'] == 'driver-wall':
            return {
                'feed': [
                    {
                        'created': '2020-06-04T16:53:53.112431+0000',
                        'feed_id': '4b10731ddf944d20b992b44a3b5493d1',
                        'request_id': 'request_id',
                        'last_status': {
                            'created': '2020-06-04T16:53:53.215061+0000',
                            'status': 'published',
                        },
                        'payload': {'text': 'Holiday Law effects, Earth'},
                    },
                ],
            }
        return {'feed': []}

    response = await taxi_driver_wall.post(
        'driver/v1/driver-wall/messages',
        headers=DEFAULT_HEADERS,
        json=['4b10731ddf944d20b992b44a3b5493d1'],
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
        taxi_driver_wall, mock_fleet_parks_list, mockserver, load_json,
):
    @mockserver.json_handler('/feeds/v1/fetch_by_id')
    def _mock_feeds(request):
        assert set(request.json['feed_ids']) == {
            '909f5466959b4df09d278d0297c45b40',
            '52e30f1c61504904b723971fa8852a8d',
            'd07c2b19b15d4d5197e17a9e89e20529',
        }
        if request.json['service'] == 'driver-wall':
            return load_json('feeds_driver_wall_fetch_by_id.json')
        if request.json['service'] == 'driver-fullscreen':
            return load_json('feeds_driver_fullscreen_fetch_by_id.json')
        if request.json['service'] == 'other-service':
            return load_json('feeds_other_service_fetch_by_id.json')
        assert False
        return {}

    response = await taxi_driver_wall.post(
        'driver/v1/driver-wall/messages',
        headers=DEFAULT_HEADERS,
        json=[
            '909f5466959b4df09d278d0297c45b40',
            '52e30f1c61504904b723971fa8852a8d',
            'd07c2b19b15d4d5197e17a9e89e20529',
        ],
    )

    assert response.status_code == 200
    assert {x for x in response.json()} == {
        '909f5466959b4df09d278d0297c45b40',
        '52e30f1c61504904b723971fa8852a8d',
        'd07c2b19b15d4d5197e17a9e89e20529',
    }

    assert _mock_feeds.times_called == 3
