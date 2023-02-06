import pytest

from tests_eats_billing_processor.tlog_writer import helper


@pytest.mark.parametrize(
    'payment_type, product, detailed_product, service_id',
    [
        pytest.param(
            'cashback',
            'eats_coupon_plus',
            'eats_coupon_plus',
            699,
            id='Plus coupon',
        ),
        pytest.param(
            'marketing',
            'eats_marketing_coupon',
            'eats_marketing_promotion',
            699,
            id='Marketing promotion',
        ),
        pytest.param(
            'marketing_promocode',
            'eats_marketing_coupon',
            'eats_marketing_promocode',
            699,
            id='Marketing promocode',
        ),
        pytest.param(
            'employee_PC',
            'eats_marketing_coupon_employee',
            'eats_marketing_coupon_employee',
            699,
            id='Employee promocode',
        ),
        pytest.param(
            'compensation_promocode',
            'eats_support_coupon',
            'eats_support_coupon',
            699,
            id='Compensation promocode',
        ),
        pytest.param(
            'corporate',
            'eats_b2b_coupon',
            'eats_b2b_coupon_corporate',
            645,
            id='Corporate',
        ),
        pytest.param(
            'paid_PC',
            'eats_b2b_coupon',
            'eats_b2b_coupon_paid_pc',
            645,
            id='Corporate promocode',
        ),
        pytest.param(
            'picker_corp',
            'eats_b2b_coupon_picker',
            'eats_b2b_coupon_picker',
            699,
            id='Picker coupon',
        ),
        pytest.param(
            'payment_not_received',
            'eats_payment_not_received',
            'eats_payment_not_received',
            699,
            id='Payment not received',
        ),
        pytest.param(
            'our_refund',
            'eats_our_refund',
            'eats_our_refund',
            699,
            id='Our refund',
        ),
    ],
)
async def test_retail_incentive(
        tlog_writer_fixtures,
        payment_type,
        product,
        detailed_product,
        service_id,
):
    await (
        helper.TlogWriterTest()
        .with_rule('retail')
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='RU',
                mvp='MSKc',
            ),
            payment=helper.payment_data(
                product_type='delivery',
                amount='1200',
                currency='RUB',
                payment_method=payment_type,
            ),
        )
        .expect_payment(
            amount_with_vat='1200',
            vat_amount='200',
            amount_without_vat='1000',
            firm_id='32',
            product=product,
            detailed_product=detailed_product,
            service_id=service_id,
            ignore_in_balance=True,
        )
        .run(tlog_writer_fixtures)
    )


@pytest.mark.parametrize(
    'payment_type, product, detailed_product, service_id',
    [
        pytest.param(
            'cashback',
            'eats_coupon_plus',
            'eats_coupon_plus',
            629,
            id='Plus coupon',
        ),
        pytest.param(
            'marketing',
            'eats_marketing_coupon',
            'eats_marketing_promotion',
            629,
            id='Marketing promotion',
        ),
        pytest.param(
            'marketing_promocode',
            'eats_marketing_coupon',
            'eats_marketing_promocode',
            629,
            id='Marketing promocode',
        ),
        pytest.param(
            'employee_PC',
            'eats_marketing_coupon_employee',
            'eats_marketing_coupon_employee',
            629,
            id='Employee promocode',
        ),
        pytest.param(
            'compensation_promocode',
            'eats_support_coupon',
            'eats_support_coupon',
            629,
            id='Compensation promocode',
        ),
        pytest.param(
            'corporate',
            'eats_b2b_coupon',
            'eats_b2b_coupon_corporate',
            645,
            id='Corporate',
        ),
        pytest.param(
            'paid_PC',
            'eats_b2b_coupon',
            'eats_b2b_coupon_paid_pc',
            645,
            id='Corporate promocode',
        ),
        pytest.param(
            'payment_not_received',
            'eats_payment_not_received',
            'eats_payment_not_received',
            629,
            id='Payment not received',
        ),
        pytest.param(
            'our_refund',
            'eats_our_refund',
            'eats_our_refund',
            629,
            id='Our refund',
        ),
    ],
)
async def test_restaurant_incentive(
        tlog_writer_fixtures,
        payment_type,
        product,
        detailed_product,
        service_id,
):
    await (
        helper.TlogWriterTest()
        .with_rule('restaurant')
        .on_billing_event(
            client=helper.client_info(
                client_id='12345',
                contract_id='55555',
                country_code='RU',
                mvp='MSKc',
            ),
            payment=helper.payment_data(
                product_type='delivery',
                amount='1200',
                currency='RUB',
                payment_method=payment_type,
            ),
        )
        .expect_payment(
            amount_with_vat='1200',
            vat_amount='200',
            amount_without_vat='1000',
            firm_id='32',
            product=product,
            detailed_product=detailed_product,
            service_id=service_id,
            ignore_in_balance=True,
        )
        .run(tlog_writer_fixtures)
    )
