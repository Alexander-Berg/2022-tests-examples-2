import aiohttp.web
import pytest

URL = '/reports-api/v1/cards/driver/transactions/download-async'

HEADERS = {
    'Accept-Language': 'ru',
    'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293',
}

QUERY = {'operation_id': '6c5c10956c2bbe505bb8c42201efe5ef'}


@pytest.mark.config(
    FLEET_TRANSACTIONS_API_BALANCES_SELECT_RESTRICTIONS={
        'chunk_size': 12,
        'concurrency': 2,
        'truncated_to_hours_offset': 168,
    },
)
async def test_success(
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
                        'id': 'baw9fja3bran0l99fjac27tct2hjbfs1p',
                    },
                    'transaction': {
                        'event_at': {
                            'from': '2022-01-21T00:00:00+00:00',
                            'to': '2022-01-28T23:00:00+00:00',
                        },
                    },
                },
            },
        },
    )

    assert response.status == 200


@pytest.mark.config(
    FLEET_TRANSACTIONS_API_BALANCES_SELECT_RESTRICTIONS={
        'chunk_size': 12,
        'concurrency': 2,
        'truncated_to_hours_offset': 168,
    },
)
@pytest.mark.parametrize(
    ['event_at', 'response_json'],
    [
        (
            {
                'from': '2022-03-21T00:00:00+00:00',
                'to': '2022-01-28T23:00:00+00:00',
            },
            {'code': 'DATES_IS_SAME', 'message': 'event.from = event.to'},
        ),
        (
            {
                'from': '2019-03-21T12:22:00+00:00',
                'to': '2019-07-28T23:00:00+00:00',
            },
            {
                'code': 'BAD_REQUEST',
                'message': (
                    'date 2019-03-21 12:22:00 must be truncated to hours'
                ),
            },
        ),
    ],
)
async def test_error400(
        web_app_client,
        headers,
        load_json,
        mock_fleet_reports_storage,
        event_at,
        response_json,
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
                        'id': 'baw9fja3bran0l99fjac27tct2hjbfs1p',
                    },
                    'transaction': {'event_at': event_at},
                },
            },
        },
    )

    assert response.status == 400
    assert await response.json() == response_json


@pytest.mark.config(
    FLEET_TRANSACTIONS_API_BALANCES_SELECT_RESTRICTIONS={
        'chunk_size': 12,
        'concurrency': 2,
        'truncated_to_hours_offset': 168,
    },
)
async def test_error429(
        web_app_client, headers, load_json, mock_fleet_reports_storage,
):
    stub = load_json('success.json')

    @mock_fleet_reports_storage('/internal/user/v1/operations/create')
    async def _create(request):
        assert request.json == stub['fleet_reports_storage']['request']
        return aiohttp.web.json_response(
            status=429, data={'code': 'NO_QUOTA', 'message': 'no quota'},
        )

    response = await web_app_client.post(
        URL,
        headers=headers,
        params=QUERY,
        json={
            'query': {
                'park': {
                    'driver_profile': {
                        'id': 'baw9fja3bran0l99fjac27tct2hjbfs1p',
                    },
                    'transaction': {
                        'event_at': {
                            'from': '2022-01-21T00:00:00+00:00',
                            'to': '2022-01-28T23:00:00+00:00',
                        },
                    },
                },
            },
        },
    )

    assert response.status == 429
