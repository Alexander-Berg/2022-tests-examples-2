import pytest

from tests_gas_stations import helpers

DB = 'db1'
UUID = 'uuid1'
SESSION = 'session1'

HANDLER = 'service/v1/account/created'

BODY = {
    'clid': '12345',
    'gas_general_contract_id': '123',
    'delivery_contract_id': '1234',
    'billing_client_id': '12',
    'limit': 1000,
}

RESPONSE400_WRONG_CLIENT = {'code': '400', 'message': 'Wrong clid.'}
RESPONSE200 = {'result': 'success'}
RESPONSE400_NOT_AVAILABLE = {
    'code': '400',
    'message': 'Not available for this park.',
}


@pytest.mark.parametrize(
    'fleet_parks_response,gas_stations_response,expected_response,status_code',
    [
        (helpers.DEFAULT_PARKS, helpers.get_finished_time(), RESPONSE200, 200),
        (helpers.DEFAULT_PARKS, helpers.get_expired_time(), RESPONSE200, 200),
        (
            helpers.DEFAULT_PARKS,
            helpers.get_in_progress_time(),
            RESPONSE200,
            200,
        ),
        (helpers.DEFAULT_PARKS, None, RESPONSE400_WRONG_CLIENT, 400),
        (None, helpers.get_in_progress_time(), RESPONSE400_NOT_AVAILABLE, 400),
        (
            helpers.make_park_not_active(helpers.DEFAULT_PARKS),
            helpers.get_in_progress_time(),
            RESPONSE400_NOT_AVAILABLE,
            400,
        ),
        (
            helpers.make_park_empty_login(helpers.DEFAULT_PARKS),
            helpers.get_in_progress_time(),
            RESPONSE400_NOT_AVAILABLE,
            400,
        ),
        (
            helpers.make_park_wrong_fleet_type(helpers.DEFAULT_PARKS),
            helpers.get_in_progress_time(),
            RESPONSE400_NOT_AVAILABLE,
            400,
        ),
        (
            helpers.make_park_without_prov_conf(helpers.DEFAULT_PARKS),
            helpers.get_in_progress_time(),
            RESPONSE400_NOT_AVAILABLE,
            400,
        ),
        (
            helpers.make_park_without_clid(helpers.DEFAULT_PARKS),
            helpers.get_in_progress_time(),
            RESPONSE400_NOT_AVAILABLE,
            400,
        ),
        (
            helpers.make_park_wrong_type(helpers.DEFAULT_PARKS),
            helpers.get_in_progress_time(),
            RESPONSE400_NOT_AVAILABLE,
            400,
        ),
        (
            helpers.make_park_wrong_partner_source(helpers.DEFAULT_PARKS),
            helpers.get_in_progress_time(),
            RESPONSE400_NOT_AVAILABLE,
            400,
        ),
    ],
)
async def test_service_account_created(
        taxi_gas_stations,
        app_tanker,
        mock_fleet_parks_list,
        mongodb,
        pgsql,
        fleet_parks_response,
        gas_stations_response,
        expected_response,
        status_code,
):
    app_tanker.set_response('200')
    if fleet_parks_response is None:
        mock_fleet_parks_list.set_parks([])
    else:
        mock_fleet_parks_list.set_parks([fleet_parks_response])

    if gas_stations_response is not None:
        cursor = pgsql['gas_stations'].cursor()
        cursor.execute(
            helpers.INSERT_PARTNER_CONTRACTS_ACCEPT.format(
                DB,
                BODY['clid'],
                gas_stations_response['started'],
                'NULL'
                if gas_stations_response['finished'] is None
                else '\'' + gas_stations_response['finished'] + '\'',
            ),
        )

    helpers.update_mongo_gas_stations(
        mongodb, DB, helpers.MongoResponse.NOT_EXIST,
    )

    response = await taxi_gas_stations.post(HANDLER, json=BODY)

    assert response.status_code == status_code
    response_json = response.json()
    assert expected_response == response_json
    if status_code != 200:
        return

    # check postgres
    cursor = pgsql['gas_stations'].cursor()
    cursor.execute(
        'SELECT park_id, clid, started, finished '
        'from gas_stations.partner_contracts_acceptance',
    )
    result = list(row for row in cursor)[0]
    assert result[0] == DB
    assert result[1] == BODY['clid']
    assert result[2] is not None  # start was recorded
    assert result[3] is not None  # finish is not None

    # check mongo
    updated_doc = mongodb.dbparks.find_one({'_id': DB})
    assert updated_doc['gas_stations']['offer_accepted_date'] is not None
    assert (
        updated_doc['gas_stations']['informed_consent_accepted_date']
        is not None
    )


async def test_service_account_created_fleet_parks_error(
        taxi_gas_stations, app_tanker, mock_fleet_parks_list, mongodb, pgsql,
):
    app_tanker.set_response('200')
    mock_fleet_parks_list.set_return_error()

    helpers.update_mongo_gas_stations(
        mongodb, DB, helpers.MongoResponse.NOT_EXIST,
    )

    times = helpers.get_finished_time()
    cursor = pgsql['gas_stations'].cursor()
    cursor.execute(
        helpers.INSERT_PARTNER_CONTRACTS_ACCEPT.format(
            DB,
            BODY['clid'],
            times['started'],
            '\'' + times['finished'] + '\'',
        ),
    )

    response = await taxi_gas_stations.post(HANDLER, json=BODY)

    assert response.status_code == 500


async def test_service_account_created_tanker_error(
        taxi_gas_stations, app_tanker, mock_fleet_parks_list, mongodb, pgsql,
):
    app_tanker.set_return_error()
    mock_fleet_parks_list.set_parks([helpers.DEFAULT_PARKS])

    helpers.update_mongo_gas_stations(
        mongodb, DB, helpers.MongoResponse.NOT_EXIST,
    )

    times = helpers.get_finished_time()
    cursor = pgsql['gas_stations'].cursor()
    cursor.execute(
        helpers.INSERT_PARTNER_CONTRACTS_ACCEPT.format(
            DB,
            BODY['clid'],
            times['started'],
            '\'' + times['finished'] + '\'',
        ),
    )

    response = await taxi_gas_stations.post(HANDLER, json=BODY)

    assert response.status_code == 500
    response_json = response.json()
    assert response_json == {
        'code': '500',
        'message': 'Failed to create account in tanker.',
    }
