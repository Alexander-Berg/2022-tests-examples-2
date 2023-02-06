import pytest

from taxi import discovery

from taxi_billing_reports import config
from taxi_billing_reports import resource_classifiers as res_cls
from . import common


@pytest.mark.parametrize(
    'data_path',
    [
        'one_account_one_accrued_at.json',
        'one_account_two_accrued_at.json',
        'one_account_one_accrued_at_yt.json',
        'one_account_two_accrued_at_dont_use_yt.json',
        'one_account_two_accrued_at_dont_use_yt_but_compare.json',
        'one_account_two_accrued_at_compare.json',
        'two_accounts_one_accrued_at_yt_absent_balance.json',
        'one_account_two_accrued_at_yt.json',
        'two_account_two_accrued_at_yt.json',
    ],
    ids=[
        'query-only-pg-by-offset',
        'query-both-yt-and-pg-by-offset',
        'query-only-yt-by-offset-do-not-compare',
        'query-only-pg-by-config',
        'query-only-pg-by-config-and-compare',
        'query-both-yt-and-pg-by-offset-and-compare',
        'query-only-yt-by-offset-absent-balance',
        'query-only-yt-by-offset-two-balances',
        'query-only-yt-by-offset-four-balances',
    ],
)
@pytest.mark.config(
    BILLING_REPORTS_REPLICATION_OFFSET_HOURS={
        '__default__': 240,
        'v1_balances_select': 24,
    },
)
@pytest.mark.now('2018-10-04T12:00:00+00:00')
async def test_balances_select(
        taxi_billing_reports_client,
        data_path,
        load_json,
        mockserver,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        patch,
):
    json_data = load_json(data_path)
    request_body = json_data['request_body']
    expected_response = json_data['expected_response']
    expected_yql = [
        ' '.join(s.strip() for s in a_query)
        for a_query in json_data['expected_yql_queries']
    ]
    expected_yql_params = json_data['expected_yql_params']
    if json_data.get('use_yt', False):
        _turn_on_yt(monkeypatch)
    if json_data.get('compare_yt_to_pg', False):
        _turn_on_comparison(monkeypatch)

    @mockserver.json_handler('/billing-accounts/v2/balances/select')
    def _handle_balances_select(request):
        assert request.json == json_data['expected_balances_request']

        return mockserver.make_response(json=json_data['pg_balances'])

    @mockserver.json_handler('/billing-accounts/v2/accounts/search')
    def _handle_accounts_search(request):
        assert request.json == json_data['expected_accounts_request']
        return mockserver.make_response(json=json_data['pg_accounts'])

    counter = {'yt': 0}

    @patch_aiohttp_session(discovery.find_service('archive_api').url, 'POST')
    def _patch_archive_api_request(method, url, headers, json, **kwargs):
        assert 'select_rows' in url
        assert json['query']['query_string'] in expected_yql
        assert json['query']['query_params'] in expected_yql_params
        data = json_data['yt_data'][counter['yt']]
        counter['yt'] += 1
        return response_mock(
            headers={'Content-Type': 'application/json'}, json=data,
        )

    requested_resources = []

    @patch('taxi.billing.resource_limiter.ResourceLimiter.request_resources')
    def _request_resources(
            client_tvm_service_name, required_resources, log_extra,
    ):
        requested_resources.extend(required_resources)

    response = await taxi_billing_reports_client.post(
        '/v1/balances/select', json=request_body,
    )

    actual_response = await response.json()
    _compare_balances(actual_response, expected_response)

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
    'data_path',
    (
        'ten_accounts_five_entities_concurrently.json',
        'ten_accounts_five_entities_sequentially.json',
    ),
    ids=[
        'query-pg-and-yt-with-chunks-concurrently',
        'query-pg-and-yt-with-chunks-sequentially',
    ],
)
@pytest.mark.config(
    BILLING_REPORTS_REPLICATION_OFFSET_HOURS={
        '__default__': 240,
        'v1_balances_select': 24,
    },
)
@pytest.mark.now('2018-10-04T12:00:00+00:00')
async def test_chunks(
        taxi_billing_reports_client,
        data_path,
        load_json,
        mockserver,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
):
    json_data = load_json(data_path)
    request_body = json_data['request_body']
    expected_accounts_requests = json_data['expected_accounts_requests']
    expected_balances_requests = json_data['expected_balances_requests']
    expected_response = json_data['expected_response']
    if json_data.get('use_yt', False):
        _turn_on_yt(monkeypatch)
    if json_data.get('compare_yt_to_pg', False):
        _turn_on_comparison(monkeypatch)

    _setup_chunks_settings(monkeypatch, json_data['chunks_config'])

    counter = {'yt': 0, 'accounts_search': 0, 'balances_select': 0}

    @mockserver.json_handler('/billing-accounts/v2/balances/select')
    def _handle_balances_select(request):
        assert request.json in expected_balances_requests
        index = counter['balances_select']
        counter['balances_select'] += 1
        return mockserver.make_response(json=json_data['pg_balances'][index])

    @mockserver.json_handler('/billing-accounts/v2/accounts/search')
    def _handle_accounts_search(request):
        assert request.json in expected_accounts_requests
        index = counter['accounts_search']
        counter['accounts_search'] += 1
        return mockserver.make_response(json=json_data['pg_accounts'][index])

    @patch_aiohttp_session(discovery.find_service('archive_api').url, 'POST')
    def _patch_archive_api_request(method, url, headers, json, **kwargs):
        assert 'select_rows' in url
        if 'GROUP' not in json['query']['query_string']:
            accounts_count = json_data['chunks_config'][
                'yt_select_rows_balances_accounts_count'
            ]
            assert len(json['query']['query_params']) == accounts_count * 2 + 1
        data = json_data['yt_data'][counter['yt']]
        counter['yt'] += 1
        return response_mock(
            headers={'Content-Type': 'application/json'}, json=data,
        )

    response = await taxi_billing_reports_client.post(
        '/v1/balances/select', json=request_body,
    )
    assert counter['yt'] == json_data['expected_yt_queries_count']
    assert (
        counter['accounts_search']
        == json_data['expected_accounts_queries_count']
    )
    assert (
        counter['balances_select']
        == json_data['expected_balances_queries_count']
    )

    actual_response = await response.json()
    _compare_balances(actual_response, expected_response)


def _compare_balances(actual, expected):
    def _sorted_balances(response):
        result = sorted(
            response['entries'], key=lambda a: a['account']['account_id'],
        )
        for entry in result:
            entry['balances'] = sorted(
                entry['balances'], key=lambda a: a['accrued_at'], reverse=True,
            )
        return result

    actual_entries = _sorted_balances(actual)
    expected_entries = _sorted_balances(expected)

    assert actual_entries == expected_entries


@pytest.mark.parametrize(
    'data_path',
    [
        'invalid_account_filter.json',
        'accrued_at_not_truncated.json',
        'empty_accounts.json',
        'empty_accrued_at.json',
    ],
    ids=[
        'without-account_id-and-entity_id',
        'accrued_at-is-not-truncated-up-to-hours',
        'empty-accounts',
        'empty-accrued_at',
    ],
)
@pytest.mark.config(
    BILLING_REPORTS_REPLICATION_OFFSET_HOURS={
        '__default__': 240,
        'v1_balances_select': 24,
    },
    BILLING_REPORTS_BALANCES_SELECT_USE_YT=True,
    BILLING_REPORTS_BALANCES_SELECT_CMP_YT_WITH_PG=False,
)
@pytest.mark.now('2018-10-04T12:00:00+00:00')
async def test_invalid_request(
        taxi_billing_reports_client, load_json, data_path,
):
    request_body = load_json(data_path)
    response = await taxi_billing_reports_client.post(
        '/v1/balances/select', json=request_body,
    )
    assert response.status == 400


@pytest.mark.parametrize('data_path', ['block_anonym_request.json'])
@pytest.mark.now('2018-10-04T12:00:00+00:00')
async def test_resource_limiter(
        taxi_billing_reports_client, data_path, load_json, monkeypatch,
):
    json_data = load_json(data_path)
    quota_config = json_data['quota_config']
    monkeypatch.setattr(
        config.Config, 'BILLING_RESOURCE_QUOTA_SETTINGS', quota_config,
    )
    request = json_data['request_body']
    expected_response_status = json_data['expected_response_status']
    response = await taxi_billing_reports_client.post(
        '/v1/balances/select', json=request,
    )
    assert response.status == expected_response_status


def _turn_on_yt(monkeypatch):
    monkeypatch.setattr(
        config.Config, 'BILLING_REPORTS_BALANCES_SELECT_USE_YT', True,
    )


def _turn_on_comparison(monkeypatch):
    monkeypatch.setattr(
        config.Config, 'BILLING_REPORTS_BALANCES_SELECT_CMP_YT_WITH_PG', True,
    )


def _setup_chunks_settings(monkeypatch, conf_data):
    monkeypatch.setattr(
        config.Config, 'BILLING_REPORTS_BALANCES_SELECT_CHUNKS', conf_data,
    )
