from aiohttp import web
import pytest


@pytest.mark.parametrize(
    'data_path',
    [
        'payments_empty.json',
        'payments_basic_search.json',
        'payments_search_with_canceled.json',
        'payments_search_with_filter.json',
        'payments_only_canceled.json',
        'payments_search_with_duplicates.json',
        'payments_search_with_empty_bank_account.json',
        'payments_search_test_cursor.json',
        'payments_basic_search_with_batch_payments.json',
    ],
)
@pytest.mark.now('2020-02-10T12:00:00')
@pytest.mark.servicetest
async def test_park_payments_search(
        web_app_client, load_json, data_path, request_headers, mockserver,
):
    @mockserver.json_handler('/billing-reports/v1/docs/select')
    async def _docs_select(request):
        if request.json['cursor'] == {}:
            if 'returned' in request.json['external_obj_id']:
                return mockserver.make_response(
                    json=data['reports_returned_response'],
                )
            return mockserver.make_response(json=data['reports_response'])
        return mockserver.make_response(
            json={'docs': [], 'cursor': request.json['cursor']},
        )

    data = load_json(data_path)
    response = await web_app_client.post(
        '/v1/parks/payments/search',
        headers=request_headers,
        json=data['request'],
    )
    assert response.status == data['response_status']
    content = await response.json()
    assert content == data['response']


@pytest.mark.parametrize(
    'request_body',
    [
        # Wrong request body
        None,
        # Empty request body
        {},
        # no time range
        {'limit': 5, 'clid': '0123456'},
        # bad limit
        {
            'begin_time': '2020-01-10T05:45:30+00:00',
            'end_time': '2020-01-25T05:45:30+00:00',
            'limit': 0,
            'clid': '0123456',
        },
        # bad cursor
        {
            'begin_time': '2020-01-10T05:45:30+00:00',
            'end_time': '2020-01-25T05:45:30+00:00',
            'cursor': 'text',
            'limit': 10,
            'clid': '0123456',
        },
    ],
)
@pytest.mark.servicetest
async def test_park_payments_search_bad_requests(
        web_app_client, request_headers, request_body,
):
    response = await web_app_client.post(
        '/v1/parks/payments/search',
        headers=request_headers,
        json=request_body,
    )
    assert response.status == web.HTTPBadRequest.status_code


@pytest.mark.parametrize('data_path', ['payments_basic_search.json'])
@pytest.mark.servicetest
async def test_park_payments_search_rate_limited(
        web_app_client, load_json, data_path, request_headers, mockserver,
):
    """
    Test client handling for 429 HTTPTooManyRequests response by rate limited
    request.
    """

    @mockserver.json_handler('/billing-reports/v1/docs/select')
    async def _docs_select(request):
        return mockserver.make_response(json={}, status=429)

    data = load_json(data_path)
    response = await web_app_client.post(
        '/v1/parks/payments/search',
        headers=request_headers,
        json=data['request'],
    )
    assert response.status == web.HTTPTooManyRequests.status_code
