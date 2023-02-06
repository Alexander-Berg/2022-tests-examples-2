import aiohttp.web

URL = '/api/v1/regular-charges/check-active/by-driver'

HEADERS = {
    'Accept-Language': 'ru',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
    'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
    'X-Real-IP': '127.0.0.1',
}


async def test_success_has_active(
        web_app_client, headers, mock_fleet_rent_py3,
):
    @mock_fleet_rent_py3('/v1/park/rents/list')
    async def _v1_park_rents_list(request):
        assert request.json == {
            'driver_id': '70f36bc91ff24ec6b7b3040b2633d09b',
            'limit': 1,
            'offset': 0,
            'states': ['will_begin', 'active'],
        }
        return aiohttp.web.json_response(
            {
                'rent_records': [
                    {
                        'acceptance_reason': (
                            'Internal rent - needs no approval'
                        ),
                        'accepted_at': '2020-03-17T01:00:48.808942+03:00',
                        'asset': {
                            'car_id': '0caab226f7874c51937e5b1d76b6fee3',
                            'type': 'car',
                        },
                        'begins_at': '2020-03-16T22:00:09+03:00',
                        'charging': {
                            'daily_price': '47.0',
                            'periodicity': {
                                'monthdays': [31],
                                'type': 'monthdays',
                            },
                            'type': 'daily',
                        },
                        'charging_starts_at': '2020-03-06T22:00:17+03:00',
                        'comment': 'фцы',
                        'created_at': '2020-03-17T01:00:48.808942+03:00',
                        'creator_uid': '4006292576',
                        'driver_id': '70f36bc91ff24ec6b7b3040b2633d09b',
                        'driver_park_id': '7ad36bc7560449998acbe2c57a75c293',
                        'owner_park_id': '7ad36bc7560449998acbe2c57a75c293',
                        'owner_serial_id': 11,
                        'record_id': 'd33652f4b84b49e5a83f52b883bd0929',
                        'state': 'active',
                    },
                ],
            },
        )

    response = await web_app_client.get(
        URL,
        headers=HEADERS,
        params={'driver_id': '70f36bc91ff24ec6b7b3040b2633d09b'},
    )

    assert response.status == 200
    assert await response.json() == {'has_active': True}


async def test_success_no_active(web_app_client, headers, mock_fleet_rent_py3):
    @mock_fleet_rent_py3('/v1/park/rents/list')
    async def _v1_park_rents_list(request):
        assert request.json == {
            'driver_id': '70f36bc91ff24ec6b7b3040b2633d09b',
            'limit': 1,
            'offset': 0,
            'states': ['will_begin', 'active'],
        }
        return aiohttp.web.json_response({'rent_records': []})

    response = await web_app_client.get(
        URL,
        headers=HEADERS,
        params={'driver_id': '70f36bc91ff24ec6b7b3040b2633d09b'},
    )

    assert response.status == 200
    assert await response.json() == {'has_active': False}
