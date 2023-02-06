# pylint: disable=redefined-outer-name

import asyncio

import aiohttp
import pytest

from taxi.clients import billing_v2

from corp_clients.generated.cron import run_cron


@pytest.fixture
def billing_data(load_json):
    return load_json('billing_data.json')


@pytest.fixture
def billing_exceptions(request):
    return request.param


@pytest.fixture
def get_passport_by_login_mock(billing_data, billing_exceptions, patch):
    @patch('taxi.clients.billing_v2.BalanceClient.get_passport_by_login')
    async def _get_passport_by_login(operator_uid, login):
        exc = billing_exceptions.get(login)
        if exc:
            raise exc.pop()
        return {'ClientId': billing_data[login]['ClientID']}

    return _get_passport_by_login


@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.parametrize(
    'test_clients, billing_exceptions',
    [
        (
            {
                'turkish': {
                    'billing_id': '1001',
                    'login_not_in_passport': False,
                },
                'tommy': {
                    'billing_id': '1002',
                    'login_not_in_passport': False,
                },
                'charley': {
                    'billing_id': '1003',
                    'login_not_in_passport': False,
                },
                'billing_error': {'billing_id': 'old_billing_id'},
                'billing_fail': {'billing_id': 'old_billing_id'},
                'no_passport': {
                    'billing_id': 'should_not_change',
                    'login_not_in_passport': True,
                },
                'not_changed': {
                    'billing_id': '1004',
                    'login_not_in_passport': False,
                },
            },
            {
                'tommy': [asyncio.TimeoutError('test timeout error')],
                'charley': [aiohttp.ClientError('test client error')],
                'billing_error': [
                    billing_v2.BillingError('test billing error'),
                ],
                'billing_fail': [
                    aiohttp.ClientError('test client error'),
                    aiohttp.ClientError('test client error'),
                    aiohttp.ClientError('test client error'),
                ],
                'no_passport': [
                    billing_v2.BillingPassportNotFound('test no passport'),
                ],
                'no_passport_again': [],
                'not_changed': [],
            },
        ),
    ],
    indirect=['billing_exceptions'],
)
async def test_sync_billing_clients(
        db, patch, get_passport_by_login_mock, test_clients,
):
    @patch('corp_personal.components.CorpPersonal.replace_pd_with_values')
    async def _replace_pd_with_values(*args, **kwargs):
        pass

    clients_before_cron = {}
    async for client in db.corp_clients.find():
        clients_before_cron[client['yandex_login']] = client

    filtered_clients = await db.corp_clients.count(
        {'is_trial': False, 'login_not_in_passport': {'$ne': True}},
    )
    module = 'corp_clients.crontasks.sync_billing_clients'
    await run_cron.main([module, '-t', '0'])

    def _filter_calls(calls, yandex_login):
        return list(filter(lambda call: call['login'] == yandex_login, calls))

    calls = get_passport_by_login_mock.calls
    assert len(calls) == 11
    assert len(_filter_calls(calls, 'turkish')) == 1
    assert len(_filter_calls(calls, 'tommy')) == 2
    assert len(_filter_calls(calls, 'charley')) == 2
    assert len(_filter_calls(calls, 'billing_error')) == 1
    assert len(_filter_calls(calls, 'billing_fail')) == 3
    assert len(_filter_calls(calls, 'no_passport')) == 1
    assert len(_filter_calls(calls, 'not_changed')) == 1

    assert len(_replace_pd_with_values.calls) == filtered_clients

    async for client in db.corp_clients.find({'is_trial': False}):
        test_client = test_clients[client['yandex_login']]
        billing_id = test_client['billing_id']
        login_not_in_passport = test_client.get('login_not_in_passport')

        assert client['billing_id'] == billing_id, client

        client_before = clients_before_cron[client['yandex_login']]
        is_changed = (
            client_before['billing_id'] != billing_id
            or client_before.get('login_not_in_passport')
            != login_not_in_passport
        )

        if is_changed:
            assert client['updated'] > client_before['updated']
        else:
            assert client['updated'] == client_before['updated']

    assert await db.corp_clients.count({'login_not_in_passport': True}) == 1
    assert await db.corp_clients.count({'login_not_in_passport': False}) == 4
