import aiohttp.web

URL = '/api/v1/reports/transactions/park/download-async'

HEADERS = {
    'Accept-Language': 'ru',
    'X-Yandex-Login': 'abacaba',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-UID': '123',
    'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
    'X-Real-IP': '127.0.0.1',
    'X-YaTaxi-Fleet-Permissions': 'permission',
}

QUERY = {'operation_id': '6c5c10956c2bbe505bb8c42201efe5ef'}


async def test_success(
        web_app_client,
        headers,
        mock_fleet_reports_storage,
        mock_fleet_transactions_api,
        load_json,
):
    stub = load_json('success.json')

    @mock_fleet_reports_storage('/internal/user/v1/operations/create')
    async def _create(request):
        assert request.json == stub['fleet_reports_storage']['request']
        return aiohttp.web.json_response(data={})

    @mock_fleet_transactions_api(
        '/v1/parks/transactions/categories/list/by-user',
    )
    async def _list_transaction_categories(request):
        return aiohttp.web.json_response(
            data={
                'categories': [
                    {
                        'group_id': 'ride_fee',
                        'group_name': 'group_name',
                        'id': 'fleet_ride_fee',
                        'is_affecting_driver_balance': False,
                        'is_creatable': True,
                        'is_editable': False,
                        'is_enabled': True,
                        'name': 'fleet ride fee',
                    },
                    {
                        'group_id': 'ride_fee',
                        'group_name': 'group_name',
                        'id': 'platform_ride_fee',
                        'is_affecting_driver_balance': False,
                        'is_creatable': True,
                        'is_editable': False,
                        'is_enabled': True,
                        'name': 'platform ride fee',
                    },
                ],
            },
        )

    response = await web_app_client.post(
        URL,
        headers=headers,
        params=QUERY,
        json={
            'query': {
                'park': {
                    'transaction': {
                        'event_at': {
                            'from': '2019-09-08T11:16:11+00:00',
                            'to': '2019-09-09T11:16:11+00:00',
                        },
                        'category_ids': [
                            'fleet_ride_fee',
                            'platform_ride_fee',
                        ],
                    },
                },
            },
        },
    )

    assert response.status == 200


async def test_success400(
        web_app_client, headers, load_json, mock_fleet_reports_storage,
):
    stub = load_json('success.json')

    @mock_fleet_reports_storage('/internal/user/v1/operations/create')
    async def _create(request):
        assert request.json == stub['fleet_reports_storage']['request']
        return aiohttp.web.json_response(data={})

    response = await web_app_client.post(
        URL,
        headers=headers,
        params=QUERY,
        json={
            'query': {
                'park': {
                    'driver_profile': {
                        'id': '769ce26febec46b0a16eee7a560d7eda',
                    },
                    'transaction': {
                        'event_at': {
                            'from': '2019-09-08T11:16:11+00:00',
                            'to': '2019-09-08T11:16:11+00:00',
                        },
                        'category_ids': [
                            'fleet_ride_fee',
                            'platform_ride_fee',
                        ],
                    },
                },
            },
        },
    )

    assert response.status == 400
    response_data = await response.json()
    assert response_data == {
        'code': 'DATES_IS_SAME',
        'message': 'event.from = event.to',
    }


async def test_success400_bad_category(
        web_app_client, headers, load_json, mock_fleet_transactions_api,
):
    @mock_fleet_transactions_api(
        '/v1/parks/transactions/categories/list/by-user',
    )
    async def _list_transaction_categories(request):
        return aiohttp.web.json_response(
            data={
                'categories': [
                    {
                        'group_id': 'ride_fee',
                        'group_name': 'group_name',
                        'id': 'fleet_ride_fee',
                        'is_affecting_driver_balance': False,
                        'is_creatable': True,
                        'is_editable': False,
                        'is_enabled': True,
                        'name': 'fleet ride fee',
                    },
                ],
            },
        )

    response = await web_app_client.post(
        URL,
        headers=headers,
        params=QUERY,
        json={
            'query': {
                'park': {
                    'driver_profile': {
                        'id': '769ce26febec46b0a16eee7a560d7eda',
                    },
                    'transaction': {
                        'event_at': {
                            'from': '2019-09-08T11:16:11+00:00',
                            'to': '2019-09-09T11:16:11+00:00',
                        },
                        'category_ids': [
                            'fleet_ride_fee',
                            'platform_ride_fee',
                        ],
                    },
                },
            },
        },
    )

    assert response.status == 400
    response_data = await response.json()
    assert response_data == {
        'code': 'INVALID_CATEGORY_IDS',
        'message': 'invalid category ids `platform_ride_fee`',
    }
