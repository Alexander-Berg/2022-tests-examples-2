from aiohttp import web
import pytest

from taxi_billing_accounts import config as ba_config
from taxi_billing_accounts import db


@pytest.mark.parametrize('limit', [0, 1, 1000])
@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            {
                'accounts': [{'account_id': 31370003}],
                'accrued_at': ['2018-10-03T23:59:00+00:00'],
                'offset': 0,
            },
            [
                {
                    'account': {
                        'account_id': 31370003,
                        'entity_external_id': (
                            'unique_driver_id/5adf9c23a3ddb1256a8542b8'
                        ),
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'RUB',
                        'sub_account': 'income',
                    },
                    'balances': [
                        {
                            'accrued_at': '2018-10-03T23:59:00.000000+00:00',
                            'balance': '0',
                        },
                    ],
                },
            ],
        ),
        (
            {
                'accounts': [{'account_id': 31370003}],
                'accrued_at': [
                    '2018-10-03T23:59:00.000000+00:00',
                    '2018-10-03T23:59:00.000001+00:00',
                    '2018-10-03T23:59:59.000000+00:00',
                    '2018-10-03T23:59:59.999999+00:00',
                    '2018-10-04T00:00:00.000000+00:00',
                    '2018-10-04T00:00:00.000001+00:00',
                    '2018-10-04T00:00:00.000001+00:00',
                    '2018-10-04T00:00:01.000001+00:00',
                    '2018-10-04T00:01:01.000001+00:00',
                    '2018-10-04T11:59:59.999999+00:00',
                    '2018-10-04T12:00:00.000000+00:00',
                    '2018-10-04T12:00:00.000001+00:00',
                    '2018-10-05T12:00:00.000001+00:00',
                ],
                'offset': 0,
            },
            [
                {
                    'account': {
                        'account_id': 31370003,
                        'entity_external_id': (
                            'unique_driver_id/5adf9c23a3ddb1256a8542b8'
                        ),
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'RUB',
                        'sub_account': 'income',
                    },
                    'balances': [
                        {
                            'accrued_at': '2018-10-03T23:59:00.000000+00:00',
                            'balance': '0',
                        },
                        {
                            'accrued_at': '2018-10-03T23:59:00.000001+00:00',
                            'balance': '1.0000',
                        },
                        {
                            'accrued_at': '2018-10-03T23:59:59.000000+00:00',
                            'balance': '1.0000',
                        },
                        {
                            'accrued_at': '2018-10-03T23:59:59.999999+00:00',
                            'balance': '3.0000',
                        },
                        {
                            'accrued_at': '2018-10-04T00:00:00.000000+00:00',
                            'balance': '6.0000',
                        },
                        {
                            'accrued_at': '2018-10-04T00:00:00.000001+00:00',
                            'balance': '11.0000',
                        },
                        {
                            'accrued_at': '2018-10-04T00:00:01.000001+00:00',
                            'balance': '29.0000',
                        },
                        {
                            'accrued_at': '2018-10-04T00:01:01.000001+00:00',
                            'balance': '40.0001',
                        },
                        {
                            'accrued_at': '2018-10-04T11:59:59.999999+00:00',
                            'balance': '51.0003',
                        },
                        {
                            'accrued_at': '2018-10-04T12:00:00.000000+00:00',
                            'balance': '56.0033',
                        },
                        {
                            'accrued_at': '2018-10-04T12:00:00.000001+00:00',
                            'balance': '63.0033',
                        },
                        {
                            'accrued_at': '2018-10-05T12:00:00.000001+00:00',
                            'balance': '74.0133',
                        },
                    ],
                },
            ],
        ),
    ],
)
@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql', 'balances@0.sql'))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_balances_select_mid(
        billing_accounts_client,
        request_headers,
        request_body,
        limit,
        expected_response,
):
    request_body['limit'] = limit
    response = await billing_accounts_client.post(
        '/v1/balances/select', json=request_body, headers=request_headers,
    )

    assert response.status == web.HTTPOk.status_code

    if limit:
        found = await response.json()
        assert found == expected_response


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            {
                'accounts': [{'account_id': 31370003}],
                'accrued_at': ['2018-10-03T23:59:00+00:00'],
                'offset': 0,
                'limit': 1,
            },
            [
                {
                    'account': {
                        'account_id': 31370003,
                        'entity_external_id': (
                            'unique_driver_id/5adf9c23a3ddb1256a8542b8'
                        ),
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'RUB',
                        'sub_account': 'income',
                    },
                    'balances': [
                        {
                            'accrued_at': '2018-10-03T23:59:00.000000+00:00',
                            'balance': '0',
                        },
                    ],
                },
            ],
        ),
        (
            {
                'accounts': [{'account_id': 31370003}],
                'accrued_at': [
                    '2018-10-03T23:59:00.000000+00:00',
                    '2018-10-03T23:59:00.000001+00:00',
                    '2018-10-03T23:59:59.000000+00:00',
                    '2018-10-03T23:59:59.999999+00:00',
                    '2018-10-04T00:00:00.000000+00:00',
                    '2018-10-04T00:00:00.000001+00:00',
                    '2018-10-04T00:00:00.000001+00:00',
                    '2018-10-04T00:00:01.000001+00:00',
                    '2018-10-04T00:01:01.000001+00:00',
                    '2018-10-04T11:59:59.999999+00:00',
                    '2018-10-04T12:00:00.000000+00:00',
                    '2018-10-04T12:00:00.000001+00:00',
                    '2018-10-05T12:00:00.000001+00:00',
                ],
                'offset': 0,
                'limit': 1,
            },
            [
                {
                    'account': {
                        'account_id': 31370003,
                        'entity_external_id': (
                            'unique_driver_id/5adf9c23a3ddb1256a8542b8'
                        ),
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'RUB',
                        'sub_account': 'income',
                    },
                    'balances': [
                        {
                            'accrued_at': '2018-10-03T23:59:00.000000+00:00',
                            'balance': '0',
                        },
                        {
                            'accrued_at': '2018-10-03T23:59:00.000001+00:00',
                            'balance': '1.0000',
                        },
                        {
                            'accrued_at': '2018-10-03T23:59:59.000000+00:00',
                            'balance': '1.0000',
                        },
                        {
                            'accrued_at': '2018-10-03T23:59:59.999999+00:00',
                            'balance': '3.0000',
                        },
                        {
                            'accrued_at': '2018-10-04T00:00:00.000000+00:00',
                            'balance': '6.0000',
                        },
                        {
                            'accrued_at': '2018-10-04T00:00:00.000001+00:00',
                            'balance': '11.0000',
                        },
                        {
                            'accrued_at': '2018-10-04T00:00:01.000001+00:00',
                            'balance': '29.0000',
                        },
                        {
                            'accrued_at': '2018-10-04T00:01:01.000001+00:00',
                            'balance': '40.0001',
                        },
                        {
                            'accrued_at': '2018-10-04T11:59:59.999999+00:00',
                            'balance': '51.0003',
                        },
                        {
                            'accrued_at': '2018-10-04T12:00:00.000000+00:00',
                            'balance': '56.0033',
                        },
                        {
                            'accrued_at': '2018-10-04T12:00:00.000001+00:00',
                            'balance': '63.0033',
                        },
                        {
                            'accrued_at': '2018-10-05T12:00:00.000001+00:00',
                            'balance': '74.0133',
                        },
                    ],
                },
            ],
        ),
        (
            {
                'accounts': [{'account_id': 31310006}],
                'accrued_at': [
                    '2018-08-20T00:00:00+00:00',
                    '2018-08-20T07:20:10+00:00',
                    '2018-08-20T12:49:12+00:00',
                    '2018-08-21T00:00:00+00:00',
                    '2018-08-20T13:00:00+00:00',
                    '2018-08-20T08:00:00+00:00',
                ],
                'offset': 0,
                'limit': 1,
            },
            [
                {
                    'account': {
                        'account_id': 31310006,
                        'entity_external_id': (
                            'unique_driver_id/5b4f48a941e102a72fefe30e'
                        ),
                        'agreement_id': 'ag-rule-autotest',
                        'currency': 'XXX',
                        'sub_account': 'autofill',
                    },
                    'balances': [
                        {
                            'accrued_at': '2018-08-20T00:00:00.000000+00:00',
                            'balance': '0',
                        },
                        {
                            'accrued_at': '2018-08-20T07:20:10.000000+00:00',
                            'balance': '966745.0000',
                        },
                        {
                            'accrued_at': '2018-08-20T08:00:00.000000+00:00',
                            'balance': '1149886.0000',
                        },
                        {
                            'accrued_at': '2018-08-20T12:49:12.000000+00:00',
                            'balance': '2953665.0000',
                        },
                        {
                            'accrued_at': '2018-08-20T13:00:00.000000+00:00',
                            'balance': '3036880.0000',
                        },
                        {
                            'accrued_at': '2018-08-21T00:00:00.000000+00:00',
                            'balance': '4504501.0000',
                        },
                    ],
                },
            ],
        ),
    ],
)
@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql', 'balances@0.sql'))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql', 'balances@1.sql'))
async def test_balances_select_rollup(
        billing_accounts_storage,
        billing_accounts_client,
        request_headers,
        request_body,
        expected_response,
):
    response = await billing_accounts_client.post(
        '/v1/balances/select', json=request_body, headers=request_headers,
    )

    assert response.status == web.HTTPOk.status_code

    found = await response.json()
    assert found == expected_response

    # rollup balances before repeating the same request
    assert await _rollups_count_is(billing_accounts_storage, [3, 6], 0)

    balances = db.BalanceStore(
        storage=billing_accounts_storage, config=ba_config.Config(),
    )
    await balances.rollup(log_extra={})

    assert await _rollups_count_is(billing_accounts_storage, [3], 0)
    assert await _rollups_count_is(billing_accounts_storage, [6], 1)

    response = await billing_accounts_client.post(
        '/v1/balances/select', json=request_body, headers=request_headers,
    )

    assert response.status == web.HTTPOk.status_code

    found = await response.json()
    assert found == expected_response

    # rollup again to check that nothing changed
    await balances.rollup(log_extra={})
    assert await _rollups_count_is(billing_accounts_storage, [3], 0)
    assert await _rollups_count_is(billing_accounts_storage, [6], 1)


async def _rollups_count_is(storage, vids, expected) -> bool:
    from taxi.billing import pgstorage

    for vid in vids:
        executor = await pgstorage.Executor.create(storage, vid)
        schema = storage.vshard_schema(vid)
        rows = await executor.fetch(
            f'SELECT * FROM {schema}.rollups', log_extra={},
        )

        if len(rows) != expected:
            return False

    return True
