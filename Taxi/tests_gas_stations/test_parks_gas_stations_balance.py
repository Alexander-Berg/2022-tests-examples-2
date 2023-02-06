import pytest

from tests_gas_stations import helpers

ENDPOINT = '/v1/parks/gas-stations/balance'

PARK_ID = 'db1'


@pytest.mark.parametrize(
    'tanker_response, expected_response',
    (
        (
            {'balance': 1000.1, 'limit': 20000.0},
            {'balance': '1000.1', 'balance_limit': '20000'},
        ),
        (
            {'balance': 300.25, 'limit': 40000.11115},
            {'balance': '300.25', 'balance_limit': '40000.1111'},
        ),
        (
            {'balance': 10.12, 'limit': 150.999},
            {'balance': '10.12', 'balance_limit': '150.999'},
        ),
    ),
)
async def test_ok(
        taxi_gas_stations,
        mockserver,
        mongodb,
        tanker_response,
        expected_response,
):
    @mockserver.json_handler('app-tanker/api/corporation/balance/taxi')
    async def tanker_balance(request):
        assert PARK_ID == request.query['dbId']
        return tanker_response

    helpers.update_mongo_gas_stations(
        mongodb, PARK_ID, helpers.MongoResponse.EXIST,
    )
    response = await taxi_gas_stations.get(
        ENDPOINT, headers={'X-Park-ID': PARK_ID},
    )

    assert response.status_code == 200
    assert response.json() == expected_response
    assert tanker_balance.has_calls


async def test_park_not_found(taxi_gas_stations, mongodb):
    park_id = 'invalid_park_id'
    helpers.update_mongo_gas_stations(
        mongodb, park_id, helpers.MongoResponse.NOT_EXIST,
    )

    response = await taxi_gas_stations.get(
        ENDPOINT, headers={'X-Park-ID': park_id},
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'park_not_found',
        'message': 'park not found',
    }


@pytest.mark.parametrize(
    'offer_status, tanker_response',
    (
        # tanker-app: balance or limit is None
        (helpers.MongoResponse.EXIST, {'balance': None, 'limit': None}),
        (helpers.MongoResponse.EXIST, {'balance': 100, 'limit': None}),
        (helpers.MongoResponse.EXIST, {'balance': None, 'limit': 100}),
        # Mongo dbparks.parks: offer was not accepted
        (helpers.MongoResponse.NOT_EXIST, {'balance': 100, 'limit': 100}),
    ),
)
async def test_offer_was_not_accepted(
        taxi_gas_stations, mockserver, mongodb, offer_status, tanker_response,
):
    @mockserver.json_handler('app-tanker/api/corporation/balance/taxi')
    async def tanker_balance(request):
        assert PARK_ID == request.query['dbId']
        return tanker_response

    helpers.update_mongo_gas_stations(mongodb, PARK_ID, offer_status)

    response = await taxi_gas_stations.get(
        ENDPOINT, headers={'X-Park-ID': PARK_ID},
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': 'offer_was_not_accepted',
        'message': 'offer was not accepted',
    }
    if offer_status == helpers.MongoResponse.NOT_EXIST:
        assert not tanker_balance.has_calls
    else:
        assert tanker_balance.has_calls
