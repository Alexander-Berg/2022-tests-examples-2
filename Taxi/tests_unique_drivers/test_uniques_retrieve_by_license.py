import pytest


@pytest.mark.parametrize(
    'license_pd_ids,expected_code,expected_response',
    [
        (
            ['driver_license_pd_id_1'],
            200,
            {
                'uniques': [
                    {
                        'license_pd_id': 'driver_license_pd_id_1',
                        'unique_driver_ids': ['000000000000000000000001'],
                    },
                ],
            },
        ),
        (
            [
                'driver_license_pd_id_1',
                'driver_license_pd_id_non',
                'driver_license_pd_id_2',
            ],
            200,
            {
                'uniques': [
                    {
                        'license_pd_id': 'driver_license_pd_id_1',
                        'unique_driver_ids': ['000000000000000000000001'],
                    },
                    {'license_pd_id': 'driver_license_pd_id_non'},
                    {
                        'license_pd_id': 'driver_license_pd_id_2',
                        'unique_driver_ids': ['000000000000000000000002'],
                    },
                ],
            },
        ),
        (
            ['driver_license_pd_id_3'],  # test deletions
            200,
            {'uniques': [{'license_pd_id': 'driver_license_pd_id_3'}]},
        ),
        ([], 200, {'uniques': []}),
    ],
)
@pytest.mark.now('2019-03-10T00:00:00')
@pytest.mark.config(TVM_ENABLED=False)
async def test_uniques_retrieve_by_profiles(
        taxi_unique_drivers,
        mockserver,
        license_pd_ids,
        expected_code,
        expected_response,
):
    response = await taxi_unique_drivers.post(
        'v1/driver/uniques/retrieve_by_license_pd_ids',
        params={'consumer': 'service'},
        json={'id_in_set': license_pd_ids},
    )

    assert response.status_code == expected_code
    assert 'application/json' in response.headers['Content-Type']
    assert response.json() == expected_response
