import json

import pytest


@pytest.mark.parametrize(
    'params,expected_code,expected_response',
    [
        ({'db': '999'}, 401, {'error': {'text': 'empty session'}}),
        (
            {'db': '999', 'session': 'asd'},
            401,
            {'error': {'text': 'driver_authorizer unauthorized'}},
        ),
    ],
)
def test_unauthorized(
        mockserver,
        taxi_driver_protocol,
        params,
        expected_code,
        expected_response,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('999', 'qwerty', '888')

    @mockserver.json_handler('/parks/driver-profiles/photo/')
    def mock_callback(request):
        assert False

    response = taxi_driver_protocol.post('driver/photo/get', params=params)
    assert response.status_code == expected_code
    assert response.json() == expected_response


def test_params_transfer(
        mockserver, taxi_driver_protocol, driver_authorizer_service,
):
    driver_authorizer_service.set_session('999', 'qwerty', 'vodilo')

    params = {'db': '999', 'session': 'qwerty'}
    parks_params = {'park_id': '999', 'driver_profile_id': 'vodilo'}

    @mockserver.json_handler('/parks/driver-profiles/photo')
    def mock_callback(request):
        return {}

    taxi_driver_protocol.post('/driver/photo/get', params=params)

    assert mock_callback.times_called == 1
    assert mock_callback.next_call()['request'].args.to_dict() == parks_params


@pytest.mark.parametrize(
    'parks_response,expected_code,' 'expected_response',
    [
        (
            {'error': {'text': 'some wrong parameter'}},
            400,
            {'error': {'text': 'some wrong parameter'}},
        ),
        ('some error', 500, None),
        ({'photos': []}, 200, {}),
        (
            {
                'photos': [
                    {
                        'href': (
                            'https://storage.mds.yandex.net/get-taximeter/'
                            '3325/6a255a958d234fa497d99c21b4a1f166_large.jpg'
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
                            'left.jpg'
                        ),
                        'scale': 'original',
                        'type': 'left',
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
                            'salon.jpg'
                        ),
                        'scale': 'original',
                        'type': 'salon',
                    },
                ],
            },
            200,
            {
                'Large': {
                    'Driver': (
                        'https://storage.mds.yandex.net/get-taximeter/'
                        '3325/6a255a958d234fa497d99c21b4a1f166_large.jpg'
                    ),
                },
                'Original': {
                    'Driver': (
                        'https://storage.mds.yandex.net/get-taximeter/'
                        'original/driver.jpg'
                    ),
                    'Left': (
                        'https://storage.mds.yandex.net/get-taximeter/'
                        'left.jpg'
                    ),
                    'Front': (
                        'https://storage.mds.yandex.net/get-taximeter/'
                        'front.jpg'
                    ),
                    'Salon': (
                        'https://storage.mds.yandex.net/get-taximeter/'
                        'salon.jpg'
                    ),
                },
            },
        ),
    ],
)
def test(
        mockserver,
        taxi_driver_protocol,
        parks_response,
        expected_code,
        expected_response,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('777', 'norm_session', 'pilot')

    @mockserver.json_handler('/parks/driver-profiles/photo')
    def mock_callback(request):
        return mockserver.make_response(
            json.dumps(parks_response), expected_code,
        )

    response = taxi_driver_protocol.post(
        '/driver/photo/get?db=777&session=norm_session',
    )

    assert response.status_code == expected_code
    if expected_response:
        assert response.json() == expected_response
