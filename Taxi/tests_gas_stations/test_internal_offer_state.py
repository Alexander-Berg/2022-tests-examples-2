import pytest

from tests_gas_stations import helpers


ENDPOINT = 'internal/v1/offer/state'
PARK_ID = 'db1'


def _make_request(park_id):
    return {'park_id': park_id}


@pytest.mark.parametrize(
    'mongo_state,is_offer_accepted',
    [
        (helpers.MongoResponse.NOT_EXIST, False),
        (helpers.MongoResponse.EXIST, True),
    ],
)
async def test_ok(taxi_gas_stations, mongodb, mongo_state, is_offer_accepted):
    helpers.update_mongo_gas_stations(mongodb, PARK_ID, mongo_state)
    response = await taxi_gas_stations.post(
        ENDPOINT, json=_make_request(PARK_ID),
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'is_offer_accepted': is_offer_accepted}


async def test_park_not_found(taxi_gas_stations):
    response = await taxi_gas_stations.post(
        ENDPOINT, json=_make_request('trash'),
    )

    assert response.status_code == 400, response.text
    assert response.json() == {'code': '400', 'message': 'park not found'}


async def test_internal_error(taxi_gas_stations, mongodb):
    helpers.update_mongo_gas_stations(
        mongodb, PARK_ID, helpers.MongoResponse.EXIST_CONSENT,
    )
    response = await taxi_gas_stations.post(
        ENDPOINT, json=_make_request(PARK_ID),
    )

    assert response.status_code == 500, response.text
