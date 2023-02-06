from aiohttp import web
import pytest

from taxi import discovery
from taxi import settings as taxi_settings
from taxi.billing.util import dates

from taxi_billing_reports import resource_classifiers as res_cls
from taxi_billing_reports.pg import doc_store
from . import common


@pytest.mark.parametrize(
    'json_data_path,now',
    [
        # query both pg and yt
        ('docs.json', '2018-12-21T19:45:42.500000+00:00'),
        # query only pg
        ('docs_only_pg.json', '2018-12-21T00:00:00+00:00'),
        # query only yt
        ('docs_only_yt.json', '2018-12-22T00:00:00+00:00'),
        # resolve duplicates
        ('docs_duplicates.json', '2018-12-21T17:45:42.500000+00:00'),
        # sort result
        ('docs_sorted.json', '2018-12-21T17:45:42.500000+00:00'),
        # query desc
        ('docs_desc.json', '2018-12-21T17:45:42.500000+00:00'),
        # query desc cursor
        ('docs_desc_pass_cursor.json', '2018-12-21T17:45:42.500000+00:00'),
        # query pg by external-event-ref
        ('docs_by_external_ref_pg.json', '2018-12-21T00:00:00+00:00'),
        # query yt by external-event-ref
        ('docs_by_external_ref_yt.json', '2018-12-22T00:00:00+00:00'),
        # empty query by external_ref
        (
            'docs_by_external_ref_pg_pages_empty.json',
            '2018-12-21T00:00:00+00:00',
        ),
        # request only in pg because there are enough docs
        ('docs_desc_and_small_limit.json', '2018-12-21T19:45:42.500000+00:00'),
        # request in pg and then in yt because there are no docs in pg
        (
            'docs_desc_and_small_limit_yt.json',
            '2018-12-21T19:45:42.500000+00:00',
        ),
        # request in pg and then in yt because there are not enough docs in pg
        (
            'docs_desc_and_small_limit_pg_and_yt.json',
            '2018-12-21T19:45:42.500000+00:00',
        ),
        # pg and yt with projection
        ('docs_projection.json', '2018-12-21T19:45:42.500000+00:00'),
    ],
    ids=[
        'query-both-pg-and-yt',
        'query-only-pg',
        'query-only-yt',
        'resolve-duplicates',
        'sort-result',
        'query-desc',
        'query-desc-cursor',
        'query-by-external-event-ref-pg',
        'query-by-external-event-ref-yt',
        'empty-query-by-external-event-ref',
        'query-with-small-limit-and-desc-sort-order',
        'query-with-small-limit-and-desc-sort-order-no-docs-in-pg',
        'query-with-small-limit-and-desc-sort-order-docs-in-pg-and-yt',
        'query-with-projection',
    ],
)
@pytest.mark.config(
    BILLING_REPORTS_REPLICATION_OFFSET_HOURS={'__default__': 24},
    BILLING_REPORTS_DOCS_SELECT_OPTIMIZE_WITH_LIMITS_UP_TO={
        '__default__': 0,
        'test': 2,
    },
    BILLING_DOC_EXTERNAL_OBJ_ID_DESC_INDEX_ENABLED=False,
)
async def test_v2_docs_select(
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
        assert (
            json['query']['query_string'] == json_data['expected_yql']
        ), json_data_path
        assert (
            json['query']['query_params'] == json_data['expected_yql_params']
        ), json_data_path
        return response_mock(
            headers={'Content-Type': 'application/json'},
            json=json_data['yt_data'],
        )

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_docs_api_request(method, url, headers, json, **kwargs):
        if 'v1/docs/select' in url:
            assert json['external_obj_id'] == request_body['topic']
            assert json.get('sort', None) == request_body.get('sort', 'asc')
            cursor = json.get('cursor', '')
            return response_mock(
                headers={'Content-Type': 'application/json'},
                json=json_data['pg_data']['v2/docs/select'][cursor],
            )
        if 'v1/docs/search' in url:
            assert json['external_obj_id'] == request_body['topic']
            cursor = json.get('cursor', '')
            return response_mock(
                headers={'Content-Type': 'application/json'},
                json=json_data['pg_data']['v1/docs/search'][cursor],
            )
        raise NotImplementedError

    requested_resources = []

    @patch('taxi.billing.resource_limiter.ResourceLimiter.request_resources')
    def _request_resources(
            client_tvm_service_name, required_resources, log_extra,
    ):
        requested_resources.extend(required_resources)

    response = await taxi_billing_reports_client.post(
        '/v2/docs/select', json=request_body,
    )
    if json_data.get('archive_calls_count') is not None:
        actual = len(_patch_archive_api_request.calls)
        expected = json_data['archive_calls_count']
        assert actual == expected

    if json_data.get('docs_calls_count') is not None:
        actual = len(_patch_docs_api_request.calls)
        expected = json_data['docs_calls_count']
        assert actual == expected

    text = await response.text()
    assert response.status == web.HTTPOk.status_code, [text, json_data_path]
    found = await response.json()
    assert found
    assert found == json_data['$expected'], json_data_path
    spent_resources = await (
        res_cls.BalancesResourceClassifier().get_spent_resources(response)
    )
    common.compare_resources(
        requested_resources, json_data['expected_requested_resources'],
    )
    common.compare_resources(
        spent_resources, json_data['expected_spent_resources'],
    )


@pytest.mark.parametrize(
    'json_data_path,now',
    [
        # query desc
        ('docs_desc_index_enabled.json', '2018-12-21T17:45:42.500000+00:00'),
        # query desc cursor
        (
            'docs_desc_pass_cursor_index_enabled.json',
            '2018-12-21T17:45:42.500000+00:00',
        ),
        # request in pg and then in yt because there are no docs in pg
        (
            'docs_desc_and_small_limit_yt_index_enabled.json',
            '2018-12-21T19:45:42.500000+00:00',
        ),
        # request in pg and then in yt because there are not enough docs in pg
        (
            'docs_desc_and_small_limit_pg_and_yt_index_enabled.json',
            '2018-12-21T19:45:42.500000+00:00',
        ),
    ],
    ids=[
        'query-desc',
        'query-desc-cursor',
        'query-with-small-limit-and-desc-sort-order-no-docs-in-pg',
        'query-with-small-limit-and-desc-sort-order-docs-in-pg-and-yt',
    ],
)
@pytest.mark.config(
    BILLING_REPORTS_REPLICATION_OFFSET_HOURS={'__default__': 24},
    BILLING_REPORTS_DOCS_SELECT_OPTIMIZE_WITH_LIMITS_UP_TO={
        '__default__': 0,
        'test': 2,
    },
    BILLING_DOC_EXTERNAL_OBJ_ID_DESC_INDEX_ENABLED=True,
)
async def test_v2_docs_select_desc_index_enabled(
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
        assert (
            json['query']['query_string'] == json_data['expected_yql']
        ), json_data_path
        assert (
            json['query']['query_params'] == json_data['expected_yql_params']
        ), json_data_path
        return response_mock(
            headers={'Content-Type': 'application/json'},
            json=json_data['yt_data'],
        )

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_docs_api_request(method, url, headers, json, **kwargs):
        if 'v1/docs/select' in url:
            assert json['external_obj_id'] == request_body['topic']
            assert json.get('sort', None) == request_body.get('sort', 'asc')
            cursor = json.get('cursor', '')
            return response_mock(
                headers={'Content-Type': 'application/json'},
                json=json_data['pg_data']['v2/docs/select'][cursor],
            )
        if 'v1/docs/search' in url:
            assert json['external_obj_id'] == request_body['topic']
            cursor = json.get('cursor', '')
            return response_mock(
                headers={'Content-Type': 'application/json'},
                json=json_data['pg_data']['v1/docs/search'][cursor],
            )
        raise NotImplementedError

    requested_resources = []

    @patch('taxi.billing.resource_limiter.ResourceLimiter.request_resources')
    def _request_resources(
            client_tvm_service_name, required_resources, log_extra,
    ):
        requested_resources.extend(required_resources)

    response = await taxi_billing_reports_client.post(
        '/v2/docs/select', json=request_body,
    )
    if json_data.get('archive_calls_count') is not None:
        actual = len(_patch_archive_api_request.calls)
        expected = json_data['archive_calls_count']
        assert actual == expected

    if json_data.get('docs_calls_count') is not None:
        actual = len(_patch_docs_api_request.calls)
        expected = json_data['docs_calls_count']
        assert actual == expected

    text = await response.text()
    assert response.status == web.HTTPOk.status_code, [text, json_data_path]
    found = await response.json()
    assert found
    assert found == json_data['$expected'], json_data_path
    spent_resources = await (
        res_cls.BalancesResourceClassifier().get_spent_resources(response)
    )
    common.compare_resources(
        requested_resources, json_data['expected_requested_resources'],
    )
    common.compare_resources(
        spent_resources, json_data['expected_spent_resources'],
    )


@pytest.mark.parametrize(
    'json_data_path,now',
    [('docs_select_all.json', '2018-12-21T00:00:00+00:00')],
)
@pytest.mark.config(
    BILLING_REPORTS_REPLICATION_OFFSET_HOURS={'__default__': 24},
)
async def test_v2_docs_select_all(
        json_data_path,
        now,
        load_json,
        patch_aiohttp_session,
        patch,
        monkeypatch,
        response_mock,
        taxi_billing_reports_client,
):
    json_data = load_json(json_data_path)
    request_body = json_data['request_body']

    @patch('datetime.datetime.utcnow')
    def _utcnow():
        return dates.parse_datetime_fromisoformat(now)

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_docs_api_request(method, url, headers, json, **kwargs):
        assert 'v1/docs/select' in url
        assert json['external_obj_id'] == request_body['topic']
        assert json.get('sort', None) == request_body.get('sort', 'asc')
        cursor = json.get('cursor', '')
        return response_mock(
            headers={'Content-Type': 'application/json'},
            json=json_data['pg_data'][cursor],
        )

    monkeypatch.setattr(doc_store, '_BILLING_DOCS_MAX_LIMIT', 1)
    requested_resources = []

    @patch('taxi.billing.resource_limiter.ResourceLimiter.request_resources')
    def _request_resources(
            client_tvm_service_name, required_resources, log_extra,
    ):
        requested_resources.extend(required_resources)

    response = await taxi_billing_reports_client.post(
        '/v2/docs/select', json=request_body,
    )

    assert response.status == web.HTTPOk.status_code
    found = await response.json()
    assert found
    assert found == json_data['$expected'], json_data_path
    spent_resources = await (
        res_cls.BalancesResourceClassifier().get_spent_resources(response)
    )
    common.compare_resources(
        requested_resources, json_data['expected_requested_resources'],
    )
    common.compare_resources(
        spent_resources, json_data['expected_spent_resources'],
    )


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        # Wrong request bodies
        (None, web.HTTPUnsupportedMediaType),
        ({}, web.HTTPBadRequest),
        # Invalid requests
        (
            # missed date range
            {'cursor': {}, 'limit': 30},
            web.HTTPBadRequest,
        ),
        (
            # zero limit
            {
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T17:45:43.100000+00:00',
                'cursor': {},
                'limit': 0,
            },
            web.HTTPBadRequest,
        ),
        (
            # pass extra property use_master
            {
                'topic': 'alias_id/some_alias_id',
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T17:45:43.100000+00:00',
                'cursor': {},
                'limit': 10,
                'use_master': True,
            },
            web.HTTPBadRequest,
        ),
    ],
)
async def test_v2_docs_select_invalid(
        taxi_billing_reports_client, request_body, expected_response,
):
    response = await taxi_billing_reports_client.post(
        '/v2/docs/select', json=request_body,
    )
    assert response.status == expected_response.status_code
