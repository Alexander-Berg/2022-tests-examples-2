import pytest

from tests_cashbox_integration import utils


ENDPOINT = '/driver/cashbox/v1/parks/cashboxes/current'
PARK_ID = 'park_123'
ALL_CASHBOXES = ['id_abc123', 'id_abc456', 'id_abc789']

AUTHORIZED_HEADERS = {
    'Accept-Language': 'en-EN',
    'X-YaTaxi-Park-Id': PARK_ID,
    'X-YaTaxi-Driver-Profile-Id': 'driverSS',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.07 (1234)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'User-Agent': 'Taximeter 9.07 (1234)',
}


def get_ordered_cashboxes(pgsql):
    return utils.get_cashboxes_by_id(pgsql, PARK_ID, ALL_CASHBOXES)


async def test_change_ok(taxi_cashbox_integration, pgsql, fleet_parks):
    rows_before = get_ordered_cashboxes(pgsql)

    response = await taxi_cashbox_integration.put(
        ENDPOINT, json={'cashbox_id': 'id_abc123'}, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'park_id': PARK_ID, 'cashbox_id': 'id_abc123'}

    rows_after = get_ordered_cashboxes(pgsql)
    assert rows_before[0].pop('date_updated') != rows_after[0].pop(
        'date_updated',
    )
    assert rows_before[1].pop('date_updated') != rows_after[1].pop(
        'date_updated',
    )
    rows_before[0]['is_current'] = True
    rows_before[1]['is_current'] = False
    assert rows_before == rows_after


async def test_nothing_changes_ok(
        taxi_cashbox_integration, pgsql, fleet_parks,
):
    rows_before = get_ordered_cashboxes(pgsql)

    response = await taxi_cashbox_integration.put(
        ENDPOINT, json={'cashbox_id': 'id_abc456'}, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'park_id': PARK_ID, 'cashbox_id': 'id_abc456'}

    rows_after = get_ordered_cashboxes(pgsql)
    assert rows_before[1].pop('date_updated') != rows_after[1].pop(
        'date_updated',
    )
    assert rows_before == rows_after


@pytest.mark.parametrize(
    'park_id, cashbox_id',
    [
        (PARK_ID, 'id_abc789'),
        (PARK_ID, 'id_net_takogo_voobsche'),
        ('park_net_takogo', 'id_abc123'),
    ],
)
async def test_no_such_cashbox(
        taxi_cashbox_integration, pgsql, park_id, cashbox_id, fleet_parks,
):
    rows_before = get_ordered_cashboxes(pgsql)

    authorized_headers = AUTHORIZED_HEADERS.copy()
    authorized_headers['X-YaTaxi-Park-Id'] = park_id

    response = await taxi_cashbox_integration.put(
        ENDPOINT, json={'cashbox_id': cashbox_id}, headers=authorized_headers,
    )
    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'no_such_cashbox',
        'message': 'no_such_cashbox',
    }

    rows_after = get_ordered_cashboxes(pgsql)
    assert rows_before == rows_after


async def test_remove_ok(taxi_cashbox_integration, pgsql, fleet_parks):
    rows_before = get_ordered_cashboxes(pgsql)

    response = await taxi_cashbox_integration.put(
        ENDPOINT, json={}, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'park_id': PARK_ID}

    rows_after = get_ordered_cashboxes(pgsql)
    assert rows_before[1].pop('date_updated') != rows_after[1].pop(
        'date_updated',
    )
    rows_before[1]['is_current'] = False
    assert rows_before == rows_after


@pytest.mark.parametrize('park_id', ['park_wo_current', 'park_net_takogo'])
async def test_remove_nothing_changes(
        taxi_cashbox_integration, pgsql, park_id, fleet_parks,
):
    rows_before = get_ordered_cashboxes(pgsql)

    authorized_headers = AUTHORIZED_HEADERS.copy()
    authorized_headers['X-YaTaxi-Park-Id'] = park_id

    response = await taxi_cashbox_integration.put(
        ENDPOINT, json={}, headers=authorized_headers,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'park_id': park_id}

    rows_after = get_ordered_cashboxes(pgsql)
    assert rows_before == rows_after


async def test_not_self_assigned(taxi_cashbox_integration, fleet_parks, pgsql):
    authorized_headers = AUTHORIZED_HEADERS
    authorized_headers['X-YaTaxi-Park-Id'] = 'big_park'

    response = await taxi_cashbox_integration.put(
        ENDPOINT, json={}, headers=authorized_headers,
    )

    assert response.status_code == 400, response.text
    assert response.json()['code'] == 'not_self_assigned'
