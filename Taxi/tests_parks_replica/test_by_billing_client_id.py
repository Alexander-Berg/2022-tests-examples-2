import operator

import pytest


@pytest.mark.parametrize(
    'input_data,expected_data',
    [
        # case 1
        (
            {
                'billing_client_ids': ['billing_client_id_1'],
                'at': '2020-02-13T05:00:00.000+0000',
            },
            {'parks': []},
        ),
        # case 2
        (
            {
                'billing_client_ids': ['billing_client_id_1'],
                'at': '2020-02-13T06:20:00.000+0000',
            },
            {
                'parks': [
                    {
                        'park_id': 'park_id_1',
                        'billing_client_id': 'billing_client_id_1',
                    },
                ],
            },
        ),
        # case 3
        (
            {
                'billing_client_ids': ['billing_client_id_1'],
                'at': '2020-02-13T06:30:00.000+0000',
            },
            {
                'parks': [
                    {
                        'park_id': 'park_id_1',
                        'billing_client_id': 'billing_client_id_1',
                    },
                    {
                        'park_id': 'park_id_2',
                        'billing_client_id': 'billing_client_id_1',
                    },
                ],
            },
        ),
        # case 4
        (
            {
                'billing_client_ids': ['billing_client_id_1'],
                'at': '2020-02-13T07:00:00.000+0000',
            },
            {
                'parks': [
                    {
                        'park_id': 'park_id_2',
                        'billing_client_id': 'billing_client_id_1',
                    },
                ],
            },
        ),
        # case 5
        (
            {
                'billing_client_ids': ['billing_client_id_3'],
                'at': '2020-02-13T09:00:00.000+0000',
            },
            {
                'parks': [
                    {
                        'park_id': 'park_id_1',
                        'billing_client_id': 'billing_client_id_3',
                    },
                ],
            },
        ),
        # case 6
        (
            {
                'billing_client_ids': [
                    'billing_client_id_3',
                    'billing_client_id_4',
                ],
                'at': '2020-02-13T09:00:00.000+0000',
            },
            {
                'parks': [
                    {
                        'park_id': 'park_id_1',
                        'billing_client_id': 'billing_client_id_3',
                    },
                    {
                        'park_id': 'park_id_2',
                        'billing_client_id': 'billing_client_id_4',
                    },
                ],
            },
        ),
    ],
)
async def test_by_billing_client_id(
        taxi_parks_replica, input_data, expected_data,
):
    response = await taxi_parks_replica.post(
        'v1/parks/by_billing_client_id/retrieve_bulk', json=input_data,
    )
    assert response.status_code == 200
    assert sorted(
        response.json()['parks'], key=operator.itemgetter('park_id'),
    ) == sorted(expected_data['parks'], key=operator.itemgetter('park_id'))
