import pytest


@pytest.mark.pgsql(
    'contractors_transport', files=['contractors_transport.sql'],
)
@pytest.mark.parametrize(
    'params, response_json',
    [
        (
            {
                'id_in_set': [
                    'park1_driver1',
                    'park4_driver4',
                    'park4_driver5',
                    'park3_driver2',
                    'park3_driver3',
                    'park5_driver5',
                ],
            },
            'all_contractors.json',
        ),
    ],
)
async def test_transport_updates(
        taxi_contractor_transport, params, response_json, load_json,
):
    response = await taxi_contractor_transport.post(
        'v1/transport-active/retrieve-by-contractor-id', json=params,
    )
    assert response.status_code == 200
    assert response.json() == load_json(response_json)
