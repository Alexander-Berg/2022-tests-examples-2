import pytest

from tests_fleet_offers import utils

ENDPOINT = '/fleet/offers/v1/offers/by-id/status'


def build_params(offer_id):
    return {'id': offer_id}


def build_payload(is_enabled):
    return {'is_enabled': is_enabled}


OK_PARAMS = [
    ('00000000-0000-0000-0000-000000000001', True),
    ('00000000-0000-0000-0000-000000000001', False),
]


@pytest.mark.parametrize('offer_id, is_enabled', OK_PARAMS)
async def test_create(taxi_fleet_offers, pgsql, offer_id, is_enabled):
    response = await taxi_fleet_offers.post(
        ENDPOINT,
        headers=utils.build_fleet_headers(park_id='park1'),
        params=build_params(offer_id=offer_id),
        json=build_payload(is_enabled=is_enabled),
    )

    assert response.status_code == 204, response.text

    cursor = pgsql['fleet_offers'].cursor()
    cursor.execute(
        f"""
        SELECT
            is_enabled
        FROM
            fleet_offers.active_offers
        WHERE
            park_id = \'park1\'
            AND id = \'{offer_id}\'
        """,
    )
    row = cursor.fetchone()
    assert row[0] == is_enabled


async def test_not_found(taxi_fleet_offers):
    response = await taxi_fleet_offers.post(
        ENDPOINT,
        headers=utils.build_fleet_headers(park_id='park1'),
        params=build_params(offer_id='00000000-0000-0000-0000-100000000001'),
        json=build_payload(is_enabled=False),
    )

    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'offer_not_found',
        'localized_message': 'Оферта не найдена',
    }
