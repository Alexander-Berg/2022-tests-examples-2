import pytest

URL = '/v1/contractor/passport-binding-events'


@pytest.mark.yt(
    schemas=['yt_passport_binding_events_dyn_schema.yaml'],
    dyn_table_data=['yt_passport_binding_events_dyn_data.yaml'],
)
@pytest.mark.config(
    DRIVER_PROFILES_PASSPORT_BINDING_EVENTS_SETTINGS={
        'cluster': 'hahn',
        'table_name': '//home/testsuite/taximeter_passport_binding_events',
        'limit': 3,
    },
)
@pytest.mark.parametrize(
    'park_id, contractor_id, expected_response',
    [
        pytest.param(
            '00000000000000000000000000000001', 'driver01', 'response.json',
        ),
        pytest.param(
            '00000000000000000000000000000002',
            'Foma Kinaev/ЛШТФУМ Ащьф',
            'cyr_response.json',
        ),
        pytest.param(
            '00000000000000000000000000000003',
            'driver03',
            'empty_response.json',
        ),
    ],
)
async def test_response(
        taxi_driver_profiles,
        taxi_config,
        yt_apply,
        load_json,
        park_id,
        contractor_id,
        expected_response,
):
    response = await taxi_driver_profiles.get(
        URL, params={'park_id': park_id, 'contractor_id': contractor_id},
    )
    assert response.status == 200
    assert response.json() == load_json(expected_response)
