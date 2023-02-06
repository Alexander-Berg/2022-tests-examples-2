from tests_eats_billing_processor.tlog_writer import helper

PATCH = {
    'external_payment_id': 'ooo',
    'client': {'id': '1111'},
    'payment': {'amount': '300'},
    'templates': [
        {
            'template_name': 'temp1',
            'context': {'amount': '100', 'currency': 'RUB'},
        },
        {
            'template_name': 'temp2',
            'context': {'amount': '200', 'currency': 'KZT', 'id': 1},
        },
    ],
}


async def test_reverse(tlog_writer_fixtures):
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
        )
        .on_reverse()
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
        .expect_refund(
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


async def test_patch(tlog_writer_fixtures):
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
        )
        .on_patch(PATCH)
        .expect_payment(
            client_id='1111',
            amount='300',
            terminal_id=222333,
            paysys_type='alfa-bank',
            company_type='retail_own_packing_and_delivery',
            firm_id='32',
            product='eats_payment',
            detailed_product='eats_payment',
            service_id=699,
            ignore_in_balance=True,
            template_entries=[
                {
                    'template_name': 'temp1',
                    'context': {'amount': '100', 'currency': 'RUB'},
                },
                {
                    'template_name': 'temp2',
                    'context': {'amount': '200', 'currency': 'KZT', 'id': 1},
                },
            ],
        )
        .run(tlog_writer_fixtures)
    )


async def test_reverse_and_patch(tlog_writer_fixtures):
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
        )
        .on_reverse()
        .on_patch(PATCH)
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
        .expect_refund(
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
        .expect_payment(
            client_id='1111',
            amount='300',
            terminal_id=222333,
            paysys_type='alfa-bank',
            company_type='retail_own_packing_and_delivery',
            firm_id='32',
            product='eats_payment',
            detailed_product='eats_payment',
            service_id=699,
            ignore_in_balance=True,
            template_entries=[
                {
                    'template_name': 'temp1',
                    'context': {'amount': '100', 'currency': 'RUB'},
                },
                {
                    'template_name': 'temp2',
                    'context': {'amount': '200', 'currency': 'KZT', 'id': 1},
                },
            ],
        )
        .run(tlog_writer_fixtures)
    )
