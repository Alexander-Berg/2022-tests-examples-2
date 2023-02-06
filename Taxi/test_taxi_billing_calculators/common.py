import copy
from typing import List
from typing import Sequence

from taxi import discovery
from taxi.stq import async_worker_ng

from taxi_billing_calculators.stq.main import task as stq_main_task


# pylint: disable=invalid-name
# pylint: disable=too-many-statements
async def test_process_doc(
        data_path,
        doc_id,
        load_json,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        taxi_billing_calculators_stq_main_ctx,
        patch,
        asserts=True,
        stq_queue_task=stq_main_task,
) -> List[tuple]:
    account_idx = 1
    doc_idx = 2001
    docs_created = []
    docs_updated = []
    entities_created = []
    accounts_created = []
    orders_created: List[dict] = []
    docs_updated_events = []
    stq_balance_update_calls = []

    json_data = load_json(data_path)
    expected_docs = json_data['expected_docs']
    expected_accounts = json_data['expected_accounts']
    expected_entities = json_data['expected_entities']
    expected_orders = json_data.get('expected_orders', [])
    expected_docs_updated = json_data.get('expected_docs_updated', [])
    expected_docs_updated_events = json_data.get(
        'expected_docs_updated_events', [],
    )
    expected_stq_balance_update_calls = json_data.get(
        'expected_stq_balance_update_calls', [],
    )

    @patch_aiohttp_session(discovery.find_service('agglomerations').url, 'GET')
    def _patch_agglomerations_request(method, url, headers, json, **kwargs):
        return response_mock(json={'oebs_mvp_id': 'mvp'})

    @mockserver.json_handler('/billing-reports/v1/docs/select')
    async def _mock_docs_select(request, *args, **kwargs):
        result = []
        for one_doc in json_data['reports']['docs/select']['docs']:
            if all(
                    one_doc[key] == value
                    for key, value in request.json.items()
                    if key in ('external_obj_id', 'kind')
            ):
                result.append(one_doc)
        return {'docs': result}

    @mockserver.json_handler('/billing-reports/v1/docs/by_id')
    async def _mock_docs_by_id(request, *args, **kwargs):
        result = []
        for one_doc in json_data['reports']['docs/by_id']['docs']:
            if one_doc['doc_id'] in request.json['doc_ids']:
                result.append(one_doc)
        return {'docs': result}

    @mockserver.json_handler('/billing-reports/v1/journal/search')
    async def _mock_journal_search(request, *args, **kwargs):
        result = []
        entries = json_data['reports']['journal/search']['entries']
        for one_entry in entries:
            if one_entry['doc_ref'] == request.json['doc_ref']:
                result.append(one_entry)
        return {'entries': result}

    @mockserver.json_handler('/billing-orders/v2/process/async')
    async def _mock_process_async(request, *args, **kwargs):
        nonlocal doc_idx

        orders_created.extend(request.json['orders'])
        orders_created.sort(key=lambda item: item['topic'])
        orders = []
        for one_order in request.json['orders']:
            new_order = one_order.copy()
            new_order['doc_id'] = doc_idx
            doc_idx += 1
            orders.append(new_order)
        return {'orders': orders}

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        nonlocal doc_idx

        if 'create' in url:
            docs_created.append(json)
            new_doc = json.copy()
            new_doc['doc_id'] = doc_idx
            doc_idx += 1
            return response_mock(json=new_doc)
        if 'execute' in url:
            new_docs = []
            for doc_to_create in json['docs']:
                doc_to_create['status'] = 'complete'
                new_doc = copy.deepcopy(doc_to_create)
                new_doc['doc_id'] = doc_idx
                new_doc['data']['status_info'] = {'status': 'success'}
                doc_idx += 1
                doc_to_create['external_obj_id'] = doc_to_create.pop('topic')
                doc_to_create['external_event_ref'] = doc_to_create.pop(
                    'external_ref',
                )
                docs_created.append(doc_to_create)
                new_docs.append(new_doc)
            return response_mock(json={'docs': new_docs})
        if 'is_ready_for_processing' in url:
            for one_doc in json_data['docs']:
                if one_doc['doc_id'] == json['doc_id']:
                    return response_mock(json={'ready': True, 'doc': one_doc})
            assert False, 'Doc not found'
        if 'search' in url:
            for one_doc in json_data['docs']:
                if one_doc['doc_id'] == json['doc_id']:
                    return response_mock(json={'docs': [one_doc]})
            assert False, 'Doc not found'
        if 'finish_processing' in url:
            return response_mock(json={})
        if 'v2/docs/update' in url:
            docs_updated_events.append(json)
            return response_mock(json=json)
        if 'update' in url:
            docs_updated.append(json)
            for one_doc in json_data['docs']:
                if one_doc['doc_id'] == json['doc_id']:
                    return response_mock(json=one_doc)
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

    @mockserver.json_handler('/billing-accounts/v2/accounts/search')
    def _patch_billing_accounts_v2_accounts_search(request):
        return mockserver.make_response(json={'accounts': []})

    @mockserver.json_handler('/billing-accounts/v1/accounts/create')
    def _patch_billing_accounts_v1_accounts_create(request):
        nonlocal account_idx

        new_acc = request.json.copy()
        new_acc['account_id'] = account_idx
        new_acc['opened'] = '2018-10-10T09:56:13.758202Z'
        account_idx += 1
        accounts_created.append(new_acc)
        return mockserver.make_response(json=new_acc)

    # pylint: disable=unused-variable
    @patch('taxi.clients.stq_agent.StqAgentClient.put_task')
    async def stq_balance_update_client_put(
            queue, eta=None, task_id=None, args=None, kwargs=None,
    ):
        if queue == 'billing_functions_internal_balance_update':
            stq_balance_update_calls.append(
                {
                    'queue': queue,
                    'eta': eta,
                    'task_id': task_id,
                    'args': args,
                    'kwargs': kwargs,
                },
            )
        return

    await stq_queue_task.process_doc(
        taxi_billing_calculators_stq_main_ctx,
        task_info=create_task_info(),
        doc_id=doc_id,
    )

    if asserts:
        assert expected_entities == entities_created
        assert expected_accounts == accounts_created
        assert expected_docs == docs_created
        assert expected_orders == orders_created
        assert expected_docs_updated == docs_updated
        assert expected_docs_updated_events == docs_updated_events
        assert expected_stq_balance_update_calls == stq_balance_update_calls
    return [
        (expected_entities, entities_created),
        (expected_accounts, accounts_created),
        (expected_docs, docs_created),
        (_sorted_orders(expected_orders), _sorted_orders(orders_created)),
        (expected_docs_updated, docs_updated),
        (expected_docs_updated_events, docs_updated_events),
        (expected_stq_balance_update_calls, stq_balance_update_calls),
    ]


def create_task_info(
        task_id='task_id',
        queue='process_doc',
        exec_tries=0,
        reschedule_counter=0,
):
    return async_worker_ng.TaskInfo(
        id=task_id,
        queue=queue,
        exec_tries=exec_tries,
        reschedule_counter=reschedule_counter,
    )


def _sorted_orders(orders: Sequence[dict]) -> Sequence[dict]:
    return sorted(
        orders, key=lambda order: (order['topic'], order['external_ref']),
    )


def make_tlog_response_entries(entries):
    entries_copy = copy.deepcopy(entries)
    for entry in entries_copy:
        entry['id'] = 1
        entry['transaction_time'] = '2019-07-17T12:00:00+03:00'
        entry['topic'] = entry.get('topic', 'topic')
        entry['partition'] = 'partition'
    return entries_copy
