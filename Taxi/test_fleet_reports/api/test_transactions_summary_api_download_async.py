import aiohttp.web
import pytest

URL = '/reports-api/v1/transactions-summary-api/download-async'

QUERY = {'operation_id': '6c5c10956c2bbe505bb8c42201efe5ef'}


@pytest.mark.config(
    FLEET_TRANSACTIONS_API_BALANCES_SELECT_RESTRICTIONS={
        'chunk_size': 12,
        'concurrency': 2,
        'truncated_to_hours_offset': 168,
    },
)
async def test_success(
        web_app_client,
        mock_parks,
        headers,
        mock_fleet_reports_storage,
        load_json,
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
            'accrued_at': {
                'from': '2019-09-08T11:00:00+00:00',
                'to': '2019-09-09T11:00:00+00:00',
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
    ['json', 'code', 'message'],
    [
        (
            {
                'accrued_at': {
                    'from': '2019-09-10T11:16:11+00:00',
                    'to': '2019-09-09T11:16:11+00:00',
                },
            },
            'DATES_ERROR',
            'accrued_at.from >= accrued_at.to',
        ),
        (
            {
                'accrued_at': {
                    'from': '2019-09-10T11:16:11+00:00',
                    'to': '2019-09-12T11:16:11+00:00',
                },
            },
            'BAD_REQUEST',
            'date 2019-09-10 11:16:11 must be truncated to hours',
        ),
    ],
)
async def test_bad_request(
        web_app_client, headers, load_json, json, code, message,
):
    response = await web_app_client.post(
        URL, headers=headers, params=QUERY, json=json,
    )

    assert response.status == 400
    response_data = await response.json()
    assert response_data == {'code': code, 'message': message}
