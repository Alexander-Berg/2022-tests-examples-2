import pytest

from taxi import discovery

from taxi_billing_calculators.stq.tlog import task as stq_tlog_task
from . import common


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'billing_calculators', 'dst': 'billing_tlog'}],
    BILLING_CALCULATORS_SEND_ENTRIES_TO_BILLING_FIN_PAYOUTS=True,
)
async def test_tlog_send_with_tvm(
        taxi_billing_calculators_stq_tlog_ctx,
        patch_aiohttp_session,
        patch,
        response_mock,
):
    @patch('taxi.clients.tvm.TVMClient.get_ticket')
    async def _get_tmv_ticket_mock(*args, **kwargs):
        # pylint: disable=unused-argument
        return 'ticket'

    @patch_aiohttp_session(discovery.find_service('billing_tlog').url, 'POST')
    def _patch_billing_tlog_request(method, url, headers, json, **kwargs):
        # pylint: disable=unused-argument
        assert 'X-Ya-Service-Ticket' in headers
        assert headers['X-Ya-Service-Ticket'] == 'ticket'
        return response_mock(json={})

    tlog_client = taxi_billing_calculators_stq_tlog_ctx.billing_tlog_client
    await tlog_client.journal_append([])


@pytest.mark.config(
    BILLING_CALCULATORS_SEND_ENTRIES_TO_BILLING_FIN_PAYOUTS=True,
)
@pytest.mark.parametrize(
    'data', ('tlog_store.json', 'tlog_store_with_tariff_class.json'),
)
@pytest.mark.now('2018-10-17T09:06:14')
async def test_task_send_tlog(
        data,
        load_json,
        taxi_billing_calculators_stq_tlog_ctx,
        patch_aiohttp_session,
        patch,
        response_mock,
        mockserver,
):

    fixtures = load_json(data)
    doc_id = fixtures['task']['doc_id']
    expected_api_entries = fixtures['api_entries']
    expected_stq_process_calls = fixtures['expected_stq_process_calls']
    api_entries = []

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        if 'is_ready_for_processing' in url:
            return response_mock(json={'ready': True, 'doc': fixtures['task']})
        if 'finish_processing' in url:
            return response_mock(json={})
        if 'v2/journal/search' in url:
            doc_ids = [query['doc_id'] for query in json['docs']]
            all_entries = fixtures['journal_entries']
            result = []
            for _doc_id in doc_ids:
                result.extend(all_entries.get(str(_doc_id), []))
            return response_mock(json={'entries': result})
        raise NotImplementedError

    @mockserver.json_handler('/billing-accounts/v2/accounts/search')
    def _patch_billing_accounts_v2_accounts_search(request):
        return mockserver.make_response(
            json={'accounts': fixtures['accounts']},
        )

    @patch_aiohttp_session(discovery.find_service('billing_tlog').url, 'POST')
    def _patch_billing_tlog_request(method, url, headers, json, **kwargs):
        if 'v1/journal/append' in url:
            nonlocal api_entries
            api_entries = json['entries']
            return response_mock(
                json={
                    'entries': common.make_tlog_response_entries(api_entries),
                },
            )
        raise NotImplementedError

    stq_process_calls = []
    # pylint: disable=unused-variable
    @patch('taxi.clients.stq_agent.StqAgentClient.put_task')
    async def _stq_process_tlog_put(queue, task_id=None, kwargs=None):
        if queue == 'billing_fin_payouts_process_tlog_transactions':
            stq_process_calls.append(
                {'queue': queue, 'task_id': task_id, 'kwargs': kwargs},
            )
        return

    await stq_tlog_task.process_doc(
        taxi_billing_calculators_stq_tlog_ctx,
        task_info=common.create_task_info(),
        doc_id=doc_id,
    )

    assert api_entries == expected_api_entries
    assert stq_process_calls == expected_stq_process_calls
