import pytest

from tests_eats_billing_processor.tlog_writer import helper


async def test_payment(tlog_writer_fixtures):
    await (
        helper.TlogWriterTest()
        .with_rule('retail')
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


async def test_payment_grocery_eats_flow(tlog_writer_fixtures):
    await (
        helper.TlogWriterTest()
        .with_rule('grocery_eats_flow')
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='RU',
                mvp='br_moscow_adm',
            ),
            payment=helper.payment_data(
                product_type='product',
                amount='150',
                currency='RUB',
                payment_method='card',
                payment_terminal_id='222333',
            ),
            templates=[{'template_name': 'some_name', 'context': {}}],
        )
        .expect_payment(
            amount='150',
            terminal_id=222333,
            paysys_type='alfa-bank',
            company_type='lavka',
            firm_id='32',
            product='eats_payment',
            detailed_product='eats_payment',
            service_id=629,
            ignore_in_balance=True,
            template_entries=[{'template_name': 'some_name', 'context': {}}],
        )
        .run(tlog_writer_fixtures)
    )


async def test_refund(tlog_writer_fixtures):
    await (
        helper.TlogWriterTest()
        .with_rule('restaurant')
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='BY',
                mvp='br_minsk',
            ),
            refund=helper.refund_data(
                product_type='product',
                amount='150',
                currency='BYN',
                payment_method='card',
                payment_terminal_id='222333',
            ),
            templates=[
                {
                    'template_name': 'with_context',
                    'context': {'one': '1', 'two': 2},
                },
            ],
        )
        .expect_refund(
            amount='150',
            terminal_id=222333,
            paysys_type='alfa-bank',
            company_type='own_delivery',
            firm_id='22',
            product='eats_payment',
            detailed_product='eats_payment',
            service_id=629,
            ignore_in_balance=True,
            template_entries=[
                {
                    'template_name': 'with_context',
                    'context': {'one': '1', 'two': 2},
                },
            ],
        )
        .run(tlog_writer_fixtures)
    )


async def test_default_mapping_restaurant(tlog_writer_fixtures):
    await (
        helper.TlogWriterTest()
        .with_rule('default')
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='BY',
                mvp='br_minsk',
            ),
            refund=helper.refund_data(
                product_type='product',
                amount='150',
                currency='BYN',
                payment_method='card',
                payment_terminal_id='222333',
            ),
            templates=[
                {'template_name': 'first', 'context': {}},
                {'template_name': 'second', 'context': {}},
            ],
        )
        .expect_refund(
            amount='150',
            terminal_id=222333,
            paysys_type='alfa-bank',
            company_type='own_delivery',
            firm_id='22',
            product='eats_payment',
            detailed_product='eats_payment',
            service_id=629,
            ignore_in_balance=True,
            template_entries=[
                {'template_name': 'first', 'context': {}},
                {'template_name': 'second', 'context': {}},
            ],
        )
        .run(tlog_writer_fixtures)
    )


async def test_default_mapping_retail(tlog_writer_fixtures):
    await (
        helper.TlogWriterTest()
        .with_rule('default')
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
        )
        .expect_payment(
            amount='150',
            terminal_id=222333,
            paysys_type='alfa-bank',
            company_type='retail_own_packing_and_delivery',
            firm_id='32',
            product='eats_payment',
            detailed_product='eats_payment',
            service_id=699,
            ignore_in_balance=True,
        )
        .run(tlog_writer_fixtures)
    )


async def test_commission(tlog_writer_fixtures):
    await (
        helper.TlogWriterTest()
        .with_rule('marketplace')
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='KZ',
                mvp='br_astana',
            ),
            commission=helper.commission_data(
                product_type='product',
                amount='1200',
                currency='KZT',
                commission_type='goods',
            ),
        )
        .expect_payment(
            amount_with_vat='1200',
            vat_amount='128.57',
            amount_without_vat='1071.43',
            company_type='marketplace',
            firm_id='24',
            product='eats_order_commission_marketplace',
            detailed_product='eats_order_commission_marketplace',
            service_id=628,
            ignore_in_balance=True,
        )
        .run(tlog_writer_fixtures)
    )


async def test_service_id_fallback(tlog_writer_fixtures):
    await (
        helper.TlogWriterTest()
        .with_rule('default')
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='RU',
                mvp='br_orenburg',
                employment='self_employed',
            ),
            commission=helper.commission_data(
                product_type='delivery',
                amount='1200',
                currency='RUB',
                product_id='delivery__001',
            ),
        )
        .expect_payment(
            amount_with_vat='1200',
            vat_amount='200',
            amount_without_vat='1000',
            company_type='own_delivery',
            firm_id='32',
            product='eats_delivery_fee',
            detailed_product='eats_delivery_fee_smz',
            service_id=645,
            ignore_in_balance=True,
        )
        .run(tlog_writer_fixtures)
    )


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_DETAILED_PRODUCT_MAP=[
        {
            'key': {'kind': 'payment', 'product_type': 'service_fee'},
            'value': {
                'detailed_product': 'eats_client_service_fee_payment',
                'product': 'eats_client_service_fee',
                'type': 'payments',
                'released_at': '2002-10-15T00:00:00+03:00',
            },
        },
    ],
)
async def test_released_at(tlog_writer_fixtures):
    await (
        helper.TlogWriterTest()
        .with_rule('retail')
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='RU',
                mvp='br_moscow_adm',
            ),
            payment=helper.payment_data(
                product_type='service_fee',
                amount='150',
                currency='RUB',
                payment_method='card',
                payment_terminal_id='222333',
            ),
        )
        .expect_payment(
            amount_with_vat='150',
            vat_amount='25',
            amount_without_vat='125',
            terminal_id=222333,
            paysys_type='alfa-bank',
            company_type='retail_own_packing_and_delivery',
            firm_id='32',
            product='eats_client_service_fee',
            detailed_product='eats_client_service_fee_payment',
            service_id=1167,
            ignore_in_balance=False,
        )
        .run(tlog_writer_fixtures)
    )


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_DETAILED_PRODUCT_MAP=[
        {
            'key': {'kind': 'payment', 'product_type': 'service_fee'},
            'value': {
                'detailed_product': 'eats_client_service_fee_payment',
                'product': 'eats_client_service_fee',
                'type': 'payments',
                'released_at': '2010-10-15T00:00:00+03:00',
            },
        },
    ],
)
async def test_released_at_error(tlog_writer_fixtures):
    await (
        helper.TlogWriterTest()
        .with_rule('retail')
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='RU',
                mvp='br_moscow_adm',
            ),
            payment=helper.payment_data(
                product_type='service_fee',
                amount='150',
                currency='RUB',
                payment_method='card',
                payment_terminal_id='222333',
            ),
        )
        .async_fail()
        .expect_fail()
        .run(tlog_writer_fixtures)
    )


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_DETAILED_PRODUCT_MAP=[
        {
            'key': {
                'kind': 'payment',
                'type': ['yandex_account_withdraw', 'yandex_account_topup'],
            },
            'value': 'ignore',
        },
    ],
)
async def test_ignore(tlog_writer_fixtures):
    await (
        helper.TlogWriterTest()
        .with_rule('retail')
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='RU',
                mvp='br_moscow_adm',
            ),
            payment=helper.payment_data(
                product_type='delivery',
                amount='150',
                currency='RUB',
                payment_method='yandex_account_withdraw',
                payment_terminal_id='222333',
            ),
        )
        .expect_no_request()
        .run(tlog_writer_fixtures)
    )


async def test_error(tlog_writer_fixtures):
    await (
        helper.TlogWriterTest()
        .with_rule('retail')
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='RU',
                mvp='br_moscow_adm',
            ),
            payment=helper.payment_data(
                product_type='service_fee',
                amount='150',
                currency='RUB',
                payment_method='card',
                payment_terminal_id='222333',
            ),
        )
        .async_fail()
        .expect_fail()
        .run(tlog_writer_fixtures)
    )


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_DETAILED_PRODUCT_MAP=[],
    EATS_BILLING_PROCESSOR_FEATURES={
        'tlog_write_enabled': {
            'agent': True,
            'expenses': True,
            'payments': True,
            'revenues': True,
        },
        'tlog_detailed_product_required': True,
    },
)
async def test_no_detailed_product_error(tlog_writer_fixtures):
    await (
        helper.TlogWriterTest()
        .with_rule('retail')
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
        .expect_fail()
        .run(tlog_writer_fixtures)
    )
