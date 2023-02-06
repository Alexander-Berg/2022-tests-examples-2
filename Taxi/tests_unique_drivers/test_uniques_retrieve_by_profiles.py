import pytest


@pytest.mark.parametrize(
    'park_driver_profile_ids,expected_code,expected_response',
    [
        (
            ['park1_driver1'],
            200,
            {
                'uniques': [
                    {
                        'park_driver_profile_id': 'park1_driver1',
                        'data': {
                            'unique_driver_id': '000000000000000000000001',
                        },
                    },
                ],
            },
        ),
        (
            ['park1_driver1', 'park_driver_non', 'park2_driver2'],
            200,
            {
                'uniques': [
                    {
                        'park_driver_profile_id': 'park1_driver1',
                        'data': {
                            'unique_driver_id': '000000000000000000000001',
                        },
                    },
                    {'park_driver_profile_id': 'park_driver_non'},
                    {
                        'park_driver_profile_id': 'park2_driver2',
                        'data': {
                            'unique_driver_id': '000000000000000000000002',
                        },
                    },
                ],
            },
        ),
        (
            ['park2_driver3'],  # test deletions
            200,
            {'uniques': [{'park_driver_profile_id': 'park2_driver3'}]},
        ),
        ([], 200, {'uniques': []}),
    ],
)
@pytest.mark.now('2019-03-10T00:00:00')
@pytest.mark.config(TVM_ENABLED=False)
async def test_uniques_retrieve_by_profiles(
        taxi_unique_drivers,
        mockserver,
        park_driver_profile_ids,
        expected_code,
        expected_response,
):
    response = await taxi_unique_drivers.post(
        'v1/driver/uniques/retrieve_by_profiles',
        params={'consumer': 'service'},
        json={'profile_id_in_set': park_driver_profile_ids},
    )

    assert response.status_code == expected_code
    assert 'application/json' in response.headers['Content-Type']
    assert response.json() == expected_response
