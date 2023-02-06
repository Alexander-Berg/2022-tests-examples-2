import pytest

from tests_gas_stations import helpers

DB = 'db1'
UUID = 'uuid1'
SESSION = 'session1'

HANDLER = 'driver/v1/offer/accept'

AUTH_PARAMS = {'park_id': DB}

HEADERS = {'User-Agent': 'Taximeter 8.80 (562)', 'X-Driver-Session': SESSION}

BODY = {
    'limit': 1000,
    'is_offer_accepted': True,
    'is_informed_consent_accepted': True,
}

RESPONSE400_DISABLED = {'code': '400', 'message': 'Disabled for this park.'}
RESPONSE400_NOT_SELF = {
    'code': '400',
    'message': 'Driver is not self-employed',
}
RESPONSE404_EMPTY_LOGIN = {'code': '404', 'message': 'Login not found/empty.'}
RESPONSE400_NOT_AGREE = {
    'code': '400',
    'message': 'Should agree with both offer and informed consent.',
}

RESPONSE400_BAD_LIMIT = {
    'code': '400',
    'message': 'Bad limit.',
    'details': {'minimum_limit': 0, 'maximum_limit': 2500},
}


@pytest.mark.parametrize(
    'fleet_parks_response,expected_response,status_code',
    [
        (helpers.DEFAULT_PARKS, helpers.RESPONSE200_IN_PROGRESS, 200),
        (None, helpers.RESPONSE404_PARK_NOT_FOUND, 404),
        (
            helpers.make_park_not_active(helpers.DEFAULT_PARKS),
            RESPONSE400_DISABLED,
            400,
        ),
        (
            helpers.make_park_empty_login(helpers.DEFAULT_PARKS),
            RESPONSE404_EMPTY_LOGIN,
            404,
        ),
        (
            helpers.make_park_wrong_fleet_type(helpers.DEFAULT_PARKS),
            RESPONSE400_DISABLED,
            400,
        ),
        (
            helpers.make_park_without_prov_conf(helpers.DEFAULT_PARKS),
            RESPONSE400_DISABLED,
            400,
        ),
        (
            helpers.make_park_without_clid(helpers.DEFAULT_PARKS),
            RESPONSE400_DISABLED,
            400,
        ),
        (
            helpers.make_park_wrong_type(helpers.DEFAULT_PARKS),
            RESPONSE400_DISABLED,
            400,
        ),
        (
            helpers.make_park_wrong_partner_source(helpers.DEFAULT_PARKS),
            RESPONSE400_NOT_SELF,
            400,
        ),
    ],
)
async def test_driver_offer_accept(
        taxi_gas_stations,
        driver_authorizer,
        mock_fleet_parks_list,
        partner_contracts,
        mongodb,
        pgsql,
        fleet_parks_response,
        expected_response,
        status_code,
):
    partner_contracts.set_response(helpers.DEFAULT_CONTRACTS_RESPONSE)
    if fleet_parks_response is None:
        mock_fleet_parks_list.set_parks([])
    else:
        mock_fleet_parks_list.set_parks([fleet_parks_response])

    driver_authorizer.set_session(DB, SESSION, UUID)
    response = await taxi_gas_stations.post(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS, json=BODY,
    )

    assert response.status_code == status_code
    response_json = response.json()
    assert expected_response == response_json
    if status_code == 200:
        cursor = pgsql['gas_stations'].cursor()
        cursor.execute(
            'SELECT park_id, clid, started, finished '
            'from gas_stations.partner_contracts_acceptance',
        )
        result = list(row for row in cursor)[0]
        assert result[0] == DB
        assert result[1] == helpers.DEFAULT_PARKS['provider_config']['clid']
        assert result[2] is not None  # start was recorded
        assert result[3] is None  # finish is None


async def test_driver_offer_accept_fleet_parks_error(
        taxi_gas_stations,
        driver_authorizer,
        mock_fleet_parks_list,
        partner_contracts,
        mongodb,
        pgsql,
):
    mock_fleet_parks_list.set_return_error()
    partner_contracts.set_response(helpers.DEFAULT_CONTRACTS_RESPONSE)

    helpers.update_mongo_gas_stations(mongodb, DB, helpers.MongoResponse.EXIST)

    driver_authorizer.set_session(DB, SESSION, UUID)
    response = await taxi_gas_stations.post(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS, json=BODY,
    )

    assert response.status_code == 500


async def test_driver_offer_accept_partner_contracts_error(
        taxi_gas_stations,
        driver_authorizer,
        mock_fleet_parks_list,
        partner_contracts,
        mongodb,
        pgsql,
):
    partner_contracts.set_return_error()
    mock_fleet_parks_list.set_parks([helpers.DEFAULT_PARKS])

    helpers.update_mongo_gas_stations(mongodb, DB, helpers.MongoResponse.EXIST)

    driver_authorizer.set_session(DB, SESSION, UUID)
    response = await taxi_gas_stations.post(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS, json=BODY,
    )

    assert response.status_code == 500


@pytest.mark.parametrize(
    'body',
    [
        {
            'limit': 1000,
            'is_offer_accepted': False,
            'is_informed_consent_accepted': True,
        },
        {
            'limit': 1000,
            'is_offer_accepted': True,
            'is_informed_consent_accepted': False,
        },
        {
            'limit': 1000,
            'is_offer_accepted': False,
            'is_informed_consent_accepted': False,
        },
        {
            'limit': 5000,
            'is_offer_accepted': True,
            'is_informed_consent_accepted': True,
        },
        {
            'limit': -100,
            'is_offer_accepted': True,
            'is_informed_consent_accepted': True,
        },
    ],
)
async def test_driver_offer_accept_not_accepted(
        taxi_gas_stations,
        driver_authorizer,
        mock_fleet_parks_list,
        partner_contracts,
        mongodb,
        pgsql,
        body,
):
    partner_contracts.set_response(helpers.DEFAULT_CONTRACTS_RESPONSE)
    mock_fleet_parks_list.set_parks([helpers.DEFAULT_PARKS])

    helpers.update_mongo_gas_stations(mongodb, DB, helpers.MongoResponse.EXIST)

    driver_authorizer.set_session(DB, SESSION, UUID)
    response = await taxi_gas_stations.post(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS, json=body,
    )

    assert response.status_code == 400
    response_json = response.json()
    assert response_json == (
        RESPONSE400_NOT_AGREE
        if body['limit'] == 1000
        else RESPONSE400_BAD_LIMIT
    )
