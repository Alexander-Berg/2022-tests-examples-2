import json

import pytest


@pytest.mark.parametrize(
    'query,expected_status',
    [
        ({}, 401),
        ({'db': '999'}, 401),
        ({'session': 'qwerty'}, 401),
        ({'db': '999', 'session': 'qwerty'}, 200),
    ],
)
def test_authorization(
        taxi_driver_protocol,
        mockserver,
        query,
        expected_status,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('999', 'qwerty', 'driver')

    URL = '/self-employment/url/to/proxy'

    @mockserver.json_handler('/selfemployed' + URL)
    def get(request):
        return {'status': 'ok'}

    response = taxi_driver_protocol.get('/driver' + URL, params=query)
    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json() == {'status': 'ok'}


@pytest.mark.parametrize('status_code', [401, 404, 418, 449, 500])
def test_error_forwarding(
        taxi_driver_protocol,
        mockserver,
        status_code,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('999', 'qwerty', 'driver')
    URL = '/self-employment/url-to/pRoXy99'

    @mockserver.json_handler('/selfemployed' + URL)
    def get(request):
        return mockserver.make_response(
            json.dumps({'error': 'msg'}),
            content_type='application/json',
            status=status_code,
        )

    response = taxi_driver_protocol.get(
        '/driver' + URL + '?db=999&session=qwerty',
    )
    assert response.status_code == status_code
    assert response.json() == {'error': 'msg'}


def test_path_traversal(taxi_driver_protocol):
    URL = '/self-employment/../admin/lessons'

    response = taxi_driver_protocol.get(
        '/driver' + URL + '?db=999&session=qwerty',
    )
    assert response.status_code == 404


@pytest.mark.parametrize('locale', ['ru', 'en', 'az'])
def test_locale_forwarding(
        taxi_driver_protocol, mockserver, locale, driver_authorizer_service,
):
    driver_authorizer_service.set_session('999', 'qwerty', 'driver')

    @mockserver.json_handler('/selfemployed/self-employment')
    def get(request):
        assert request.headers['Accept-Language'] == locale
        return {}

    response = taxi_driver_protocol.get(
        '/driver/self-employment?db=999&session=qwerty',
        headers={'Accept-Language': locale},
    )
    assert response.status_code == 200


def test_body_forwarding(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('999', 'qwerty', 'driver')

    payload = {'sample': 'body', 'sample2': 'body'}

    @mockserver.json_handler('/selfemployed/self-employment')
    def get(request):
        assert request.json == payload
        return payload

    response = taxi_driver_protocol.post(
        '/driver/self-employment?db=999&session=qwerty', json=payload,
    )
    assert response.status_code == 200


def test_query_forwarding(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('999', 'qwerty', 'driver')

    req_params = {
        'db': 999,
        'session': 'qwerty',
        'tags': 'newbie',
        'arg': 'arg',
        'параметр': 'zна4ение',
    }
    forward_params = {
        'driver': 'driver',
        'park': '999',
        'tags': 'newbie',
        'arg': 'arg',
        'параметр': 'z%D0%BD%D0%B04%D0%B5%D0%BD%D0%B8%D0%B5',
    }

    @mockserver.json_handler('/selfemployed/self-employment')
    def get(request):
        query = dict(
            arg_str.split('=')
            for arg_str in request.query_string.decode().split('&')
        )
        assert query == forward_params
        return {}

    response = taxi_driver_protocol.get(
        '/driver/self-employment', params=req_params,
    )
    assert response.status_code == 200


@pytest.mark.parametrize('polling_delay', [None, '1000'])
def test_polling_delay_response(
        taxi_driver_protocol,
        mockserver,
        polling_delay,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('999', 'qwerty', 'driver')

    @mockserver.json_handler('/selfemployed/self-employment')
    def get(request):
        if polling_delay is None:
            return {}
        return mockserver.make_response(
            '{}', headers={'X-Polling-Delay': polling_delay},
        )

    response = taxi_driver_protocol.get(
        '/driver/self-employment?db=999&session=qwerty',
    )
    assert response.status_code == 200
    assert response.headers.get('X-Polling-Delay', None) == polling_delay
