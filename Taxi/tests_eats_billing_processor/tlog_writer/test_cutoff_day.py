import pytest

from tests_eats_billing_processor.tlog_writer import helper


@pytest.mark.parametrize(
    'transaction_date, expect_event_time',
    [
        pytest.param('2022-02-10T00:00:00+00:00', '2022-02-10T00:00:00+00:00'),
        pytest.param('2022-01-05T00:00:00+00:00', '2022-02-20T09:00:00+00:00'),
        pytest.param('2022-02-02T00:00:00+00:00', '2022-02-02T00:00:00+00:00'),
    ],
)
@pytest.mark.config(
    EATS_BILLING_PROCESSOR_FEATURES={
        'tlog_write_enabled': {'agent': True},
        'cutoff_day': 6,
    },
)
@pytest.mark.now('2022-02-20T09:00:00+00:00')
async def test_now_after_cutoff_day(
        tlog_writer_fixtures, transaction_date, expect_event_time,
):
    await (
        helper.TlogWriterTest()
        .with_rule('retail')
        .with_transaction_date(transaction_date)
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='RU',
                mvp='br_moscow_adm',
            ),
            payment=helper.payment_data(
                product_type='retail',
                amount='150',
                currency='RUB',
                payment_method='card',
                payment_terminal_id='222333',
            ),
            templates=[{'template_name': 'some_name', 'context': {}}],
        )
        .expect_payment(
            event_time=expect_event_time,
            amount='150',
            terminal_id=222333,
            paysys_type='alfa-bank',
            company_type='retail_own_packing_and_delivery',
            firm_id='32',
            product='eats_payment',
            detailed_product='eats_payment',
            service_id=699,
            ignore_in_balance=True,
            template_entries=[{'template_name': 'some_name', 'context': {}}],
        )
        .run(tlog_writer_fixtures)
    )


@pytest.mark.parametrize(
    'transaction_date, expect_event_time',
    [
        pytest.param('2022-03-01T00:00:00+00:00', '2022-03-01T00:00:00+00:00'),
        pytest.param('2022-02-10T00:00:00+00:00', '2022-02-10T00:00:00+00:00'),
        pytest.param('2022-01-30T00:00:00+00:00', '2022-03-04T09:00:00+00:00'),
    ],
)
@pytest.mark.config(
    EATS_BILLING_PROCESSOR_FEATURES={
        'tlog_write_enabled': {'agent': True},
        'cutoff_day': 6,
    },
)
@pytest.mark.now('2022-03-04T09:00:00+00:00')
async def test_now_pref_cutoff_day(
        tlog_writer_fixtures, transaction_date, expect_event_time,
):
    await (
        helper.TlogWriterTest()
        .with_rule('retail')
        .with_transaction_date(transaction_date)
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='RU',
                mvp='br_moscow_adm',
            ),
            payment=helper.payment_data(
                product_type='retail',
                amount='150',
                currency='RUB',
                payment_method='card',
                payment_terminal_id='222333',
            ),
            templates=[{'template_name': 'some_name', 'context': {}}],
        )
        .expect_payment(
            event_time=expect_event_time,
            amount='150',
            terminal_id=222333,
            paysys_type='alfa-bank',
            company_type='retail_own_packing_and_delivery',
            firm_id='32',
            product='eats_payment',
            detailed_product='eats_payment',
            service_id=699,
            ignore_in_balance=True,
            template_entries=[{'template_name': 'some_name', 'context': {}}],
        )
        .run(tlog_writer_fixtures)
    )


@pytest.mark.parametrize(
    'transaction_date, expect_event_time',
    [
        pytest.param('2022-01-01T00:00:00+00:00', '2022-01-01T00:00:00+00:00'),
        pytest.param('2021-12-10T00:00:00+00:00', '2021-12-10T00:00:00+00:00'),
        pytest.param('2021-12-02T00:00:00+00:00', '2021-12-02T00:00:00+00:00'),
    ],
)
@pytest.mark.config(
    EATS_BILLING_PROCESSOR_FEATURES={
        'tlog_write_enabled': {'agent': True},
        'cutoff_day': 6,
    },
)
@pytest.mark.now('2022-01-03T09:00:00+00:00')
async def test_last_years_cutoff_day(
        tlog_writer_fixtures, transaction_date, expect_event_time,
):
    await (
        helper.TlogWriterTest()
        .with_rule('retail')
        .with_transaction_date(transaction_date)
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='RU',
                mvp='br_moscow_adm',
            ),
            payment=helper.payment_data(
                product_type='retail',
                amount='150',
                currency='RUB',
                payment_method='card',
                payment_terminal_id='222333',
            ),
            templates=[{'template_name': 'some_name', 'context': {}}],
        )
        .expect_payment(
            event_time=expect_event_time,
            amount='150',
            terminal_id=222333,
            paysys_type='alfa-bank',
            company_type='retail_own_packing_and_delivery',
            firm_id='32',
            product='eats_payment',
            detailed_product='eats_payment',
            service_id=699,
            ignore_in_balance=True,
            template_entries=[{'template_name': 'some_name', 'context': {}}],
        )
        .run(tlog_writer_fixtures)
    )
