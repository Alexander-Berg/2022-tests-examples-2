from aiohttp import web
import pytest

from taxi import settings as taxi_settings


@pytest.mark.parametrize(
    'json_data_path',
    [
        'pg_and_yt_entries.json',
        'pg_and_yt_empty.json',
        'pg_only_entries.json',
        'yt_only_entries.json',
    ],
)
async def test_journal_by_id(
        json_data_path,
        load_json,
        patch_aiohttp_session,
        patch,
        response_mock,
        taxi_billing_reports_client,
        mockserver,
):
    json_data = load_json(json_data_path)
    request_body = json_data['request_body']
    pg_params = []
    pg_requests_counter = 0

    @patch_aiohttp_session(taxi_settings.Settings.ARCHIVE_API_URL, 'POST')
    def _patch_archive_api_request(method, url, headers, json, **kwargs):
        assert 'select_rows' in url
        assert json['query']['query_string'] == json_data['yt_query']
        assert json['query']['query_params'] == json_data['yt_params']
        return response_mock(
            headers={'Content-Type': 'application/json'},
            json=json_data['yt_data'],
        )

    @mockserver.json_handler('/billing-accounts/v1/journal/by_id')
    def _handle_journal_by_id(request):
        nonlocal pg_params
        nonlocal pg_requests_counter
        pg_params.append(request.json)
        pg_requests_counter += 1
        return mockserver.make_response(json=json_data['pg_data'])

    response = await taxi_billing_reports_client.post(
        '/v1/journal/by_id', json=request_body,
    )

    assert pg_params == json_data['pg_params']

    if json_data.get('archive_calls_count') is not None:
        actual = len(_patch_archive_api_request.calls)
        expected = json_data['archive_calls_count']
        assert actual == expected

    if json_data.get('accounts_calls_count') is not None:
        expected = json_data['accounts_calls_count']
        assert pg_requests_counter == expected

    assert response.status == web.HTTPOk.status_code
    response = await response.json()
    assert response == json_data['response']


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            # Wrong request body
            None,
            web.HTTPUnsupportedMediaType,
        ),
        (
            # Empty request body
            {},
            web.HTTPBadRequest,
        ),
        (
            # Wrong type for entry ids
            {'entry_ids': ['string']},
            web.HTTPBadRequest,
        ),
        (
            # Wrong number of requested entry ids
            {'entry_ids': []},
            web.HTTPBadRequest,
        ),
    ],
)
async def test_journal_by_id_invalid_requests(
        taxi_billing_reports_client, request_body, expected_response,
):
    response = await taxi_billing_reports_client.post(
        '/v1/journal/by_id', json=request_body,
    )
    assert response.status == expected_response.status_code
