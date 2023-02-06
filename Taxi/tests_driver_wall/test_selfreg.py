import pytest

import tests_driver_wall.error404 as error

SELFREG_HEADERS = {
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'Accept-language': 'ru',
}


@pytest.mark.now('2018-08-05T00:00:00Z')
async def test_messages_handler(taxi_driver_wall, selfreg, mockserver):
    @mockserver.json_handler('/feeds/v1/fetch_by_id')
    def _mock_feeds(request):
        assert set(request.json['channels']) == {
            'taximeter:Park:selfreg',
            'taximeter:Driver:selfreg:selfreg_id',
            'taximeter:City:CITY_ID',
            'taximeter:Tag:selfreg_v2_driver_unreg',
        }
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
        return {'feed': []}

    selfreg.set_selfreg(selfreg_type='driver')
    response = await taxi_driver_wall.post(
        'driver/v1/driver-wall/messages',
        headers=SELFREG_HEADERS,
        params={'selfreg_token': 'selfreg_token'},
        json=['PUBLIC:selfreg'],
    )
    assert response.status_code == 200
    assert response.json() == {
        '111f5466959b4df09d278d0297c45b40': {
            'format': 'Raw',
            'series_id': 'my_series1',
            'text': 'Привет, водитель!',
            'timestamp': '2018-08-04T23:59:57.000Z',
            'title': 'Новость 1',
            'type': 'newsletter',
        },
    }


@pytest.mark.now('2018-08-05T00:00:00Z')
@pytest.mark.parametrize(
    'selfreg_type,selfreg_tags,channels',
    [
        (
            None,
            None,
            {
                'taximeter:Park:selfreg',
                'taximeter:Driver:selfreg:selfreg_id',
                'taximeter:City:CITY_ID',
                'taximeter:Tag:selfreg_v2_profi_unreg',
            },
        ),
        (
            'driver',
            None,
            {
                'taximeter:Park:selfreg',
                'taximeter:Driver:selfreg:selfreg_id',
                'taximeter:City:CITY_ID',
                'taximeter:Tag:selfreg_v2_driver_unreg',
            },
        ),
        (
            'courier',
            None,
            {
                'taximeter:Park:selfreg',
                'taximeter:Driver:selfreg:selfreg_id',
                'taximeter:City:CITY_ID',
                'taximeter:Tag:selfreg_v2_courier_unreg',
            },
        ),
        (
            None,
            ['selfreg_v2_profi_unreg'],
            {
                'taximeter:Park:selfreg',
                'taximeter:Driver:selfreg:selfreg_id',
                'taximeter:City:CITY_ID',
                'taximeter:Tag:selfreg_v2_profi_unreg',
            },
        ),
        (
            None,
            ['selfreg_v2_driver_unreg'],
            {
                'taximeter:Park:selfreg',
                'taximeter:Driver:selfreg:selfreg_id',
                'taximeter:City:CITY_ID',
                'taximeter:Tag:selfreg_v2_driver_unreg',
            },
        ),
        (
            None,
            ['selfreg_v2_courier_unreg'],
            {
                'taximeter:Park:selfreg',
                'taximeter:Driver:selfreg:selfreg_id',
                'taximeter:City:CITY_ID',
                'taximeter:Tag:selfreg_v2_courier_unreg',
            },
        ),
    ],
)
async def test_list_handler(
        taxi_driver_wall,
        selfreg,
        selfreg_type,
        selfreg_tags,
        channels,
        mockserver,
):
    def fetch(request):
        assert set(request['channels']) == channels
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

    selfreg.set_selfreg(selfreg_type=selfreg_type, mock_tags=selfreg_tags)
    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/list',
        headers=SELFREG_HEADERS,
        params={'selfreg_token': 'selfreg_token'},
    )
    assert response.status_code == 200


@pytest.mark.now('2018-08-05T00:00:00Z')
@pytest.mark.parametrize(
    'selfreg_type,channels',
    [
        (
            None,
            {
                'taximeter:Park:selfreg',
                'taximeter:Driver:selfreg:selfreg_id',
                'taximeter:City:CITY_ID',
                'taximeter:Tag:selfreg_v2_profi_unreg',
            },
        ),
        (
            'driver',
            {
                'taximeter:Park:selfreg',
                'taximeter:Driver:selfreg:selfreg_id',
                'taximeter:City:CITY_ID',
                'taximeter:Tag:selfreg_v2_driver_unreg',
            },
        ),
        (
            'courier',
            {
                'taximeter:Park:selfreg',
                'taximeter:Driver:selfreg:selfreg_id',
                'taximeter:City:CITY_ID',
                'taximeter:Tag:selfreg_v2_courier_unreg',
            },
        ),
    ],
)
async def test_polling_handler(
        taxi_driver_wall, selfreg, selfreg_type, channels, mockserver,
):
    def fetch(request):
        assert set(request['channels']) == channels
        if request['etag'] == '18d667a167fa5d35b6ab67bfb29c2eef':
            return {'etag_chaned': False}
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
                        'created': '2018-08-02T12:00:00.000000+0000',
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

    selfreg.set_selfreg(selfreg_type=selfreg_type)
    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/polling',
        headers=SELFREG_HEADERS,
        params={'selfreg_token': 'selfreg_token'},
    )
    assert response.status_code == 200
    assert response.json() == [
        '111d7e58b5a14bff9f65b8dc0bede3b4',
        '11117e58b5a14bff9f65b8dc0bede3b4',
    ]


@pytest.mark.now('2018-08-05T00:00:00Z')
@pytest.mark.parametrize('code', [404, 500])
async def test_errors(taxi_driver_wall, selfreg, code):
    selfreg.set_error_code(code)
    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/polling',
        headers=SELFREG_HEADERS,
        params={'selfreg_token': 'selfreg_token'},
    )
    assert response.status_code == 401
    response = await taxi_driver_wall.get(
        'driver/v1/driver-wall/list',
        headers=SELFREG_HEADERS,
        params={'selfreg_token': 'selfreg_token'},
    )
    assert response.status_code == 401
    response = await taxi_driver_wall.post(
        'driver/v1/driver-wall/messages',
        headers=SELFREG_HEADERS,
        params={'selfreg_token': 'selfreg_token'},
        json=['PUBLIC:selfreg'],
    )
    assert response.status_code == 401
