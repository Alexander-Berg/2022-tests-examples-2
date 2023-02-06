import pytest


@pytest.mark.parametrize(
    'unique_driver_ids,expected_code,expected_response',
    [
        (
            ['000000000000000000000001'],
            200,
            {
                'profiles': [
                    {
                        'unique_driver_id': '000000000000000000000001',
                        'data': [
                            {
                                'park_driver_profile_id': 'park1_driver1',
                                'park_id': 'park1',
                                'driver_profile_id': 'driver1',
                            },
                        ],
                    },
                ],
            },
        ),
        (
            [
                '000000000000000000000001',
                'unique_driver_id_non',
                '000000000000000000000003',
            ],
            200,
            {
                'profiles': [
                    {
                        'unique_driver_id': '000000000000000000000001',
                        'data': [
                            {
                                'park_driver_profile_id': 'park1_driver1',
                                'park_id': 'park1',
                                'driver_profile_id': 'driver1',
                            },
                        ],
                    },
                    {'unique_driver_id': 'unique_driver_id_non', 'data': []},
                    {
                        'unique_driver_id': '000000000000000000000003',
                        'data': [
                            {
                                'park_driver_profile_id': 'park2_driver3',
                                'park_id': 'park2',
                                'driver_profile_id': 'driver3',
                            },
                        ],
                    },
                ],
            },
        ),
        ([], 200, {'profiles': []}),
    ],
)
@pytest.mark.now('2019-03-10T00:00:00')
@pytest.mark.config(TVM_ENABLED=False)
async def test_uniques_retrieve_by_profiles(
        taxi_unique_drivers,
        mockserver,
        unique_driver_ids,
        expected_code,
        expected_response,
):
    response = await taxi_unique_drivers.post(
        'v1/driver/profiles/retrieve_by_uniques',
        params={'consumer': 'service'},
        json={'id_in_set': unique_driver_ids},
    )

    assert response.status_code == expected_code
    assert 'application/json' in response.headers['Content-Type']
    assert response.json() == expected_response
