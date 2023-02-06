import pytest

from taxi.billing.util import dates

from taxi_billing_reports import config as orders_config
from taxi_billing_reports.models import doc as doc_models

OK_RESPONSE = 200
FORBIDDEN_RESPONSE = 403

GROUPS_RULES = {
    'full_access_group': {
        'accounts': [{'kind': '%', 'agreement': '%'}],
        'documents': [{'external_obj_id': '%'}],
        'tags': [{'tag': '%'}],
    },
    'valid_access_group': {
        'accounts': [
            {'kind': 'driver', 'agreement': '%driver_balance%'},
            {'kind': 'park', 'agreement': '%driver_balance%'},
            {'kind': 'driver', 'agreement': 'taxi/yandex_ride'},
        ],
        'documents': [{'external_obj_id': 'taxi/subvention/%'}],
        'tags': [{'tag': 'taxi/alias_id/%'}, {'tag': 'alias_id/%'}],
    },
    'restricted_access_group': {
        'accounts': [{'kind': 'test', 'agreement': 'test'}],
        'documents': [{'external_obj_id': 'test'}],
        'tags': [{'tag': 'test%'}],
    },
}
SERVICE_GROUPS_FULL_ACCESS = {'billing-reports': ['full_access_group']}
SERVICE_GROUPS_VALID_ACCESS = {'billing-reports': ['valid_access_group']}
SERVICE_GROUPS_RESTRICTED_ACCESS = {
    'billing-reports': ['restricted_access_group'],
}


@pytest.mark.config(BILLING_AUTH_GROUPS_RULES=GROUPS_RULES, TVM_ENABLED=True)
@pytest.mark.parametrize(
    'test_data_path',
    [
        'journal_select.json',
        'journal_select_duplicates.json',
        'journal_select_empty.json',
        'journal_select_limit.json',
        'journal_select_cursor.json',
        'journal_select_skip_zero.json',
        'journal_select_via_mask.json',
    ],
)
async def test_auth_journal_select(
        test_data_path,
        patch,
        load_py_json_dir,
        request_headers,
        monkeypatch,
        patched_tvm_ticket_check,
        taxi_billing_reports_client,
):
    data = load_py_json_dir(
        'test_v1_journal/test_journal_select', test_data_path,
    )

    @patch('taxi_billing_reports.actions.journal_select._fetch_pg_data')
    async def _patch_fetch_pg_data(*args, **kwargs):
        return [], 0

    @patch('taxi_billing_reports.actions.journal_select._query_yt')
    async def _patch_fetch_query_yt(*args, **kwargs):
        return [], 0

    # Test positive result with turned off Auth
    monkeypatch.setattr(orders_config.Config, 'BILLING_AUTH_ENABLED', False)

    response = await taxi_billing_reports_client.post(
        '/v1/journal/select',
        headers=request_headers,
        json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test positive result with turned on Auth and full access
    monkeypatch.setattr(orders_config.Config, 'BILLING_AUTH_ENABLED', True)
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_FULL_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v1/journal/select',
        headers=request_headers,
        json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test positive result with turned on Auth and valid for this rules request
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_VALID_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v1/journal/select',
        headers=request_headers,
        json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test negative result with turned on Auth and non-valid request for rules
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_RESTRICTED_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v1/journal/select',
        headers=request_headers,
        json=data['request_body'],
    )
    assert response.status == FORBIDDEN_RESPONSE


@pytest.mark.config(BILLING_AUTH_GROUPS_RULES=GROUPS_RULES, TVM_ENABLED=True)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                BILLING_REPORTS_JOURNAL_BY_TAG_FETCH_DOC_IDS=True,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_REPORTS_JOURNAL_BY_TAG_FETCH_DOC_IDS=False,
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'test_data_path',
    [
        'journal_by_tag.json',
        'journal_by_tag_duplicates.json',
        'journal_by_tag_only_pg.json',
        'journal_by_tag_only_yt.json',
        'journal_by_tag_skip_zero.json',
    ],
)
async def test_auth_journal_select_by_tag(
        test_data_path,
        patch,
        load_py_json_dir,
        request_headers,
        monkeypatch,
        patched_tvm_ticket_check,
        taxi_billing_reports_client,
):
    data = load_py_json_dir(
        'test_v2_journal/test_journal_by_tag', test_data_path,
    )

    @patch(
        'taxi_billing_reports.pg.journal_store.JournalStore.'
        'v2_by_tag_fetch_doc_ids_only',
    )
    async def _patch_fetch_pg_journalstore_v2_by_tag_1(*args, **kwargs):
        return {}, []

    @patch(
        'taxi_billing_reports.pg.journal_store.JournalStore.'
        'v2_by_tag_fetch_full_docs',
    )
    async def _patch_fetch_pg_journalstore_v2_by_tag_2(*args, **kwargs):
        return {}, []

    @patch('taxi_billing_reports.yt.journal_store.JournalStore.v2_by_tag')
    async def _patch_fetch_yt_journalstore_v2_by_tag(*args, **kwargs):
        return {}, []

    # Test positive result with turned off Auth
    monkeypatch.setattr(orders_config.Config, 'BILLING_AUTH_ENABLED', False)

    response = await taxi_billing_reports_client.post(
        '/v2/journal/by_tag',
        headers=request_headers,
        json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test positive result with turned on Auth and full access
    monkeypatch.setattr(orders_config.Config, 'BILLING_AUTH_ENABLED', True)
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_FULL_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v2/journal/by_tag',
        headers=request_headers,
        json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test positive result with turned on Auth and valid for this rules request
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_VALID_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v2/journal/by_tag',
        headers=request_headers,
        json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test negative result with turned on Auth and non-valid request for rules
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_RESTRICTED_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v2/journal/by_tag',
        headers=request_headers,
        json=data['request_body'],
    )
    assert response.status == FORBIDDEN_RESPONSE


@pytest.mark.config(BILLING_AUTH_GROUPS_RULES=GROUPS_RULES, TVM_ENABLED=True)
@pytest.mark.parametrize('test_data_path', ['one_account_one_accrued_at.json'])
async def test_auth_balances_select(
        test_data_path,
        patch,
        load_py_json_dir,
        request_headers,
        monkeypatch,
        patched_tvm_ticket_check,
        taxi_billing_reports_client,
):
    data = load_py_json_dir(
        'test_v1_balances/test_balances_select', test_data_path,
    )

    @patch('taxi_billing_reports.pg.balance_store.BalanceStore.select')
    async def _patch_fetch_asyncio_tasks(*args, **kwargs):
        return []

    # Test positive result with turned off Auth
    monkeypatch.setattr(orders_config.Config, 'BILLING_AUTH_ENABLED', False)

    response = await taxi_billing_reports_client.post(
        '/v1/balances/select',
        headers=request_headers,
        json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test positive result with turned on Auth and full access
    monkeypatch.setattr(orders_config.Config, 'BILLING_AUTH_ENABLED', True)
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_FULL_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v1/balances/select',
        headers=request_headers,
        json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test positive result with turned on Auth and valid for this rules request
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_VALID_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v1/balances/select',
        headers=request_headers,
        json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test negative result with turned on Auth and non-valid request for rules
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_RESTRICTED_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v1/balances/select',
        headers=request_headers,
        json=data['request_body'],
    )
    assert response.status == FORBIDDEN_RESPONSE


@pytest.mark.config(BILLING_AUTH_GROUPS_RULES=GROUPS_RULES, TVM_ENABLED=True)
@pytest.mark.parametrize(
    'test_data_path',
    [
        'docs_sorted.json',
        'docs_by_external_event_ref_pg_pages_empty.json',
        'docs_only_pg.json',
        'docs_by_external_event_ref_yt.json',
        'docs_only_yt.json',
        'docs_desc.json',
        'docs_by_external_event_ref_pg.json',
        'docs.json',
        'docs_pass_cursor.json',
        'docs_duplicates.json',
    ],
)
async def test_auth_docs_select(
        test_data_path,
        patch,
        load_py_json_dir,
        request_headers,
        monkeypatch,
        patched_tvm_ticket_check,
        taxi_billing_reports_client,
):
    data = load_py_json_dir('test_v1_docs', test_data_path)

    @patch('taxi_billing_reports.pg.doc_store.DocStore.select')
    async def _patch_fetch_pg_docs_select(*args, **kwargs):
        return []

    @patch('taxi_billing_reports.yt.doc_store.DocStore.select')
    async def _patch_fetch_yt_docs_select(*args, **kwargs):
        return []

    # Test positive result with turned off Auth
    monkeypatch.setattr(orders_config.Config, 'BILLING_AUTH_ENABLED', False)

    response = await taxi_billing_reports_client.post(
        '/v1/docs/select', headers=request_headers, json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test positive result with turned on Auth and full access
    monkeypatch.setattr(orders_config.Config, 'BILLING_AUTH_ENABLED', True)
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_FULL_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v1/docs/select', headers=request_headers, json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test positive result with turned on Auth and valid for this rules request
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_VALID_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v1/docs/select', headers=request_headers, json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test negative result with turned on Auth and non-valid request for rules
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_RESTRICTED_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v1/docs/select', headers=request_headers, json=data['request_body'],
    )
    assert response.status == FORBIDDEN_RESPONSE


@pytest.mark.config(BILLING_AUTH_GROUPS_RULES=GROUPS_RULES, TVM_ENABLED=True)
@pytest.mark.parametrize(
    'test_data_path',
    [
        'docs_sorted.json',
        'docs_by_external_ref_pg_pages_empty.json',
        'docs_only_pg.json',
        'docs_by_external_ref_yt.json',
        'docs_only_yt.json',
        'docs_desc.json',
        'docs_by_external_ref_pg.json',
        'docs.json',
        'docs_projection.json',
        'docs_duplicates.json',
    ],
)
async def test_auth_v2_docs_select(
        test_data_path,
        patch,
        load_py_json_dir,
        request_headers,
        monkeypatch,
        patched_tvm_ticket_check,
        taxi_billing_reports_client,
):
    data = load_py_json_dir('test_v2_docs_select', test_data_path)

    @patch('taxi_billing_reports.pg.doc_store.DocStore.select')
    async def _patch_fetch_pg_docs_select(*args, **kwargs):
        return []

    @patch('taxi_billing_reports.yt.doc_store.DocStore.select')
    async def _patch_fetch_yt_docs_select(*args, **kwargs):
        return []

    # Test positive result with turned off Auth
    monkeypatch.setattr(orders_config.Config, 'BILLING_AUTH_ENABLED', False)

    response = await taxi_billing_reports_client.post(
        '/v2/docs/select', headers=request_headers, json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test positive result with turned on Auth and full access
    monkeypatch.setattr(orders_config.Config, 'BILLING_AUTH_ENABLED', True)
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_FULL_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v2/docs/select', headers=request_headers, json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test positive result with turned on Auth and valid for this rules request
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_VALID_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v2/docs/select', headers=request_headers, json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test negative result with turned on Auth and non-valid request for rules
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_RESTRICTED_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v2/docs/select', headers=request_headers, json=data['request_body'],
    )
    assert response.status == FORBIDDEN_RESPONSE


@pytest.mark.config(BILLING_AUTH_GROUPS_RULES=GROUPS_RULES, TVM_ENABLED=True)
@pytest.mark.parametrize(
    'test_data_path',
    [
        'pg_only_docs_empty.json',
        'pg_only_docs.json',
        'pg_only_docs_with_cursor.json',
        'yt_only_docs.json',
        'yt_only_docs_with_cursor.json',
        'pg_and_yt_docs.json',
        'pg_and_yt_docs_with_cursor.json',
        'pg_and_yt_docs_with_limit.json',
    ],
)
async def test_auth_docs_by_tag(
        test_data_path,
        patch,
        load_py_json_dir,
        request_headers,
        monkeypatch,
        patched_tvm_ticket_check,
        taxi_billing_reports_client,
):
    data = load_py_json_dir('test_v1_docs_by_tag', test_data_path)

    @patch('taxi_billing_reports.pg.doc_store.DocStore.by_tag')
    async def _patch_fetch_pg_docs_select(*args, **kwargs):
        return []

    @patch('taxi_billing_reports.yt.doc_store.DocStore.by_tag')
    async def _patch_fetch_yt_docs_select(*args, **kwargs):
        return []

    # Test positive result with turned off Auth
    monkeypatch.setattr(orders_config.Config, 'BILLING_AUTH_ENABLED', False)

    response = await taxi_billing_reports_client.post(
        '/v1/docs/by_tag', headers=request_headers, json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test positive result with turned on Auth and full access
    monkeypatch.setattr(orders_config.Config, 'BILLING_AUTH_ENABLED', True)
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_FULL_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v1/docs/by_tag', headers=request_headers, json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test positive result with turned on Auth and valid for this rules request
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_VALID_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v1/docs/by_tag', headers=request_headers, json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test negative result with turned on Auth and non-valid request for rules
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_RESTRICTED_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v1/docs/by_tag', headers=request_headers, json=data['request_body'],
    )
    assert response.status == FORBIDDEN_RESPONSE


@pytest.mark.config(BILLING_AUTH_GROUPS_RULES=GROUPS_RULES, TVM_ENABLED=True)
@pytest.mark.parametrize(
    'test_data_path',
    [
        'pg_and_yt_docs.json',
        'pg_and_yt_docs_empty.json',
        'pg_only_docs.json',
        'yt_only_docs.json',
    ],
)
async def test_auth_docs_by_id(
        test_data_path,
        patch,
        load_py_json_dir,
        request_headers,
        monkeypatch,
        patched_tvm_ticket_check,
        taxi_billing_reports_client,
):
    data = load_py_json_dir('test_v1_docs_by_id', test_data_path)

    @patch('taxi_billing_reports.pg.doc_store.DocStore.search_by_id')
    async def _patch_fetch_pg_docs_select(*args, **kwargs):
        return [
            doc_models.V2Doc(
                doc_id=25031235,
                data={
                    'alias_id': '3295fd59714d23edbeadd65a3168cfe1',
                    'based_on_doc_id': 25031235,
                    'order_id': 'b16f99de28662f25909446dec4035884',
                    'version': 1,
                },
                created=dates.parse_datetime_fromisoformat(
                    '2020-04-15T17:21:18.929141+00:00',
                ),
                event_at=dates.parse_datetime_fromisoformat(
                    '2020-04-15T17:10:05.000000+00:00',
                ),
                external_ref='taxi/3295fd59714d23edbeadd65a3168cfe1',
                topic='taxi/subvention/on_hold/',
                kind='journal',
                process_at=dates.parse_datetime_fromisoformat(
                    '2020-04-15T17:21:18.935056+00:00',
                ),
                service='billing-calculators',
                entry_ids=[],
                revision=561544,
                status='complete',
                tags=['alias_id/3295fd59714d23edbeadd65a3168cfe1'],
                source=doc_models.Source.PG.value,
            ),
        ]

    @patch('taxi_billing_reports.yt.doc_store.DocStore.search_by_id')
    async def _patch_fetch_yt_docs_select(*args, **kwargs):
        return [
            doc_models.V2Doc(
                doc_id=25031234,
                data={
                    'alias_id': '3295fd59711234edbeadd65a3168cfe1',
                    'based_on_doc_id': 25031234,
                    'order_id': 'b16f99de28662f25909446dec4035884',
                    'version': 1,
                },
                created=dates.parse_datetime_fromisoformat(
                    '2020-04-10T17:21:18.929141+00:00',
                ),
                event_at=dates.parse_datetime_fromisoformat(
                    '2020-04-10T17:10:05.000000+00:00',
                ),
                external_ref='taxi/3295fd59711234edbeadd65a3168cfe1',
                topic='taxi/subvention/on_hold/',
                kind='journal',
                process_at=dates.parse_datetime_fromisoformat(
                    '2020-04-10T17:21:18.935056+00:00',
                ),
                service='billing-calculators',
                entry_ids=[],
                revision=43634167436,
                status='complete',
                tags=['alias_id/3295fd59711234edbeadd65a3168cfe1'],
                source=doc_models.Source.YT_SENECA.value,
            ),
        ]

    # Test positive result with turned off Auth
    monkeypatch.setattr(orders_config.Config, 'BILLING_AUTH_ENABLED', False)

    response = await taxi_billing_reports_client.post(
        '/v1/docs/by_id', headers=request_headers, json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test positive result with turned on Auth and full access
    monkeypatch.setattr(orders_config.Config, 'BILLING_AUTH_ENABLED', True)
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_FULL_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v1/docs/by_id', headers=request_headers, json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test positive result with turned on Auth and valid for this rules request
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_VALID_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v1/docs/by_id', headers=request_headers, json=data['request_body'],
    )
    assert response.status == OK_RESPONSE

    # Test negative result with turned on Auth and non-valid request for rules
    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_AUTH_SERVICE_GROUPS',
        SERVICE_GROUPS_RESTRICTED_ACCESS,
    )
    response = await taxi_billing_reports_client.post(
        '/v1/docs/by_id', headers=request_headers, json=data['request_body'],
    )
    assert response.status == FORBIDDEN_RESPONSE
