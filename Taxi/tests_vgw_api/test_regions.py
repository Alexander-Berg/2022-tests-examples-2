import pytest


@pytest.mark.parametrize(
    'response_data',
    [
        (
            [
                {'id': 1, 'name': 'Moscow and Moscow Oblast', 'parent_id': 3},
                {'id': 2, 'name': 'Saint Petersburg', 'parent_id': 10174},
                {
                    'id': 3,
                    'name': 'Central Federal District',
                    'parent_id': 225,
                },
            ]
        ),
    ],
)
async def test_regions_get(taxi_vgw_api, response_data):
    response = await taxi_vgw_api.get('v1/voice_gateways_regions')

    assert response.status_code == 200
    json = response.json()
    assert len(json) == 3
    assert response_data[0] in json
    assert response_data[1] in json
    assert response_data[2] in json


@pytest.mark.parametrize(
    'response_data, gateway, status_code',
    [
        (
            [{'id': 1, 'name': 'Moscow and Moscow Oblast', 'parent_id': 3}],
            'id_1',
            200,
        ),
        (None, 'bad_id', 404),
    ],
)
async def test_regions_get_gateway(
        taxi_vgw_api, response_data, gateway, status_code,
):
    params = {'voice_gateway': gateway}
    response = await taxi_vgw_api.get(
        'v1/voice_gateways_regions', params=params,
    )
    assert response.status_code == status_code
    if response.status_code == 200:
        assert response_data == response.json()
