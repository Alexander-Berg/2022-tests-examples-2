import copy

import pytest

from taxi import discovery


@pytest.mark.config(
    TVM_ENABLED=True,
    BILLING_ORDERS_USE_STQ_RESCHEDULE=True,
    BILLING_DO_NOT_FINISH_SUBSCRIPTION_DOC=True,
    BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS={'__default__': 10 ** 6},
)
@pytest.mark.parametrize(
    'test_data_path',
    [
        'arbitrary_wallet/arbitrary_wallet.json',
        'arbitrary_wallet/arbitrary_wallet_not_enough_funds.json',
    ],
)
async def test_execute(
        test_data_path,
        *,
        load_py_json_dir,
        patch,
        patch_aiohttp_session,
        response_mock,
        taxi_billing_orders_client,
        request_headers,
        patched_tvm_ticket_check,
        mockserver,
):
    data = load_py_json_dir('test_v2_execute', test_data_path)
    functions_request = {}

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        if 'v1/docs/create' in url:
            found_doc = data.get('doc')
            if found_doc:
                return response_mock(json=found_doc)
            doc = json.copy()
            doc['doc_id'] = 6
            doc['created'] = doc['event_at']
            doc['process_at'] = doc['event_at']
            doc['revision'] = 1
            doc.setdefault('tags', [])
            return response_mock(status=200, json=doc)
        raise NotImplementedError(f'No mock for {url}')

    @patch_aiohttp_session(
        discovery.find_service('billing_functions').url, 'POST',
    )
    def _patch_billing_functions_request(method, url, headers, json, **kwargs):
        functions_request.update(copy.deepcopy(json))
        default = {'status': 'success'}
        json['data']['status_info'] = data.get('status_info') or default
        json['status'] = 'complete'
        return response_mock(json=json)

    @patch_aiohttp_session(
        discovery.find_service('billing_subventions').url, 'POST',
    )
    def _patch_billing_subventions_request(
            method, url, headers, json, **kwargs,
    ):
        assert '/v1/rules/select' in url
        subvention_response = data['subvention_response']
        return response_mock(
            status=subvention_response['status'],
            json=subvention_response['data'],
        )

    response = await taxi_billing_orders_client.post(
        '/v2/execute', headers=request_headers, json=data['request'],
    )

    assert response.status == data['expected_response']['status']
    content = await response.json()
    assert content == data['expected_response']['data']
    assert functions_request == data['expected_functions_request']
