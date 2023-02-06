import decimal

from freezegun import api
import pytest
import pytz


ACQUIRED_DATES_FEW = [
    api.FakeDatetime(2020, 1, 1, 0, 0),
    api.FakeDatetime(2020, 1, 2, 0, 0),
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


TEST_CALCULATE_ENTRY_SPENDING_NUM_ORDERS_PARAMS = dict(
    argnames=['now', 'period', 'balance_diff'],
    argvalues=[
        pytest.param(
            api.FakeDatetime(2020, 1, 30, 0, 0, tzinfo=pytz.utc),
            api.FakeDatetime(2020, 1, 15, 0, 0, tzinfo=pytz.utc),
            decimal.Decimal(119.00),
        ),
        pytest.param(
            api.FakeDatetime(2020, 1, 7, 0, 0, tzinfo=pytz.utc),
            api.FakeDatetime(2020, 1, 1, 0, 0, tzinfo=pytz.utc),
            decimal.Decimal(92.00),
        ),
        pytest.param(
            api.FakeDatetime(2020, 1, 23, 0, 0, tzinfo=pytz.utc),
            api.FakeDatetime(2020, 1, 23, 0, 0, tzinfo=pytz.utc),
            decimal.Decimal(0.00),
        ),
    ],
)


@pytest.mark.parametrize(**TEST_CALCULATE_ENTRY_SPENDING_NUM_ORDERS_PARAMS)
async def test_calculate_entry_spending_num_orders(
        library_context, mockserver, load_json, now, period, balance_diff,
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
    entry_key = my_spending.make_user_entry_key(
        client_id='client_id_1',
        user_id='user_id_1',
        service='taxi',
        currency=None,
    )
    entries = dict(
        await my_spending.select_balance_from_billing(
            accounts, ACQUIRED_DATES_MANY,
        ),
    )
    assert (
        my_spending.calculate_entry_spending(
            entries=entries,
            key=entry_key,
            now=now,
            period=period,
            num_orders=True,
        )
        == balance_diff
    )


TEST_CALCULATE_ENTRY_SPENDING_NUM_ORDERS_SUB_ACCOUNT_PARAMS = dict(
    argnames=['now', 'period', 'balance_diff'],
    argvalues=[
        pytest.param(
            api.FakeDatetime(2020, 1, 1, 0, 0, tzinfo=pytz.utc),
            api.FakeDatetime(2019, 12, 30, 0, 0, tzinfo=pytz.utc),
            decimal.Decimal(100.00),
        ),
        pytest.param(
            api.FakeDatetime(2020, 1, 2, 0, 0, tzinfo=pytz.utc),
            api.FakeDatetime(2019, 12, 30, 0, 0, tzinfo=pytz.utc),
            decimal.Decimal(200.00),
        ),
        pytest.param(
            api.FakeDatetime(2020, 1, 2, 7, 0, tzinfo=pytz.utc),
            api.FakeDatetime(2019, 12, 30, 0, 0, tzinfo=pytz.utc),
            decimal.Decimal(300.00),
        ),
    ],
)


@pytest.mark.parametrize(
    **TEST_CALCULATE_ENTRY_SPENDING_NUM_ORDERS_SUB_ACCOUNT_PARAMS,
)
async def test_calculate_entry_spending_payment_sub_account(
        library_context, mockserver, load_json, now, period, balance_diff,
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

    entries = dict(
        await my_spending.select_balance_from_billing(
            accounts, ACQUIRED_DATES_FEW,
        ),
    )

    entry_key = my_spending.make_user_entry_key(
        client_id='client_id_1',
        user_id='user_id_1',
        service='taxi',
        currency='RUB',
    )

    assert (
        my_spending.calculate_entry_spending(
            entries=entries,
            key=entry_key,
            now=now,
            period=period,
            num_orders=False,
        )
        == balance_diff
    )
