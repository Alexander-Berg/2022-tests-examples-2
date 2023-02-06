import pytest

from taxi import discovery

from taxi_billing_calculators.stq.main import task as stq_main_task
from . import common


@pytest.mark.config(BILLING_GET_MVP_OEBS_ID=True)
@pytest.mark.parametrize(
    'data_path',
    [
        'tlog_workshift_bought.json',
        'tlog_workshift_bought_with_tariff_class.json',
        pytest.param(
            'b2b_trip_payment_no_reversal.json',
            marks=pytest.mark.config(BILLING_TLOG_REBATE_ENABLED=True),
        ),
        pytest.param(
            'b2b_trip_payment_with_non_detailed_reversal.json',
            marks=pytest.mark.config(BILLING_TLOG_REBATE_ENABLED=True),
        ),
        'b2b_trip_payment_no_reversal_with_tariff_class.json',
        pytest.param(
            'b2b_trip_payment_test_trip.json',
            marks=pytest.mark.config(BILLING_TLOG_REBATE_ENABLED=True),
        ),
        pytest.param(
            'b2b_trip_payment_with_detailed_reversal_with_payment_transaction'
            '.json',
            marks=pytest.mark.config(BILLING_TLOG_REBATE_ENABLED=True),
        ),
        pytest.param(
            'b2b_trip_payment_with_detailed_reversal_with_refund_transaction'
            '.json',
            marks=pytest.mark.config(BILLING_TLOG_REBATE_ENABLED=True),
        ),
        pytest.param(
            'b2b_trip_payment_no_decoupling_and_no_rebate.json',
            marks=pytest.mark.config(BILLING_TLOG_REBATE_ENABLED=True),
        ),
        pytest.param(
            'b2b_trip_payment_with_entries.json',
            marks=pytest.mark.config(
                BILLING_CALCULATORS_SEND_B2B_TRIP_PAYMENT_CUSTOM_ENTRIES=True,
            ),
        ),
        pytest.param(
            'b2b_trip_payment_with_external_rebate_std.json',
            marks=pytest.mark.config(
                BILLING_TLOG_REBATE_ENABLED=True,
                BILLING_CALCULATORS_B2B_EVENT_REBATE_MIGRATION={
                    'b2b_trip_payment': {'__default__': {}},
                },
            ),
            id='external_rebate_off_use_internal',
        ),
        pytest.param(
            'b2b_trip_payment_with_external_rebate_std.json',
            marks=pytest.mark.config(
                BILLING_TLOG_REBATE_ENABLED=True,
                BILLING_CALCULATORS_B2B_EVENT_REBATE_MIGRATION={
                    'b2b_trip_payment': {
                        '__default__': {
                            'enabled': [
                                {'since': '1999-06-18T07:15:00+00:00'},
                            ],
                        },
                    },
                },
            ),
            id='external_rebate_on_and_have_same_value_use_external',
        ),
        pytest.param(
            'b2b_trip_payment_with_external_rebate_ng.json',
            marks=pytest.mark.config(
                BILLING_TLOG_REBATE_ENABLED=True,
                BILLING_CALCULATORS_B2B_EVENT_REBATE_MIGRATION={
                    'b2b_trip_payment': {
                        '__default__': {
                            'enabled': [
                                {'since': '1999-06-18T07:15:00+00:00'},
                            ],
                        },
                    },
                },
            ),
            id='external_rebate_on_and_have_different_value_use_external',
        ),
        pytest.param(
            'b2b_trip_payment_with_external_rebate_ng_with_bounds.json',
            marks=pytest.mark.config(
                BILLING_TLOG_REBATE_ENABLED=True,
                BILLING_CALCULATORS_B2B_EVENT_REBATE_MIGRATION={
                    'b2b_trip_payment': {
                        '__default__': {
                            'enabled': [
                                {'since': '1999-06-18T07:15:00+00:00'},
                            ],
                        },
                    },
                },
            ),
            id=(
                'external_rebate_on_and_have_'
                'different_value_use_external_with_max_cost'
            ),
        ),
    ],
)
@pytest.mark.config(
    BILLING_TLOG_IGNORE_EVENTS_WITH_DUE_BEFORE={
        '__default__': '2018-01-01T00:00:00+00:00',
    },
)
# pylint: too-many-locals
async def test_process_tlog_doc(
        data_path,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_main_ctx,
):
    account_idx = 1
    accounts_created_idx = {}
    docs_created = []
    doc_idx = 6000
    entities_created = []
    accounts_created = []
    docs_finished = []

    json_data = load_json(data_path)
    event = json_data['event']
    expected_docs = json_data['expected_docs']
    expected_accounts = json_data['expected_accounts']
    expected_entities = json_data['expected_entities']
    expected_docs_finished = json_data['expected_docs_finished']
    docs_chain = json_data['docs_chain']
    doc_journal_entries = json_data['doc_journal_entries']

    @patch_aiohttp_session(discovery.find_service('agglomerations').url, 'GET')
    def _patch_agglomerations_request(method, url, headers, json, **kwargs):
        return response_mock(json={'oebs_mvp_id': 'mvp'})

    @mockserver.json_handler('/billing-reports/v1/docs/select')
    async def _mock_docs_select(request, *args, **kwargs):
        return {'docs': docs_chain}

    @mockserver.json_handler('/billing-commissions/v1/rebate/match')
    async def _mock_rebate_match(request, *args, **kwargs):
        return json_data.get('billing_commission_response', {})

    @mockserver.json_handler('/billing-reports/v1/journal/search')
    async def _mock_journal_search(request, *args, **kwargs):
        doc_id = request.json['doc_ref']
        return {'entries': doc_journal_entries[str(doc_id)]}

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        nonlocal doc_idx
        if 'create' in url:
            if json['kind'] == 'bypass_b2b_trip_payment':
                alias_id = json['data']['alias_id']
                version = json['data']['version']
                assert (
                    json['external_obj_id']
                    == f'taxi/bypass_b2b_trip_payment/{alias_id}'
                )
                assert (
                    json['external_event_ref']
                    == f'taxi/bypass_b2b_trip_payment/{alias_id}/{version}'
                )
                return response_mock(json={'doc_id': 100500})
            new_doc = json.copy()
            new_doc['doc_id'] = doc_idx
            doc_idx += 10
            docs_created.append(new_doc)
            return response_mock(json=new_doc)
        if 'search' in url:
            return response_mock(json={'docs': docs_chain})
        if 'is_ready_for_processing' in url:
            return response_mock(json={'ready': True, 'doc': event})
        if 'finish_processing' in url:
            docs_finished.append(json)
            return response_mock(json={})
        if 'update' in url:
            updated_doc = event.copy()
            updated_doc['data'].update(json['data'])
            return response_mock(json=updated_doc)
        return None

    @patch_aiohttp_session(
        discovery.find_service('billing_accounts').url, 'POST',
    )
    def _patch_billing_accounts_request(method, url, headers, json, **kwargs):
        nonlocal account_idx
        nonlocal accounts_created_idx

        if 'accounts/create' in url:
            new_acc = json.copy()
            new_acc_with_idx = accounts_created_idx.get(
                tuple(sorted(new_acc.items())),
            )
            if new_acc_with_idx is None:
                new_acc_with_idx = new_acc.copy()
                new_acc_with_idx['account_id'] = account_idx
                new_acc_with_idx['opened'] = '2018-10-10T09:56:13.758202Z'
                accounts_created_idx[
                    tuple(sorted(new_acc.items()))
                ] = new_acc_with_idx
                account_idx += 1
                accounts_created.append(new_acc_with_idx)
            return response_mock(json=new_acc_with_idx)
        return None

    @mockserver.json_handler('/billing-accounts/v1/entities/search')
    def _patch_billing_accounts_entities_search(request):
        return mockserver.make_response(json=[])

    @mockserver.json_handler('/billing-accounts/v1/entities/create')
    def _patch_billing_accounts_entities_create(request):
        new_entity = request.json.copy()
        new_entity['created'] = '2018-10-10T09:56:13.758202Z'
        entities_created.append(request.json)
        return mockserver.make_response(json=new_entity)

    @mockserver.json_handler('/billing-accounts/v1/accounts/search')
    def _patch_billing_accounts_v1_accounts_search(request):
        return mockserver.make_response(json=[])

    @mockserver.json_handler('/billing-accounts/v1/accounts/create')
    def _patch_billing_accounts_v1_accounts_create(request):
        nonlocal account_idx
        nonlocal accounts_created_idx

        new_acc = request.json.copy()
        new_acc_with_idx = accounts_created_idx.get(
            tuple(sorted(new_acc.items())),
        )
        if new_acc_with_idx is None:
            new_acc_with_idx = new_acc.copy()
            new_acc_with_idx['account_id'] = account_idx
            new_acc_with_idx['opened'] = '2018-10-10T09:56:13.758202Z'
            accounts_created_idx[
                tuple(sorted(new_acc.items()))
            ] = new_acc_with_idx
            account_idx += 1
            accounts_created.append(new_acc_with_idx)
        return mockserver.make_response(json=new_acc_with_idx)

    @mockserver.json_handler('/billing-replication/v1/active-contracts/')
    def _patch_billing_replication_v1_active_contracts(request):
        return mockserver.make_response(
            json=[
                {
                    'ID': request.query['service_id'],
                    'DT': '2020-03-05 00:00:00',
                },
            ],
        )

    await stq_main_task.process_doc(
        taxi_billing_calculators_stq_main_ctx,
        task_info=common.create_task_info(),
        doc_id=event['doc_id'],
    )

    assert entities_created == expected_entities
    assert accounts_created == expected_accounts
    assert docs_created == expected_docs
    assert docs_finished == expected_docs_finished


@pytest.mark.parametrize(
    'data_path',
    ['tlog_workshift_bought.json', 'b2b_trip_payment_no_reversal.json'],
)
@pytest.mark.config(
    BILLING_TLOG_IGNORE_EVENTS_WITH_DUE_BEFORE={
        '__default__': '2019-05-01T00:00:00+00:00',
    },
)
# pylint: disable=invalid-name
async def test_process_tlog_doc_ignored_by_due_date(
        data_path,
        load_json,
        mockserver,
        patch_aiohttp_session,
        response_mock,
        taxi_billing_calculators_stq_main_ctx,
):
    json_data = load_json(data_path)
    event = json_data['event']
    docs_chain = json_data['docs_chain']
    finish_reason = ''

    @mockserver.json_handler('/billing-reports/v1/docs/select')
    async def _mock_docs_select(request, *args, **kwargs):
        return {'docs': docs_chain}

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        nonlocal finish_reason
        if 'is_ready_for_processing' in url:
            return response_mock(json={'ready': True, 'doc': event})
        if 'search' in url:
            return response_mock(json={'docs': docs_chain})
        if 'finish_processing' in url:
            finish_reason = json['details']['reason']
            return response_mock(json={})
        if 'create' in url:
            assert json['kind'] == 'bypass_b2b_trip_payment'
            return response_mock(json={'doc_id': 1000})
        if 'update' in url:
            updated_doc = event.copy()
            updated_doc['data'].update(json['data'])
            return response_mock(json=updated_doc)
        raise AssertionError('Unexpected call to billing-docs')

    @patch_aiohttp_session(
        discovery.find_service('billing_accounts').url, 'POST',
    )
    def _patch_billing_accounts_request(method, url, headers, json, **kwargs):
        raise AssertionError('Unexpected call to billing-accounts')

    @mockserver.json_handler('/billing-replication/v1/active-contracts/')
    def _patch_billing_replication_v1_active_contracts(request):
        return mockserver.make_response(
            json=[
                {
                    'ID': request.query['service_id'],
                    'DT': '2020-03-05 00:00:00',
                },
            ],
        )

    await stq_main_task.process_doc(
        taxi_billing_calculators_stq_main_ctx,
        task_info=common.create_task_info(),
        doc_id=1000,
    )
    assert finish_reason.startswith('Due date is absent or too old')
