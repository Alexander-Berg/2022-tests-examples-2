import collections

from freezegun import api

from generated.models import billing_reports as billing_models

import corp_spending.components

DATA = [
    {
        'account': {
            'account_id': 223322,
            'agreement_id': 'taxi/orders/limit',
            'currency': 'RUB',
            'entity_external_id': 'corp/client_employee/client_id_1/user_id_1',
            'sub_account': 'payment',
        },
        'balances': [
            {
                'accrued_at': '2020-01-02T07:00:00Z',
                'balance': '1240.00',
                'last_created': '2020-01-02T10:00:00+03:00',
                'last_entry_id': 55,
            },
            {
                'accrued_at': '2020-01-02T00:00:00+00:00',
                'balance': '1160.00',
                'last_created': '2020-01-02T10:00:00+03:00',
                'last_entry_id': 66,
            },
            {
                'accrued_at': '2020-01-01T00:00:00+00:00',
                'balance': '1080.00',
                'last_created': '2020-01-02T10:00:00+00:00',
                'last_entry_id': 77,
            },
            {
                'accrued_at': '2019-12-30T00:00:00+00:00',
                'balance': '1000.00',
                'last_created': '2020-01-02T10:00:00+00:00',
                'last_entry_id': 88,
            },
        ],
    },
    {
        'account': {
            'account_id': 223322,
            'agreement_id': 'taxi/orders/limit',
            'currency': 'RUB',
            'entity_external_id': 'corp/client_employee/client_id_1/user_id_1',
            'sub_account': 'payment/vat',
        },
        'balances': [
            {
                'accrued_at': '2020-01-02T07:00:00Z',
                'balance': '160.00',
                'last_created': '2020-01-02T10:00:00+03:00',
                'last_entry_id': 55,
            },
            {
                'accrued_at': '2020-01-02T00:00:00+00:00',
                'balance': '140.00',
                'last_created': '2020-01-02T10:00:00+03:00',
                'last_entry_id': 66,
            },
            {
                'accrued_at': '2020-01-01T00:00:00+00:00',
                'balance': '120.00',
                'last_created': '2020-01-02T10:00:00+00:00',
                'last_entry_id': 77,
            },
            {
                'accrued_at': '2019-12-30T00:00:00+00:00',
                'balance': '100.00',
                'last_created': '2020-01-02T10:00:00+00:00',
                'last_entry_id': 88,
            },
        ],
    },
    {
        'account': {
            'account_id': 223322,
            'agreement_id': 'taxi/orders/limit',
            'currency': 'XXX',
            'entity_external_id': 'corp/client_employee/client_id_1/user_id_1',
            'sub_account': 'num_orders',
        },
        'balances': [
            {
                'accrued_at': '2020-01-02T07:00:00Z',
                'balance': '3.00',
                'last_created': '2020-01-02T10:00:00+03:00',
                'last_entry_id': 55,
            },
            {
                'accrued_at': '2020-01-02T00:00:00+00:00',
                'balance': '2.00',
                'last_created': '2020-01-02T10:00:00+03:00',
                'last_entry_id': 66,
            },
            {
                'accrued_at': '2020-01-01T00:00:00+00:00',
                'balance': '1.00',
                'last_created': '2020-01-02T10:00:00+00:00',
                'last_entry_id': 77,
            },
            {
                'accrued_at': '2019-12-30T00:00:00+00:00',
                'balance': '0.00',
                'last_created': '2020-01-02T10:00:00+00:00',
                'last_entry_id': 88,
            },
        ],
    },
    {
        'account': {
            'account_id': 223322,
            'agreement_id': 'taxi/orders',
            'currency': 'RUB',
            'entity_external_id': 'corp/client/client_id_1',
            'sub_account': 'payment',
        },
        'balances': [
            {
                'accrued_at': '2020-01-02T07:00:00Z',
                'balance': '1240.00',
                'last_created': '2020-01-02T10:00:00+03:00',
                'last_entry_id': 55,
            },
            {
                'accrued_at': '2020-01-02T00:00:00+00:00',
                'balance': '1160.00',
                'last_created': '2020-01-02T10:00:00+03:00',
                'last_entry_id': 66,
            },
            {
                'accrued_at': '2020-01-01T00:00:00+00:00',
                'balance': '1080.00',
                'last_created': '2020-01-02T10:00:00+00:00',
                'last_entry_id': 77,
            },
            {
                'accrued_at': '2019-12-30T00:00:00+00:00',
                'balance': '1000.00',
                'last_created': '2020-01-02T10:00:00+00:00',
                'last_entry_id': 88,
            },
        ],
    },
    {
        'account': {
            'account_id': 223322,
            'agreement_id': 'taxi/orders',
            'currency': 'RUB',
            'entity_external_id': 'corp/client/client_id_1',
            'sub_account': 'payment/vat',
        },
        'balances': [
            {
                'accrued_at': '2020-01-02T07:00:00Z',
                'balance': '160.00',
                'last_created': '2020-01-02T10:00:00+03:00',
                'last_entry_id': 55,
            },
            {
                'accrued_at': '2020-01-02T00:00:00+00:00',
                'balance': '140.00',
                'last_created': '2020-01-02T10:00:00+03:00',
                'last_entry_id': 66,
            },
            {
                'accrued_at': '2020-01-01T00:00:00+00:00',
                'balance': '120.00',
                'last_created': '2020-01-02T10:00:00+00:00',
                'last_entry_id': 77,
            },
            {
                'accrued_at': '2019-12-30T00:00:00+00:00',
                'balance': '100.00',
                'last_created': '2020-01-02T10:00:00+00:00',
                'last_entry_id': 88,
            },
        ],
    },
    {
        'account': {
            'account_id': 223322,
            'agreement_id': 'taxi/orders/limit',
            'currency': 'RUB',
            'entity_external_id': (
                'corp/client_department/client_id_1/department_id_1'
            ),
            'sub_account': 'payment/vat',
        },
        'balances': [
            {
                'accrued_at': '2020-01-02T07:00:00Z',
                'balance': '160.00',
                'last_created': '2020-01-02T10:00:00+03:00',
                'last_entry_id': 55,
            },
            {
                'accrued_at': '2020-01-02T00:00:00+00:00',
                'balance': '140.00',
                'last_created': '2020-01-02T10:00:00+03:00',
                'last_entry_id': 66,
            },
            {
                'accrued_at': '2020-01-01T00:00:00+00:00',
                'balance': '120.00',
                'last_created': '2020-01-02T10:00:00+00:00',
                'last_entry_id': 77,
            },
            {
                'accrued_at': '2019-12-30T00:00:00+00:00',
                'balance': '100.00',
                'last_created': '2020-01-02T10:00:00+00:00',
                'last_entry_id': 88,
            },
        ],
    },
    {
        'account': {
            'account_id': 223322,
            'agreement_id': 'taxi/orders/limit',
            'currency': 'RUB',
            'entity_external_id': (
                'corp/client_department/client_id_1/department_id_1'
            ),
            'sub_account': 'payment',
        },
        'balances': [
            {
                'accrued_at': '2020-01-02T07:00:00Z',
                'balance': '1240.00',
                'last_created': '2020-01-02T10:00:00+03:00',
                'last_entry_id': 55,
            },
            {
                'accrued_at': '2020-01-02T00:00:00+00:00',
                'balance': '1160.00',
                'last_created': '2020-01-02T10:00:00+03:00',
                'last_entry_id': 66,
            },
            {
                'accrued_at': '2020-01-01T00:00:00+00:00',
                'balance': '1080.00',
                'last_created': '2020-01-02T10:00:00+00:00',
                'last_entry_id': 77,
            },
            {
                'accrued_at': '2019-12-30T00:00:00+00:00',
                'balance': '1000.00',
                'last_created': '2020-01-02T10:00:00+00:00',
                'last_entry_id': 88,
            },
        ],
    },
    {
        'account': {
            'account_id': 223322,
            'agreement_id': 'taxi/orders/limit',
            'currency': 'RUB',
            'entity_external_id': (
                'corp/client_department/client_id_1/department_id_2'
            ),
            'sub_account': 'payment/vat',
        },
        'balances': [
            {
                'accrued_at': '2020-01-02T07:00:00Z',
                'balance': '160.00',
                'last_created': '2020-01-02T10:00:00+03:00',
                'last_entry_id': 55,
            },
            {
                'accrued_at': '2020-01-02T00:00:00+00:00',
                'balance': '140.00',
                'last_created': '2020-01-02T10:00:00+03:00',
                'last_entry_id': 66,
            },
            {
                'accrued_at': '2020-01-01T00:00:00+00:00',
                'balance': '120.00',
                'last_created': '2020-01-02T10:00:00+00:00',
                'last_entry_id': 77,
            },
            {
                'accrued_at': '2019-12-30T00:00:00+00:00',
                'balance': '100.00',
                'last_created': '2020-01-02T10:00:00+00:00',
                'last_entry_id': 88,
            },
        ],
    },
    {
        'account': {
            'account_id': 223322,
            'agreement_id': 'taxi/orders/limit',
            'currency': 'RUB',
            'entity_external_id': (
                'corp/client_department/client_id_1/department_id_2'
            ),
            'sub_account': 'payment',
        },
        'balances': [
            {
                'accrued_at': '2020-01-02T07:00:00Z',
                'balance': '1240.00',
                'last_created': '2020-01-02T10:00:00+03:00',
                'last_entry_id': 55,
            },
            {
                'accrued_at': '2020-01-02T00:00:00+00:00',
                'balance': '1160.00',
                'last_created': '2020-01-02T10:00:00+03:00',
                'last_entry_id': 66,
            },
            {
                'accrued_at': '2020-01-01T00:00:00+00:00',
                'balance': '1080.00',
                'last_created': '2020-01-02T10:00:00+00:00',
                'last_entry_id': 77,
            },
            {
                'accrued_at': '2019-12-30T00:00:00+00:00',
                'balance': '1000.00',
                'last_created': '2020-01-02T10:00:00+00:00',
                'last_entry_id': 88,
            },
        ],
    },
]

ACQUIRED_DATES_FEW = [
    api.FakeDatetime(2020, 1, 2, 0, 0),
    api.FakeDatetime(2020, 1, 1, 0, 0),
    api.FakeDatetime(2019, 12, 30, 0, 0),
]

ACQUIRED_DATES_MANY = [
    api.FakeDatetime(2020, 1, 1, 0, 0),
    api.FakeDatetime(2020, 1, 4, 0, 0),
    api.FakeDatetime(2020, 1, 7, 0, 0),
    api.FakeDatetime(2020, 1, 15, 0, 0),
    api.FakeDatetime(2020, 1, 21, 0, 0),
    api.FakeDatetime(2020, 1, 23, 0, 0),
    api.FakeDatetime(2020, 1, 30, 0, 0),
]


async def test_select_ballace_from_billing(
        library_context, mockserver, load_json,
):
    @mockserver.json_handler('/billing-reports/v1/balances/select')
    def _mock_balances(request):
        return load_json('billing_reports_get_balances.json')

    my_spending = library_context.corp_spending

    accounts = my_spending.make_user_accounts(
        client_id='client_id_1',
        user_id='user_id_1',
        service='taxi',
        currency='RUB',
    )
    accounts.extend(
        my_spending.make_user_accounts(
            client_id='client_id_1',
            user_id='user_id_1',
            service='taxi',
            currency=None,
            num_orders=True,
        ),
    )
    accounts.extend(
        my_spending.make_client_accounts(
            client_id='client_id_1', service='taxi', currency='RUB',
        ),
    )
    accounts.extend(
        my_spending.make_department_accounts(
            client_id='client_id_1',
            department_id='department_id_2',
            service='taxi',
            currency='RUB',
        ),
    )

    accounts.extend(
        my_spending.make_department_accounts(
            client_id='client_id_1',
            department_id='department_id_1',
            service='taxi',
            currency='RUB',
        ),
    )

    expected_result_balance = [
        billing_models.BalanceEntry.deserialize(single_data)
        for single_data in DATA
    ]

    expected_result = collections.defaultdict(lambda: [])
    for entry in expected_result_balance:
        key = corp_spending.components.EntryKey(
            entity_external_id=entry.account.entity_external_id,
            agreement_id=entry.account.agreement_id,
            currency=entry.account.currency,
        )
        expected_result[key].append(entry)

    entries = await my_spending.select_balance_from_billing(
        accounts, ACQUIRED_DATES_FEW,
    )
    entriesd = dict(entries)

    assert len(expected_result) == len(entriesd)

    for key in entriesd.keys():
        assert billing_models.BalanceEntry.serialize(
            entriesd[key][0],
        ) == billing_models.BalanceEntry.serialize(expected_result[key][0])
        if expected_result[key][0].account.sub_account != 'num_orders':
            assert len(entriesd[key]) == 2
            assert billing_models.BalanceEntry.serialize(
                entriesd[key][1],
            ) == billing_models.BalanceEntry.serialize(expected_result[key][1])


async def test_select_ballace_from_billing_dates(
        library_context, mockserver, load_json,
):
    @mockserver.json_handler('/billing-reports/v1/balances/select')
    def _mock_balances(request):
        return load_json('billing_reports_get_balances_many_dates.json')

    my_spending = library_context.corp_spending
    accounts = my_spending.make_user_accounts(
        client_id='client_id_1',
        user_id='user_id_1',
        service='taxi',
        currency=None,
        num_orders=True,
    )

    entries = dict(
        await my_spending.select_balance_from_billing(
            accounts, ACQUIRED_DATES_MANY,
        ),
    )
    recieved_dates = []
    for balance_entry_list in entries.values():
        for balance_entry in balance_entry_list:
            for balance in balance_entry.balances:
                recieved_dates.extend([balance.accrued_at])

    assert recieved_dates == ACQUIRED_DATES_MANY
