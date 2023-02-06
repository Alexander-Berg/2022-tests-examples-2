from aiohttp import web
import pytest

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.config(
        PERSONAL_WALLET_FIRM_BY_SERVICE={'yataxi': {'RUB': '13', 'EUR': '22'}},
    ),
]

TRANS_ID = '123456'
AMOUNT = '100500'
EVENT_AT = '2020-05-05T10:34:45.650109+00:00'
TRANSFER_PAYLOAD = {
    'source_wallet': 'w/phonish',
    'target_wallet': 'w/portal',
    'is_transfer': True,
    'source_yandex_uid': 'phonish',
    'target_yandex_uid': 'portal',
}

_enable_new_merge = pytest.mark.config(PERSONAL_WALLET_MERGE_NEWWAY=True)

_parametrize_old_new_way_merge = pytest.mark.parametrize(
    'is_newway',
    [pytest.param(False), pytest.param(True, marks=_enable_new_merge)],
)


@pytest.fixture(name='mock_external')
def _mock_external(mockserver):
    @mockserver.handler('/billing-wallet/topup')
    async def _topup(request):
        assert request.json['payload']['payload'] == TRANSFER_PAYLOAD
        assert request.json['transaction_type'] == 'payment'
        response = {'transaction_id': '11111'}
        return web.json_response(response, status=200)

    @mockserver.handler('/billing-wallet/withdraw')
    async def _withdraw(request):
        assert request.json['payload']['payload'] == TRANSFER_PAYLOAD
        assert request.json['transaction_type'] == 'payment'
        response = {'transaction_id': TRANS_ID}
        return web.json_response(response, status=200)

    @mockserver.handler('/billing-wallet/order')
    async def _order(request):
        transaction = dict(
            id=TRANS_ID,
            amount=f'-{AMOUNT}',
            currency='RUB',
            event_at=EVENT_AT,
        )
        response = {'transactions': [transaction]}
        return web.json_response(response, status=200)

    @mockserver.handler('/billing-wallet/balance')
    async def _balance(request):
        response = {'currency': 'RUB', 'balance': '0'}
        if request.json['wallet_id'] == 'w/portal':
            response.update({'balance': AMOUNT})
        return web.json_response(response, status=200)

    @mockserver.handler('/billing-wallet/create')
    async def _create(request):
        response = {'wallet_id': 'abcd123'}
        return web.json_response(response, status=200)


async def _call_task(
        stq_runner, has_calls, stq, source_balance=None, target_balance=None,
):
    kwargs = {
        'source_wallet': dict(
            wallet_id='w/phonish', currency='RUB', yandex_uid='phonish',
        ),
        'target_wallet': dict(
            wallet_id='w/portal', currency='RUB', yandex_uid='portal',
        ),
    }
    if source_balance is not None:
        kwargs['source_wallet']['balance'] = source_balance
    if target_balance is not None:
        kwargs['target_wallet']['balance'] = target_balance

    task_id = '1234567890abcdef'
    await stq_runner.personal_wallet_merge_accounts.call(
        task_id=task_id, args=[], kwargs=kwargs,
    )

    assert stq.personal_wallet_merge_accounts.has_calls == has_calls

    return kwargs, task_id


async def _get_wallet_from_pg(context, wallet_id) -> dict:
    result = await context.pg.master_pool.fetch(
        f'select fallback_balance, merge_status, merged_at '
        f'from personal_wallet.wallets where id=\'{wallet_id}\'',
    )
    assert len(result) == 1
    return result[0]


@_parametrize_old_new_way_merge
async def test_merge_accounts_basic(
        stq_runner, stq, mock_external, stq3_context, is_newway,
):
    await _call_task(stq_runner, 0, stq)

    source = await _get_wallet_from_pg(stq3_context, 'w/phonish')
    assert source['merge_status'] == 'merged'
    if is_newway:
        assert source['merged_at'] is not None
    else:
        assert source['merged_at'].isoformat() == EVENT_AT
    assert source['fallback_balance'] == '0'

    target = await _get_wallet_from_pg(stq3_context, 'w/portal')
    assert target['merge_status'] is None
    assert target['merged_at'] is None
    assert target['fallback_balance'] == AMOUNT


async def test_merge_accounts_incomplete(
        stq_runner, stq, mock_external, mockserver, stq3_context,
):
    @mockserver.handler('/billing-wallet/balance')
    async def _balance(request):
        response = {'currency': 'RUB', 'balance': '1'}
        if request.json['wallet_id'] == 'w/portal':
            response.update({'balance': AMOUNT})
        return web.json_response(response, status=200)

    kwargs, task_id = await _call_task(stq_runner, 1, stq)

    source = await _get_wallet_from_pg(stq3_context, 'w/phonish')
    assert source['merge_status'] == 'merged'
    assert source['merged_at'].isoformat() == EVENT_AT

    next_call = stq.personal_wallet_merge_accounts.next_call()

    assert next_call['kwargs'] == kwargs
    assert next_call['id'] != task_id


async def test_merge_accounts_not_enough_funds(
        stq_runner, stq, mock_external, mockserver, stq3_context,
):
    @mockserver.handler('/billing-wallet/withdraw')
    async def _withdraw(request):
        response = {'code': 'not_enough_funds', 'message': 'not_enough_funds'}
        return web.json_response(response, status=409)

    kwargs, task_id = await _call_task(stq_runner, 1, stq)

    source = await _get_wallet_from_pg(stq3_context, 'w/phonish')
    assert source['merge_status'] == 'processing'
    assert source['merged_at'] is None

    next_call = stq.personal_wallet_merge_accounts.next_call()

    assert next_call['kwargs'] == kwargs
    assert next_call['id'] != task_id


@_enable_new_merge
async def test_merge_negative_balance(
        stq_runner, stq, mock_external, mockserver, stq3_context,
):
    @mockserver.handler('/billing-wallet/balance')
    async def _balance(request):
        response = {'currency': 'RUB', 'balance': '-10'}
        if request.json['wallet_id'] == 'w/portal':
            response.update({'balance': AMOUNT})
        return web.json_response(response, status=200)

    @mockserver.handler('/billing-wallet/withdraw')
    async def _withdraw(request):
        assert request.json['amount'] == '10'
        assert request.json['payload']['payload'] == TRANSFER_PAYLOAD
        assert request.json['transaction_type'] == 'refund'
        response = {'transaction_id': '22222'}
        return web.json_response(response, status=200)

    @mockserver.handler('/billing-wallet/topup')
    async def _topup(request):
        assert request.json['amount'] == '10'
        assert request.json['payload']
        assert request.json['transaction_type'] == 'refund'
        response = {'transaction_id': '11111'}
        return web.json_response(response, status=200)

    @mockserver.handler('/billing-wallet/order')
    async def _order(request):
        response = {
            'transactions': [
                {
                    'amount': '10',
                    'currency': 'RUB',
                    'event_at': EVENT_AT,
                    'id': '11111',
                },
            ],
        }
        return web.json_response(response, status=200)

    await _call_task(
        stq_runner, 1, stq, source_balance='-10', target_balance=AMOUNT,
    )

    source = await _get_wallet_from_pg(stq3_context, 'w/phonish')
    assert source['merge_status'] == 'merged'
    assert source['merged_at'] is not None


@_enable_new_merge
async def test_merge_negative_balance_changed(
        stq_runner, stq, mock_external, mockserver, stq3_context,
):
    @mockserver.handler('/billing-wallet/balance')
    async def _balance(request):
        response = {'currency': 'RUB', 'balance': '10'}
        if request.json['wallet_id'] == 'w/portal':
            response.update({'balance': '10'})
        return web.json_response(response, status=200)

    @mockserver.handler('/billing-wallet/withdraw')
    async def _withdraw(request):
        assert request.json['amount'] == '10'
        assert request.json['payload']['payload'] == TRANSFER_PAYLOAD
        assert request.json['transaction_type'] == 'refund'
        response = {'transaction_id': '22222'}
        return web.json_response(response, status=200)

    @mockserver.handler('/billing-wallet/topup')
    async def _topup(request):
        assert request.json['amount'] == '10'
        assert request.json['payload']
        assert request.json['transaction_type'] == 'refund'
        response = {'transaction_id': '11111'}
        return web.json_response(response, status=200)

    @mockserver.handler('/billing-wallet/order')
    async def _order(request):
        response = {
            'transactions': [
                {
                    'amount': '-10',
                    'currency': 'RUB',
                    'event_at': EVENT_AT,
                    'id': '11111',
                },
            ],
        }
        return web.json_response(response, status=200)

    await _call_task(
        stq_runner, 1, stq, source_balance='-10', target_balance='10',
    )

    source = await _get_wallet_from_pg(stq3_context, 'w/phonish')
    assert source['merge_status'] == 'merged'
    assert source['merged_at'] is not None
