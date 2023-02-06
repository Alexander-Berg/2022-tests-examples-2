import pytest

ENDPOINT = '/internal/v1/fleet-offers/v1/offers/by-kind'


def build_params(park_id, driver_id, kind):
    return {'park_id': park_id, 'driver_id': driver_id, 'kind': kind}


OK_PARAMS = [
    (
        'park1',
        'driver1',
        'offer',
        {
            'id': '00000000-0000-0000-0000-000000000001',
            'kind': 'offer',
            'name': 'offer1',
            'number': 1,
            'rev': 0,
            'signed_at': '2019-12-31T21:00:00+00:00',
        },
    ),
    (
        'park1',
        'driver1',
        'rent',
        {
            'id': '00000000-0000-0000-0000-000000000002',
            'kind': 'rent',
            'name': 'rent1',
            'number': 2,
            'rev': 0,
            'signed_at': '2019-12-31T21:00:00+00:00',
        },
    ),
]


@pytest.mark.parametrize(
    'park_id, driver_id, kind, expected_response', OK_PARAMS,
)
async def test_ok(
        taxi_fleet_offers, park_id, driver_id, kind, expected_response,
):
    response = await taxi_fleet_offers.get(
        ENDPOINT,
        params=build_params(park_id=park_id, driver_id=driver_id, kind=kind),
    )

    assert response.status_code == 200, response.text
    assert response.json() == expected_response


async def test_not_found(taxi_fleet_offers):
    response = await taxi_fleet_offers.get(
        ENDPOINT,
        params=build_params(
            park_id='park1', driver_id='driver1', kind='labor_contract',
        ),
    )

    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'offer_not_found',
        'message': 'Offer not found',
    }
