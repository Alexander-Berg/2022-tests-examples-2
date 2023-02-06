# pylint: disable=redefined-outer-name

import pytest


@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_cards_get(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/cards/list',
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert mock_corp_clients.get_cards_list.has_calls


@pytest.mark.parametrize(
    'passport_mock, status',
    [
        pytest.param(
            ['client1', {'attributes': {'200': '1'}}], 200, id='client1',
        ),
        pytest.param(['client1', {'attributes': {}}], 403, id='client1'),
    ],
    indirect=['passport_mock'],
)
async def test_cards_main_post(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients, status,
):
    json = {'card_id': 'card-123'}

    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/client1/cards/main', json=json,
    )
    response_json = await response.json()
    assert response.status == status, response_json

    if status == 200:
        assert mock_corp_clients.cards_main.has_calls


@pytest.mark.parametrize(
    'passport_mock',
    [['client1', {'attributes': {'200': '1'}}]],
    indirect=['passport_mock'],
)
async def test_cards_main_post_bad_request(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/client1/cards/main', json={},
    )
    assert response.status == 400


@pytest.mark.parametrize(
    'passport_mock, status',
    [
        pytest.param(
            ['client1', {'attributes': {'200': '1'}}], 200, id='client1',
        ),
        pytest.param(['client1', {'attributes': {}}], 403, id='client1'),
    ],
    indirect=['passport_mock'],
)
async def test_cards_main_delete(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients, status,
):
    response = await taxi_corp_real_auth_client.delete(
        '/1.0/client/client1/cards/main',
    )
    response_json = await response.json()
    assert response.status == status, response_json

    if status == 200:
        assert mock_corp_clients.cards_main.has_calls


@pytest.mark.parametrize(
    'passport_mock, status',
    [
        pytest.param(
            ['client1', {'attributes': {'200': '1'}}], 200, id='client1',
        ),
        pytest.param(['client1', {'attributes': {}}], 403, id='client1'),
    ],
    indirect=['passport_mock'],
)
async def test_cards_bindings(
        taxi_corp_real_auth_client, passport_mock, status, mock_corp_clients,
):
    json = {}

    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/client1/cards/bindings', json=json,
    )
    response_json = await response.json()
    assert response.status == status, response_json
