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
                mvp='SPBc',
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
            ignore_in_balance=True,
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
                country_code='RU',
                mvp='SPBc',
            ),
            refund=helper.refund_data(
                product_type='service_fee',
                amount='150',
                currency='RUB',
                payment_method='card',
                payment_terminal_id='222333',
            ),
        )
        .expect_refund(
            amount_with_vat='150',
            vat_amount='25',
            amount_without_vat='125',
            terminal_id=222333,
            paysys_type='alfa-bank',
            company_type='own_delivery',
            firm_id='32',
            product='eats_client_service_fee',
            detailed_product='eats_client_service_fee_payment',
            service_id=1167,
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
                country_code='RU',
                mvp='SPBc',
            ),
            commission=helper.commission_data(
                product_type='service_fee',
                amount='1200',
                currency='RUB',
                commission_type='service_fee',
            ),
        )
        .expect_payment(
            amount_with_vat='1200',
            vat_amount='200',
            amount_without_vat='1000',
            company_type='marketplace',
            firm_id='32',
            product='eats_client_service_fee',
            detailed_product='eats_client_service_fee',
            service_id=1167,
            ignore_in_balance=True,
        )
        .run(tlog_writer_fixtures)
    )


async def test_commission_return(tlog_writer_fixtures):
    await (
        helper.TlogWriterTest()
        .with_rule('restaurant')
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='RU',
                mvp='SPBc',
            ),
            commission=helper.commission_data(
                product_type='service_fee',
                amount='-1200',
                currency='RUB',
                commission_type='service_fee',
            ),
        )
        .expect_refund(
            amount_with_vat='1200',
            vat_amount='200',
            amount_without_vat='1000',
            company_type='own_delivery',
            firm_id='32',
            product='eats_client_service_fee',
            detailed_product='eats_client_service_fee',
            service_id=1167,
            ignore_in_balance=True,
        )
        .run(tlog_writer_fixtures)
    )


async def test_incentives(tlog_writer_fixtures):
    await (
        helper.TlogWriterTest()
        .with_rule('retail')
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='RU',
                mvp='SPBc',
            ),
            payment=helper.payment_data(
                product_type='service_fee',
                amount='150',
                currency='RUB',
                payment_method='corporate',
            ),
        )
        .expect_payment(
            amount_with_vat='150',
            vat_amount='25',
            amount_without_vat='125',
            company_type='retail_own_packing_and_delivery',
            firm_id='32',
            product='eats_b2b_coupon',
            detailed_product='eats_b2b_coupon_corporate',
            service_id=1167,
            ignore_in_balance=True,
        )
        .run(tlog_writer_fixtures)
    )
