# pylint: disable=redefined-outer-name

import datetime

import pytest

NOW = datetime.datetime.now().replace(microsecond=0)

BASE_SERVICES = {'taxi': {'is_active': True, 'is_visible': True}}


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_get_services(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    mock_corp_clients.data.get_services_response = BASE_SERVICES

    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/services',
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert mock_corp_clients.get_services.has_calls
    assert response_json == BASE_SERVICES


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_get_service_taxi(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/services/taxi',
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert mock_corp_clients.service_taxi.has_calls
    assert response_json == {'is_active': True}


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_get_service_cargo(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/services/cargo',
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert mock_corp_clients.service_cargo.has_calls
    assert response_json == {'is_active': True}


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_get_service_drive(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/services/drive',
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert mock_corp_clients.service_drive.has_calls
    assert response_json == {'is_active': True}


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_get_service_eats(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/services/eats',
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert mock_corp_clients.service_eats.has_calls
    assert response_json == {'is_active': True}


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_get_service_eats2(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/services/eats2',
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert mock_corp_clients.service_eats2.has_calls
    assert response_json == {'is_active': True}


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_update_service_taxi(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    data = {
        'is_visible': True,
        'comment': 'comment',
        'default_category': 'econom',
    }

    response = await taxi_corp_real_auth_client.patch(
        '/1.0/client/client1/services/taxi', json=data,
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {}

    mock_call = mock_corp_clients.service_taxi.next_call()
    assert mock_call['request'].json == data
    assert not mock_corp_clients.service_taxi.has_calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_update_service_cargo(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    data = {'is_visible': True}

    response = await taxi_corp_real_auth_client.patch(
        '/1.0/client/client1/services/cargo', json=data,
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {}

    mock_call = mock_corp_clients.service_cargo.next_call()
    assert mock_call['request'].json == data
    assert not mock_corp_clients.service_cargo.has_calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_update_service_drive(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    data = {'is_visible': True}

    response = await taxi_corp_real_auth_client.patch(
        '/1.0/client/client1/services/drive', json=data,
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {}

    mock_call = mock_corp_clients.service_drive.next_call()
    assert mock_call['request'].json == data
    assert not mock_corp_clients.service_drive.has_calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_update_service_eats(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    data = {'is_visible': True}

    response = await taxi_corp_real_auth_client.patch(
        '/1.0/client/client1/services/eats', json=data,
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {}

    mock_call = mock_corp_clients.service_eats.next_call()
    assert mock_call['request'].json == data
    assert not mock_corp_clients.service_eats.has_calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_update_service_eats2(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    data = {'is_visible': True}

    response = await taxi_corp_real_auth_client.patch(
        '/1.0/client/client1/services/eats2', json=data,
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {}

    mock_call = mock_corp_clients.service_eats2.next_call()
    assert mock_call['request'].json == data
    assert not mock_corp_clients.service_eats2.has_calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_update_service_market(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    data = {'is_visible': True}

    response = await taxi_corp_real_auth_client.patch(
        '/1.0/client/client1/services/market', json=data,
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {}

    mock_call = mock_corp_clients.service_market.next_call()
    assert mock_call['request'].json == data
    assert not mock_corp_clients.service_market.has_calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_update_service_tanker(
        taxi_corp_real_auth_client, passport_mock, mock_corp_clients,
):
    data = {'is_visible': True, 'payment_method': 'card'}

    response = await taxi_corp_real_auth_client.patch(
        '/1.0/client/client1/services/tanker', json=data,
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {}

    mock_call = mock_corp_clients.service_tanker.next_call()
    assert mock_call['request'].json == data
    assert not mock_corp_clients.service_tanker.has_calls
