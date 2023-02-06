import pytest

from tests_eats_billing_processor.tlog_writer import helper


@pytest.mark.parametrize(
    'payment_type, product, detailed_product',
    [
        pytest.param(
            'marketing',
            'eats_marketing_coupon_picker',
            'eats_marketing_promotion_picker',
            id='Marketing promotion',
        ),
        pytest.param(
            'marketing_promocode',
            'eats_marketing_coupon_picker',
            'eats_marketing_promocode_picker',
            id='Marketing promocode',
        ),
        pytest.param(
            'compensation_promocode',
            'eats_support_coupon_picker',
            'eats_compensation_promocode_picker',
            id='Compensation promocode',
        ),
    ],
)
async def test_incentive(
        tlog_writer_fixtures, payment_type, product, detailed_product,
):
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
                product_type='assembly',
                amount='1200',
                currency='RUB',
                payment_terminal_id='553344',
                payment_method=payment_type,
            ),
        )
        .expect_payment(
            amount_with_vat='1200',
            vat_amount='0',
            amount_without_vat='1200',
            firm_id='32',
            product=product,
            detailed_product=detailed_product,
            service_id=699,
            ignore_in_balance=True,
            paysys_type='yaeda',
        )
        .run(tlog_writer_fixtures)
    )


@pytest.mark.parametrize(
    'rule',
    [
        pytest.param('restaurant'),
        pytest.param('retail'),
        pytest.param('shop'),
        pytest.param('marketplace'),
    ],
)
@pytest.mark.pgsql(
    'eats_billing_processor', files=['test_order_accounting_correction.sql'],
)
async def test_payment_accounting_correction(tlog_writer_fixtures, rule):
    await (
        helper.TlogWriterTest()
        .with_rule(rule)
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='RU',
                mvp='br_moscow_adm',
            ),
            payment=helper.payment_data(
                product_type='product',
                amount='1200',
                currency='RUB',
                payment_terminal_id='553344',
                payment_method='account_correction',
            ),
            payload={'correction_id': '1'},
        )
        .expect_payment(
            amount_with_vat='1200',
            vat_amount='0',
            amount_without_vat='1200',
            firm_id='32',
            product='eats_account_correction',
            detailed_product='eats_account_correction',
            service_id=629,
            ignore_in_balance=True,
            payload={'product': 'product'},
            paysys_type='yaeda',
        )
        .check_tlog_flag()
        .run(tlog_writer_fixtures)
    )


async def test_payment_mercury_discount(tlog_writer_fixtures):
    await (
        helper.TlogWriterTest()
        .with_rule('inplace')
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
                payment_terminal_id='553344',
                payment_method='inplace_coupons',
            ),
        )
        .expect_payment(
            amount_with_vat='150',
            vat_amount='0',
            amount_without_vat='150',
            firm_id='32',
            product='eats_inplace_coupons',
            detailed_product='eats_inplace_coupons',
            service_id=1176,
            ignore_in_balance=True,
            payload={'product': 'product'},
            paysys_type='yaeda',
        )
        .run(tlog_writer_fixtures)
    )
