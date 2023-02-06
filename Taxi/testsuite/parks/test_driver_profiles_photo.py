import json

import pytest

from taxi_tests.utils import ordered_object

from . import error


def get_requests(mock_object):
    requests = []
    for _ in range(mock_object.times_called):
        requests.append(mock_object.next_call()['request'])
    return requests


def get_photos(redis_store, park, driver):
    return json.loads(redis_store.hget('Driver:Photos:' + park, driver))


@pytest.mark.redis_store(
    ['hset', 'Driver:Photos:2128506', 'vodilo', '{}'],
    [
        'hset',
        'Driver:Photos:2128506',
        'pilot',
        json.dumps(
            {
                'Large': {
                    'Driver': (
                        'https://storage.mds.yandex.net/get-taximeter/'
                        'https://storage.mds.yandex.net/get-taximeter/'
                        'https://storage.mds.yandex.net/get-taximeter/'
                        '3325/6a255a958d234fa497d99c21b4a1f166_small.jpg'
                    ),
                },
                'Original': {
                    'Driver': 'original/driver.jpg',
                    'Front': 'front.jpg',
                    'Left': 'left.jpg',
                    'Salon': 'salon.jpg',
                },
            },
        ),
    ],
)
@pytest.mark.parametrize(
    'params,expected_code,expected_response',
    [
        (
            {'park_id': '2128506'},
            400,
            {'error': {'text': 'parameter driver_profile_id must be set'}},
        ),
        (
            {'driver_profile_id': 'vodilo'},
            400,
            {'error': {'text': 'parameter park_id must be set'}},
        ),
        (
            {'park_id': '2128506', 'driver_profile_id': 'vodilo'},
            200,
            {'photos': []},
        ),
        (
            {'park_id': 'net_takogo', 'driver_profile_id': 'vodilo'},
            200,
            {'photos': []},
        ),
        (
            {'park_id': '2128506', 'driver_profile_id': 'pilot'},
            200,
            {
                'photos': [
                    {
                        'href': (
                            'https://storage.mds.yandex.net/get-taximeter/'
                            '3325/6a255a958d234fa497d99c21b4a1f166_small.jpg'
                        ),
                        'scale': 'large',
                        'type': 'driver',
                    },
                    {
                        'href': (
                            'https://storage.mds.yandex.net/get-taximeter/'
                            'original/driver.jpg'
                        ),
                        'scale': 'original',
                        'type': 'driver',
                    },
                    {
                        'href': (
                            'https://storage.mds.yandex.net/get-taximeter/'
                            'front.jpg'
                        ),
                        'scale': 'original',
                        'type': 'front',
                    },
                    {
                        'href': (
                            'https://storage.mds.yandex.net/get-taximeter/'
                            'left.jpg'
                        ),
                        'scale': 'original',
                        'type': 'left',
                    },
                    {
                        'href': (
                            'https://storage.mds.yandex.net/get-taximeter/'
                            'salon.jpg'
                        ),
                        'scale': 'original',
                        'type': 'salon',
                    },
                ],
            },
        ),
    ],
)
def test_get(taxi_parks, params, expected_code, expected_response):
    response = taxi_parks.get('/driver-profiles/photo', params=params)

    assert response.status_code == expected_code
    assert response.json() == expected_response


TEST_AVATAR = (
    'https://avatars.mdst.yandex.net/get-driver-photos/'
    '65737/b088f49591e94e85a705280867bef3bb/orig'
)

TEST_PORTRAIT = (
    'https://avatars.mdst.yandex.net/get-driver-photos/'
    '65737/4babd87b831f49dcbdb8354a7fe5b0f8/orig'
)


@pytest.mark.parametrize(
    (
        'params',
        'mock_status',
        'mock_response',
        'expected_code',
        'expected_response',
    ),
    [
        (
            {'park_id': '0', 'driver_profile_id': '0'},
            200,
            {
                'photos': [
                    {'type': 'avatar', 'url': TEST_AVATAR},
                    {'type': 'portrait', 'url': TEST_PORTRAIT},
                ],
            },
            200,
            {
                'photos': [
                    {'href': TEST_AVATAR, 'scale': 'small', 'type': 'driver'},
                    {
                        'href': TEST_AVATAR,
                        'scale': 'original',
                        'type': 'driver',
                    },
                    {'href': TEST_AVATAR, 'scale': 'large', 'type': 'driver'},
                ],
            },
        ),
        (
            {'park_id': '1', 'driver_profile_id': '0'},
            400,
            None,
            200,
            {'photos': []},
        ),
        (
            {'park_id': '1', 'driver_profile_id': '0'},
            429,
            None,
            200,
            {'photos': []},
        ),
    ],
)
@pytest.mark.experiments3(
    name='parks_use_py3_driver_photo',
    consumers=['parks/photo'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'parks_use_py3_driver_photo',
            'value': 9875,
            'predicate': {'type': 'true'},
        },
    ],
)
def test_get_from_py3_with_experiments3(
        mockserver,
        taxi_parks,
        params,
        mock_status,
        mock_response,
        expected_code,
        expected_response,
):
    @mockserver.json_handler(
        '/driver_photos/driver-photos/v1/taximeter-photos',
    )
    def mock_driver_photos(request):
        if mock_status != 200:
            return mockserver.make_response(response=None, status=mock_status)
        return mock_response

    response = taxi_parks.get('/driver-profiles/photo', params=params)
    assert mock_driver_photos.times_called == 1
    assert response.status_code == expected_code
    assert response.json() == expected_response


def load_photos(photos, load_binary):
    for type, data in photos.items():
        photos[type] = load_binary(data)


EXPECTED_POST_RESPONSE = {
    'photos': [
        {
            'href': (
                'https://storage.mds.yandex.net/get-taximeter/' '1234/some.jpg'
            ),
            'scale': 'original',
            'type': 'driver',
        },
        {
            'href': (
                'https://storage.mds.yandex.net/get-taximeter/' '1234/some.jpg'
            ),
            'scale': 'small',
            'type': 'driver',
        },
        {
            'href': (
                'https://storage.mds.yandex.net/get-taximeter/' '1234/some.jpg'
            ),
            'scale': 'large',
            'type': 'driver',
        },
        {
            'href': (
                'https://storage.mds.yandex.net/get-taximeter/' '1234/some.jpg'
            ),
            'scale': 'original',
            'type': 'left',
        },
        {
            'href': (
                'https://storage.mds.yandex.net/get-taximeter/' '1234/some.jpg'
            ),
            'scale': 'small',
            'type': 'left',
        },
        {
            'href': (
                'https://storage.mds.yandex.net/get-taximeter/' '1234/some.jpg'
            ),
            'scale': 'large',
            'type': 'left',
        },
    ],
}
EXPECTED_STORED_PHOTOS = {
    'Original': {'Driver': '1234/some.jpg', 'Left': '1234/some.jpg'},
    'Large': {'Driver': '1234/some.jpg', 'Left': '1234/some.jpg'},
    'Small': {'Driver': '1234/some.jpg', 'Left': '1234/some.jpg'},
}


@pytest.mark.redis_store(
    ['hset', 'Driver:Photos:123', 'pilot1', '{}'],
    [
        'hset',
        'Driver:Photos:123',
        'pilot2',
        json.dumps(
            {
                'Original': {'Driver': '1234/some.jpg'},
                'Large': {'Driver': '1234/some.jpg'},
                'Small': {'Driver': '1234/some.jpg'},
            },
        ),
    ],
    [
        'hset',
        'Driver:Photos:123',
        'pilot3',
        json.dumps(
            {
                'Original': {'Driver': '1234/other.jpg'},
                'Large': {'Driver': '1234/other.jpg'},
                'Small': {'Driver': '1234/other.jpg'},
            },
        ),
    ],
)
@pytest.mark.parametrize(
    'driver_id, files, args, times_loaded, enable_photo_check,'
    'driver_photos_status',
    [
        ('pilot0', {'driver': 'pes.jpg', 'left': 'pes.jpg'}, {}, 2, True, 429),
        ('pilot0', {'driver': 'pes.jpg', 'left': 'pes.jpg'}, {}, 2, True, 200),
        ('pilot0', {}, {'driver': 'pes.jpg', 'left': 'pes.jpg'}, 2, True, 200),
        ('pilot1', {'driver': 'pes.jpg', 'left': 'pes.jpg'}, {}, 2, True, 200),
        ('pilot2', {'left': 'pes.jpg'}, {}, 1, True, 200),
        ('pilot3', {'driver': 'pes.jpg', 'left': 'pes.jpg'}, {}, 2, True, 200),
        ('pilot3', {'driver': 'pes.jpg'}, {'left': 'pes.jpg'}, 2, True, 200),
        (
            'pilot3',
            {'driver': 'pes_invalid.jpg'},
            {'left': 'pes_invalid.jpg'},
            2,
            False,
            200,
        ),
    ],
)
def test_post(
        mockserver,
        redis_store,
        load_binary,
        load,
        taxi_parks,
        config,
        driver_id,
        times_loaded,
        files,
        args,
        enable_photo_check,
        driver_photos_status,
):
    config.set_values(
        dict(PARKS_ENABLE_PHOTO_VALIDITY_CHECK=enable_photo_check),
    )

    load_photos(files, load_binary)
    load_photos(args, load_binary)
    expected_data = files['left'] if 'left' in files else args['left']

    @mockserver.json_handler(
        '/driver_photos/driver-photos/v1/photos/upload_mds',
    )
    def mock_driver_photos(request):
        assert request.path.startswith(
            '/driver_photos/driver-photos/v1/photos/upload_mds',
        )
        assert request.json == {
            'driver_profile_id': driver_id,
            'park_id': '123',
            'mds_photo_path': '1234/some.jpg',
        }
        return mockserver.make_response(status=driver_photos_status)

    @mockserver.handler('/mds-int-host:1111/upload-taximeter/', prefix=True)
    def mock_mds(request):
        assert (
            request.headers['Authorization']
            == 'Basic topsecret_mds_taximeter_token'
        )
        assert request.path.startswith('/mds-int-host:1111/upload-taximeter/')
        assert request.path.endswith('.jpg')
        assert request.get_data() == expected_data
        # just pass back some constant value. so it is easy to check later
        file_key = '1234/' + 'some.jpg'
        answer = load('mds_answer.xml.tmpl').format(file_key)
        return mockserver.make_response(answer)

    response = taxi_parks.post(
        '/driver-profiles/photo',
        params={'park_id': '123', 'driver_profile_id': driver_id},
        files=files,
        data=args,
    )

    assert get_photos(redis_store, '123', driver_id) == EXPECTED_STORED_PHOTOS
    assert mock_mds.times_called == times_loaded
    if 'driver' in files or 'driver' in args:
        assert mock_driver_photos.times_called == 1
    else:
        assert mock_driver_photos.times_called == 0
    assert response.status_code == 200, response.text
    ordered_object.assert_eq(
        response.json(), EXPECTED_POST_RESPONSE, ['photos'],
    )


@pytest.mark.redis_store(
    [
        'hset',
        'Driver:Photos:123',
        'pilot',
        json.dumps({'Original': {'Driver': 'original/driver.jpg'}}),
    ],
)
@pytest.mark.parametrize(
    'files, error0, error1',
    [
        (
            {'driver': 'pes_warning.jpg', 'left': 'pes_invalid.jpg'},
            'Invalid jpeg photo in files: Left',
            None,
        ),
        (
            {'driver': 'pes_invalid.jpg', 'left': 'pes_invalid.jpg'},
            'Invalid jpeg photo in files: Driver, Left',
            'Invalid jpeg photo in files: Left, Driver',
        ),
    ],
)
def test_invalid_jpeg(
        mockserver,
        redis_store,
        load_binary,
        taxi_parks,
        files,
        error0,
        error1,
):
    load_photos(files, load_binary)

    @mockserver.handler('/mds-int-host:1111/upload-taximeter/', prefix=True)
    def mock_mds(request):
        return {}

    photos_before = get_photos(redis_store, '123', 'pilot')
    response = taxi_parks.post(
        '/driver-profiles/photo',
        params={'park_id': '123', 'driver_profile_id': 'pilot'},
        files=files,
    )
    photos_after = get_photos(redis_store, '123', 'pilot')

    assert photos_before == photos_after
    assert mock_mds.times_called == 0
    assert response.status_code == 400, response.text
    assert response.json() == error.make_error_response(
        error0,
    ) or response.json() == error.make_error_response(error1)


@pytest.mark.redis_store(
    [
        'hset',
        'Driver:Photos:123',
        'pilot',
        json.dumps({'Original': {'Driver': 'original/driver.jpg'}}),
    ],
)
def test_mds_post_failed(mockserver, redis_store, load_binary, taxi_parks):
    @mockserver.handler('/mds-int-host:1111/upload-taximeter/', prefix=True)
    def mock_mds(request):
        return mockserver.make_response(500, 'test failed')

    photos_before = get_photos(redis_store, '123', 'pilot')
    response = taxi_parks.post(
        '/driver-profiles/photo',
        params={'park_id': '123', 'driver_profile_id': 'pilot'},
        files={
            'driver': load_binary('pes.jpg'),
            'left': load_binary('pes.jpg'),
        },
    )
    photos_after = get_photos(redis_store, '123', 'pilot')

    assert photos_before == photos_after
    assert mock_mds.times_called > 0
    assert response.status_code == 500, response.text
