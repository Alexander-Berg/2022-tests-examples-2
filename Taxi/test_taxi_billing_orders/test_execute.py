import copy

import pytest

from taxi import discovery
from taxi.billing.clients.models import billing_calculators

from taxi_billing_orders import config as orders_config
from taxi_billing_orders.api import common
from taxi_billing_orders.api import exceptions

DOC_PREFAB = {
    'doc_id': 6,
    'external_event_ref': 'unknown',
    'external_obj_id': 'unknown',
    'event_at': '2020-06-05T00:00:00+00:00',
    'created': '2020-06-05T00:00:00+00:00',
    'kind': 'unknown',
    'status': 'complete',
    'data': {},
}


@pytest.mark.config(
    TVM_ENABLED=True,
    BILLING_SUBSCRIPTION_DETAILS_MAX_BYTES=64,
    BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS={'__default__': 10 ** 6},
)
@pytest.mark.parametrize(
    'test_data_path',
    [
        'subscribe_driver_fix.json',
        'subscribe_driver_fix_error_resp.json',
        'subscribe_orders.json',
        'subscribe_orders_with_settings.json',
        'subscribe_details_too_large.json',
    ],
)
async def test_execute(
        test_data_path,
        load_py_json_dir,
        patch_aiohttp_session,
        response_mock,
        taxi_billing_orders_client,
        request_headers,
        patched_tvm_ticket_check,
):
    data = load_py_json_dir('test_execute', test_data_path)

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        assert '/v1/docs/create' in url
        doc = json.copy()
        doc['doc_id'] = 111111
        doc['created'] = doc['event_at']
        doc['entry_ids'] = []
        doc['revision'] = 456823
        return response_mock(status=200, json=doc)

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
        '/v1/execute', headers=request_headers, json=data['request'],
    )

    assert response.status == data['expected_response']['status']

    assert len(_patch_billing_docs_request.calls) == data['docs_calls']
    assert (
        len(_patch_billing_subventions_request.calls)
        == data['subventions_calls']
    )

    content = await response.json()

    assert content == data['expected_response']['data']


@pytest.mark.config(
    TVM_ENABLED=True,
    BILLING_ORDERS_USE_STQ_RESCHEDULE=True,
    BILLING_DO_NOT_FINISH_SUBSCRIPTION_DOC=True,
    BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS={'__default__': 10 ** 6},
)
@pytest.mark.parametrize(
    'test_data_path',
    [
        # billing_wallet
        'billing_wallet/billing_wallet_create.json',
        'billing_wallet/billing_wallet_create_twice.json',
        'billing_wallet/billing_wallet_topup.json',
        'billing_wallet/billing_wallet_topup_payment.json',
        'billing_wallet/billing_wallet_topup_refund.json',
        'billing_wallet/billing_wallet_topup_no_wallet.json',
        'billing_wallet/billing_wallet_withdraw.json',
        'billing_wallet/billing_wallet_withdraw_payment.json',
        'billing_wallet/billing_wallet_withdraw_refund.json',
        'billing_wallet/billing_wallet_withdraw_no_wallet.json',
        'billing_wallet/billing_wallet_withdraw_not_enough_funds.json',
        # subscriptions
        'driver_mode_subscription/subscribe_driver_fix.json',
    ],
)
async def test_execute_via_calculators(
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
    data = load_py_json_dir('test_execute', test_data_path)
    calculators_request = {}

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
            doc.setdefault('tags', [])
            return response_mock(status=200, json=doc)
        raise NotImplementedError(f'No mock for {url}')

    @patch_aiohttp_session(
        discovery.find_service('billing_calculators').url, 'POST',
    )
    def _patch_billing_calculators_request(
            method, url, headers, json, **kwargs,
    ):
        calculators_request.update(copy.deepcopy(json))
        if 'v1/process_doc' in url:
            return response_mock(json=json)
        if 'v1/execute_doc' in url:
            default = {'status': 'success'}
            json['data']['status_info'] = data.get('status_info') or default
            json['status'] = 'complete'
            return response_mock(json=json)
        raise NotImplementedError(f'No mock for {url}')

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

    @patch('taxi.stq.client.put')
    async def _patch_stq_client_put(*args, **kwargs):
        pass

    response = await taxi_billing_orders_client.post(
        '/v1/execute', headers=request_headers, json=data['request'],
    )

    assert len(_patch_billing_subventions_request.calls) == data.get(
        'expected_num_subventions_calls', 0,
    )
    assert response.status == data['expected_response']['status']
    content = await response.json()
    assert content == data['expected_response']['data']
    assert len(_patch_stq_client_put.calls) == data['expected_num_stq_calls']
    assert calculators_request == data['expected_calculators_request']


@pytest.mark.parametrize(
    'testcase, expected_exc',
    [
        (
            {
                'status': 'complete',
                'data': {'status_info': {'status': 'success'}},
            },
            None,
        ),
        (
            {'status': 'new', 'data': {'status_info': {'status': 'success'}}},
            None,
        ),
        ({'status': 'new'}, ValueError),
        (
            {
                'status': 'complete',
                'data': {
                    'status_info': {
                        'status': 'failed',
                        'code': 'bad_request_error',
                    },
                },
            },
            exceptions.BadRequestError,
        ),
        (
            {
                'status': 'complete',
                'data': {
                    'status_info': {
                        'status': 'failed',
                        'code': 'conflict_error',
                    },
                },
            },
            exceptions.ConflictError,
        ),
        (
            {
                'status': 'complete',
                'data': {
                    'status_info': {
                        'status': 'failed',
                        'code': 'unknown_error',
                    },
                },
            },
            ValueError,
        ),
    ],
)
def test_reraise_execution_exception(testcase, expected_exc):
    # pylint: disable=protected-access
    data = copy.deepcopy(DOC_PREFAB)
    data.update(testcase)
    doc = billing_calculators.DocExecuteResponse.from_json(data)
    if expected_exc:
        with pytest.raises(expected_exc):
            common._reraise_execution_exceptions(doc)
    else:
        common._reraise_execution_exceptions(doc)


@pytest.mark.config(
    TVM_ENABLED=True, BILLING_SUBSCRIPTION_DETAILS_MAX_BYTES=64,
)
@pytest.mark.parametrize(
    'test_data_path',
    [
        'subscribe_driver_fix.json',
        'subscribe_driver_fix_error_resp.json',
        'subscribe_orders.json',
        'subscribe_orders_with_settings.json',
        'subscribe_details_too_large.json',
    ],
)
async def test_execute_event_at(
        test_data_path,
        load_py_json_dir,
        patch_aiohttp_session,
        response_mock,
        taxi_billing_orders_client,
        request_headers,
        patched_tvm_ticket_check,
        monkeypatch,
):
    data = load_py_json_dir('test_execute', test_data_path)

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        assert '/v1/docs/create' in url
        doc = json.copy()
        doc['doc_id'] = 111111
        doc['created'] = doc['event_at']
        doc['entry_ids'] = []
        doc['revision'] = 456823
        return response_mock(status=200, json=doc)

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

    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS',
        {'__default__': 24},
    )
    response = await taxi_billing_orders_client.post(
        '/v1/execute', headers=request_headers, json=data['request'],
    )

    assert response.status == 400

    monkeypatch.setattr(
        orders_config.Config,
        'BILLING_ORDERS_EVENT_LIMIT_KIND_HOURS',
        {'__default__': 10 ** 6},
    )
    response = await taxi_billing_orders_client.post(
        '/v1/execute', headers=request_headers, json=data['request'],
    )

    assert response.status == data['expected_response']['status']
