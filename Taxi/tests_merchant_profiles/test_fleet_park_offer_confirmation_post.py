import pytest

from tests_merchant_profiles import utils

ENDPOINT = '/fleet/merchant-profiles/v1/park/offer/confirmation'

HEADERS = {
    'X-Ya-User-Ticket': 'ticket_valid1',
    'X-Ya-User-Ticket-Provider': 'yandex_team',
    'X-Yandex-UID': '1',
    'X-Park-ID': 'test_park_id',
}


async def test_ok(
        taxi_merchant_profiles,
        mock_fleet_parks_list,
        mock_parks_replica,
        pgsql,
):
    response = await taxi_merchant_profiles.post(ENDPOINT, headers={**HEADERS})
    assert response.status_code == 200
    db_result = utils.get_park_offer_confirmation(
        pgsql['merchant_profiles'].cursor(), '187701087',
    )
    assert db_result[0]['billing_client_id'] == '187701087'


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
    response = await taxi_merchant_profiles.post(ENDPOINT, headers={**HEADERS})
    assert response.status_code == 409


async def test_conflict_billing_id(
        taxi_merchant_profiles,
        mock_fleet_parks_list,
        mock_parks_replica,
        pgsql,
):
    mock_parks_replica.response = {}
    response = await taxi_merchant_profiles.post(ENDPOINT, headers={**HEADERS})
    assert response.status_code == 409


@pytest.mark.pgsql('merchant_profiles', files=['offer_1.sql'])
async def test_not_modified(
        taxi_merchant_profiles,
        mock_fleet_parks_list,
        mock_parks_replica,
        pgsql,
):
    before_db_result = utils.get_park_offer_confirmation(
        pgsql['merchant_profiles'].cursor(), '187701087',
    )
    response = await taxi_merchant_profiles.post(ENDPOINT, headers={**HEADERS})
    assert response.status_code == 200
    after_db_result = utils.get_park_offer_confirmation(
        pgsql['merchant_profiles'].cursor(), '187701087',
    )
    assert before_db_result == after_db_result
