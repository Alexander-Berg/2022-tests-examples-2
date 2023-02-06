import pytest

from tests_gas_stations import helpers

DB = 'db1'
UUID = 'uuid1'
SESSION = 'session1'
CLID = '12345'


@pytest.mark.parametrize('gas_stations_existed', [False, True])
async def test_taximeter_flow(
        taxi_gas_stations,
        driver_authorizer,
        partner_contracts,
        app_tanker,
        mock_fleet_parks_list,
        mongodb,
        pgsql,
        gas_stations_existed,
):
    if gas_stations_existed:
        helpers.update_mongo_gas_stations(
            mongodb, DB, helpers.MongoResponse.EXIST,
        )
        times = helpers.get_finished_time()
        cursor = pgsql['gas_stations'].cursor()
        cursor.execute(
            helpers.INSERT_PARTNER_CONTRACTS_ACCEPT.format(
                DB, CLID, times['started'], '\'' + times['finished'] + '\'',
            ),
        )
    else:
        helpers.update_mongo_gas_stations(
            mongodb, DB, helpers.MongoResponse.NOT_EXIST,
        )
    partner_contracts.set_response({'inquiry_id': 'something', 'status': 'OK'})
    mock_fleet_parks_list.set_parks([helpers.DEFAULT_PARKS])
    driver_authorizer.set_session(DB, SESSION, UUID)
    helpers.update_mongo_gas_stations(
        mongodb,
        DB,
        helpers.MongoResponse.EXIST
        if gas_stations_existed
        else helpers.MongoResponse.NOT_EXIST,
    )

    response = await taxi_gas_stations.get(
        'driver/v1/offer/state',
        params={'park_id': DB},
        headers={
            'User-Agent': 'Taximeter 8.80 (562)',
            'X-Driver-Session': SESSION,
        },
    )

    assert response.status_code == 200
    response_json = response.json()
    if gas_stations_existed:
        assert (
            response_json['offer_state']
            == helpers.RESPONSE200_ACCEPTED['offer_state']
        )
    else:
        assert response_json == helpers.RESPONSE200_NOT_ACCEPTED

    response = await taxi_gas_stations.post(
        'driver/v1/offer/accept',
        params={'park_id': DB},
        headers={
            'User-Agent': 'Taximeter 8.80 (562)',
            'X-Driver-Session': SESSION,
        },
        json={
            'limit': 1000,
            'is_offer_accepted': True,
            'is_informed_consent_accepted': True,
        },
    )

    assert response.status_code == 200

    response = await taxi_gas_stations.get(
        'driver/v1/offer/state',
        params={'park_id': DB},
        headers={
            'User-Agent': 'Taximeter 8.80 (562)',
            'X-Driver-Session': SESSION,
        },
    )

    assert response.status_code == 200
    response_json = response.json()
    assert response_json == helpers.RESPONSE200_IN_PROGRESS

    app_tanker.set_response('200')

    response = await taxi_gas_stations.post(
        'service/v1/account/created',
        json={
            'clid': CLID,
            'gas_general_contract_id': '123',
            'delivery_contract_id': '1234',
            'billing_client_id': '12',
            'limit': 1000,
        },
    )

    assert response.status_code == 200

    response = await taxi_gas_stations.get(
        'driver/v1/offer/state',
        params={'park_id': DB},
        headers={
            'User-Agent': 'Taximeter 8.80 (562)',
            'X-Driver-Session': SESSION,
        },
    )

    assert response.status_code == 200
    response_json = response.json()
    assert (
        response_json['offer_state']
        == helpers.RESPONSE200_ACCEPTED['offer_state']
    )

    # check postgres
    cursor = pgsql['gas_stations'].cursor()
    cursor.execute(
        'SELECT park_id, clid, started, finished '
        'from gas_stations.partner_contracts_acceptance',
    )
    result = list(row for row in cursor)[0]
    assert result[0] == DB
    assert result[1] == CLID
    assert result[2] is not None  # start was recorded
    assert result[3] is not None  # finish is not None

    # check mongo
    updated_doc = mongodb.dbparks.find_one({'_id': DB})
    assert updated_doc['gas_stations']['offer_accepted_date'] is not None
    assert (
        updated_doc['gas_stations']['informed_consent_accepted_date']
        is not None
    )
