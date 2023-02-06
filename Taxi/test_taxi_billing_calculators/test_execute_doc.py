import copy
import datetime

import pytest
import pytz

from taxi import discovery

_NOW = datetime.datetime(2020, 12, 21, tzinfo=pytz.utc)


@pytest.mark.parametrize(
    'test_data_path, expected_data_path',
    [
        ('create.json', 'create_expected.json'),
        ('create_twice.json', 'create_twice_expected.json'),
        ('topup.json', 'topup_expected.json'),
        ('topup_taxi.json', 'topup_taxi_expected.json'),
        ('topup_no_account.json', 'topup_no_account_expected.json'),
        ('topup_with_payload.json', 'topup_with_payload_expected.json'),
        ('withdraw.json', 'withdraw_expected.json'),
        ('withdraw_no_account.json', 'withdraw_no_account_expected.json'),
        (
            'withdraw_not_enough_funds.json',
            'withdraw_not_enough_funds_expected.json',
        ),
        ('topup_payment.json', 'topup_payment_expected.json'),
        ('withdraw_refund.json', 'withdraw_refund_expected.json'),
        ('withdraw_payment.json', 'withdraw_payment_expected.json'),
        ('topup_refund.json', 'topup_refund_expected.json'),
        ('topup_taxi_refund.json', 'topup_taxi_refund_expected.json'),
        pytest.param(
            'topup_with_replica_lag.json',
            'topup_expected.json',
            marks=pytest.mark.config(
                BILLING_WALLET_SEARCH_MISSING_ACCOUNT_IN_MASTER=True,
            ),
        ),
        pytest.param(
            'withdraw_with_replica_lag.json',
            'withdraw_expected.json',
            marks=pytest.mark.config(
                BILLING_WALLET_SEARCH_MISSING_ACCOUNT_IN_MASTER=True,
            ),
        ),
        pytest.param(
            'topup_with_payload.json',
            'topup_with_payload_expected_balance_sync.json',
            marks=pytest.mark.config(
                BILLING_CALCULATORS_TRIGGER_WALLET_BALANCE_SYNC=True,
            ),
        ),
        pytest.param(
            'withdraw.json',
            'withdraw_expected_balance_sync.json',
            marks=pytest.mark.config(
                BILLING_CALCULATORS_TRIGGER_WALLET_BALANCE_SYNC=True,
            ),
        ),
        pytest.param(
            'create.json',
            'create_expected_balance_sync.json',
            marks=pytest.mark.config(
                BILLING_CALCULATORS_TRIGGER_WALLET_BALANCE_SYNC=True,
            ),
        ),
    ],
)
@pytest.mark.config(BILLING_WALLET_BALANCE_SYNC_MAX_DELAY=60)
@pytest.mark.now(_NOW.isoformat())
async def test_execute_doc_billing_wallet(
        test_data_path,
        expected_data_path,
        *,
        load_json,
        mockserver,
        patch_aiohttp_session,
        response_mock,
        request_headers,
        taxi_billing_calculators_client,
        patch,
):
    data = load_json(f'billing_wallet/{test_data_path}')
    expected = load_json(f'billing_wallet/{expected_data_path}')
    actual_payouts = []
    actual_docs = []
    actual_accounts = []
    actual_entities = []
    actual_doc_update_request = {}
    lagging_replica = data.get('lagging_replica', False)

    @patch_aiohttp_session(discovery.find_service('billing_docs').url, 'POST')
    def _patch_billing_docs_request(method, url, headers, json, **kwargs):
        if '/v2/docs/execute' in url:
            actual_docs.append(copy.deepcopy(json))
            doc = json['docs'][0].copy()
            if data.get('doc'):
                return response_mock(json={'docs': [data['doc']]})
            doc['doc_id'] = 28
            doc['created'] = doc['event_at']
            doc['process_at'] = doc['event_at']
            doc['status'] = 'complete'
            if 'execution_modes' in doc['data']:
                doc['data']['status_info'] = {'status': data['handle_status']}
            return response_mock(json={'docs': [doc]})
        if 'v1/docs/update' in url:
            actual_doc_update_request.update(copy.deepcopy(json))
            doc = data['request']
            doc['data'].update(json['data'])
            doc['process_at'] = '2020-04-09T00:00:00.000000+00:00'
            doc['service'] = 'billing-orders'
            doc['status'] = json['status']
            return response_mock(json=doc)
        raise NotImplementedError

    @mockserver.json_handler('/billing-accounts/v2/accounts/search')
    def _handle_accounts_search(request):
        use_master = request.json.get('use_master', False)
        assert len(request.json['accounts']) == 1
        sub_account = request.json['accounts'][0]['sub_account']
        deposit_sub_account = data['request']['data']['account']['sub_account']
        if (
                lagging_replica
                and sub_account == deposit_sub_account
                and not use_master
        ):
            return mockserver.make_response(json={'accounts': []})
        accounts = list(
            filter(
                lambda person: person['sub_account'] == sub_account,
                data['accounts'],
            ),
        )
        return mockserver.make_response(json={'accounts': accounts})

    @mockserver.json_handler('/billing-accounts/v1/accounts/create')
    def _handle_accounts_create(request):
        actual_accounts.append(copy.deepcopy(request.json))
        account = request.json.copy()
        account['account_id'] = _get_account_id_by_subaccount(
            account['sub_account'],
        )
        account['opened'] = account['expired']
        return mockserver.make_response(json=account)

    @mockserver.json_handler('/billing-accounts/v1/entities/create')
    def _handle_entities_create(request):
        actual_entities.append(copy.deepcopy(request.json))
        return mockserver.make_response(
            json={
                'external_id': request.json['external_id'],
                'kind': request.json['kind'],
                'created': '2020-05-25T00:00:00+00:00',
            },
        )

    @mockserver.json_handler('/billing-orders/v2/process/async')
    def _handle_process_async(request):
        actual_payouts.extend(copy.deepcopy(request.json['orders']))
        return mockserver.make_response(
            json={
                'orders': [
                    {
                        'doc_id': 28,
                        'topic': order['topic'],
                        'external_ref': order['external_ref'],
                    }
                    for order in actual_payouts
                ],
            },
        )

    @patch('taxi.clients.stq_agent.StqAgentClient.put_task')
    async def _patch_stq_client_put(*args, **kwargs):
        pass

    response = await taxi_billing_calculators_client.post(
        '/v1/execute_doc', headers=request_headers, json=data['request'],
    )
    assert response.status == 200

    assert actual_entities == expected['entities']
    assert actual_accounts == expected['accounts']
    assert actual_doc_update_request == expected['doc_update_request']
    assert actual_docs == expected['docs']
    assert actual_payouts == expected['payouts']
    assert _get_calls(_patch_stq_client_put) == expected.get('stq_calls', [])


def _get_calls(stq_client_put):
    calls = []
    for raw_call in stq_client_put.calls:
        assert not raw_call['args']
        call = {
            k: copy.deepcopy(v)
            for k, v in raw_call['kwargs'].items()
            if k != 'loop'
        }
        call['kwargs'].pop('log_extra', None)
        calls.append(
            {
                'queue': call['queue'],
                'task_id': call['task_id'],
                'eta': call['eta'],
                'kwargs': call['kwargs'],
            },
        )
    return calls


def _get_account_id_by_subaccount(subaccount):
    return {
        '<sub_account>': 42,
        'topup/payment': 43,
        'topup/refund': 44,
        'topup/migration': 45,
        'taxi/topup/payment': 46,
        'taxi/topup/refund': 47,
    }[subaccount]
