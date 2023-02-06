import dateutil
import pytest


def build_headers(park_id):
    headers = {
        'X-Ya-User-Ticket': 'user_ticket',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
    }
    return headers


@pytest.mark.pgsql('fleet_orders', files=['notes.sql'])
async def test_get(taxi_fleet_orders):
    response = await taxi_fleet_orders.get(
        '/fleet/fleet-orders/v1/note',
        headers=build_headers(park_id='PARK-01'),
        params={'order_id': 'ORDER-01'},
    )
    assert response.status_code == 200
    assert response.json() == {'note': 'TEXT'}


@pytest.mark.pgsql('fleet_orders', files=['notes.sql'])
async def test_get_empty(taxi_fleet_orders):
    response = await taxi_fleet_orders.get(
        '/fleet/fleet-orders/v1/note',
        headers=build_headers(park_id='PARK-01'),
        params={'order_id': 'ORDER-02'},
    )
    assert response.status_code == 200
    assert response.json() == {'note': ''}


@pytest.mark.now('2022-01-02T12:00:00+00:00')
@pytest.mark.pgsql('fleet_orders', files=['notes.sql'])
async def test_put(taxi_fleet_orders, pgsql):
    response = await taxi_fleet_orders.put(
        '/fleet/fleet-orders/v1/note',
        headers=build_headers(park_id='PARK-01'),
        params={'order_id': 'ORDER-01'},
        json={'note': 'TEXT_NEW'},
    )
    assert response.status_code == 204

    cursor = pgsql['fleet_orders'].cursor()

    cursor.execute(
        f"""
        SELECT * FROM fleet.order_notes
        """,
    )

    pg_result = cursor.fetchall()
    assert pg_result == [
        (
            'PARK-01',
            'ORDER-01',
            'TEXT_NEW',
            dateutil.parser.parse('2022-01-02T12:00:00+00:00'),
            '1',
        ),
    ]
