# pylint: disable=redefined-outer-name
import copy
from typing import Any
from typing import Dict

import aiohttp
import pytest

from taxi import config
from taxi import discovery
from taxi.billing import clients as billing_clients

_SEARCH_RESULT = {
    'accounts': [
        {
            'account_id': 1230001,
            'entity_external_id': 'foo',
            'agreement_id': 'test',
            'currency': 'XXX',
            'sub_account': 'bar',
            'expired': '2020-11-01T21:00:00.000000+00:00',
            'opened': '2020-11-01T15:54:05.564871+00:00',
        },
    ],
}
_EMPTY_SEARCH_RESULT: Dict[str, Any] = {'accounts': []}
_ACCOUNT_SAMPLE = billing_clients.models.billing_accounts.Account(
    account_id=None,
    entity_external_id='foo',
    agreement_id='test',
    sub_account='bar',
    currency='XXX',
    expired=billing_clients.models.billing_accounts.DEFAULT_ACCOUNT_EXPIRED,
)
_FOUND_ACCOUNT = (
    billing_clients.models.billing_accounts.AccountStrict.from_json(
        _SEARCH_RESULT['accounts'][0],
    )
)


@pytest.fixture
async def client(loop):
    class Config(config.Config):
        BILLING_ACCOUNTS_CLIENT_QOS = {
            '__default__': {'attempts': 5, 'timeout-ms': 500},
        }

    session = aiohttp.ClientSession(loop=loop)
    yield billing_clients.BillingAccountsClient(
        service=discovery.find_service('billing_accounts'),
        session=session,
        config=Config(),
    )
    await session.close()


async def test_billing_accounts_client(
        client: billing_clients.BillingAccountsClient,
        mockserver,
        mock_accounts_search_v2,
):

    some_entity = {'external_id': 'uuid/f00', 'kind': 'driver'}

    @mockserver.json_handler('/billing-accounts/v1/entities/create')
    def _handle_entities_create(request):
        assert request.method == 'POST'
        return mockserver.make_response(json=some_entity)

    @mockserver.json_handler('/billing-accounts/v1/entities/search')
    def _handle_entities_search(request):
        assert request.method == 'POST'
        return mockserver.make_response(json=[some_entity])

    doc = await client.create_entity({})
    assert _handle_entities_create.times_called == 1
    assert doc == some_entity
    found_doc = await client.search_entities('uuid/f00')
    assert _handle_entities_search.times_called == 1
    assert found_doc == [some_entity]

    mock_accounts_search_v2(
        response_data=_SEARCH_RESULT, expected_request={'use_master': None},
    )
    response = await client.search_accounts_v2(
        *_make_accounts_for_search(_SEARCH_RESULT),
    )
    assert response == _SEARCH_RESULT

    mock_accounts_search_v2(
        response_data=_SEARCH_RESULT, expected_request={'use_master': True},
    )
    response = await client.search_accounts_v2(
        *_make_accounts_for_search(_SEARCH_RESULT), use_master=True,
    )
    assert response == _SEARCH_RESULT


@pytest.mark.parametrize(
    'master_retry_enabled, found_on_replica, found_on_master, '
    'expected_account, expected_error, expected_use_master',
    [
        (False, True, True, _FOUND_ACCOUNT, None, [False]),
        (
            False,
            False,
            True,
            None,
            billing_clients.exceptions.NotFoundError,
            [False],
        ),
        (True, True, True, _FOUND_ACCOUNT, None, [False]),
        (True, False, True, _FOUND_ACCOUNT, None, [False, True]),
        (
            True,
            False,
            False,
            None,
            billing_clients.exceptions.NotFoundError,
            [False, True],
        ),
    ],
)
async def test_get_unique_account(
        client: billing_clients.BillingAccountsClient,
        mockserver,
        master_retry_enabled,
        found_on_replica,
        found_on_master,
        expected_account,
        expected_error,
        expected_use_master,
):
    @mockserver.json_handler('/billing-accounts/v2/accounts/search')
    def _handle_search(request):
        assert request.method == 'POST'
        use_master = request.json.get('use_master', False)
        if (use_master and not found_on_master) or (
                not use_master and not found_on_replica
        ):
            return mockserver.make_response(
                status=200, json=_EMPTY_SEARCH_RESULT,
            )
        return mockserver.make_response(json=_SEARCH_RESULT)

    actual_account_future = client.get_unique_account(
        acc=_ACCOUNT_SAMPLE,
        master_retry_enabled=master_retry_enabled,
        log_extra=None,
    )
    if expected_error:
        with pytest.raises(expected_error):
            await actual_account_future
        actual_account = None
    else:
        actual_account = await actual_account_future
    assert actual_account == expected_account
    for use_master in expected_use_master:
        call = _handle_search.next_call()
        assert call['request'].json.get('use_master', False) == use_master
    assert not _handle_search.has_calls


@pytest.fixture(name='mock_accounts_search_v2')
def _mock_accounts_search_v2(mockserver):
    def do_mock(response_data, expected_request):
        @mockserver.json_handler('/billing-accounts/v2/accounts/search')
        def _handle(request):
            assert request.method == 'POST'
            for key, value in expected_request.items():
                if value is None:
                    assert key not in request.json
                else:
                    assert request.json[key] == value
            return mockserver.make_response(json=response_data)

    return do_mock


def _make_accounts_for_search(search_result):
    response = copy.deepcopy(search_result)
    for account in response['accounts']:
        del account['account_id']
        del account['expired']
        del account['opened']
    return response['accounts']
