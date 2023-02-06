import pytest

ROUTE = '/v2/hiring-conditions/{}'


@pytest.mark.parametrize(
    ('hc_id', 'response_name'),
    [
        ('success_park', 'success'),
        ('deleted_park', 'not_found'),
        ('not_existed_park', 'not_found'),
    ],
)
async def test_get_hiring_condition(
        taxi_hiring_taxiparks_gambling_web, load_json, hc_id, response_name,
):
    expected_response = load_json('expected_responses.json')[response_name]
    route = ROUTE.format(hc_id)
    response = await taxi_hiring_taxiparks_gambling_web.get(route)
    assert expected_response['status'] == response.status
    assert expected_response['data'] == await response.json()
