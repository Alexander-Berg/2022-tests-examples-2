import operator

import pytest


@pytest.mark.ydb(files=['fill_issues.sql'])
@pytest.mark.parametrize(
    'test_data_json',
    [
        'request.json',
        'request_exists.json',
        'request_update_amount.json',
        'request_with_amount.json',
    ],
)
async def test_register_issue(
        taxi_billing_payment_admin, test_data_json, ydb, load_json,
):
    test_data = load_json(test_data_json)
    response = await taxi_billing_payment_admin.post(
        'v1/issue/register', json=test_data['request'],
    )
    assert response.status_code == 200
    assert response.json() == {}

    ids = ','.join(
        map(
            lambda row: '\'{}\''.format(row['invoice_id']),
            test_data['expected']['ydb'],
        ),
    )
    cursor = ydb.execute(
        f"""
        --!syntax_v1
        SELECT
            CAST(invoice_id_hash as Uint64) AS invoice_id_hash,
            CAST(invoice_id as Utf8) AS invoice_id,
            CAST(namespace_id as Utf8) AS namespace_id,
            CAST(kind as Utf8) AS kind,
            CAST(target as Utf8) AS target,
            CAST(external_id as Utf8?) AS external_id,
            payload,
            CAST(description as Utf8) AS description,
            created,
            payload_updated,
            CAST(description_updated as Utf8) AS description_updated,
            updated,
            counter,
            CAST(amount AS Utf8) AS amount,
            CAST(currency AS Utf8) AS currency,
            processed,
            ticket
        FROM issues
        WHERE invoice_id in [{ids}]
    """,
    )
    assert len(cursor) == 1
    assert len(cursor[0].rows) == len(test_data['expected']['ydb'])
    if test_data['expected']['ydb']:
        actual_rows = []
        columns = list(test_data['expected']['ydb'][0].keys())
        # extract fields by first line
        fields_getter = operator.itemgetter(*columns)
        for actual_row in cursor[0].rows:
            actual_rows.append(dict(zip(columns, fields_getter(actual_row))))
        sorted(actual_rows, key=lambda item: item['invoice_id'])
        assert actual_rows == test_data['expected']['ydb']
