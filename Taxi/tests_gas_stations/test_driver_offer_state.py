import pytest

from tests_gas_stations import helpers

DB = 'db1'
UUID = 'uuid1'
SESSION = 'session1'

HANDLER = 'driver/v1/offer/state'

AUTH_PARAMS = {'park_id': DB}

HEADERS = {'User-Agent': 'Taximeter 8.80 (562)', 'X-Driver-Session': SESSION}


@pytest.mark.parametrize(
    'fleet_parks_response,acceptance_response,'
    'mongo_response,expected_response,status_code',
    [
        (
            helpers.DEFAULT_PARKS,
            None,
            helpers.MongoResponse.EXIST,
            helpers.RESPONSE200_NOT_ACCEPTED,
            200,
        ),
        (
            helpers.DEFAULT_PARKS,
            helpers.get_finished_time(),
            helpers.MongoResponse.EXIST,
            helpers.get_response200_accepted(
                'some_login', helpers.OFFER_ACCEPTED_TIME_TEST,
            ),
            200,
        ),
        (
            None,
            helpers.get_finished_time(),
            helpers.MongoResponse.EXIST,
            helpers.RESPONSE404_PARK_NOT_FOUND,
            404,
        ),
        (
            helpers.make_park_not_active(helpers.DEFAULT_PARKS),
            helpers.get_finished_time(),
            helpers.MongoResponse.EXIST,
            helpers.RESPONSE200_NOT_AVAILABLE,
            200,
        ),
        (
            helpers.make_park_empty_login(helpers.DEFAULT_PARKS),
            helpers.get_finished_time(),
            helpers.MongoResponse.EXIST,
            helpers.RESPONSE200_NOT_AVAILABLE,
            200,
        ),
        (
            helpers.make_park_wrong_fleet_type(helpers.DEFAULT_PARKS),
            helpers.get_finished_time(),
            helpers.MongoResponse.EXIST,
            helpers.RESPONSE200_NOT_AVAILABLE,
            200,
        ),
        (
            helpers.make_park_without_prov_conf(helpers.DEFAULT_PARKS),
            helpers.get_finished_time(),
            helpers.MongoResponse.EXIST,
            helpers.RESPONSE200_NOT_AVAILABLE,
            200,
        ),
        (
            helpers.make_park_without_clid(helpers.DEFAULT_PARKS),
            helpers.get_finished_time(),
            helpers.MongoResponse.EXIST,
            helpers.RESPONSE200_NOT_AVAILABLE,
            200,
        ),
        (
            helpers.make_park_wrong_type(helpers.DEFAULT_PARKS),
            helpers.get_finished_time(),
            helpers.MongoResponse.EXIST,
            helpers.RESPONSE200_NOT_AVAILABLE,
            200,
        ),
        (
            helpers.make_park_wrong_partner_source(helpers.DEFAULT_PARKS),
            helpers.get_finished_time(),
            helpers.MongoResponse.EXIST,
            helpers.RESPONSE200_NOT_AVAILABLE,
            200,
        ),
        (
            helpers.DEFAULT_PARKS,
            helpers.get_expired_time(),
            helpers.MongoResponse.EXIST,
            helpers.RESPONSE200_EXPIRED,
            200,
        ),
        (
            helpers.DEFAULT_PARKS,
            helpers.get_expired_time(),
            helpers.MongoResponse.NOT_EXIST,
            helpers.RESPONSE200_EXPIRED,
            200,
        ),
        (
            helpers.DEFAULT_PARKS,
            helpers.get_in_progress_time(),
            helpers.MongoResponse.EXIST,
            helpers.RESPONSE200_IN_PROGRESS,
            200,
        ),
        (
            helpers.DEFAULT_PARKS,
            helpers.get_in_progress_time(),
            helpers.MongoResponse.NOT_EXIST,
            helpers.RESPONSE200_IN_PROGRESS,
            200,
        ),
        (
            helpers.DEFAULT_PARKS,
            helpers.get_finished_time(),
            helpers.MongoResponse.NOT_EXIST,
            helpers.RESPONSE200_NOT_ACCEPTED,
            200,
        ),
        (
            helpers.DEFAULT_PARKS,
            helpers.get_finished_time(),
            helpers.MongoResponse.EXIST_OFFER,
            helpers.RESPONSE500,
            500,
        ),
        (
            helpers.DEFAULT_PARKS,
            helpers.get_finished_time(),
            helpers.MongoResponse.EXIST_CONSENT,
            helpers.RESPONSE500,
            500,
        ),
    ],
)
async def test_driver_offer_state(
        taxi_gas_stations,
        driver_authorizer,
        mock_fleet_parks_list,
        mongodb,
        pgsql,
        fleet_parks_response,
        acceptance_response,
        mongo_response,
        expected_response,
        status_code,
):
    if fleet_parks_response is None:
        mock_fleet_parks_list.set_parks([])
    else:
        mock_fleet_parks_list.set_parks([fleet_parks_response])

    if (
            acceptance_response is not None
            and fleet_parks_response is not None
            and 'provider_config' in fleet_parks_response
            and 'clid' in fleet_parks_response['provider_config']
    ):
        cursor = pgsql['gas_stations'].cursor()
        cursor.execute(
            helpers.INSERT_PARTNER_CONTRACTS_ACCEPT.format(
                DB,
                fleet_parks_response['provider_config']['clid'],
                acceptance_response['started'],
                'NULL'
                if acceptance_response['finished'] is None
                else '\'' + acceptance_response['finished'] + '\'',
            ),
        )
    helpers.update_mongo_gas_stations(mongodb, DB, mongo_response)

    driver_authorizer.set_session(DB, SESSION, UUID)
    response = await taxi_gas_stations.get(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS,
    )

    assert response.status_code == status_code
    response_json = response.json()
    assert expected_response == response_json


async def test_driver_offer_state_fleet_parks_error(
        taxi_gas_stations,
        driver_authorizer,
        mock_fleet_parks_list,
        mongodb,
        pgsql,
):
    mock_fleet_parks_list.set_return_error()

    helpers.update_mongo_gas_stations(mongodb, DB, helpers.MongoResponse.EXIST)

    driver_authorizer.set_session(DB, SESSION, UUID)
    response = await taxi_gas_stations.get(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS,
    )

    assert response.status_code == 500
