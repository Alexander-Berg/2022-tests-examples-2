import pytest


@pytest.mark.now('2021-07-20T12:00:00+0000')
@pytest.mark.config(
    SCOOTERS_MOSTRANS_POLYGONS_SETTINGS={
        'parking_tag': 'allow_drop_car',
        'work_zone_tag': 'user_app_work_zones_prod',
    },
)
@pytest.mark.parametrize(
    'expected_response',
    [
        pytest.param(
            'expected_scooter_parking_get_response.json',
            id='test_scooter_parking_get',
            marks=pytest.mark.scooters_mostrans_scooters_areas_mock(
                filename='scooters_misc_v1_areas_response.json',
            ),
        ),
    ],
)
async def test_scooter_parking_get(
        taxi_scooters_mostrans, load_json, expected_response,
):

    response = await taxi_scooters_mostrans.get(
        '/scooter-parking', headers={'Api-Key': 'secret'},
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)
