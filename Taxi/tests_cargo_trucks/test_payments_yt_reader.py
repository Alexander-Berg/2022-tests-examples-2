import pytest

PAYMENTS_YT_READER_SETTINGS = {
    'is_enabled': True,
    'batch_size': 1000,
    'launches_pause_ms': 5000,
    'yt_cluster': 'hahn',
    'yt_path': '//home/testsuite/static/payments',
}

PAYMENTS_YT_READER_SETTINGS_BATCH_LIMITED = {
    'is_enabled': True,
    'batch_size': 2,
    'launches_pause_ms': 5000,
    'yt_cluster': 'hahn',
    'yt_path': '//home/testsuite/static/payments',
}


@pytest.mark.config(
    CARGO_TRUCKS_PAYMENTS_YT_READER_SETTINGS=PAYMENTS_YT_READER_SETTINGS_BATCH_LIMITED,
)
@pytest.mark.yt(
    schemas=['yt_payments_schema.yaml'],
    static_table_data=['yt_payments.yaml'],
)
async def test_insert_batch_size(
        taxi_cargo_trucks, yt_apply, get_payments, expected_payments,
):
    await taxi_cargo_trucks.run_distlock_task(
        'cargo-trucks-payments-yt-reader',
    )

    payments = get_payments()
    assert len(payments) == 2
    assert payments == expected_payments

    await taxi_cargo_trucks.run_distlock_task(
        'cargo-trucks-payments-yt-reader',
    )

    payments = get_payments()
    assert len(payments) == 3
    assert payments[2]['yt_line_num'] == 3


@pytest.mark.config(
    CARGO_TRUCKS_PAYMENTS_YT_READER_SETTINGS=PAYMENTS_YT_READER_SETTINGS,
)
@pytest.mark.yt(
    schemas=['yt_payments_schema.yaml'],
    static_table_data=['yt_payments_error.yaml'],
)
async def test_stop_writing_on_error(
        taxi_cargo_trucks, yt_apply, get_payments,
):
    await taxi_cargo_trucks.run_distlock_task(
        'cargo-trucks-payments-yt-reader',
    )

    payments = get_payments()
    assert len(payments) == 1
    assert payments[0]['yt_line_num'] == 1

    await taxi_cargo_trucks.run_distlock_task(
        'cargo-trucks-payments-yt-reader',
    )

    payments = get_payments()
    assert len(payments) == 1


@pytest.fixture(name='get_payments')
def _get_payments(pgsql):
    def _wrapper():
        cursor = pgsql['cargo_trucks'].cursor()
        cursor.execute(
            'SELECT yt_line_num, cash_payment_id, amount, effective_date, '
            'trx_text, customer_text, currency, inn, payment_num, '
            'payment_date, yandex_account_num, trx_number, '
            'billing_person_id, creation_date, bik, account_name, '
            'oebs_export_req_id '
            'FROM cargo_trucks.payments '
            'ORDER BY id ASC',
        )
        result = [
            {
                'yt_line_num': row[0],
                'cash_payment_id': row[1],
                'amount': str(row[2]),
                'effective_date': str(row[3]),
                'trx_text': row[4],
                'customer_text': row[5],
                'currency': row[6],
                'inn': row[7],
                'payment_num': row[8],
                'payment_date': str(row[9]),
                'yandex_account_num': row[10],
                'trx_number': row[11],
                'billing_person_id': row[12],
                'creation_date': str(row[13]),
                'bik': row[14],
                'account_name': row[15],
                'oebs_export_req_id': row[16],
            }
            for row in cursor
        ]
        return result

    return _wrapper


@pytest.fixture(name='expected_payments')
def _expected_payments(load_json):
    return load_json('expected_payments.json')
