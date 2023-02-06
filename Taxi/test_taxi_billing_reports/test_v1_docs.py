from aiohttp import web
import pytest

from taxi import discovery
from taxi import settings as taxi_settings
from taxi.billing.util import dates

from taxi_billing_reports import resource_classifiers as res_cls
from taxi_billing_reports.pg import doc_store
from . import common


@pytest.mark.parametrize(
    'json_data_path,use_master,expected_yql,expected_yql_params,now',
    [
        # query both pg and yt
        (
            'docs.json',
            False,
            (
                '* '
                'FROM %t AS idx '
                'JOIN %t AS d ON idx.doc_id = d.id '
                'WHERE idx.event_at >= %p AND idx.event_at < %p '
                'AND idx.external_obj_id = %p '
                'AND d.kind = %p '
                'LIMIT %p'
            ),
            [
                '//home/taxi/unstable/replica/api/billing_docs/indexes/doc/'
                'external_obj_id',
                '//home/taxi/unstable/replica/api/billing_docs/doc',
                1545327942000000,
                1545335142500000,
                'taxi/subvention/79713996b6a5615fad35a254b675f1e7',
                'journal',
                3,
            ],
            '2018-12-21T19:45:42.500000+00:00',
        ),
        # query only pg
        ('docs_only_pg.json', False, '', [], '2018-12-21T00:00:00+00:00'),
        # query only yt
        (
            'docs_only_yt.json',
            False,
            (
                '* '
                'FROM %t AS idx '
                'JOIN %t AS d ON idx.doc_id = d.id '
                'WHERE idx.event_at >= %p AND idx.event_at < %p '
                'AND idx.external_obj_id = %p '
                'AND d.kind = %p '
                'LIMIT %p'
            ),
            [
                '//home/taxi/unstable/replica/api/billing_docs/indexes/doc/'
                'external_obj_id',
                '//home/taxi/unstable/replica/api/billing_docs/doc',
                1545327942000000,
                1545327943000000,
                'taxi/subvention/79713996b6a5615fad35a254b675f1e7',
                'journal',
                3,
            ],
            '2018-12-22T00:00:00+00:00',
        ),
        # query pg-master and yt
        (
            'docs.json',
            True,
            (
                '* '
                'FROM %t AS idx '
                'JOIN %t AS d ON idx.doc_id = d.id '
                'WHERE idx.event_at >= %p AND idx.event_at < %p '
                'AND idx.external_obj_id = %p '
                'AND d.kind = %p '
                'LIMIT %p'
            ),
            [
                '//home/taxi/unstable/replica/api/billing_docs/indexes/doc/'
                'external_obj_id',
                '//home/taxi/unstable/replica/api/billing_docs/doc',
                1545327942000000,
                1545327942000000,
                'taxi/subvention/79713996b6a5615fad35a254b675f1e7',
                'journal',
                3,
            ],
            '2018-12-21T17:45:42+00:00',
        ),
        # resolve duplicates
        (
            'docs_duplicates.json',
            False,
            (
                '* '
                'FROM %t AS idx '
                'JOIN %t AS d ON idx.doc_id = d.id '
                'WHERE idx.event_at >= %p AND idx.event_at < %p '
                'AND idx.external_obj_id = %p '
                'AND d.kind = %p '
                'LIMIT %p'
            ),
            [
                '//home/taxi/unstable/replica/api/billing_docs/indexes/doc/'
                'external_obj_id',
                '//home/taxi/unstable/replica/api/billing_docs/doc',
                1545327942000000,
                1545327942500000,
                'taxi/subvention/79713996b6a5615fad35a254b675f1e7',
                'journal',
                3,
            ],
            '2018-12-21T17:45:42.500000+00:00',
        ),
        # sort result
        (
            'docs_sorted.json',
            False,
            (
                '* '
                'FROM %t AS idx '
                'JOIN %t AS d ON idx.doc_id = d.id '
                'WHERE idx.event_at >= %p AND idx.event_at < %p '
                'AND idx.external_obj_id = %p '
                'AND d.kind = %p '
                'LIMIT %p'
            ),
            [
                '//home/taxi/unstable/replica/api/billing_docs/indexes/doc/'
                'external_obj_id',
                '//home/taxi/unstable/replica/api/billing_docs/doc',
                1545327942000000,
                1545327942500000,
                'taxi/subvention/79713996b6a5615fad35a254b675f1e7',
                'journal',
                10,
            ],
            '2018-12-21T17:45:42.500000+00:00',
        ),
        # pass cursor
        (
            'docs_pass_cursor.json',
            False,
            (
                '* '
                'FROM %t AS idx '
                'JOIN %t AS d ON idx.doc_id = d.id '
                'WHERE idx.event_at >= %p AND idx.event_at < %p '
                'AND idx.external_obj_id = %p '
                'AND d.kind = %p '
                'AND (idx.event_at, idx.doc_id) > (%p, %p) '
                'LIMIT %p'
            ),
            [
                '//home/taxi/unstable/replica/api/billing_docs/indexes/doc/'
                'external_obj_id',
                '//home/taxi/unstable/replica/api/billing_docs/doc',
                1545327942400000,
                1545327942500000,
                'taxi/subvention/79713996b6a5615fad35a254b675f1e7',
                'journal',
                1545327942400000,
                2,
                10,
            ],
            '2018-12-21T17:45:42.500000+00:00',
        ),
        # query desc
        (
            'docs_desc.json',
            False,
            (
                '* '
                'FROM %t AS idx '
                'JOIN %t AS d ON idx.doc_id = d.id '
                'WHERE idx.event_at >= %p AND idx.event_at < %p '
                'AND idx.external_obj_id = %p '
                'AND d.kind = %p '
                'ORDER BY idx.event_at DESC, idx.doc_id DESC '
                'LIMIT %p'
            ),
            [
                '//home/taxi/unstable/replica/api/billing_docs/indexes/doc/'
                'external_obj_id',
                '//home/taxi/unstable/replica/api/billing_docs/doc',
                1545327942000000,
                1545327942500000,
                'taxi/subvention/79713996b6a5615fad35a254b675f1e7',
                'journal',
                3,
            ],
            '2018-12-21T17:45:42.500000+00:00',
        ),
        # query desc cursor
        (
            'docs_desc_pass_cursor.json',
            False,
            (
                '* '
                'FROM %t AS idx '
                'JOIN %t AS d ON idx.doc_id = d.id '
                'WHERE idx.event_at >= %p AND idx.event_at < %p '
                'AND idx.external_obj_id = %p '
                'AND d.kind = %p '
                'AND (idx.event_at, idx.doc_id) < (%p, %p) '
                'ORDER BY idx.event_at DESC, idx.doc_id DESC '
                'LIMIT %p'
            ),
            [
                '//home/taxi/unstable/replica/api/billing_docs/indexes/doc/'
                'external_obj_id',
                '//home/taxi/unstable/replica/api/billing_docs/doc',
                1545327942000000,
                1545327942500000,
                'taxi/subvention/79713996b6a5615fad35a254b675f1e7',
                'journal',
                1545327942400000,
                2,
                10,
            ],
            '2018-12-21T17:45:42.500000+00:00',
        ),
        # query pg by external-event-ref
        (
            'docs_by_external_event_ref_pg.json',
            False,
            '',
            [],
            '2018-12-21T00:00:00+00:00',
        ),
        # query yt by external-event-ref
        (
            'docs_by_external_event_ref_yt.json',
            False,
            (
                '* '
                'FROM %t AS idx '
                'JOIN %t AS d ON idx.doc_id = d.id '
                'WHERE idx.event_at >= %p AND idx.event_at < %p '
                'AND idx.external_obj_id = %p '
                'AND d.external_event_ref = %p '
                'AND d.kind = %p '
                'LIMIT %p'
            ),
            [
                '//home/taxi/unstable/replica/api/billing_docs/indexes/doc/'
                'external_obj_id',
                '//home/taxi/unstable/replica/api/billing_docs/doc',
                1545327942000000,
                1545327943000000,
                'taxi/subvention/79713996b6a5615fad35a254b675f1e7',
                (
                    'taxi/journal/subvention/on_hold/'
                    '79713996b6a5615fad35a254b675f1e7/1'
                ),
                'journal',
                3,
            ],
            '2018-12-22T00:00:00+00:00',
        ),
        # empty query by external_event_ref
        (
            'docs_by_external_event_ref_pg_pages_empty.json',
            False,
            '',
            [],
            '2018-12-21T00:00:00+00:00',
        ),
        # request only in pg because there are enough docs
        (
            'docs_desc_and_small_limit.json',
            False,
            '* FROM %t AS idx JOIN %t AS d ON idx.doc_id = d.id '
            'WHERE idx.event_at >= %p AND idx.event_at < %p '
            'AND idx.external_obj_id = %p AND d.kind = %p '
            'ORDER BY idx.event_at DESC, idx.doc_id DESC LIMIT %p',
            [],
            '2018-12-21T19:45:42.500000+00:00',
        ),
        # request in pg and then in yt because there are no docs in pg
        (
            'docs_desc_and_small_limit_yt.json',
            False,
            '* FROM %t AS idx JOIN %t AS d ON idx.doc_id = d.id '
            'WHERE idx.event_at >= %p AND idx.event_at < %p '
            'AND idx.external_obj_id = %p AND d.kind = %p '
            'ORDER BY idx.event_at DESC, idx.doc_id DESC LIMIT %p',
            [
                '//home/taxi/unstable/replica/api/billing_docs/indexes/doc/'
                'external_obj_id',
                '//home/taxi/unstable/replica/api/billing_docs/doc',
                1545327942000000,
                1545335142500000,
                'test/subvention/79713996b6a5615fad35a254b675f1e7',
                'journal',
                1,
            ],
            '2018-12-21T19:45:42.500000+00:00',
        ),
        # request in pg and then in yt because there are not enough docs in pg
        (
            'docs_desc_and_small_limit_pg_and_yt.json',
            False,
            '* FROM %t AS idx JOIN %t AS d ON idx.doc_id = d.id '
            'WHERE idx.event_at >= %p AND idx.event_at < %p '
            'AND idx.external_obj_id = %p AND d.kind = %p '
            'ORDER BY idx.event_at DESC, idx.doc_id DESC LIMIT %p',
            [
                '//home/taxi/unstable/replica/api/billing_docs/indexes/doc/'
                'external_obj_id',
                '//home/taxi/unstable/replica/api/billing_docs/doc',
                1545327942000000,
                1545335142500000,
                'test/subvention/79713996b6a5615fad35a254b675f1e7',
                'journal',
                2,
            ],
            '2018-12-21T19:45:42.500000+00:00',
        ),
    ],
    ids=[
        'query-both-pg-and-yt',
        'query-only-pg',
        'query-only-yt',
        'query-pg-master-and-yt',
        'resolve-duplicates',
        'sort-result',
        'pass-cursor',
        'query-desc',
        'query-desc-cursor',
        'query-by-external-event-ref-pg',
        'query-by-external-event-ref-yt',
        'empty-query-by-external-event-ref',
        'query-with-small-limit-and-desc-sort-order',
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
    BILLING_DOC_EXTERNAL_OBJ_ID_DESC_INDEX_ENABLED=False,
)
async def test_docs_select(
        json_data_path,
        use_master,
        expected_yql,
        expected_yql_params,
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
        assert json['query']['query_string'] == expected_yql
        assert json['query']['query_params'] == expected_yql_params
        return response_mock(
            headers={'Content-Type': 'application/json'},
            json=json_data['yt_data'],
        )

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_docs_api_request(method, url, headers, json, **kwargs):
        if 'v1/docs/select' in url:
            assert json['external_obj_id'] == request_body['external_obj_id']
            assert json['use_master'] == use_master
            assert json.get('sort', None) == request_body.get('sort', 'asc')
            cursor = json.get('cursor', '')
            return response_mock(
                headers={'Content-Type': 'application/json'},
                json=json_data['pg_data']['v1/docs/select'][cursor],
            )
        if 'v1/docs/search' in url:
            assert json['external_obj_id'] == request_body['external_obj_id']
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
        '/v1/docs/select', json=request_body,
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
    found = await response.json()
    assert found
    assert found == json_data['$expected']
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
    'json_data_path,use_master,expected_yql,expected_yql_params,now',
    [
        # query desc
        (
            'docs_desc.json',
            False,
            (
                '* '
                'FROM %t AS idx '
                'JOIN %t AS d ON idx.doc_id = d.id '
                'WHERE idx.event_at >= %p AND idx.event_at < %p '
                'AND idx.external_obj_id = %p '
                'AND d.kind = %p '
                'LIMIT %p'
            ),
            [
                '//home/taxi/unstable/replica/api/billing_docs/indexes/doc/'
                'external_obj_id_desc',
                '//home/taxi/unstable/replica/api/billing_docs/doc',
                -1545327942499999,
                -1545327941999999,
                'taxi/subvention/79713996b6a5615fad35a254b675f1e7',
                'journal',
                3,
            ],
            '2018-12-21T17:45:42.500000+00:00',
        ),
        # query desc cursor
        (
            'docs_desc_pass_cursor.json',
            False,
            (
                '* '
                'FROM %t AS idx '
                'JOIN %t AS d ON idx.doc_id = d.id '
                'WHERE idx.event_at >= %p AND idx.event_at < %p '
                'AND idx.external_obj_id = %p '
                'AND d.kind = %p '
                'AND (idx.event_at, idx.doc_id) < (%p, %p) '
                'LIMIT %p'
            ),
            [
                '//home/taxi/unstable/replica/api/billing_docs/indexes/doc/'
                'external_obj_id_desc',
                '//home/taxi/unstable/replica/api/billing_docs/doc',
                -1545327942499999,
                -1545327941999999,
                'taxi/subvention/79713996b6a5615fad35a254b675f1e7',
                'journal',
                -1545327942400000,
                2,
                10,
            ],
            '2018-12-21T17:45:42.500000+00:00',
        ),
        # request in pg and then in yt because there are no docs in pg
        (
            'docs_desc_and_small_limit_yt.json',
            False,
            '* FROM %t AS idx JOIN %t AS d ON idx.doc_id = d.id '
            'WHERE idx.event_at >= %p AND idx.event_at < %p '
            'AND idx.external_obj_id = %p AND d.kind = %p '
            'LIMIT %p',
            [
                '//home/taxi/unstable/replica/api/billing_docs/indexes/doc/'
                'external_obj_id_desc',
                '//home/taxi/unstable/replica/api/billing_docs/doc',
                -1545335142499999,
                -1545327941999999,
                'test/subvention/79713996b6a5615fad35a254b675f1e7',
                'journal',
                1,
            ],
            '2018-12-21T19:45:42.500000+00:00',
        ),
        # request in pg and then in yt because there are not enough docs in pg
        (
            'docs_desc_and_small_limit_pg_and_yt.json',
            False,
            '* FROM %t AS idx JOIN %t AS d ON idx.doc_id = d.id '
            'WHERE idx.event_at >= %p AND idx.event_at < %p '
            'AND idx.external_obj_id = %p AND d.kind = %p '
            'LIMIT %p',
            [
                '//home/taxi/unstable/replica/api/billing_docs/indexes/doc/'
                'external_obj_id_desc',
                '//home/taxi/unstable/replica/api/billing_docs/doc',
                -1545335142499999,
                -1545327941999999,
                'test/subvention/79713996b6a5615fad35a254b675f1e7',
                'journal',
                2,
            ],
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
async def test_docs_select_desc_index_enabled(
        json_data_path,
        use_master,
        expected_yql,
        expected_yql_params,
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
        assert json['query']['query_string'] == expected_yql
        assert json['query']['query_params'] == expected_yql_params
        return response_mock(
            headers={'Content-Type': 'application/json'},
            json=json_data['yt_data'],
        )

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_docs_api_request(method, url, headers, json, **kwargs):
        if 'v1/docs/select' in url:
            assert json['external_obj_id'] == request_body['external_obj_id']
            assert json['use_master'] == use_master
            assert json.get('sort', None) == request_body.get('sort', 'asc')
            cursor = json.get('cursor', '')
            return response_mock(
                headers={'Content-Type': 'application/json'},
                json=json_data['pg_data']['v1/docs/select'][cursor],
            )
        if 'v1/docs/search' in url:
            assert json['external_obj_id'] == request_body['external_obj_id']
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
        '/v1/docs/select', json=request_body,
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
    found = await response.json()
    assert found
    assert found == json_data['$expected']
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
async def test_docs_select_all(
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
        assert json['external_obj_id'] == request_body['external_obj_id']
        assert json['use_master'] is False
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
        '/v1/docs/select', json=request_body,
    )

    assert response.status == web.HTTPOk.status_code
    found = await response.json()
    assert found
    assert found == json_data['$expected']
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
                'external_obj_id': 'alias_id/some_alias_id',
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
async def test_docs_select_invalid(
        taxi_billing_reports_client, request_body, expected_response,
):
    response = await taxi_billing_reports_client.post(
        '/v1/docs/select', json=request_body,
    )
    assert response.status == expected_response.status_code
