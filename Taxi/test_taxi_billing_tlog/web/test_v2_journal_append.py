import pytest

from taxi_billing_tlog import pgaas


@pytest.mark.config(BILLING_TLOG_RETURN_ENTRIES_ENABLED=True)
@pytest.mark.now('2019-07-17T09:00:00')
@pytest.mark.parametrize(
    'test_data_json',
    [
        'topics_validated.json',
        'entries_inserted.json',
        'payments_entries_inserted.json',
        'antifraud_entries_inserted.json',
        'payment_requests_inserted.json',
        'grocery_agent.json',
        'grocery_revenues.json',
        'eats_revenues.json',
    ],
)
async def test_append_entries(
        web_app_client, load_py_json, web_context, test_data_json,
):
    test_data = load_py_json(test_data_json)

    db = pgaas.TLogEntryStorage(web_context.pg)

    request = test_data['request']
    response = await web_app_client.post('/v2/journal/append', json=request)

    expected_response = test_data['expected_response']

    actual_response = {
        'status': response.status,
        'data': await response.json(),
    }
    assert actual_response == expected_response

    expected_rows = test_data.get('expected_rows')

    if expected_rows is not None:
        rows = await db.select(table=test_data['expected_table'])
        assert rows == expected_rows
