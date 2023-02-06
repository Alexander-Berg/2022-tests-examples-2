import pytest


@pytest.mark.parametrize(
    'query_parameters, status_code, response_json',
    [
        (
            {
                'consumer': 'test',
                'last_known_revision_unique_drivers': '11111_2',
                'last_known_revision_driver_profiles': '1546300750_2',
            },
            200,
            {
                'licenses_by_unique_drivers': {
                    'last_revision': '11112_2',
                    'items': [
                        {
                            'id': '000000000000000000000003',
                            'is_deleted': True,
                            'revision': '11111_3',
                            'data': {
                                'license_ids': ['driver_license_pd_id_3'],
                            },
                        },
                        {
                            'id': '000000000000000000000005',
                            'revision': '11112_1',
                            'data': {
                                'license_ids': ['driver_license_pd_id_5'],
                            },
                        },
                        {
                            'id': '000000000000000000000004',
                            'revision': '11112_2',
                            'data': {
                                'license_ids': ['driver_license_pd_id_4'],
                            },
                        },
                    ],
                },
                'license_by_driver_profile': {
                    'last_revision': '1546300750_3',
                    'items': [
                        {
                            'id': 'park2_driver3',
                            'revision': '1546300750_3',
                            'data': {'license_id': 'driver_license_pd_id_3'},
                        },
                    ],
                },
            },
        ),
        (
            {'consumer': 'test'},
            200,
            {
                'licenses_by_unique_drivers': {
                    'last_revision': '11112_2',
                    'items': [
                        {
                            'id': '000000000000000000000001',
                            'revision': '11111_1',
                            'data': {
                                'license_ids': ['driver_license_pd_id_1'],
                            },
                        },
                        {
                            'id': '000000000000000000000002',
                            'revision': '11111_2',
                            'data': {
                                'license_ids': ['driver_license_pd_id_2'],
                            },
                        },
                        {
                            'id': '000000000000000000000003',
                            'is_deleted': True,
                            'revision': '11111_3',
                            'data': {
                                'license_ids': ['driver_license_pd_id_3'],
                            },
                        },
                        {
                            'id': '000000000000000000000005',
                            'revision': '11112_1',
                            'data': {
                                'license_ids': ['driver_license_pd_id_5'],
                            },
                        },
                        {
                            'id': '000000000000000000000004',
                            'revision': '11112_2',
                            'data': {
                                'license_ids': ['driver_license_pd_id_4'],
                            },
                        },
                    ],
                },
                'license_by_driver_profile': {
                    'last_revision': '1546300750_3',
                    'items': [
                        {
                            'id': 'park1_driver1',
                            'revision': '1546300750_1',
                            'data': {'license_id': 'driver_license_pd_id_1'},
                        },
                        {
                            'id': 'park2_driver2',
                            'revision': '1546300750_2',
                            'data': {'license_id': 'driver_license_pd_id_2'},
                        },
                        {
                            'id': 'park2_driver3',
                            'revision': '1546300750_3',
                            'data': {'license_id': 'driver_license_pd_id_3'},
                        },
                    ],
                },
            },
        ),
        (
            {
                'consumer': 'test',
                'last_known_revision_unique_drivers': '11115_2',
                'last_known_revision_driver_profiles': '1546300759_2',
            },
            200,
            {
                'licenses_by_unique_drivers': {
                    'last_revision': '11115_2',
                    'items': [],
                },
                'license_by_driver_profile': {
                    'last_revision': '1546300759_2',
                    'items': [],
                },
            },
        ),
        ({}, 400, {'code': '400', 'message': 'Missing consumer in query'}),
    ],
)
async def test_bindings_updates(
        query_parameters, status_code, response_json, taxi_unique_drivers,
):
    response = await taxi_unique_drivers.post(
        'v1/bindings/updates', params=query_parameters,
    )
    assert response.status_code == status_code
    assert response.json() == response_json
