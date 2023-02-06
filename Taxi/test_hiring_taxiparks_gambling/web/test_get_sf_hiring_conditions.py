import pytest

ROUTE = '/v2/hiring-conditions'


@pytest.mark.usefixtures('group_experiment')
@pytest.mark.parametrize(
    'test_name',
    [
        'some_territory_with_rent',
        'some_territory_without_rent',
        'other_territory_with_rent',
        'other_territory_without_rent',
        'unknown_territory',
    ],
)
async def test_new_get_sf_hiring_conditions(
        web_app_client, load_json, test_name,
):
    request_params = load_json('request_params.json')[test_name]
    expected = load_json('expected_responses.json')[test_name]

    response = await web_app_client.get(ROUTE, params=request_params)

    assert response.status == expected['status']
    if response.status == 200:
        data = await response.json()
        conditions = sorted(data, key=lambda x: x['sf_id'])
        assert conditions == expected['data']
