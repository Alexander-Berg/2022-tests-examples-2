import pytest

from taxi_billing_tlog import pgaas


_URL = '/v1/journal/append'


@pytest.mark.now('2019-07-17T09:00:00')
@pytest.mark.config(BILLING_TLOG_PRODUCTS={'payment': {'table': 'payments'}})
@pytest.mark.config(BILLING_TLOG_RETURN_ENTRIES_ENABLED=True)
@pytest.mark.config(
    BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT={
        'coupon': {'payment': -1, 'refund': 1},
        'order': {'payment': -1, 'refund': 1},
        'client_b2b_trip_payment': {'payment': -1, 'refund': 1},
        'payment': {'payment': -1, 'refund': 1},
    },
)
async def test_append_entries(web_app_client, load_py_json, web_context):
    data = load_py_json('request.json')
    expected_journal = load_py_json('journal.json')
    expected_payments = load_py_json('payments.json')
    db = pgaas.TLogEntryStorage(web_context.pg)

    response = await web_app_client.post(_URL, json=data)
    journal_entries = await db.select(table='journal')
    payments_entries = await db.select(table='payments')
    assert response.status == 200
    data = await response.json()
    assert data == load_py_json('response.json')
    assert journal_entries == expected_journal
    assert payments_entries == expected_payments
