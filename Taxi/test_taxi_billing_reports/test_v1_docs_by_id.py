from aiohttp import web
import pytest

from taxi import discovery
from taxi import settings as taxi_settings


@pytest.mark.parametrize(
    'json_data_path',
    [
        'pg_and_yt_docs.json',
        'pg_and_yt_docs_empty.json',
        'pg_only_docs.json',
        'yt_only_docs.json',
        'pg_and_yt_docs_empty_projection.json',
        'pg_and_yt_docs_full_projection.json',
        'pg_and_yt_docs_full_projection_old_format.json',
    ],
)
async def test_docs_by_id(
        json_data_path,
        load_json,
        patch_aiohttp_session,
        patch,
        response_mock,
        taxi_billing_reports_client,
):
    json_data = load_json(json_data_path)
    request_body = json_data['request_body']
    pg_params = []

    @patch_aiohttp_session(taxi_settings.Settings.ARCHIVE_API_URL, 'POST')
    def _patch_archive_api_request(method, url, headers, json, **kwargs):
        assert 'select_rows' in url
        assert json['query']['query_string'] == json_data['yt_query']
        assert json['query']['query_params'] == json_data['yt_params']
        return response_mock(
            headers={'Content-Type': 'application/json'},
            json=json_data['yt_data'],
        )

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_docs_api_request(method, url, headers, json, **kwargs):
        nonlocal pg_params
        assert 'v1/docs/search' in url
        pg_params.append(json)
        if len(pg_params) > 1:
            return response_mock(
                headers={'Content-Type': 'application/json'},
                json=json_data['pg_data_next'],
            )
        return response_mock(
            headers={'Content-Type': 'application/json'},
            json=json_data['pg_data'],
        )

    response = await taxi_billing_reports_client.post(
        '/v1/docs/by_id', json=request_body,
    )

    assert pg_params == json_data['pg_params']

    if json_data.get('archive_calls_count') is not None:
        actual = len(_patch_archive_api_request.calls)
        expected = json_data['archive_calls_count']
        assert actual == expected

    if json_data.get('docs_calls_count') is not None:
        actual = len(_patch_docs_api_request.calls)
        expected = json_data['docs_calls_count']
        assert actual == expected

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
            # Wront type for document ids
            {'doc_ids': ['string']},
            web.HTTPBadRequest,
        ),
        (
            # Wrot number of requested document ids
            {'doc_ids': []},
            web.HTTPBadRequest,
        ),
    ],
)
async def test_docs_by_id_invalid_requests(
        taxi_billing_reports_client, request_body, expected_response,
):
    response = await taxi_billing_reports_client.post(
        '/v1/docs/by_id', json=request_body,
    )
    assert response.status == expected_response.status_code
