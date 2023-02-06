from aiohttp import web
import pytest

from taxi import discovery
from taxi import settings as taxi_settings
from taxi.billing.util import dates


@pytest.mark.parametrize(
    'json_data_path,now',
    [
        ('pg_only_docs_empty.json', '2020-01-10T12:00:00+00:00'),
        ('pg_only_docs.json', '2020-01-10T12:00:00+00:00'),
        ('pg_only_docs_with_cursor.json', '2020-01-10T12:00:00+00:00'),
        ('yt_only_docs.json', '2020-01-25T12:00:00+00:00'),
        ('yt_only_docs_with_cursor.json', '2020-01-25T12:00:00+00:00'),
        ('pg_and_yt_docs.json', '2020-01-16T12:00:00+00:00'),
        ('pg_and_yt_docs_with_cursor.json', '2020-01-19T12:00:00+00:00'),
        ('pg_and_yt_docs_with_limit.json', '2020-01-19T12:00:00+00:00'),
    ],
)
@pytest.mark.config(
    BILLING_REPORTS_REPLICATION_OFFSET_HOURS={'__default__': 24},
)
async def test_docs_by_tag(
        json_data_path,
        now,
        load_json,
        patch_aiohttp_session,
        patch,
        response_mock,
        taxi_billing_reports_client,
):
    json_data = load_json(json_data_path)
    request_body = json_data['request_body']

    @patch('datetime.datetime.utcnow')
    def _utcnow():
        return dates.parse_datetime_fromisoformat(now)

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
        assert 'v1/docs/by_tag' in url
        assert json == json_data['pg_params']
        return response_mock(
            headers={'Content-Type': 'application/json'},
            json=json_data['pg_data'],
        )

    response = await taxi_billing_reports_client.post(
        '/v1/docs/by_tag', json=request_body,
    )

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
            # no time range
            {'limit': 5, 'tag': 'alias_id/3295fd59714d23edbeadd65a3168cfe1'},
            web.HTTPBadRequest,
        ),
        (
            # bad limit
            {
                'begin_time': '2020-01-10T05:45:30+00:00',
                'end_time': '2020-01-25T05:45:30+00:00',
                'limit': 0,
                'tag': 'alias_id/3295fd59714d23edbeadd65a3168cfe1',
            },
            web.HTTPBadRequest,
        ),
        (
            # bad cursor
            {
                'begin_time': '2020-01-10T05:45:30+00:00',
                'end_time': '2020-01-25T05:45:30+00:00',
                'cursor': 'text',
                'limit': 10,
                'tag': 'alias_id/3295fd59714d23edbeadd65a3168cfe1',
            },
            web.HTTPBadRequest,
        ),
    ],
)
async def test_docs_by_tag_invalid_requests(
        taxi_billing_reports_client, request_body, expected_response,
):
    response = await taxi_billing_reports_client.post(
        '/v1/docs/by_tag', json=request_body,
    )
    assert response.status == expected_response.status_code
