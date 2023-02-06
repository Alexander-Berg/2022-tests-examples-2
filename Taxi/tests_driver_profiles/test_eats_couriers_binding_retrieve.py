import pytest

HANDLER = '/v1/eats-couriers-binding/retrieve_by_park_driver_profile_id'

BINDING_1 = {
    'taxi_id': 'park_id_1_driver_id_1',
    'eats_id': 'external_id_1',
    'courier_app': 'taximeter',
}
BINDING_2 = {
    'taxi_id': 'park_id_1_driver_id_2',
    'eats_id': 'external_id_2',
    'courier_app': 'taximeter',
}
BINDING_NOT_A_COURIER = {'taxi_id': 'not_a_courier'}
BINDING_NOT_EXISTING_COURIER = {'taxi_id': 'park_id_1_not_existing'}
BINDING_NOT_WORKING_COURIER = {'taxi_id': 'park_id_1_not_working_courier'}


@pytest.mark.parametrize(
    ('params', 'expected_code', 'expected_response'),
    [
        pytest.param({}, 400, None, id='invalid request'),
        pytest.param(
            {'id_in_set': []}, 200, {'binding': []}, id='empty request',
        ),
        pytest.param(
            {'id_in_set': ['park_id_1_driver_id_1']},
            200,
            {'binding': [BINDING_1]},
            id='single id in request',
        ),
        pytest.param(
            {
                'id_in_set': [
                    'park_id_1_driver_id_1',
                    'park_id_1_driver_id_2',
                    'not_a_courier',
                    'park_id_1_not_existing',
                    'park_id_1_not_working_courier',
                ],
            },
            200,
            {
                'binding': [
                    BINDING_1,
                    BINDING_2,
                    BINDING_NOT_A_COURIER,
                    BINDING_NOT_EXISTING_COURIER,
                    BINDING_NOT_WORKING_COURIER,
                ],
            },
            id='all ids',
        ),
    ],
)
async def test_courier_profiles_retrieve(
        taxi_driver_profiles, params, expected_code, expected_response,
):
    response = await taxi_driver_profiles.post(HANDLER, json=params)
    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == expected_response
