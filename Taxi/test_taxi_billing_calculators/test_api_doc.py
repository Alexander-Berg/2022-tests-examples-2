import copy

import pytest

from taxi import discovery
from taxi.billing.clients.models import billing_calculators

from taxi_billing_calculators import settings
from taxi_billing_calculators.api import _execute
from taxi_billing_calculators.calculators import handling_exceptions


@pytest.mark.parametrize(
    'kind, expected_queue',
    [
        (
            'driver_mode_subscription',
            settings.STQ_BILLING_CALCULATORS_SUBSCRIPTIONS_QUEUE,
        ),
        ('subvention', settings.STQ_BILLING_CALCULATORS_MAIN_QUEUE),
        ('commission', settings.STQ_BILLING_CALCULATORS_MAIN_QUEUE),
        (None, settings.STQ_BILLING_CALCULATORS_MAIN_QUEUE),
    ],
)
async def test_process_doc(
        kind,
        expected_queue,
        *,
        taxi_billing_calculators_client,
        request_headers,
        patched_tvm_ticket_check,
        patched_tvm_get_headers,
        patch,
):
    actual_queue = None

    @patch('taxi.clients.stq_agent.StqAgentClient.put_task')
    async def _patch_stq_client_put(*args, **kwargs):
        nonlocal actual_queue
        actual_queue = kwargs['queue']

    data = {'doc': {'id': 1001}}
    if kind:
        data['doc']['kind'] = kind
    response = await taxi_billing_calculators_client.post(
        '/v1/process_doc', headers=request_headers, json=data,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'doc': {'id': 1001}}
    assert actual_queue == expected_queue


async def test_process_doc_invalid_data(
        taxi_billing_calculators_client, request_headers,
):
    data = {}
    response = await taxi_billing_calculators_client.post(
        '/v1/process_doc', headers=request_headers, json=data,
    )
    assert response.status == 400


@pytest.mark.parametrize(
    'testcase_path',
    [
        'test_api_execute_unknown_kind.json',
        'test_api_execute_ok.json',
        'test_api_execute_finish_handling.json',
        'test_api_execute_finish_handling_default.json',
        'test_api_execute_postponed.json',
    ],
)
async def test_execute_doc(
        testcase_path,
        *,
        load_json,
        patch_aiohttp_session,
        request_headers,
        response_mock,
        taxi_billing_calculators_client,
):
    testcase = load_json(testcase_path)
    actual_doc_update_request = {}

    async def dummy_handler(ctx, doc, log_extra):
        desired_handle_result = testcase['desired_handle_result']
        if desired_handle_result == 'ok':
            return
        if desired_handle_result == 'postpone_handling':
            raise handling_exceptions.PostponeHandling()
        if desired_handle_result == 'finish_handling_default':
            raise handling_exceptions.FinishHandling('something went wrong')
        if desired_handle_result == 'finish_handling':
            raise handling_exceptions.FinishHandling(
                message='something went wrong',
                code=billing_calculators.HandleErrorCode.NOT_FOUND_ERROR,
            )

    _execute.EXECUTE_DOC_HANDLERS['__test__'] = dummy_handler

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        if 'v1/docs/update' in url:
            actual_doc_update_request.update(copy.deepcopy(json))
            doc = testcase['request']
            doc['data'].update(json['data'])
            doc['process_at'] = '2020-04-09T00:00:00.000000+00:00'
            doc['service'] = 'billing-orders'
            doc['status'] = json['status']
            return response_mock(json=doc)
        raise NotImplementedError

    response = await taxi_billing_calculators_client.post(
        '/v1/execute_doc', headers=request_headers, json=testcase['request'],
    )
    assert response.status == testcase['expected_status']
    assert actual_doc_update_request == testcase['expected_doc_update_request']
