# pylint: disable=redefined-outer-name

import datetime

import pytest

NOW = datetime.datetime.now().replace(microsecond=0)

BASE_CLIENT = {
    'id': 'client1',
    'name': 'test',
    'country': 'rus',
    'created': '2021-07-01T13:00:00+03:00',
    'yandex_login': 'yandex_login_1',
    'is_trial': False,
    'billing_id': '12345',
    'features': [],
    'email': 'example@yandex.ru',
}


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_get_client(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    mock_corp_clients.data.get_client_response = BASE_CLIENT

    response = await taxi_corp_real_auth_client.get('/1.0/clients/client1')
    response_json = await response.json()
    assert response.status == 200, response_json
    assert mock_corp_clients.clients.has_calls
    assert response_json == BASE_CLIENT


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client2'], indirect=['passport_mock'],
)
async def test_get_client_not_found(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    response = await taxi_corp_real_auth_client.get('/1.0/clients/client2')
    assert response.status == 404
    assert mock_corp_clients.clients.has_calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_update_client(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    data = {'email': 'example@yandex.ru'}

    response = await taxi_corp_real_auth_client.patch(
        '/1.0/clients/client1', json=data,
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {}

    mock_call = mock_corp_clients.clients.next_call()
    assert mock_call['request'].json == data
    assert not mock_corp_clients.clients.has_calls
