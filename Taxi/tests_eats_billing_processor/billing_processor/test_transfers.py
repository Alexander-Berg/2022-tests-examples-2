import pytest

from tests_eats_billing_processor.billing_processor import helper


async def test_payment_service_id(billing_processor_fixtures):
    await (
        helper.BillingProcessorTest()
        .for_order_nr('123456-654321')
        .insert_billing_event(
            data=billing_processor_fixtures.load_json('billing_payment.json'),
        )
        .checking_columns('kind', 'service_id', 'product', 'paysys_partner_id')
        .expect_transfers(('payment', 629, 'goods', 'sberbank'))
        .run(billing_processor_fixtures)
    )


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_CUSTOM_PAYMENT_TYPES={
        'product__001': {'card': 'picker_card'},
    },
)
async def test_payment_with_custom_payment_type(billing_processor_fixtures):
    await (
        helper.BillingProcessorTest()
        .for_order_nr('123456-654321')
        .insert_billing_event(
            data=billing_processor_fixtures.load_json('billing_payment.json'),
        )
        .checking_columns('kind', 'payment_type')
        .expect_transfers(('payment', 'picker_card'))
        .run(billing_processor_fixtures)
    )


async def test_refund_service_id(billing_processor_fixtures):
    await (
        helper.BillingProcessorTest()
        .for_order_nr('123456-654321')
        .insert_billing_event(
            data=billing_processor_fixtures.load_json('billing_payment.json'),
        )
        .insert_billing_event(
            data=billing_processor_fixtures.load_json('billing_refund.json'),
        )
        .checking_columns('kind', 'service_id', 'paysys_partner_id')
        .expect_transfers(
            ('payment', 629, 'sberbank'), ('refund', 629, 'alfa-bank'),
        )
        .run(billing_processor_fixtures)
    )


async def test_commission_service_id(billing_processor_fixtures):
    await (
        helper.BillingProcessorTest()
        .for_order_nr('123456-654321')
        .insert_billing_event(
            data=billing_processor_fixtures.load_json(
                'billing_commission.json',
            ),
        )
        .checking_columns('kind', 'service_id', 'product')
        .expect_transfers(('commission', 628, 'goods'))
        .run(billing_processor_fixtures)
    )


async def test_commission_plus_cashback_service_id(billing_processor_fixtures):
    commission = billing_processor_fixtures.load_json(
        'billing_commission.json',
    )
    commission['commission']['product_id'] = 'plus_cashback_retail'
    await (
        helper.BillingProcessorTest()
        .for_order_nr('123456-654321')
        .insert_billing_event(data=commission)
        .checking_columns('kind', 'service_id', 'product')
        .expect_transfers(('commission', 661, 'native_delivery'))
        .run(billing_processor_fixtures)
    )


async def test_orig_id(billing_processor_fixtures):
    payment1 = billing_processor_fixtures.load_json('billing_payment.json')
    payment1['external_payment_id'] = 'another_payment'
    payment2 = billing_processor_fixtures.load_json('billing_payment.json')
    refund1 = billing_processor_fixtures.load_json('billing_refund.json')
    refund1['external_payment_id'] = 'another_payment'
    commission1 = billing_processor_fixtures.load_json(
        'billing_commission.json',
    )
    payment3 = billing_processor_fixtures.load_json('billing_payment.json')
    refund2 = billing_processor_fixtures.load_json('billing_refund.json')
    commission2 = billing_processor_fixtures.load_json(
        'billing_commission.json',
    )
    await (
        helper.BillingProcessorTest()
        .for_order_nr('123456-654321')
        .insert_billing_event(data=payment1)
        .insert_billing_event(data=payment2)
        .insert_billing_event(data=refund1)
        .insert_billing_event(data=commission1)
        .insert_billing_event(data=payment3)
        .insert_billing_event(data=refund2)
        .insert_billing_event(data=commission2)
        .checking_columns('kind', 'orig_id')
        .expect_transfers(
            ('payment', None),
            ('payment', None),
            ('refund', None),
            ('commission', 2),
            ('payment', None),
            ('refund', None),
            ('commission', 6),
        )
        .run(billing_processor_fixtures)
    )


async def test_orig_id_by_product(billing_processor_fixtures):
    payment1 = billing_processor_fixtures.load_json('billing_payment.json')
    payment2 = billing_processor_fixtures.load_json('billing_payment.json')
    payment2['payment']['product_type'] = 'delivery'
    payment2['payment']['product_id'] = 'delivery__001'
    refund1 = billing_processor_fixtures.load_json('billing_refund.json')
    refund1['refund']['product_type'] = 'delivery'
    refund1['refund']['product_id'] = 'delivery__001'
    payment3 = billing_processor_fixtures.load_json('billing_payment.json')
    refund2 = billing_processor_fixtures.load_json('billing_refund.json')
    commission = billing_processor_fixtures.load_json(
        'billing_commission.json',
    )
    commission['commission']['product_type'] = 'delivery'
    commission['commission']['product_id'] = 'delivery__001'
    await (
        helper.BillingProcessorTest()
        .for_order_nr('123456-654321')
        .insert_billing_event(data=payment1)
        .insert_billing_event(data=payment2)
        .insert_billing_event(data=refund1)
        .insert_billing_event(data=payment3)
        .insert_billing_event(data=refund2)
        .insert_billing_event(data=commission)
        .checking_columns('kind', 'orig_id')
        .expect_transfers(
            ('payment', None),
            ('payment', None),
            ('refund', None),
            ('payment', None),
            ('refund', None),
            ('commission', 3),
        )
        .run(billing_processor_fixtures)
    )
