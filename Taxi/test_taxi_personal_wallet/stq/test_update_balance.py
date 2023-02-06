from typing import NamedTuple

from aiohttp import web
import pytest

from testsuite.utils import callinfo


class ExternalMocks(NamedTuple):
    billing_balance: callinfo.AsyncCallQueue
    billing_create: callinfo.AsyncCallQueue
    user_api: callinfo.AsyncCallQueue


@pytest.fixture(name='mock_ucomm')
def _mock_ucomm(mockserver):
    @mockserver.handler('/ucommunications/user/notification/push')
    async def _push(request):
        body = request.json
        assert body['user']
        data = body['data']
        assert data['repack']['apns']['aps']['content-available'] == 1
        assert data['payload']['extra']['personal_wallet_balance_update']
        return web.json_response(status=200)

    return _push


@pytest.fixture(name='mock_external')
def _mock_external(mockserver):
    @mockserver.handler('/billing-wallet/balance')
    async def _billing_balance(request):
        response = {'balance': '100500', 'currency': 'RUB'}
        return web.json_response(response, status=200)

    @mockserver.handler('/billing-wallet/create')
    async def _create(request):
        response = {'wallet_id': 'new_wallet'}
        return web.json_response(response, status=200)

    @mockserver.handler('/user_api-api/users/search')
    async def _user_api(request):
        response = {'items': [{'id': 'user_id', 'application': 'android'}]}
        return web.json_response(response, status=200)

    return ExternalMocks(
        billing_balance=_billing_balance,
        billing_create=_create,
        user_api=_user_api,
    )


async def _call_task(stq_runner, wallet_id):
    await stq_runner.personal_wallet_update_balance.call(
        task_id='task_id', args=['yandex_uid', wallet_id], kwargs={},
    )


async def _check_balance_in_pg(
        web_context, wallet_id, expected_exist=False, expected_balance='0',
):
    result = await web_context.pg.master_pool.fetch(
        f'select fallback_balance from personal_wallet.wallets '
        f'where id=\'{wallet_id}\'',
    )

    if expected_exist:
        assert len(result) == 1
        assert result[0]['fallback_balance'] == expected_balance
    else:
        assert not result


async def test_update_balance_basic(
        stq_runner, web_context, mock_external, mock_ucomm,
):
    await _call_task(stq_runner, 'wallet_id')
    await _check_balance_in_pg(web_context, 'wallet_id', True, '100500')
    assert mock_ucomm.times_called == 1
    assert not mock_external.billing_create.has_calls


@pytest.mark.config(PERSONAL_WALLET_CREATE_NEW_ON_UPDATE_BALANCE=True)
async def test_update_balance_new_wallet_create(
        stq_runner, web_context, mock_external, mock_ucomm,
):
    await _call_task(stq_runner, 'new_wallet')
    await _check_balance_in_pg(web_context, 'wallet_id', True, '100')
    await _check_balance_in_pg(web_context, 'new_wallet', True, '100500')
    assert not mock_external.billing_create.has_calls


@pytest.mark.config(PERSONAL_WALLET_CREATE_NEW_ON_UPDATE_BALANCE=False)
async def test_update_balance_new_wallet_not_create(
        stq_runner, web_context, mock_external, mock_ucomm,
):
    await _call_task(stq_runner, 'new_wallet')
    await _check_balance_in_pg(web_context, 'wallet_id', True, '100')
    await _check_balance_in_pg(web_context, 'new_wallet')
    assert not mock_external.billing_create.has_calls


async def test_update_balance_user_api_fail(
        stq_runner, mock_external, mock_ucomm, mockserver, web_context,
):
    @mockserver.handler('/user_api-api/users/search')
    async def _user_api(request):
        response = {'code': '500', 'message': '500'}
        return web.json_response(response, status=500)

    await _call_task(stq_runner, 'wallet_id')
    await _check_balance_in_pg(web_context, 'wallet_id', True, '100500')

    assert not mock_ucomm.times_called


async def test_update_balance_ucommunications_fail(
        stq_runner, mock_external, mockserver, web_context,
):
    @mockserver.handler('/ucommunications/user/notification/push')
    async def _push(request):
        response = {'code': '500', 'message': '500'}
        return web.json_response(response, status=500)

    await _call_task(stq_runner, 'wallet_id')
    await _check_balance_in_pg(web_context, 'wallet_id', True, '100500')


@pytest.mark.parametrize(
    'items, times_called',
    [
        ([{'id': 'user_id'}], 0),
        ([{'id': 'user_id', 'application': 'any'}], 1),
        ([{'id': 'user_id', 'application': 'android', 'uber_id': 'id'}], 0),
        (
            [
                {'id': 'id_1', 'application': 'any'},
                {'id': 'id_2', 'application': 'any'},
            ],
            2,
        ),
        ([{'id': 'id_1', 'application': 'any'}, {'id': 'id_2'}], 1),
    ],
)
async def test_update_balance_ucommunications_filter(
        stq_runner,
        mock_external,
        mock_ucomm,
        mockserver,
        web_context,
        items,
        times_called,
):
    @mockserver.handler('/user_api-api/users/search')
    async def _user_api(request):
        response = {'items': items}
        return web.json_response(response, status=200)

    await _call_task(stq_runner, 'wallet_id')
    await _check_balance_in_pg(web_context, 'wallet_id', True, '100500')

    assert mock_ucomm.times_called == times_called
