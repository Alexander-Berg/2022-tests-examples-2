import pytest

ROUTE = '/v2/cars/upsert'
FETCH_CAR_BY_SF_IF = """
SELECT * FROM hiring_taxiparks_gambling_salesforce.cars WHERE
sf_id = ANY(ARRAY{})
"""


@pytest.mark.parametrize('case', ['insert', 'update', 'upsert'])
async def test_park_cars_upsert(
        taxi_hiring_taxiparks_gambling_web, pgsql, load_json, case,
):
    # arrange
    request = load_json('requests.json')[case]
    car_sf_ids = [car['sf_id'] for car in request['cars']]
    expected_response = load_json('expected_responses.json')[case]
    expected_data = load_json('expected_data.json')[case]

    # act
    response = await taxi_hiring_taxiparks_gambling_web.post(
        ROUTE, json=request,
    )

    # assert
    assert expected_response['status'] == response.status
    assert expected_response['data'] == await response.json()

    cursor = pgsql['hiring_misc'].cursor()
    cursor.execute(FETCH_CAR_BY_SF_IF.format(car_sf_ids))
    cars = [list(car) for car in cursor.fetchall()]
    assert cars == expected_data
