import aiohttp.web


async def test_success_car(
        web_app_client,
        headers,
        load_json,
        mockserver,
        mock_fleet_rent_py3,
        mock_api7,
):
    service_stub = load_json('service_success.json')
    fleet_rent_stub = load_json('fleet_rent_success.json')
    parks_drivers_stub = load_json('parks_drivers_success.json')
    api7_cars_stub = load_json('api7_cars_success.json')

    @mock_fleet_rent_py3('/v1/park/rents/')
    async def _v1_park_rents_post(request):
        assert request.json == fleet_rent_stub['request']
        assert 'X-Idempotency-Token' in request.headers
        return aiohttp.web.json_response(fleet_rent_stub['response'])

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_parks_driver_profiles_list(request):
        assert request.json == parks_drivers_stub['request']
        return aiohttp.web.json_response(parks_drivers_stub['response'])

    @mock_api7('/v1/parks/cars/list')
    async def _v1_parks_cars_list(request):
        assert request.json == api7_cars_stub['request']
        return aiohttp.web.json_response(api7_cars_stub['response'])

    response = await web_app_client.post(
        '/api/v1/regular-charges/create',
        headers={**headers, 'X-Idempotency-Token': 'a1-b2-c3-d4'},
        json=service_stub['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == service_stub['response']


async def test_success_active_days(
        web_app_client,
        headers,
        load_json,
        mockserver,
        mock_fleet_rent_py3,
        mock_api7,
):
    parks_drivers_stub = load_json('parks_drivers_success.json')

    @mock_fleet_rent_py3('/v1/park/rents/')
    async def _v1_park_rents_post(request):
        assert request.json == {
            'asset': {
                'description': '',
                'subtype': 'deposit',
                'type': 'other',
            },
            'balance_notify_limit': '0.00',
            'begins_at': '2021-07-14T10:00:00+03:00',
            'charging': {
                'daily_price': '10.0',
                'type': 'active_days',
                'total_withhold_limit': '10.0',
            },
            'charging_starts_at': '2021-07-14T10:00:00+03:00',
            'driver_id': '70f36bc91ff24ec6b7b3040b2633d09b',
        }
        assert 'X-Idempotency-Token' in request.headers
        return aiohttp.web.json_response(
            {
                'acceptance_reason': 'Internal rent - needs no approval',
                'accepted_at': '2021-07-13T09:02:59.458594+03:00',
                'asset': {
                    'description': '',
                    'subtype': 'deposit',
                    'type': 'other',
                },
                'balance_notify_limit': '0.00',
                'begins_at': '2021-07-14T10:00:00+03:00',
                'charging': {
                    'daily_price': '10',
                    'type': 'active_days',
                    'total_withhold_limit': '10',
                },
                'charging_starts_at': '2021-07-14T10:00:00+03:00',
                'created_at': '2021-07-13T09:02:59.458594+03:00',
                'creator_uid': '4032161274',
                'driver_id': '70f36bc91ff24ec6b7b3040b2633d09b',
                'owner_park_id': '7ad36bc7560449998acbe2c57a75c293',
                'owner_serial_id': 479,
                'record_id': '7ceb2ca011204eb29f6105562fd1699d',
                'state': 'will_begin',
            },
        )

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_parks_driver_profiles_list(request):
        assert request.json == parks_drivers_stub['request']
        return aiohttp.web.json_response(parks_drivers_stub['response'])

    response = await web_app_client.post(
        '/api/v1/regular-charges/create',
        headers={**headers, 'X-Idempotency-Token': 'a1-b2-c3-d4'},
        json={
            'asset': {
                'description': '',
                'subtype': 'deposit',
                'type': 'other',
            },
            'balance_notify_limit': '0.00',
            'charging': {
                'daily_price': '10',
                'total_withhold_limit': '10',
                'type': 'active_days',
            },
            'charging_at': '2021-07-14T10:00:00+03:00',
            'driver_id': '70f36bc91ff24ec6b7b3040b2633d09b',
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == {
        'asset': {'description': '', 'subtype': 'deposit', 'type': 'other'},
        'balance_notify_limit': '0.00',
        'charging': {
            'daily_price': '10',
            'type': 'active_days',
            'total_withhold_limit': '10',
        },
        'charging_at': '2021-07-14T10:00:00+03:00',
        'date_from': '2021-07-14T10:00:00+03:00',
        'driver': {
            'balance': '-138000.0000',
            'first_name': 'Вазген1',
            'id': '70f36bc91ff24ec6b7b3040b2633d09b',
            'last_name': 'Одиннадцатый',
            'middle_name': 'Зурабович',
            'phone': '+79161748340',
            'status': 'offline',
            'work_status': 'working',
        },
        'id': '7ceb2ca011204eb29f6105562fd1699d',
        'serial_id': '479',
        'state': 'will_begin',
    }
