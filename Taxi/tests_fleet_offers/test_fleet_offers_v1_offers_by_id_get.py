import pytest

from tests_fleet_offers import utils

ENDPOINT = '/fleet/offers/v1/offers/by-id'


def build_params(offer_id):
    return {'id': offer_id}


OK_PARAMS = [
    (
        'park1',
        '00000000-0000-0000-0000-000000000001',
        {
            'signers_count': 1,
            'created_at': '2019-12-31T21:00:00+00:00',
            'id': '00000000-0000-0000-0000-000000000001',
            'is_enabled': True,
            'kind': 'offer',
            'name': 'offer1',
            'rev': 0,
            'section': 'Баланс',
        },
    ),
    (
        'park1',
        '00000000-0000-0000-0000-000000000002',
        {
            'signers_count': 1,
            'created_at': '2019-12-31T21:00:00+00:00',
            'id': '00000000-0000-0000-0000-000000000002',
            'is_enabled': True,
            'kind': 'custom',
            'name': 'offer2',
            'rev': 2,
            'section': 'Главный экран',
        },
    ),
]


@pytest.mark.parametrize('park_id, offer_id, expected_response', OK_PARAMS)
async def test_ok(taxi_fleet_offers, park_id, offer_id, expected_response):
    response = await taxi_fleet_offers.get(
        ENDPOINT,
        headers=utils.build_fleet_headers(park_id=park_id),
        params=build_params(offer_id=offer_id),
    )

    assert response.status_code == 200, response.text
    assert response.json() == expected_response


async def test_not_found(taxi_fleet_offers):
    response = await taxi_fleet_offers.get(
        ENDPOINT,
        headers=utils.build_fleet_headers(park_id='park1'),
        params=build_params(offer_id='00000000-0000-0000-0000-100000000001'),
    )

    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'offer_not_found',
        'localized_message': 'Оферта не найдена',
    }
