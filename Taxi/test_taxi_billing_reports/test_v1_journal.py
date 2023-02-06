from aiohttp import web
import pytest

from taxi import discovery
from taxi import settings as taxi_settings

from taxi_billing_reports import config
from taxi_billing_reports import resource_classifiers as res_cls
from . import common


@pytest.mark.now('2018-12-21T00:00:00+00:00')
@pytest.mark.config(
    BILLING_REPORTS_REPLICATION_OFFSET_HOURS={
        '__default__': 240,
        'journal_select': 24,
    },
)
@pytest.mark.parametrize('pre_request', [True, False])
@pytest.mark.parametrize(
    'data_path,expected_yql',
    [
        (
            'journal_select.json',
            [
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND ((acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p AND acc_idx.sub_account = %p)) '
                'LIMIT %p',
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND ((acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p)) '
                'LIMIT %p',
            ],
        ),
        (
            'journal_select_pg.json',
            [
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND ((acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p AND acc_idx.sub_account = %p)) '
                'LIMIT %p',
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND ((acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p)) '
                'LIMIT %p',
            ],
        ),
        (
            'journal_select_duplicates.json',
            [
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND ((acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p AND acc_idx.sub_account = %p)) '
                'LIMIT %p',
            ],
        ),
        (
            'journal_select_empty.json',
            [
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND ((acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p AND acc_idx.sub_account = %p)) '
                'LIMIT %p',
            ],
        ),
        (
            'journal_select_limit.json',
            [
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND ((acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p AND acc_idx.sub_account = %p)) '
                'LIMIT %p',
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND ((acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p)) '
                'LIMIT %p',
            ],
        ),
        (
            'journal_select_cursor.json',
            [
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND ((acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p AND acc_idx.sub_account = %p)) '
                'LIMIT %p',
            ],
        ),
        (
            'journal_select_skip_zero.json',
            [
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND (NOT regex_full_match(%p, j.amount)) '
                'AND ((acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p AND acc_idx.sub_account = %p)) '
                'LIMIT %p',
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND (NOT regex_full_match(%p, j.amount)) '
                'AND ((acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p)) '
                'LIMIT %p',
            ],
        ),
        (
            'journal_select_via_mask.json',
            [
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND ((acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p AND acc_idx.sub_account = %p)) '
                'LIMIT %p',
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND ((acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p '
                'AND regex_full_match(%p, acc_idx.sub_account))) '
                'LIMIT %p',
            ],
        ),
    ],
    ids=[
        'query-both-pg-and-yt',
        'query-pg',
        'resolve-duplicates',
        'empty-result',
        'limit',
        'pass-cursor',
        'query-both-pg-and-yt-skip-zero',
        'query-both-pg-and-yt-via-mask',
    ],
)
async def test_journal_select(
        taxi_billing_reports_client,
        pre_request,
        data_path,
        expected_yql,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        monkeypatch,
        patch,
):
    json_data = load_json(data_path)
    request_body = json_data['request_body']
    expected_response = json_data['expected_response']
    expected_yql_params = json_data['expected_yql_params']

    monkeypatch.setattr(
        config.Config,
        'BILLING_REPORTS_JOURNAL_SELECT_PRE_REQUEST_YT',
        pre_request,
    )

    yt_requests_counter = {}

    @patch_aiohttp_session(taxi_settings.Settings.ARCHIVE_API_URL, 'POST')
    def _patch_archive_api_request(method, url, headers, json, **kwargs):
        assert 'select_rows' in url
        key = _get_account_key_yql(json)
        assert json['query']['query_string'] in expected_yql
        assert json['query']['query_params'] in expected_yql_params
        i = yt_requests_counter.setdefault(key, 0)
        data = json_data['yt_data'][key][i]
        yt_requests_counter[key] += 1
        return response_mock(
            headers={'Content-Type': 'application/json'}, json=data,
        )

    pg_requests_counter = {}

    @mockserver.json_handler('/billing-accounts/v1/journal/select_advanced')
    def _handle_journal_select_advanced(request):
        assert request.json in json_data['expected_journal_requests']
        key = _get_account_key(request.json)
        i = pg_requests_counter.setdefault(key, 0)
        data = json_data['pg_data'][key][i]
        pg_requests_counter[key] += 1
        return mockserver.make_response(json=data)

    @mockserver.json_handler('/billing-accounts/v2/accounts/search')
    def _handle_accounts_search(request):
        return mockserver.make_response(json=json_data['pg_accounts_data'])

    requested_resources = []

    @patch('taxi.billing.resource_limiter.ResourceLimiter.request_resources')
    def _request_resources(
            client_tvm_service_name, required_resources, log_extra,
    ):
        requested_resources.extend(required_resources)

    response = await taxi_billing_reports_client.post(
        '/v1/journal/select', json=request_body,
    )

    actual_response = await response.json()
    assert actual_response == expected_response

    spent_resources = await (
        res_cls.JournalSelectV1ResourceClassifier().get_spent_resources(
            response,
        )
    )
    common.compare_resources(
        requested_resources, json_data['expected_requested_resources'],
    )
    common.compare_resources(
        spent_resources, json_data['expected_spent_resources'],
    )


@pytest.mark.parametrize('request_url', ['/v1/journal/select'])
@pytest.mark.parametrize(
    'request_body,expected_response',
    [
        # Wrong request bodies
        (None, web.HTTPUnsupportedMediaType),
        ({}, web.HTTPBadRequest),
        # Invalid requests
        (
            # missed date range
            {'cursor': '', 'limit': 30},
            web.HTTPBadRequest,
        ),
        (
            # zero limit
            {
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T17:45:43.100000+00:00',
                'cursor': '',
                'limit': 0,
            },
            web.HTTPBadRequest,
        ),
    ],
)
async def test_journal_select_invalid(
        taxi_billing_reports_client,
        request_url,
        request_body,
        expected_response,
):
    response = await taxi_billing_reports_client.post(
        request_url, json=request_body,
    )
    assert response.status == expected_response.status_code


@pytest.mark.parametrize(
    'data_path,request_body,expected_yql,expected_yql_params,now',
    [
        (
            'journal_search.json',
            {
                'accounts': [
                    {
                        'entity_external_id': (
                            'taximeter_driver_id/a3608/c6bda'
                        ),
                        'agreement_id': 'taxi/yandex_ride',
                        'currency': 'RUB',
                    },
                ],
                'doc_ref': '619640012',
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T17:45:43+00:00',
            },
            (
                '* '
                'FROM %t as doc_ref_idx '
                'JOIN %t as journal ON doc_ref_idx.id = journal.id '
                'WHERE doc_ref_idx.doc_ref = %p '
                'AND journal.event_at >= %p AND journal.event_at < %p '
                'AND (('
                'journal.entity_external_id = %p '
                'AND journal.agreement_id = %p '
                'AND journal.currency = %p'
                '))'
            ),
            [
                '//home/taxi/unstable/replica/api/billing_accounts/indexes/'
                'journal/doc_ref',
                '//home/taxi/unstable/replica/api/billing_accounts/journal',
                '619640012',
                1545327942000000,
                1545327943000000,
                'taximeter_driver_id/a3608/c6bda',
                'taxi/yandex_ride',
                'RUB',
            ],
            '2018-12-21T17:45:42.500000+00:00',
        ),
        (
            'journal_search_only_pg.json',
            {
                'accounts': [
                    {
                        'entity_external_id': (
                            'taximeter_driver_id/a3608/c6bda'
                        ),
                        'agreement_id': 'taxi/yandex_ride',
                        'currency': 'RUB',
                    },
                ],
                'doc_ref': '619640012',
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T17:45:43+00:00',
            },
            '',
            [],
            '2018-12-21T00:00:00+00:00',
        ),
        (
            'journal_search_only_pg_filter_by_acc.json',
            {
                'accounts': [
                    {
                        'entity_external_id': (
                            'taximeter_driver_id/a3608/c6bda'
                        ),
                        'agreement_id': 'taxi/yandex_ride',
                        'currency': 'RUB',
                        'sub_account': 'commission/ride/vat',
                    },
                ],
                'doc_ref': '619640012',
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T17:45:43+00:00',
            },
            '',
            [],
            '2018-12-21T00:00:00+00:00',
        ),
        (
            'journal_search_duplicates.json',
            {
                'accounts': [
                    {
                        'entity_external_id': (
                            'taximeter_driver_id/a3608/c6bda'
                        ),
                        'agreement_id': 'taxi/yandex_ride',
                        'currency': 'RUB',
                    },
                ],
                'doc_ref': '619640012',
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T17:45:43+00:00',
            },
            (
                '* '
                'FROM %t as doc_ref_idx '
                'JOIN %t as journal ON doc_ref_idx.id = journal.id '
                'WHERE doc_ref_idx.doc_ref = %p '
                'AND journal.event_at >= %p AND journal.event_at < %p '
                'AND (('
                'journal.entity_external_id = %p '
                'AND journal.agreement_id = %p '
                'AND journal.currency = %p'
                '))'
            ),
            [
                '//home/taxi/unstable/replica/api/billing_accounts/indexes/'
                'journal/doc_ref',
                '//home/taxi/unstable/replica/api/billing_accounts/journal',
                '619640012',
                1545327942000000,
                1545327943000000,
                'taximeter_driver_id/a3608/c6bda',
                'taxi/yandex_ride',
                'RUB',
            ],
            '2018-12-21T17:45:42.500000+00:00',
        ),
        (
            'journal_search_only_yt.json',
            {
                'accounts': [
                    {
                        'entity_external_id': (
                            'taximeter_driver_id/a3608/c6bda'
                        ),
                        'agreement_id': 'taxi/yandex_ride',
                        'currency': 'RUB',
                    },
                ],
                'doc_ref': '619640012',
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T17:45:43+00:00',
            },
            (
                '* '
                'FROM %t as doc_ref_idx '
                'JOIN %t as journal ON doc_ref_idx.id = journal.id '
                'WHERE doc_ref_idx.doc_ref = %p '
                'AND journal.event_at >= %p AND journal.event_at < %p '
                'AND (('
                'journal.entity_external_id = %p '
                'AND journal.agreement_id = %p '
                'AND journal.currency = %p'
                '))'
            ),
            [
                '//home/taxi/unstable/replica/api/billing_accounts/indexes/'
                'journal/doc_ref',
                '//home/taxi/unstable/replica/api/billing_accounts/journal',
                '619640012',
                1545327942000000,
                1545327943000000,
                'taximeter_driver_id/a3608/c6bda',
                'taxi/yandex_ride',
                'RUB',
            ],
            '2018-12-22T00:00:00+00:00',
        ),
    ],
    ids=[
        'from-yt-and-pg',
        'from-pg-only',
        'from-pg-only-filtered-by-account',
        'resolve-duplicates',
        'from-yt-only',
    ],
)
# pylint: disable=too-many-arguments
@pytest.mark.config(
    BILLING_DOCS_REPLICATION_SETTINGS={'__default__': {'TTL_DAYS': 1}},
)
async def test_journal_search(
        data_path,
        request_body,
        expected_yql,
        expected_yql_params,
        now,
        load_json,
        patch_aiohttp_session,
        patch,
        response_mock,
        taxi_billing_reports_client,
        mockserver,
):
    json_data = load_json(data_path)

    @patch('datetime.datetime.utcnow')
    def utcnow():  # pylint: disable=unused-variable
        from taxi.billing.util import dates
        return dates.parse_datetime_fromisoformat(now)

    @patch_aiohttp_session(taxi_settings.Settings.ARCHIVE_API_URL, 'POST')
    def _patch_archive_api_request(method, url, headers, json, **kwargs):
        assert 'select_rows' in url
        assert json['query']['query_string'] == expected_yql
        assert json['query']['query_params'] == expected_yql_params
        return response_mock(
            headers={'Content-Type': 'application/json'},
            json=json_data['yt_journal_data'],
        )

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_docs_api_request(method, url, headers, json, **kwargs):
        assert 'v1/journal/search' in url
        assert json['doc_id'] == int(request_body['doc_ref'])
        return response_mock(
            headers={'Content-Type': 'application/json'},
            json=json_data['pg_journal_data'],
        )

    @mockserver.json_handler('/billing-accounts/v2/accounts/search')
    def _handle_accounts_search(request):
        return mockserver.make_response(json=json_data['pg_accounts_data'])

    response = await taxi_billing_reports_client.post(
        '/v1/journal/search', json=request_body,
    )

    if json_data.get('archive_calls_count') is not None:
        actual = len(_patch_archive_api_request.calls)
        expected = json_data['archive_calls_count']
        assert actual == expected

    if json_data.get('docs_calls_count') is not None:
        actual = len(_patch_docs_api_request.calls)
        expected = json_data['docs_calls_count']
        assert actual == expected

        actual = _handle_accounts_search.times_called
        assert actual == expected

    assert response.status == web.HTTPOk.status_code
    found_entries = await response.json()
    assert found_entries['entries'] == json_data['$expected']


def _get_account_key(request_data):
    entity_external_id = request_data['account']['entity_external_id']
    agreement = request_data['account']['agreement_id']
    currency = request_data['account']['currency']
    sub_account = request_data['account'].get('sub_account')
    return f'{entity_external_id}/{agreement}/{currency}/{sub_account}'


def _get_account_key_yql(request_data):
    params = request_data['query']['query_params']
    entity_external_id = params[7]
    agreement = params[8]
    currency = params[9]
    sub_account = params[10]
    return f'{entity_external_id}/{agreement}/{currency}/{sub_account}'


@pytest.mark.config(BILLING_REPORTS_JOURNAL_SELECT_LIMIT_CONTROL=10)
@pytest.mark.parametrize('data_path', ['journal_select.json'])
async def test_journal_select_limit_config(
        taxi_billing_reports_client,
        data_path,
        load_json,
        patch_aiohttp_session,
        response_mock,
):

    json_data = load_json(data_path)
    request_body_good = json_data['request_body_good']
    request_body_bad = json_data['request_body_bad']

    @patch_aiohttp_session(taxi_settings.Settings.ARCHIVE_API_URL, 'POST')
    def _patch_archive_api_request(method, url, headers, json, **kwargs):
        data = {'items': []}
        return response_mock(
            headers={'Content-Type': 'application/json'}, json=data,
        )

    response = await taxi_billing_reports_client.post(
        '/v1/journal/select', json=request_body_good,
    )
    assert response.status == 200

    response = await taxi_billing_reports_client.post(
        '/v1/journal/select', json=request_body_bad,
    )
    assert response.status == 400
