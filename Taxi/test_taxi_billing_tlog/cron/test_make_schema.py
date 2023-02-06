import pytest

from taxi_billing_tlog.yt import schemas


def _to_dict(what):
    return {el['name']: el for el in what}


@pytest.mark.config(
    BILLING_TLOG_YT_COLUMNS_FILTERS={
        'revenues': {
            'aggregation_sign': {'from_date': '2019-07-21'},
            'contract_id': {'from_date': '2019-07-21'},
        },
        'expenses': {
            'ignore_in_balance': {'to_date': '2019-07-22'},
            'contract_id': {'to_date': '2019-07-22'},
        },
        'payments': {
            'invoice_date': {'from_date': '2019-07-21'},
            'contract_id': {'from_date': '2019-07-21'},
        },
        'cashback': {
            'invoice_date': {'from_date': '2019-07-21'},
            'payload': {'from_date': '2019-07-21'},
            'wallet_id': {'from_date': '2019-07-21'},
            'transaction_type': {'from_date': '2019-07-21'},
        },
    },
)
@pytest.mark.parametrize(
    'expected_json,what_date',
    [
        # all fields must be in result schemas
        ('schemas_without_filters.json', '2019-07-21'),
        # aggregation_sign, contract_id must not be in revenues schema
        # invoice_date, contract_id must not be in payments schema
        ('schemas_with_from_date_filter.json', '2019-07-20'),
        # ignore_in_balance, contract_id must not be in expenses schema
        ('schemas_with_to_date_filter.json', '2019-07-23'),
    ],
)
async def test_schema_without_filters(
        cron_context, load_json, expected_json, what_date,
):
    all_expected = load_json(expected_json)

    schema = schemas.RevenuesYtSchema(cron_context)
    schema_for_date = schema.for_date(what_date)
    expected_revenues = all_expected['expected_revenues']
    assert _to_dict(schema_for_date) == _to_dict(expected_revenues['columns'])
    assert schema_for_date.attributes == expected_revenues['attributes']

    schema = schemas.ExpensesYtSchema(cron_context)
    schema_for_date = schema.for_date(what_date)
    expected_expenses = all_expected['expected_expenses']
    assert _to_dict(schema_for_date) == _to_dict(expected_expenses['columns'])
    assert schema_for_date.attributes == expected_expenses['attributes']

    schema = schemas.PaymentsYtSchema(cron_context)
    schema_for_date = schema.for_date(what_date)
    expected_payments = all_expected['expected_payments']
    assert _to_dict(schema_for_date) == _to_dict(expected_payments['columns'])
    assert schema_for_date.attributes == expected_payments['attributes']

    schema = schemas.CashbackYtSchema(cron_context)
    schema_for_date = schema.for_date(what_date)
    expected_cashback = all_expected['expected_cashback']
    assert _to_dict(schema_for_date) == _to_dict(expected_cashback['columns'])
    assert schema_for_date.attributes == expected_cashback['attributes']
