import pytest


@pytest.mark.config(
    SCOOTERS_MOSTRANS_PROXY={
        'upstream': {'$mockserver': ''},
        'timeout': 5000,
        'attempts': 2,
    },
)
async def test_ok(taxi_scooters_mostrans, mockserver):
    @mockserver.json_handler('/offer')
    def mock_offer(request):
        assert request.headers.get('X-API-Key', None) is None
        return {'version': 1, 'content': 'Some offer'}

    response = await taxi_scooters_mostrans.get(
        '/proxy/offer', headers={'Locale': 'en', 'X-API-Key': 'secret'},
    )
    assert response.json() == {'version': 1, 'content': 'Some offer'}
    assert response.status_code == 200
    assert mock_offer.times_called == 1


@pytest.mark.config(
    SCOOTERS_MOSTRANS_PROXY={
        'upstream': {'$mockserver': ''},
        'timeout': 5000,
        'attempts': 2,
    },
)
@pytest.mark.parametrize(
    ['api_key', 'expected_response'],
    [
        pytest.param('secret', 200, id='Ok'),
        pytest.param('invalid', 401, id='Invalid X-API-Key'),
        pytest.param(None, 401, id='Without X-API-Key'),
    ],
)
async def test_headers(
        taxi_scooters_mostrans, mockserver, api_key, expected_response,
):
    @mockserver.json_handler('/offer')
    def mock_offer(request):
        assert request.headers.get('X-API-Key', None) is None
        assert request.headers.get('X-User-Token', None) is None
        assert request.headers.get('Locale', None) == 'en'
        return {}

    headers = {'Locale': 'en', 'X-User-Token': 'user'}
    if api_key is not None:
        headers['X-API-Key'] = api_key
    response = await taxi_scooters_mostrans.get(
        '/proxy/offer', headers=headers,
    )
    assert response.status_code == expected_response
    assert mock_offer.times_called == (1 if expected_response == 200 else 0)


@pytest.mark.config(
    SCOOTERS_MOSTRANS_PROXY={
        'upstream': {'$mockserver': ''},
        'timeout': 5000,
        'attempts': 2,
    },
)
@pytest.mark.parametrize(
    'response_dict',
    [
        pytest.param({'code': 200, 'body': {}}, id='Ok'),
        pytest.param(
            {'code': 400, 'body': {'message': 'error'}}, id='HTTP 400',
        ),
        pytest.param(
            {'code': 401, 'body': {'message': 'need auth'}}, id='HTTP 401',
        ),
        pytest.param({'code': 404, 'body': {}}, id='HTTP 404'),
        pytest.param(
            {'code': 500, 'body': {'message': 'internal error'}},
            id='HTTP 500',
        ),
    ],
)
async def test_handle_fail(taxi_scooters_mostrans, mockserver, response_dict):
    @mockserver.json_handler('/offer')
    def _mock_offer(request):
        return mockserver.make_response(
            status=response_dict['code'], json=response_dict['body'],
        )

    response = await taxi_scooters_mostrans.get(
        '/proxy/offer', headers={'X-API-Key': 'secret'},
    )
    assert {
        'code': response.status_code,
        'body': response.json(),
    } == response_dict
