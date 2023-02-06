from aiohttp import web
import pytest

from taxi import discovery
from taxi import settings as taxi_settings

from taxi_billing_reports import config
from taxi_billing_reports import resource_classifiers as res_cls
from . import common


@pytest.mark.parametrize('fetch_doc_ids', [True, False])
@pytest.mark.parametrize(
    'data_path,expected_yql,expected_yql_params,now',
    [
        (
            'journal_by_tag.json',
            (
                '* '
                'FROM %t AS tag_idx '
                'JOIN %t AS j_idx ON to_string(tag_idx.doc_id) = j_idx.doc_ref'
                ' JOIN %t AS j ON j_idx.id = j.id '
                'WHERE %p <= tag_idx.event_at AND tag_idx.event_at < %p '
                'AND tag_idx.tag IN %p '
                'AND ((j.entity_external_id = %p '
                'AND j.agreement_id = %p '
                'AND j.currency = %p))'
            ),
            [
                '//home/taxi/unstable/replica/api/billing_docs/indexes/'
                'doc/tag',
                '//home/taxi/unstable/replica/api/billing_accounts/indexes/'
                'journal/doc_ref',
                '//home/taxi/unstable/replica/api/billing_accounts/journal',
                1545327942000000,
                1545327943000000,
                [
                    'taxi/alias_id/123456789abcde',
                    'taxi/alias_id/987654321zyxwq',
                ],
                'taximeter_driver_id/a3608/c6bda',
                'taxi/yandex_ride',
                'RUB',
            ],
            '2018-12-21T17:45:42.500000+00:00',
        ),
        ('journal_by_tag_only_pg.json', '', [], '2018-12-21T00:00:00+00:00'),
        (
            'journal_by_tag_duplicates.json',
            (
                '* '
                'FROM %t AS tag_idx '
                'JOIN %t AS j_idx ON to_string(tag_idx.doc_id) = j_idx.doc_ref'
                ' JOIN %t AS j ON j_idx.id = j.id '
                'WHERE %p <= tag_idx.event_at AND tag_idx.event_at < %p '
                'AND tag_idx.tag IN %p '
                'AND ((j.entity_external_id = %p '
                'AND j.agreement_id = %p '
                'AND j.currency = %p))'
            ),
            [
                '//home/taxi/unstable/replica/api/billing_docs/indexes/'
                'doc/tag',
                '//home/taxi/unstable/replica/api/billing_accounts/indexes/'
                'journal/doc_ref',
                '//home/taxi/unstable/replica/api/billing_accounts/journal',
                1545327942000000,
                1545327943000000,
                [
                    'taxi/alias_id/123456789abcde',
                    'taxi/alias_id/987654321zyxwq',
                ],
                'taximeter_driver_id/a3608/c6bda',
                'taxi/yandex_ride',
                'RUB',
            ],
            '2018-12-21T17:45:42.500000+00:00',
        ),
        (
            'journal_by_tag_only_yt.json',
            (
                '* '
                'FROM %t AS tag_idx '
                'JOIN %t AS j_idx ON to_string(tag_idx.doc_id) = j_idx.doc_ref'
                ' JOIN %t AS j ON j_idx.id = j.id '
                'WHERE %p <= tag_idx.event_at AND tag_idx.event_at < %p '
                'AND tag_idx.tag IN %p '
                'AND ((j.entity_external_id = %p '
                'AND j.agreement_id = %p '
                'AND j.currency = %p))'
            ),
            [
                '//home/taxi/unstable/replica/api/billing_docs/indexes/'
                'doc/tag',
                '//home/taxi/unstable/replica/api/billing_accounts/indexes/'
                'journal/doc_ref',
                '//home/taxi/unstable/replica/api/billing_accounts/journal',
                1545327942000000,
                1545327943000000,
                [
                    'taxi/alias_id/123456789abcde',
                    'taxi/alias_id/987654321zyxwq',
                ],
                'taximeter_driver_id/a3608/c6bda',
                'taxi/yandex_ride',
                'RUB',
            ],
            '2018-12-22T00:00:00+00:00',
        ),
        (
            'journal_by_tag_skip_zero.json',
            (
                '* '
                'FROM %t AS tag_idx '
                'JOIN %t AS j_idx ON to_string(tag_idx.doc_id) = j_idx.doc_ref'
                ' JOIN %t AS j ON j_idx.id = j.id '
                'WHERE %p <= tag_idx.event_at AND tag_idx.event_at < %p '
                'AND tag_idx.tag IN %p '
                'AND (NOT regex_full_match(%p, j.amount)) '
                'AND ((j.entity_external_id = %p '
                'AND j.agreement_id = %p '
                'AND j.currency = %p))'
            ),
            [
                '//home/taxi/unstable/replica/api/billing_docs/indexes/'
                'doc/tag',
                '//home/taxi/unstable/replica/api/billing_accounts/indexes/'
                'journal/doc_ref',
                '//home/taxi/unstable/replica/api/billing_accounts/journal',
                1545327942000000,
                1545327943000000,
                [
                    'taxi/alias_id/123456789abcde',
                    'taxi/alias_id/987654321zyxwq',
                ],
                r'^0+(\.0+)?$',
                'taximeter_driver_id/a3608/c6bda',
                'taxi/yandex_ride',
                'RUB',
            ],
            '2018-12-21T17:45:42.500000+00:00',
        ),
        (
            'journal_by_tag_required.json',
            '',
            [],
            '2018-12-21T17:45:42.500000+00:00',
        ),
        (
            'journal_by_tag_only_pg_2_doc_ref.json',
            '',
            [],
            '2018-12-21T00:00:00+00:00',
        ),
    ],
    ids=[
        '2tags-from-yt-and-pg',
        '2tags-from-pg-only',
        'resolve-duplicates',
        'from-yt-only',
        '2tags-from-yt-and-pg-skip-zero',
        'validation-check',
        'pg_doc_ref_request_by_chunks',
    ],
)
# pylint: disable=too-many-arguments
@pytest.mark.config(
    BILLING_DOCS_REPLICATION_SETTINGS={'__default__': {'TTL_DAYS': 1}},
    BILLING_REPORTS_JOURNAL_BY_TAG_V2_SETTINGS={
        'pg_journal_select_limit': 1000,
        'pg_journal_select_max_request': 5,
        'pg_journal_select_chunk_size': 1,
    },
)
async def test_journal_by_tag(
        data_path,
        fetch_doc_ids,
        expected_yql,
        expected_yql_params,
        now,
        load_json,
        patch_aiohttp_session,
        patch,
        monkeypatch,
        response_mock,
        taxi_billing_reports_client,
        mockserver,
):
    json_data = load_json(data_path)
    request_body = json_data['request_body']

    monkeypatch.setattr(
        config.Config,
        'BILLING_REPORTS_JOURNAL_BY_TAG_FETCH_DOC_IDS',
        fetch_doc_ids,
    )

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
        if 'v3/docs/by_tag' in url:
            response_json = json_data['pg_docs_data']['v3/docs/by_tag']
            docs_by_tags = {}
            for tag in json['tags']:
                if tag in response_json['docs']:
                    docs_by_tags[tag] = response_json['docs'][tag]
            result = {'docs': docs_by_tags}
            return response_mock(
                headers={'Content-Type': 'application/json'}, json=result,
            )
        if 'v1/doc_ids/by_tag' in url:
            response_json = json_data['pg_docs_data']['v1/doc_ids/by_tag']
            return response_mock(
                headers={'Content-Type': 'application/json'},
                json=response_json,
            )
        raise NotImplementedError

    expected_doc_refs = set()
    if json_data.get('pg_docs_data'):
        docs_data = json_data['pg_docs_data']['v3/docs/by_tag']['docs']
        expected_doc_refs = set()
        for tag in docs_data:
            for doc in docs_data[tag]:
                expected_doc_refs.add(str(doc['doc_id']))

    requested_doc_refs = []

    @mockserver.json_handler('/billing-accounts/v2/journal/select')
    def _handle_journal_select(request):
        nonlocal requested_doc_refs
        requested_doc_refs.extend(request.json['doc_refs'])
        assert request.json['skip_zero_entries'] == request_body.get(
            'exclude', {},
        ).get('zero_entries', False)
        if 'cursor' in request.json:
            result = {'entries': [], 'cursor': {}}
        else:
            result = json_data['pg_journal_data']

        entries = result['entries']
        entries_filtered_by_doc_ref = [
            entry
            for entry in entries
            if entry['doc_ref'] in request.json['doc_refs']
        ]
        result['entries'] = entries_filtered_by_doc_ref
        return mockserver.make_response(json=result)

    requested_resources = []

    @patch('taxi.billing.resource_limiter.ResourceLimiter.request_resources')
    def _request_resources(
            client_tvm_service_name, required_resources, log_extra,
    ):
        requested_resources.extend(required_resources)

    response = await taxi_billing_reports_client.post(
        '/v2/journal/by_tag', json=request_body,
    )

    if json_data.get('archive_calls_count') is not None:
        actual = len(_patch_archive_api_request.calls)
        expected = json_data['archive_calls_count']
        assert actual == expected

    if json_data.get('docs_calls_count') is not None:
        actual = len(_patch_docs_api_request.calls)
        expected = json_data['docs_calls_count']
        assert actual == expected
        # something weird
        assert _handle_journal_select.times_called == expected

    if json_data.get('accounts_calls_count') is not None:
        assert json_data.get('docs_calls_count')
        expected = json_data['accounts_calls_count']
        assert _handle_journal_select.times_called == expected

    expected_resp_status = json_data.get(
        'response_status_code', web.HTTPOk.status_code,
    )
    assert response.status == expected_resp_status

    if response.status != web.HTTPOk.status_code:
        return

    assert set(requested_doc_refs) == expected_doc_refs

    found_entries = await response.json()
    assert found_entries['entries'] == json_data['$expected']

    spent_resources = await (
        res_cls.JournalSelectV1ResourceClassifier().get_spent_resources(
            response,
        )
    )
    if fetch_doc_ids:
        expected_requested_resources = json_data[
            'expected_requested_resources'
        ]['fetch_doc_ids_only']
        expected_spent_resources = json_data['expected_spent_resources'][
            'fetch_doc_ids_only'
        ]
    else:
        expected_requested_resources = json_data[
            'expected_requested_resources'
        ]['fetch_full_docs']
        expected_spent_resources = json_data['expected_spent_resources'][
            'fetch_full_docs'
        ]
    common.compare_resources(requested_resources, expected_requested_resources)
    common.compare_resources(spent_resources, expected_spent_resources)


@pytest.mark.now('2018-12-21T00:00:00+00:00')
@pytest.mark.config(
    BILLING_REPORTS_REPLICATION_OFFSET_HOURS={
        '__default__': 240,
        'v2_journal_select': 24,
    },
)
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
                'AND (acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p AND (acc_idx.sub_account = %p)) '
                'LIMIT %p',
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND (acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p) '
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
                'AND (acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p AND (acc_idx.sub_account = %p)) '
                'LIMIT %p',
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND (acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p) '
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
                'AND (acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p AND (acc_idx.sub_account = %p)) '
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
                'AND (acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p AND (acc_idx.sub_account = %p)) '
                'LIMIT %p',
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND (acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p) '
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
                'AND (acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p AND (acc_idx.sub_account = %p)) '
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
                'AND (acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p AND (acc_idx.sub_account = %p)) '
                'LIMIT %p',
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND (NOT regex_full_match(%p, j.amount)) '
                'AND (acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p) '
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
                'AND (acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p AND (acc_idx.sub_account = %p)) '
                'LIMIT %p',
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND (acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p '
                'AND (regex_full_match(%p, acc_idx.sub_account))) '
                'LIMIT %p',
            ],
        ),
        (
            'journal_select_with_yt_config.json',
            [
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND (acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p AND (acc_idx.sub_account = %p)) '
                'LIMIT %p',
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND (acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p) '
                'LIMIT %p',
            ],
        ),
        (
            'journal_select_via_blacklist.json',
            [
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND (acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p AND (acc_idx.sub_account = %p)) '
                'LIMIT %p',
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND (acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p '
                'AND (regex_full_match(%p, acc_idx.sub_account)) '
                'AND NOT (regex_full_match(%p, acc_idx.sub_account))) '
                'LIMIT %p',
            ],
        ),
        (
            'journal_select_cursor_out_of_range.json',
            [
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND (acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p AND (acc_idx.sub_account = %p)) '
                'LIMIT %p',
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND (acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p) '
                'LIMIT %p',
            ],
        ),
        (
            'journal_select_yt_multiple_subaccount_filter.json',
            [
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND (NOT regex_full_match(%p, j.amount)) '
                'AND (acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p '
                'AND (acc_idx.sub_account = %p '
                'OR regex_full_match(%p, acc_idx.sub_account)) '
                'AND NOT (acc_idx.sub_account = %p '
                'OR regex_full_match(%p, acc_idx.sub_account))) '
                'LIMIT %p',
                '* '
                'FROM %t AS acc_idx '
                'JOIN %t AS j ON acc_idx.id = j.id '
                'WHERE %p < acc_idx.event_at '
                'AND acc_idx.event_at <= %p '
                'AND (acc_idx.event_at > %p '
                'OR (acc_idx.event_at = %p AND acc_idx.id > %p)) '
                'AND (NOT regex_full_match(%p, j.amount)) '
                'AND (acc_idx.entity_external_id = %p '
                'AND acc_idx.agreement_id = %p '
                'AND acc_idx.currency = %p '
                'AND (regex_full_match(%p, acc_idx.sub_account)) '
                'AND NOT (regex_full_match(%p, acc_idx.sub_account))) '
                'LIMIT %p',
            ],
        ),
    ],
    ids=[
        'query-both-pg-and-yt',
        'query-pg',
        'empty-result',
        'limit',
        'pass-cursor',
        'query-both-pg-and-yt-skip-zero',
        'query-both-pg-and-yt-via-mask',
        'query-both-pg-and-yt-via-yt-config',
        'query-both-pg-and-yt-via-blacklist',
        'dont-query-pg-if-cursor-is-out-of-range',
        'yt-multiple-subaccount-filters',
    ],
)
async def test_v2_journal_select(
        taxi_billing_reports_client,
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
    yt_max_limit = json_data.get('yt_max_limit')
    if yt_max_limit is not None:
        monkeypatch.setattr(
            config.Config,
            'BILLING_REPORTS_JOURNAL_SELECT_V2_LIMIT_CONTROL',
            yt_max_limit,
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

    @mockserver.json_handler('/billing-accounts/v2/journal/select_advanced')
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
        '/v2/journal/select', json=request_body,
    )
    actual_response = await response.json()
    assert actual_response == expected_response

    spent_resources = await (
        res_cls.JournalSelectV2ResourceClassifier().get_spent_resources(
            response,
        )
    )
    common.compare_resources(
        requested_resources, json_data['expected_requested_resources'],
    )
    common.compare_resources(
        spent_resources, json_data['expected_spent_resources'],
    )


@pytest.mark.parametrize(
    'request_body,expected_response',
    [
        # Wrong request bodies
        (None, web.HTTPUnsupportedMediaType),
        ({}, web.HTTPBadRequest),
        # Invalid requests
        (
            # missed date range
            {'accounts': [], 'cursor': '', 'limit': 30},
            web.HTTPBadRequest,
        ),
        (
            # zero limit
            {
                'accounts': [],
                'begin_time': '2018-12-20T17:45:42+00:00',
                'end_time': '2018-12-20T17:45:43.100000+00:00',
                'cursor': '',
                'limit': 0,
            },
            web.HTTPBadRequest,
        ),
    ],
)
async def test_v2_journal_select_invalid(
        taxi_billing_reports_client, request_body, expected_response,
):
    response = await taxi_billing_reports_client.post(
        '/v2/journal/select', json=request_body,
    )
    assert response.status == expected_response.status_code


def _get_account_key(request_data):
    def _key(data):
        entity_external_id = data['entity_external_id']
        agreement = data['agreement_id']
        currency = data['currency']
        sub_account = data.get('sub_account')
        return f'{entity_external_id}/{agreement}/{currency}/{sub_account}'

    first = min(request_data['accounts'], key=_key)
    return _key(first)


def _get_account_key_yql(request_data):
    params = request_data['query']['query_params']
    entity_external_id = params[7]
    agreement = params[8]
    currency = params[9]
    sub_account = params[10]
    return f'{entity_external_id}/{agreement}/{currency}/{sub_account}'
