import pytest

ROUTE = '/v2/cars/bulk/delete'
FETCH_CAR_BY_SF_IF = """
SELECT * FROM hiring_taxiparks_gambling_salesforce.cars WHERE
sf_id = ANY(ARRAY{}) AND is_deleted=FALSE
"""


@pytest.mark.parametrize('case', ['two', 'deleted'])
async def test_park_cars_delete(
        taxi_hiring_taxiparks_gambling_web, pgsql, load_json, case,
):
    # arrange
    request = load_json('requests.json')[case]
    expected_response = load_json('expected_responses.json')[case]

    # act
    response = await taxi_hiring_taxiparks_gambling_web.post(
        ROUTE, json=request,
    )

    # assert
    assert expected_response['status'] == response.status
    assert expected_response['data'] == await response.json()

    cursor = pgsql['hiring_misc'].cursor()
    cursor.execute(FETCH_CAR_BY_SF_IF.format(request['ids']))
    assert cursor.fetchall() == []
