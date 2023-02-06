import pytest

from tests_uapi_keys import auth
from tests_uapi_keys import utils


ENDPOINTS = [
    ('/v2/clients/by-user', auth.DISPATCHER_HEADERS, auth.DISPATCHER_CREATOR),
    ('/v2/clients/by-user', auth.SUPPORT_HEADERS, auth.SUPPORT_CREATOR),
    ('/v2/clients/by-admin', auth.ADMIN_HEADERS, auth.ADMIN_CREATOR),
    ('/internal/v2/clients', auth.INTERNAL_HEADERS, auth.DISPATCHER_CREATOR),
    ('/internal/v2/clients', auth.INTERNAL_HEADERS, auth.SUPPORT_CREATOR),
    ('/internal/v2/clients', auth.INTERNAL_HEADERS, auth.ADMIN_CREATOR),
]

OK_REQUEST = {
    'consumer_id': 'fleet-api',
    'client_id': 'abc',
    'name': 'Абв',
    'comment': 'тестовый комментарий',
}


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.config(TVM_USER_TICKETS_ENABLED=True)
async def test_create_unauthorized(taxi_uapi_keys):
    headers = auth.DISPATCHER_HEADERS.copy()
    headers['X-Ya-User-Ticket-Provider'] = 'trash'
    response = await taxi_uapi_keys.post(
        '/v2/clients/by-user', headers=headers, json=OK_REQUEST,
    )
    assert response.status_code == 401


OK_PARAMS = [
    OK_REQUEST,
    {
        'consumer_id': 'fleet-api-internal',
        'client_id': 'taxi/park/' + 'ABC' * 18,
        'name': 'Для парка',
        'comment': '',
    },
    {
        'consumer_id': 'fleet-api',
        'client_id': 'antony',
        'name': 'Антон Тодуа',
        'comment': 'Для тестирования',
    },
]


def _make_request(headers, creator, client):
    return (
        {'client': client, 'creator': creator}
        if headers == auth.INTERNAL_HEADERS
        else client
    )


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.config(TVM_USER_TICKETS_ENABLED=True)
@pytest.mark.parametrize('endpoint, headers, creator', ENDPOINTS)
@pytest.mark.parametrize('request_client', OK_PARAMS)
async def test_ok(taxi_uapi_keys, endpoint, headers, creator, request_client):
    response = await taxi_uapi_keys.post(
        endpoint,
        headers=headers,
        json=_make_request(headers, creator, request_client),
    )
    assert response.status_code == 200
    response_client = response.json()

    client_id = request_client['client_id'].lower()
    assert utils.check_timestamps_after_creation(response_client.copy()) == {
        **request_client,
        'creator': creator,
        'client_id': client_id,
    }

    await taxi_uapi_keys.invalidate_caches()

    list_response = await taxi_uapi_keys.post(
        '/v2/clients/list',
        headers={'X-Ya-Service-Ticket': auth.MOCK_SERVICE_TICKET},
        json={
            'query': {
                'consumer_id': request_client['consumer_id'],
                'client_id': client_id,
            },
        },
    )
    assert list_response.status_code == 200, list_response.text
    assert list_response.json()['clients'] == [response_client]


@pytest.mark.parametrize('endpoint, headers, creator', ENDPOINTS)
async def test_idempotency(taxi_uapi_keys, endpoint, headers, creator):
    request_json = _make_request(headers, creator, OK_REQUEST)

    response = await taxi_uapi_keys.post(
        endpoint, headers=headers, json=request_json,
    )
    assert response.status_code == 200
    response_json = response.json()

    response = await taxi_uapi_keys.post(
        endpoint, headers=headers, json=request_json,
    )
    assert response.status_code == 200
    assert response.json() == response_json


@pytest.mark.parametrize('endpoint, headers, creator', ENDPOINTS)
async def test_already_exists(taxi_uapi_keys, endpoint, headers, creator):
    response = await taxi_uapi_keys.post(
        endpoint,
        headers=headers,
        json=_make_request(headers, creator, OK_REQUEST),
    )
    assert response.status_code == 200

    another_ok_request = OK_REQUEST.copy()
    another_ok_request['comment'] = 'другой тестовый комментарий'

    response = await taxi_uapi_keys.post(
        endpoint,
        headers=headers,
        json=_make_request(headers, creator, another_ok_request),
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'client_already_exists',
        'message': 'client with id `abc` already exists',
    }
