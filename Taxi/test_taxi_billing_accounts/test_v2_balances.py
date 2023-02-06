import copy

from aiohttp import web
import pytest

from taxi_billing_accounts import config as ba_config
from taxi_billing_accounts import db


@pytest.mark.now('2019-08-21T00:00:00')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                BILLING_ACCOUNTS_FETCH_BALANCES_SEQUENTIALLY=True,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_ACCOUNTS_FETCH_BALANCES_SEQUENTIALLY=False,
            ),
        ),
    ],
)
@pytest.mark.parametrize('use_master', [True, False])
@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            {
                'accounts': [{'account_id': 31370003}],
                'accrued_at': ['2018-10-03T23:59:00+00:00'],
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
                            'last_entry_id': 110003,
                            'last_created': '2019-08-21T00:00:00.000000+00:00',
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
                            'last_entry_id': 110003,
                            'last_created': '2019-08-21T00:00:00.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-10-03T23:59:00.000001+00:00',
                            'balance': '1.0000',
                            'last_entry_id': 10003,
                            'last_created': '2018-10-04T00:00:00.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-10-03T23:59:59.000000+00:00',
                            'balance': '1.0000',
                            'last_entry_id': 10003,
                            'last_created': '2018-10-04T00:00:00.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-10-03T23:59:59.999999+00:00',
                            'balance': '3.0000',
                            'last_entry_id': 20003,
                            'last_created': '2018-10-04T00:00:00.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-10-04T00:00:00.000000+00:00',
                            'balance': '6.0000',
                            'last_entry_id': 30003,
                            'last_created': '2018-10-04T00:00:00.999999+00:00',
                        },
                        {
                            'accrued_at': '2018-10-04T00:00:00.000001+00:00',
                            'balance': '11.0000',
                            'last_entry_id': 40003,
                            'last_created': '2018-10-04T00:00:01.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-10-04T00:00:01.000001+00:00',
                            'balance': '29.0000',
                            'last_entry_id': 60003,
                            'last_created': '2018-10-04T00:00:01.000001+00:00',
                        },
                        {
                            'accrued_at': '2018-10-04T00:01:01.000001+00:00',
                            'balance': '40.0001',
                            'last_entry_id': 70003,
                            'last_created': '2018-10-04T00:00:02.000001+00:00',
                        },
                        {
                            'accrued_at': '2018-10-04T11:59:59.999999+00:00',
                            'balance': '51.0003',
                            'last_entry_id': 80003,
                            'last_created': '2018-10-04T00:01:02.000001+00:00',
                        },
                        {
                            'accrued_at': '2018-10-04T12:00:00.000000+00:00',
                            'balance': '56.0033',
                            'last_entry_id': 90003,
                            'last_created': '2018-10-04T12:00:00.999999+00:00',
                        },
                        {
                            'accrued_at': '2018-10-04T12:00:00.000001+00:00',
                            'balance': '63.0033',
                            'last_entry_id': 100003,
                            'last_created': '2018-10-04T12:00:01.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-10-05T12:00:00.000001+00:00',
                            'balance': '74.0133',
                            'last_entry_id': 110003,
                            'last_created': '2018-10-04T12:00:01.000001+00:00',
                        },
                    ],
                },
            ],
        ),
        (
            {
                'accounts': [
                    {'account_id': 31370003},
                    {'account_id': 31310006},
                ],
                'accrued_at': ['2018-10-03T23:59:00+00:00'],
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
                            'last_entry_id': 110003,
                            'last_created': '2019-08-21T00:00:00.000000+00:00',
                        },
                    ],
                },
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
                            'accrued_at': '2018-10-03T23:59:00.000000+00:00',
                            'balance': '4504501.0000',
                            'last_entry_id': 30010006,
                            'last_created': '2018-08-20T15:50:01.000000+00:00',
                        },
                    ],
                },
            ],
        ),
        # Check that response has unique accounts despite overlapping filter
        (
            {
                'accounts': [
                    {'account_id': 31370003},
                    {
                        'entity_external_id': (
                            'unique_driver_id/5adf9c23a3ddb1256a8542b8'
                        ),
                    },
                ],
                'accrued_at': ['2018-10-03T23:59:00+00:00'],
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
                            'last_entry_id': 110003,
                            'last_created': '2019-08-21T00:00:00.000000+00:00',
                        },
                    ],
                },
                {
                    'account': {
                        'account_id': 31380003,
                        'entity_external_id': (
                            'unique_driver_id/5adf9c23a3ddb1256a8542b8'
                        ),
                        'agreement_id': 'ag-rule-nMFG-000',
                        'currency': 'XXX',
                        'sub_account': 'num_orders',
                    },
                    'balances': [
                        {
                            'accrued_at': '2018-10-03T23:59:00.000000+00:00',
                            'balance': '0',
                            'last_entry_id': 110003,
                            'last_created': '2019-08-21T00:00:00.000000+00:00',
                        },
                    ],
                },
            ],
        ),
    ],
)
@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql', 'balances@0.sql'))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql', 'balances@1.sql'))
async def test_balances_select_mid(
        billing_accounts_client,
        request_headers,
        use_master,
        request_body,
        expected_response,
):
    response = await billing_accounts_client.post(
        '/v2/balances/select',
        json={'use_master': use_master, **request_body},
        headers=request_headers,
    )

    assert response.status == web.HTTPOk.status_code

    found = await response.json()
    _assert_balances_equal(actual=found, expected=expected_response)


@pytest.mark.now('2019-08-21T00:00:00')
@pytest.mark.parametrize('use_master', [True, False])
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                BILLING_ACCOUNTS_FETCH_BALANCES_SEQUENTIALLY=True,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_ACCOUNTS_FETCH_BALANCES_SEQUENTIALLY=False,
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'request_body, expected_response_before, expected_response_after',
    [
        (
            {
                'accounts': [{'account_id': 31370003}],
                'accrued_at': ['2018-10-03T23:59:00+00:00'],
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
                            'last_entry_id': 110003,
                            'last_created': '2019-08-21T00:00:00.000000+00:00',
                        },
                    ],
                },
            ],
            None,
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
                            'last_entry_id': 110003,
                            'last_created': '2019-08-21T00:00:00.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-10-03T23:59:00.000001+00:00',
                            'balance': '1.0000',
                            'last_entry_id': 10003,
                            'last_created': '2018-10-04T00:00:00.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-10-03T23:59:59.000000+00:00',
                            'balance': '1.0000',
                            'last_entry_id': 10003,
                            'last_created': '2018-10-04T00:00:00.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-10-03T23:59:59.999999+00:00',
                            'balance': '3.0000',
                            'last_entry_id': 20003,
                            'last_created': '2018-10-04T00:00:00.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-10-04T00:00:00.000000+00:00',
                            'balance': '6.0000',
                            'last_entry_id': 30003,
                            'last_created': '2018-10-04T00:00:00.999999+00:00',
                        },
                        {
                            'accrued_at': '2018-10-04T00:00:00.000001+00:00',
                            'balance': '11.0000',
                            'last_entry_id': 40003,
                            'last_created': '2018-10-04T00:00:01.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-10-04T00:00:01.000001+00:00',
                            'balance': '29.0000',
                            'last_entry_id': 60003,
                            'last_created': '2018-10-04T00:00:01.000001+00:00',
                        },
                        {
                            'accrued_at': '2018-10-04T00:01:01.000001+00:00',
                            'balance': '40.0001',
                            'last_entry_id': 70003,
                            'last_created': '2018-10-04T00:00:02.000001+00:00',
                        },
                        {
                            'accrued_at': '2018-10-04T11:59:59.999999+00:00',
                            'balance': '51.0003',
                            'last_entry_id': 80003,
                            'last_created': '2018-10-04T00:01:02.000001+00:00',
                        },
                        {
                            'accrued_at': '2018-10-04T12:00:00.000000+00:00',
                            'balance': '56.0033',
                            'last_entry_id': 90003,
                            'last_created': '2018-10-04T12:00:00.999999+00:00',
                        },
                        {
                            'accrued_at': '2018-10-04T12:00:00.000001+00:00',
                            'balance': '63.0033',
                            'last_entry_id': 100003,
                            'last_created': '2018-10-04T12:00:01.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-10-05T12:00:00.000001+00:00',
                            'balance': '74.0133',
                            'last_entry_id': 110003,
                            'last_created': '2018-10-04T12:00:01.000001+00:00',
                        },
                    ],
                },
            ],
            None,
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
                            'last_entry_id': 30010006,
                            'last_created': '2019-08-21T00:00:00.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-08-20T07:20:10.000000+00:00',
                            'balance': '966745.0000',
                            'last_entry_id': 13900006,
                            'last_created': '2018-08-20T07:19:52.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-08-20T08:00:00.000000+00:00',
                            'balance': '1149886.0000',
                            'last_entry_id': 15160006,
                            'last_created': '2018-08-20T07:59:46.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-08-20T12:49:12.000000+00:00',
                            'balance': '2953665.0000',
                            'last_entry_id': 24300006,
                            'last_created': '2018-08-20T12:49:12.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-08-20T13:00:00.000000+00:00',
                            'balance': '3036880.0000',
                            'last_entry_id': 24640006,
                            'last_created': '2018-08-20T12:59:58.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-08-21T00:00:00.000000+00:00',
                            'balance': '4504501.0000',
                            'last_entry_id': 30010006,
                            'last_created': '2018-08-20T15:50:01.000000+00:00',
                        },
                    ],
                },
            ],
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
                            'last_entry_id': 30010006,
                            'last_created': '2019-08-21T00:00:00.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-08-20T07:20:10.000000+00:00',
                            'balance': '966745.0000',
                            'last_entry_id': 20010006,
                            'last_created': '2018-08-20T10:33:21.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-08-20T08:00:00.000000+00:00',
                            'balance': '1149886.0000',
                            'last_entry_id': 20010006,
                            'last_created': '2018-08-20T10:33:21.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-08-20T12:49:12.000000+00:00',
                            'balance': '2953665.0000',
                            'last_entry_id': 24300006,
                            'last_created': '2018-08-20T12:49:12.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-08-20T13:00:00.000000+00:00',
                            'balance': '3036880.0000',
                            'last_entry_id': 24640006,
                            'last_created': '2018-08-20T12:59:58.000000+00:00',
                        },
                        {
                            'accrued_at': '2018-08-21T00:00:00.000000+00:00',
                            'balance': '4504501.0000',
                            'last_entry_id': 30010006,
                            'last_created': '2018-08-20T15:50:01.000000+00:00',
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
        use_master,
        request_body,
        expected_response_before,
        expected_response_after,
):
    response = await billing_accounts_client.post(
        '/v2/balances/select',
        json={'use_master': use_master, **request_body},
        headers=request_headers,
    )

    assert response.status == web.HTTPOk.status_code

    found = await response.json()
    _assert_balances_equal(actual=found, expected=expected_response_before)

    # rollup balances before repeating the same request
    assert await _rollups_count_is(billing_accounts_storage, [3, 6], 0)

    balances = db.BalanceStore(
        storage=billing_accounts_storage, config=ba_config.Config(),
    )
    await balances.rollup(log_extra={})

    assert await _rollups_count_is(billing_accounts_storage, [3], 0)
    assert await _rollups_count_is(billing_accounts_storage, [6], 1)

    response = await billing_accounts_client.post(
        '/v2/balances/select', json=request_body, headers=request_headers,
    )

    assert response.status == web.HTTPOk.status_code

    found = await response.json()
    if expected_response_after is not None:
        _assert_balances_equal(actual=found, expected=expected_response_after)
    else:
        _assert_balances_equal(actual=found, expected=expected_response_before)

    # rollup again to check that nothing changed
    await balances.rollup(log_extra={})
    assert await _rollups_count_is(billing_accounts_storage, [3], 0)
    assert await _rollups_count_is(billing_accounts_storage, [6], 1)


@pytest.mark.now('2019-08-21T00:00:00')
@pytest.mark.parametrize('use_master', [True, False])
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                BILLING_ACCOUNTS_FETCH_BALANCES_SEQUENTIALLY=True,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_ACCOUNTS_FETCH_BALANCES_SEQUENTIALLY=False,
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            {
                'accounts': [{'account_id': 31370003}],
                'accrued_at': ['2018-10-03T23:59:00+00:00'],
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
                            'balance': '1000.0000',
                            'last_entry_id': 10003,
                            'last_created': '2018-10-03T23:00:00.000000+00:00',
                        },
                    ],
                },
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'balances_with_empty_journal@0.sql'),
)
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql', 'balances@1.sql'))
async def test_empty_journal_with_rolled_balance(
        billing_accounts_client,
        request_headers,
        use_master,
        request_body,
        expected_response,
):
    response = await billing_accounts_client.post(
        '/v2/balances/select',
        json={'use_master': use_master, **request_body},
        headers=request_headers,
    )

    assert response.status == web.HTTPOk.status_code

    found = await response.json()
    _assert_balances_equal(actual=found, expected=expected_response)


@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql', 'balances@0.sql'))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql', 'balances@1.sql'))
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                BILLING_ACCOUNTS_FETCH_BALANCES_SEQUENTIALLY=True,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_ACCOUNTS_FETCH_BALANCES_SEQUENTIALLY=False,
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'request_body',
    [
        # Query without account_id or entity_id (so we don't know the shard)
        {
            'accounts': [{'sub_account': 'qwe'}],
            'accrued_at': ['2018-10-03T23:59:00+00:00'],
        },
        # Query with empty account
        {'accounts': [], 'accrued_at': ['2018-10-03T23:59:00+00:00']},
    ],
)
async def test_invalid_request(
        billing_accounts_client, request_headers, request_body,
):
    response = await billing_accounts_client.post(
        '/v2/balances/select', json=request_body, headers=request_headers,
    )
    assert response.status == web.HTTPBadRequest.status_code


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


def _assert_balances_equal(expected, actual):
    expected_cp = copy.deepcopy(expected)
    actual_cp = copy.deepcopy(actual)

    for balance in expected_cp:
        balance['balances'] = sorted(
            balance['balances'], key=lambda x: x['accrued_at'],
        )

    for balance in actual_cp:
        balance['balances'] = sorted(
            balance['balances'], key=lambda x: x['accrued_at'],
        )

    assert expected_cp == actual_cp
