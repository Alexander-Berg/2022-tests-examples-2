import pytest

PARK_ID = 'PARK-ID-01'
PARK_ID_03 = 'PARK-ID-03'
PARK_ID_INACTIVE = 'PARK-ID-INACTIVE'
AUTH_HEADERS = {
    'X-Park-Id': PARK_ID,
    'X-Yandex-UID': '999',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Ya-User-Ticket': 'TESTSUITE-USER-TICKET',
    'X-Idempotency-Token': 'TOKEN_01',
}


def _make_headers(park_id, **kwargs):
    return {**AUTH_HEADERS, 'X-Park-Id': park_id}


@pytest.mark.now('2021-12-31T12:00:00.000000+03:00')
async def test_fines_change_park_activity(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.put(
        'fleet/traffic-fines/v1/activity',
        headers=_make_headers(PARK_ID_03),
        json={'is_active': False},
    )
    assert response.status_code == 204, response.text

    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/fines/retrieve',
        headers=_make_headers(PARK_ID_03),
        json={'query': {}},
    )
    assert response.status_code == 400, response.text

    response = await taxi_fleet_traffic_fines.put(
        'fleet/traffic-fines/v1/activity',
        headers=_make_headers(PARK_ID_03),
        json={'is_active': True},
    )
    assert response.status_code == 204, response.text

    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/fines/retrieve',
        headers=_make_headers(PARK_ID_03),
        json={'query': {}},
    )
    fines = load_json('fines.json')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'fines': [fines['FINE_04'], fines['FINE_03']],
        'total': {'count': 2, 'sum': '3500'},
    }


@pytest.mark.parametrize(
    'header,status',
    [
        (AUTH_HEADERS, True),
        (_make_headers(PARK_ID_03), True),
        (_make_headers(PARK_ID_INACTIVE), False),
    ],
)
async def test_fines_get_park_activity(
        taxi_fleet_traffic_fines, load_json, mock_api, header, status,
):
    response = await taxi_fleet_traffic_fines.get(
        'fleet/traffic-fines/v1/activity', headers=header,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'status': status}
