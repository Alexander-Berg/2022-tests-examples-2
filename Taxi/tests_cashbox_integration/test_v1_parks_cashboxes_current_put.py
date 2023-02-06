import pytest

from tests_cashbox_integration import utils


ENDPOINT = '/fleet/cashbox/v1/parks/cashboxes/current'
PARK_ID = 'park_123'
ALL_CASHBOXES = ['id_abc123', 'id_abc456', 'id_abc789']


def get_ordered_cashboxes(pgsql):
    return utils.get_cashboxes_by_id(pgsql, PARK_ID, ALL_CASHBOXES)


async def test_change_ok(taxi_cashbox_integration, pgsql):
    rows_before = get_ordered_cashboxes(pgsql)

    response = await taxi_cashbox_integration.put(
        ENDPOINT,
        params={'park_id': PARK_ID},
        json={'cashbox_id': 'id_abc123'},
        headers={'X-Ya-User-Ticket-Provider': 'yandex', 'X-Yandex-UID': '123'},
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


async def test_nothing_changes_ok(taxi_cashbox_integration, pgsql):
    rows_before = get_ordered_cashboxes(pgsql)

    response = await taxi_cashbox_integration.put(
        ENDPOINT,
        params={'park_id': PARK_ID},
        json={'cashbox_id': 'id_abc456'},
        headers={'X-Ya-User-Ticket-Provider': 'yandex', 'X-Yandex-UID': '123'},
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
        taxi_cashbox_integration, pgsql, park_id, cashbox_id,
):
    rows_before = get_ordered_cashboxes(pgsql)

    response = await taxi_cashbox_integration.put(
        ENDPOINT,
        params={'park_id': park_id},
        json={'cashbox_id': cashbox_id},
        headers={'X-Ya-User-Ticket-Provider': 'yandex', 'X-Yandex-UID': '123'},
    )
    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'no_such_cashbox',
        'message': 'no_such_cashbox',
    }

    rows_after = get_ordered_cashboxes(pgsql)
    assert rows_before == rows_after


async def test_remove_ok(taxi_cashbox_integration, pgsql):
    rows_before = get_ordered_cashboxes(pgsql)

    response = await taxi_cashbox_integration.put(
        ENDPOINT,
        params={'park_id': PARK_ID},
        json={},
        headers={'X-Ya-User-Ticket-Provider': 'yandex', 'X-Yandex-UID': '123'},
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
        taxi_cashbox_integration, pgsql, park_id,
):
    rows_before = get_ordered_cashboxes(pgsql)

    response = await taxi_cashbox_integration.put(
        ENDPOINT,
        params={'park_id': park_id},
        json={},
        headers={'X-Ya-User-Ticket-Provider': 'yandex', 'X-Yandex-UID': '123'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'park_id': park_id}

    rows_after = get_ordered_cashboxes(pgsql)
    assert rows_before == rows_after
