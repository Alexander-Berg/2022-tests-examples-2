import json

from aiohttp import web
import pytest

from taxi.billing import util
from taxi.billing.util import dates as billing_dates

from taxi_billing_accounts import models
from taxi_billing_accounts.models import tools


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            {
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
                'agreement_id': 'AG-001',
                'currency': 'RUB',
                'sub_account': 'RIDE',
                'expired': '2118-07-18T17:26:31.000000+00:00',
            },
            web.HTTPOk,
        ),
        (
            {
                'entity_external_id': (
                    'unique_driver_id/5b60199b41e102a72fe8268c'
                ),
                'agreement_id': 'testsuite-AG-001',
                'currency': 'USD',
                'sub_account': 'RIDE',
                'expired': '9999-12-31T23:59:59.999999+00:00',
            },
            web.HTTPOk,
        ),
    ],
)
@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql', 'entities@0.sql'))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql', 'entities@1.sql'))
async def test_accounts_create(
        billing_accounts_client,
        request_headers,
        request_body,
        expected_response,
):
    first = await billing_accounts_client.post(
        '/v1/accounts/create', json=request_body, headers=request_headers,
    )

    second = await billing_accounts_client.post(
        '/v1/accounts/create', json=request_body, headers=request_headers,
    )

    # check idempotency feature
    assert first.status == second.status
    assert await first.json() == await second.json()

    assert first.status == web.HTTPOk.status_code
    ans = await first.json()

    assert ans.get('account_id') is not None
    ans.pop('account_id')

    assert ans.get('opened') is not None
    ans.pop('opened')

    assert ans == request_body


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        # Wrong request bodies
        (None, web.HTTPUnsupportedMediaType),
        ({}, web.HTTPBadRequest),
        # Test everything is fine with valid test request
        (
            {
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
                'agreement_id': 'AG-001',
                'currency': 'RUB',
                'sub_account': 'RIDE',
                'expired': '2118-07-18T17:26:31.000000+00:00',
            },
            web.HTTPOk,
        ),
        # Invalid requests
        (
            # wrong entity id
            {
                'entity_external_id': 'non-existing-id',
                'agreement_id': 'AG-001',
                'currency': 'RUB',
                'sub_account': 'RIDE',
                'expired': '2118-07-18T17:26:31.000000+00:00',
            },
            web.HTTPBadRequest,
        ),
        (
            # missed entity id
            {
                'agreement_id': 'AG-001',
                'currency': 'RUB',
                'sub_account': 'RIDE',
                'expired': '2118-07-18T17:26:31.000000+00:00',
            },
            web.HTTPBadRequest,
        ),
        (
            # missed agreement id
            {
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
                'currency': 'RUB',
                'sub_account': 'RIDE',
                'expired': '2118-07-18T17:26:31.000000+00:00',
            },
            web.HTTPBadRequest,
        ),
        (
            # missed currency
            {
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
                'agreement_id': 'AG-001',
                'sub_account': 'RIDE',
                'expired': '2118-07-18T17:26:31.000000+00:00',
            },
            web.HTTPBadRequest,
        ),
        (
            # missed sub-account
            {
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
                'agreement_id': 'AG-001',
                'currency': 'RUB',
                'expired': '2118-07-18T17:26:31.000000+00:00',
            },
            web.HTTPBadRequest,
        ),
        (
            # missed expired
            {
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
                'agreement_id': 'AG-001',
                'currency': 'RUB',
                'sub_account': 'RIDE',
            },
            web.HTTPBadRequest,
        ),
        (
            # Wrong timestamp
            {
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
                'agreement_id': 'AG-001',
                'currency': 'RUB',
                'sub_account': 'RIDE',
                'expired': '2118-07-18T24:26:31.000000+00:00',
            },
            web.HTTPBadRequest,
        ),
        (
            # Timestamp without timezone
            {
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
                'agreement_id': 'AG-001',
                'currency': 'RUB',
                'sub_account': 'RIDE',
                'expired': '2118-07-18T17:26:31',
            },
            web.HTTPBadRequest,
        ),
    ],
)
@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql', 'entities@0.sql'))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_accounts_create_invalid(
        billing_accounts_client,
        request_headers,
        request_body,
        expected_response,
):
    response = await billing_accounts_client.post(
        '/v1/accounts/create', json=request_body, headers=request_headers,
    )
    assert response.status == expected_response.status_code


@pytest.mark.parametrize(
    'account',
    [
        models.Account(
            account_id=10007,
            entity_external_id='unique_driver_id/5b60199b41e102a72fe8268c',
            agreement_id='ag-testsuite-001',
            currency='RUB',
            sub_account='income',
            opened='2018-08-09T16:13:16.818875',
            expired='2018-08-15T22:00:00',
        ),
        models.Account(
            account_id=50001,
            entity_external_id='unique_driver_id/5b0913df30a2e52b7633b3e6',
            agreement_id='ag-testsuite-nMFG-000',
            currency='RUB',
            sub_account='income',
            opened='2018-08-09T17:05:41.406741',
            expired='2018-08-15T22:00:00',
        ),
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'entities@0.sql', 'accounts@0.sql'),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'entities@1.sql', 'accounts@1.sql'),
)
async def test_accounts_search_full(
        billing_accounts_client, request_headers, account,
):
    request_body = {
        'entity_external_id': account.entity_external_id,
        'agreement_id': account.agreement_id,
        'currency': account.currency,
        'sub_account': account.sub_account,
    }

    response = await billing_accounts_client.post(
        '/v1/accounts/search', json=request_body, headers=request_headers,
    )

    assert response.status == web.HTTPOk.status_code

    found_all = await response.json()
    assert found_all and len(found_all) == 1

    found_account = models.Account(**found_all[0])
    assert found_account == account


@pytest.mark.parametrize(
    'account',
    [
        models.Account(
            account_id=10007,
            entity_external_id='unique_driver_id/5b60199b41e102a72fe8268c',
            agreement_id='ag-testsuite-001',
            currency='RUB',
            sub_account='income',
            opened='2018-08-09T16:13:16.818875',
            expired='2018-08-15T22:00:00',
        ),
        models.Account(
            account_id=9740001,
            entity_external_id='unique_driver_id/5b0913df30a2e52b7633b3e6',
            agreement_id='subvention_agreement/voronezh_daily_guarantee_2018',
            currency='RUB',
            sub_account='income',
            opened='2018-11-23T09:12:37.281163',
            expired='9999-12-31T23:59:59.999999',
        ),
        models.Account(
            account_id=20001,
            entity_external_id='unique_driver_id/5ac2856ae342c7944bff60b6',
            agreement_id='subvention_agreement/2018_10_17',
            currency='XXX',
            sub_account='num_orders',
            opened='2018-07-09T16:31:52.758819',
            expired='2018-09-10T22:00:00',
        ),
        models.Account(
            account_id=5256730001,
            entity_external_id='unique_driver_id/5ac2856ae342c7944bff60b6',
            agreement_id='subvention_agreement/2018_10_17',
            currency='RUB',
            sub_account='net',
            opened='2018-07-09T16:31:52.758819',
            expired='2018-09-10T22:00:00',
        ),
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'entities@0.sql', 'accounts@0.sql'),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'entities@1.sql', 'accounts@1.sql'),
)
async def test_accounts_search_by_id(
        billing_accounts_client, request_headers, account,
):
    request_body = {'account_id': account.account_id}

    response = await billing_accounts_client.post(
        '/v1/accounts/search', json=request_body, headers=request_headers,
    )

    assert response.status == web.HTTPOk.status_code
    found_all = await response.json()

    assert found_all and len(found_all) == 1

    found_account = models.Account(**found_all[0])
    assert found_account == account


@pytest.mark.parametrize(
    'search_request, expected_accounts',
    [
        (
            {
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
            },
            [
                models.Account(
                    account_id=50001,
                    entity_external_id=(
                        'unique_driver_id/5b0913df30a2e52b7633b3e6'
                    ),
                    agreement_id='ag-testsuite-nMFG-000',
                    currency='RUB',
                    sub_account='income',
                    opened='2018-08-09T17:05:41.406741',
                    expired='2018-08-15T22:00:00',
                ),
                models.Account(
                    account_id=51001,
                    entity_external_id=(
                        'unique_driver_id/5b0913df30a2e52b7633b3e6'
                    ),
                    agreement_id='ag-testsuite-nMFG-000',
                    currency='XXX',
                    sub_account='num_orders',
                    opened='2018-08-09T17:05:41.651405',
                    expired='2109-07-18T17:26:31.000000+00:00',
                ),
                models.Account(
                    account_id=9740001,
                    entity_external_id=(
                        'unique_driver_id/5b0913df30a2e52b7633b3e6'
                    ),
                    agreement_id=(
                        'subvention_agreement/voronezh_daily_guarantee_2018'
                    ),
                    currency='RUB',
                    sub_account='income',
                    opened='2018-11-23T09:12:37.281163',
                    expired='9999-12-31T23:59:59.999999',
                ),
            ],
        ),
        (
            {
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
                'sub_account': 'income',
            },
            [
                models.Account(
                    account_id=50001,
                    entity_external_id=(
                        'unique_driver_id/5b0913df30a2e52b7633b3e6'
                    ),
                    agreement_id='ag-testsuite-nMFG-000',
                    currency='RUB',
                    sub_account='income',
                    opened='2018-08-09T17:05:41.406741',
                    expired='2018-08-15T22:00:00',
                ),
                models.Account(
                    account_id=9740001,
                    entity_external_id=(
                        'unique_driver_id/5b0913df30a2e52b7633b3e6'
                    ),
                    agreement_id=(
                        'subvention_agreement/voronezh_daily_guarantee_2018'
                    ),
                    currency='RUB',
                    sub_account='income',
                    opened='2018-11-23T09:12:37.281163',
                    expired='9999-12-31T23:59:59.999999',
                ),
            ],
        ),
        (
            {
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
                'currency': 'XXX',
            },
            [
                models.Account(
                    account_id=51001,
                    entity_external_id=(
                        'unique_driver_id/5b0913df30a2e52b7633b3e6'
                    ),
                    agreement_id='ag-testsuite-nMFG-000',
                    currency='XXX',
                    sub_account='num_orders',
                    opened='2018-08-09T17:05:41.651405',
                    expired='2109-07-18T17:26:31.000000+00:00',
                ),
            ],
        ),
        (
            {
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
                'agreement_id': 'ag-testsuite-nMFG-000',
            },
            [
                models.Account(
                    account_id=50001,
                    entity_external_id=(
                        'unique_driver_id/5b0913df30a2e52b7633b3e6'
                    ),
                    agreement_id='ag-testsuite-nMFG-000',
                    currency='RUB',
                    sub_account='income',
                    opened='2018-08-09T17:05:41.406741',
                    expired='2018-08-15T22:00:00',
                ),
                models.Account(
                    account_id=51001,
                    entity_external_id=(
                        'unique_driver_id/5b0913df30a2e52b7633b3e6'
                    ),
                    agreement_id='ag-testsuite-nMFG-000',
                    currency='XXX',
                    sub_account='num_orders',
                    opened='2018-08-09T17:05:41.651405',
                    expired='2109-07-18T17:26:31.000000+00:00',
                ),
            ],
        ),
        (
            {
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
                'agreement_id': 'ag-testsuite-nMFG-000',
                'sub_account': 'num_orders',
            },
            [
                models.Account(
                    account_id=51001,
                    entity_external_id=(
                        'unique_driver_id/5b0913df30a2e52b7633b3e6'
                    ),
                    agreement_id='ag-testsuite-nMFG-000',
                    currency='XXX',
                    sub_account='num_orders',
                    opened='2018-08-09T17:05:41.651405',
                    expired='2109-07-18T17:26:31.000000+00:00',
                ),
            ],
        ),
        (
            {
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
                'agreement_id': 'ag-testsuite-nMFG-000',
                'currency': 'RUB',
            },
            [
                models.Account(
                    account_id=50001,
                    entity_external_id=(
                        'unique_driver_id/5b0913df30a2e52b7633b3e6'
                    ),
                    agreement_id='ag-testsuite-nMFG-000',
                    currency='RUB',
                    sub_account='income',
                    opened='2018-08-09T17:05:41.406741',
                    expired='2018-08-15T22:00:00',
                ),
            ],
        ),
        # not found
        (
            {
                'entity_external_id': 'unique_driver_id/no-such-id',
                'agreement_id': 'ag-testsuite-nMFG-000',
                'currency': 'RUB',
            },
            [],
        ),
        ({'account_id': 0}, []),
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'entities@0.sql', 'accounts@0.sql'),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'entities@1.sql', 'accounts@1.sql'),
)
async def test_accounts_search_many(
        billing_accounts_client,
        request_headers,
        search_request,
        expected_accounts,
):
    response = await billing_accounts_client.post(
        '/v1/accounts/search', json=search_request, headers=request_headers,
    )

    assert response.status == web.HTTPOk.status_code
    found_accounts = [models.Account(**it) for it in await response.json()]

    assert sorted(found_accounts, key=lambda a: a.account_id) == sorted(
        expected_accounts, key=lambda a: a.account_id,
    )


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        # Wrong request bodies
        (None, web.HTTPUnsupportedMediaType),
        ({}, web.HTTPBadRequest),
        # Test everything is fine with valid test request
        (
            {
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
                'agreement_id': 'ag-testsuite-nMFG-000',
                'currency': 'XXX',
                'sub_account': 'num_orders',
            },
            web.HTTPOk,
        ),
        # Invalid requests
        (
            # ambiguous primary keys (account_id or full)
            {
                'account_id': 51001,
                'entity_external_id': (
                    'unique_driver_id/5b0913df30a2e52b7633b3e6'
                ),
                'agreement_id': 'ag-testsuite-nMFG-000',
                'currency': 'XXX',
                'sub_account': 'num_orders',
            },
            web.HTTPBadRequest,
        ),
        (
            # no primary keys (account_id or full)
            {
                'agreement_id': 'ag-testsuite-nMFG-000',
                'currency': 'XXX',
                'sub_account': 'num_orders',
            },
            web.HTTPBadRequest,
        ),
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'entities@0.sql', 'accounts@0.sql'),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'entities@1.sql', 'accounts@1.sql'),
)
async def test_accounts_search_invalid(
        billing_accounts_client,
        request_headers,
        request_body,
        expected_response,
):
    response = await billing_accounts_client.post(
        '/v1/accounts/search', json=request_body, headers=request_headers,
    )
    assert response.status == expected_response.status_code


@pytest.mark.now('2022-01-07T00:01:01.333444')
@pytest.mark.parametrize(
    'request_body, expected_response, expected_updates',
    [
        # The first account update
        (
            {
                'account_id': 20007,
                'data': {'expired': '2118-07-18T17:26:31.000000+00:00'},
                'doc_ref': 'doc_ref',
                'idempotency_key': 'idempotency_key',
            },
            {
                'account_id': 20007,
                'data': {'expired': '2118-07-18T17:26:31.000000+00:00'},
                'idempotency_key': 'idempotency_key',
                'doc_ref': 'doc_ref',
                'created': '2022-01-07T00:01:01.333444+00:00',
            },
            [
                {
                    'created': 1533831196818875,
                    'data': {'expired': 253402300799999999},
                },
                {
                    'created': 1641513661333444,
                    'data': {'expired': 4687608391000000},
                    'doc_ref': 'doc_ref',
                    'idempotency_key': 'idempotency_key',
                },
            ],
        ),
        # New update
        (
            {
                'account_id': 51001,
                'data': {'expired': '2118-07-18T17:26:31.000000+00:00'},
                'doc_ref': 'doc_ref_2',
                'idempotency_key': 'idempotency_key_2',
            },
            {
                'account_id': 51001,
                'data': {'expired': '2118-07-18T17:26:31.000000+00:00'},
                'idempotency_key': 'idempotency_key_2',
                'doc_ref': 'doc_ref_2',
                'created': '2022-01-07T00:01:01.333444+00:00',
            },
            [
                {
                    'created': 1533834341651410,
                    'data': {'expired': 253402300799999999},
                },
                {
                    'created': 1637749366324790,
                    'data': {'expired': 4403611591000000},
                    'doc_ref': 'doc_ref',
                    'idempotency_key': 'idempotency_key',
                },
                {
                    'created': 1641513661333444,
                    'data': {'expired': 4687608391000000},
                    'doc_ref': 'doc_ref_2',
                    'idempotency_key': 'idempotency_key_2',
                },
            ],
        ),
        # Infinity
        (
            {
                'account_id': 9740001,
                'data': {'expired': '9999-12-31T23:59:59.999999+00:00'},
                'doc_ref': 'doc_ref_3',
                'idempotency_key': 'idempotency_key_3',
            },
            {
                'account_id': 9740001,
                'data': {'expired': '9999-12-31T23:59:59.999999+00:00'},
                'idempotency_key': 'idempotency_key_3',
                'doc_ref': 'doc_ref_3',
                'created': '2022-01-07T00:01:01.333444+00:00',
            },
            [
                {
                    'created': 1542964357281163,
                    'data': {'expired': 253402300799999999},
                },
                {
                    'created': 1641513661333444,
                    'data': {'expired': 253402300799999999},
                    'doc_ref': 'doc_ref_3',
                    'idempotency_key': 'idempotency_key_3',
                },
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'entities@0.sql', 'accounts@0.sql'),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'entities@1.sql', 'accounts@1.sql'),
)
async def test_accounts_update(
        billing_accounts_client,
        request_headers,
        billing_accounts_storage,
        request_body,
        expected_response,
        expected_updates,
):
    account_before_update = util.not_none(
        util.first(
            await _get_account(
                billing_accounts_storage, request_body['account_id'],
            ),
        ),
    )

    response = await billing_accounts_client.post(
        '/v1/accounts/update', json=request_body, headers=request_headers,
    )

    assert response.status == web.HTTPOk.status_code
    response_body = await response.json()
    assert response_body == expected_response

    account_after_update = util.not_none(
        util.first(
            await _get_account(
                billing_accounts_storage, request_body['account_id'],
            ),
        ),
    )
    assert account_after_update['expired'] == tools.make_datetime(
        expected_response['data']['expired'],
    )
    updates = json.loads(account_after_update['updates'])
    assert updates == expected_updates

    assert len(updates) > 1
    assert (
        billing_dates.microseconds_from_timestamp(
            account_before_update['updated'],
        )
        == updates[-2]['created']
    )
    assert (
        billing_dates.microseconds_from_timestamp(
            account_before_update['expired'],
        )
        == updates[-2]['data']['expired']
    )
    assert (
        billing_dates.microseconds_from_timestamp(
            account_after_update['updated'],
        )
        == updates[-1]['created']
    )
    assert (
        billing_dates.microseconds_from_timestamp(
            account_after_update['expired'],
        )
        == updates[-1]['data']['expired']
    )


@pytest.mark.now('2022-01-07T00:01:01.333444')
@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        # With existing idempotency_key
        (
            {
                'account_id': 51001,
                'data': {'expired': '2119-07-18T17:26:31.000000+00:00'},
                'doc_ref': 'doc_ref',
                'idempotency_key': 'idempotency_key',
            },
            {
                'account_id': 51001,
                'data': {'expired': '2109-07-18T17:26:31.000000+00:00'},
                'idempotency_key': 'idempotency_key',
                'doc_ref': 'doc_ref',
                'created': '2021-11-24T10:22:46.324790+00:00',
            },
        ),
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'entities@0.sql', 'accounts@0.sql'),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'entities@1.sql', 'accounts@1.sql'),
)
async def test_accounts_update_idempotency_key(
        billing_accounts_client,
        request_headers,
        billing_accounts_storage,
        request_body,
        expected_response,
):
    account_before_update = util.not_none(
        util.first(
            await _get_account(
                billing_accounts_storage, request_body['account_id'],
            ),
        ),
    )

    response = await billing_accounts_client.post(
        '/v1/accounts/update', json=request_body, headers=request_headers,
    )

    assert response.status == web.HTTPOk.status_code
    response_body = await response.json()
    assert response_body == expected_response

    account_after_update = util.not_none(
        util.first(
            await _get_account(
                billing_accounts_storage, request_body['account_id'],
            ),
        ),
    )
    assert account_before_update == account_after_update


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            # No doc ref
            {
                'account_id': 50001,
                'data': {'expired': '2118-07-18T17:26:31.000000+00:00'},
                'idempotency_key': 'idempotency_key',
            },
            web.HTTPBadRequest,
        ),
        (
            # No idempotency_key
            {
                'account_id': 50001,
                'data': {'expired': '2118-07-18T17:26:31.000000+00:00'},
                'doc_ref': 'doc_ref',
            },
            web.HTTPBadRequest,
        ),
        (
            # No account_id
            {
                'data': {'expired': '2118-07-18T17:26:31.000000+00:00'},
                'doc_ref': 'doc_ref',
                'idempotency_key': 'idempotency_key',
            },
            web.HTTPBadRequest,
        ),
        (
            # No update field
            {
                'account_id': 50001,
                'doc_ref': 'doc_ref',
                'idempotency_key': 'idempotency_key',
            },
            web.HTTPBadRequest,
        ),
        (
            # No updates in update field
            {
                'account_id': 50001,
                'data': {},
                'doc_ref': 'doc_ref',
                'idempotency_key': 'idempotency_key',
            },
            web.HTTPBadRequest,
        ),
        (
            # No account with account_id
            {
                'account_id': 9990001,
                'data': {'expired': '2118-07-18T17:26:31.000000+00:00'},
                'doc_ref': 'doc_ref',
                'idempotency_key': 'idempotency_key',
            },
            web.HTTPNotFound,
        ),
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'entities@0.sql', 'accounts@0.sql'),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'entities@1.sql', 'accounts@1.sql'),
)
async def test_accounts_update_invalid(
        billing_accounts_client,
        request_headers,
        request_body,
        expected_response,
):
    response = await billing_accounts_client.post(
        '/v1/accounts/update', json=request_body, headers=request_headers,
    )
    assert response.status == expected_response.status_code


async def _get_account(billing_accounts_storage, account_id):
    vid = billing_accounts_storage.vshard_from_id(account_id)
    schema = billing_accounts_storage.vshard_schema(vid)
    master = await billing_accounts_storage.master(vid)
    return await master.fetch(
        f"""
        SELECT expired, updated, updates
        FROM {schema}.account
        WHERE id = $1
        """,
        account_id,
        log_extra={},
    )
