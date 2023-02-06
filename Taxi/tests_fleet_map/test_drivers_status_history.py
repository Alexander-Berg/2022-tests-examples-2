import pytest

ENDPOINT = '/fleet/map/v1/drivers/status-history'

HEADERS = {
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
    'X-Park-Id': 'park_id',
}

CONTRACTOR_STATUS_HISTORY_REQUEST = {
    'interval': {'from': 1638452066, 'to': 1638538466},
    'contractors': [{'park_id': 'park_id', 'profile_id': 'driver_id'}],
    'verbose': False,
}

CONTRACTOR_STATUS_HISTORY_RESPONSE = {
    'contractors': [
        {
            'park_id': 'park_id',
            'profile_id': 'driver_id',
            'events': [
                {
                    'timestamp': 1638452455,
                    'status': 'online',
                    'on_order': True,
                },
                {'timestamp': 1638453275, 'status': 'busy'},
                {'timestamp': 1638453280, 'status': 'busy', 'on_order': True},
                {
                    'timestamp': 1638453558,
                    'status': 'online',
                    'on_order': True,
                },
                {'timestamp': 1638457197, 'status': 'online'},
                {
                    'timestamp': 1638457308,
                    'status': 'online',
                    'on_order': True,
                },
                {'timestamp': 1638458861, 'status': 'online'},
                {
                    'timestamp': 1638458935,
                    'status': 'online',
                    'on_order': True,
                },
                {'timestamp': 1638460539, 'status': 'online'},
                {
                    'timestamp': 1638460657,
                    'status': 'online',
                    'on_order': True,
                },
                {'timestamp': 1638461329, 'status': 'online'},
                {
                    'timestamp': 1638461340,
                    'status': 'online',
                    'on_order': True,
                },
                {'timestamp': 1638461388, 'status': 'online'},
            ],
        },
    ],
}


SERVICE_REQUEST = {'driver_id': 'driver_id'}

SERVICE_RESPONSE = {
    'items': [
        {'status': 'free', 'date': '2021-12-02T16:09:48+00:00'},
        {'status': 'in_order', 'date': '2021-12-02T16:09:00+00:00'},
        {'status': 'free', 'date': '2021-12-02T16:08:49+00:00'},
        {'status': 'in_order', 'date': '2021-12-02T15:57:37+00:00'},
        {'status': 'free', 'date': '2021-12-02T15:55:39+00:00'},
        {'status': 'in_order', 'date': '2021-12-02T15:28:55+00:00'},
        {'status': 'free', 'date': '2021-12-02T15:27:41+00:00'},
        {'status': 'in_order', 'date': '2021-12-02T15:01:48+00:00'},
        {'status': 'free', 'date': '2021-12-02T14:59:57+00:00'},
        {'status': 'in_order', 'date': '2021-12-02T13:59:18+00:00'},
        {'status': 'in_order', 'date': '2021-12-02T13:54:40+00:00'},
        {'status': 'busy', 'date': '2021-12-02T13:54:35+00:00'},
        {'status': 'in_order', 'date': '2021-12-02T13:40:55+00:00'},
    ],
}


@pytest.mark.now('2021-12-03T13:34:26+00:00')
async def test_default(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/contractor-status-history/events')
    def _events(request):
        assert request.json == CONTRACTOR_STATUS_HISTORY_REQUEST
        return CONTRACTOR_STATUS_HISTORY_RESPONSE

    response = await taxi_fleet_map.get(
        ENDPOINT, headers=HEADERS, params=SERVICE_REQUEST,
    )

    assert response.status_code == 200
    assert response.json() == SERVICE_RESPONSE


@pytest.mark.now('2021-12-03T13:34:26+00:00')
async def test_empty(taxi_fleet_map, mockserver):
    @mockserver.json_handler('/contractor-status-history/events')
    def _events(request):
        assert request.json == CONTRACTOR_STATUS_HISTORY_REQUEST
        return {'contractors': []}

    response = await taxi_fleet_map.get(
        ENDPOINT, headers=HEADERS, params=SERVICE_REQUEST,
    )

    assert response.status_code == 200
    assert response.json() == {'items': []}
