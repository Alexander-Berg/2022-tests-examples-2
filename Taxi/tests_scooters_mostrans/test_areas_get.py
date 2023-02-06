import pytest


@pytest.mark.now('2021-07-20T12:00:00+0000')
@pytest.mark.scooters_mostrans_scooters_areas_mock(
    filename='scooters_misc_v1_areas_response.json',
)
@pytest.mark.parametrize(
    'expected_response',
    [
        pytest.param(
            'expected_areas_get_old_config.json',
            id='test_old_config',
            marks=pytest.mark.config(
                SCOOTERS_MOSTRANS_POLYGONS_SETTINGS={
                    'parking_tag': 'allow_drop_car',
                    'work_zone_tag': 'user_app_work_zones_prod',
                },
            ),
        ),
        pytest.param(
            'expected_areas_get_full_config.json',
            id='test_full_config',
            marks=pytest.mark.config(
                SCOOTERS_MOSTRANS_POLYGONS_SETTINGS={
                    'parking_tag': 'allow_drop_car',
                    'work_zone_tag': 'user_app_work_zones_prod',
                    'work_zone': {'rental_end_fine': 100},
                    'restricted_zone': {
                        'tag': 'area_for_bad',
                        'rental_end_fine': 500,
                    },
                    'slowdown_zone': {'tag': 'slowdown_area_tag', 'limit': 15},
                    'slowdown_low_zone': {
                        'tag': 'slowdown_low_area_tag',
                        'limit': 5,
                    },
                },
            ),
        ),
    ],
)
async def test_areas_get(taxi_scooters_mostrans, load_json, expected_response):

    response = await taxi_scooters_mostrans.get('/areas')
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)
