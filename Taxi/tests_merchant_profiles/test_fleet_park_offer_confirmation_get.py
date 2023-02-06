import pytest

ENDPOINT = '/fleet/merchant-profiles/v1/park/offer/confirmation'

HEADERS = {
    'X-Ya-User-Ticket': 'ticket_valid1',
    'X-Ya-User-Ticket-Provider': 'yandex_team',
    'X-Yandex-UID': '1',
    'X-Park-ID': 'test_park_id',
}


@pytest.mark.pgsql('merchant_profiles', files=['offer_1.sql'])
async def test_ok(
        taxi_merchant_profiles,
        mock_fleet_parks_list,
        mock_parks_replica,
        pgsql,
):
    response = await taxi_merchant_profiles.get(ENDPOINT, headers={**HEADERS})
    assert response.status_code == 200
    assert response.json() == {'confirmed': True}


@pytest.mark.parametrize(
    ['billing_client_id'],
    [
        pytest.param('0', id='Non existing billing_id'),
        pytest.param('187701087', id='Withdrawn offer'),
    ],
)
@pytest.mark.pgsql('merchant_profiles', files=['offer_2.sql'])
async def test_not_confirmed(
        taxi_merchant_profiles,
        mock_fleet_parks_list,
        mock_parks_replica,
        pgsql,
        billing_client_id,
):
    mock_parks_replica.response = {'billing_client_id': billing_client_id}
    response = await taxi_merchant_profiles.get(ENDPOINT, headers={**HEADERS})
    assert response.status_code == 200
    assert response.json() == {'confirmed': False}


@pytest.mark.parametrize(
    'provider_config',
    [
        pytest.param(None, id='No provider config'),
        pytest.param({'type': 'production'}, id='No clid in provider config'),
    ],
)
async def test_conflict_clid(
        taxi_merchant_profiles,
        mock_fleet_parks_list,
        mock_parks_replica,
        pgsql,
        provider_config,
):
    mock_fleet_parks_list.provider_config = provider_config
    response = await taxi_merchant_profiles.get(ENDPOINT, headers={**HEADERS})
    assert response.status_code == 409


async def test_conflict_billing_id(
        taxi_merchant_profiles,
        mock_fleet_parks_list,
        mock_parks_replica,
        pgsql,
):
    mock_parks_replica.response = {}
    response = await taxi_merchant_profiles.get(ENDPOINT, headers={**HEADERS})
    assert response.status_code == 409
